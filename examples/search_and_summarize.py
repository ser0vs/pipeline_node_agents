import random, os, sys
import time, json, requests

os.environ["OLLAMA_HOST"] = "http://localhost:11434"

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from src.adapters.python_fn_adapter import PythonFnAdapter
from src.adapters.crewai_adapter import CrewAIAdapter
from src.core.node import FunctionNode, AgentNode
from src.core.pipeline import Pipeline
from crewai import Agent, LLM
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup


def extract_first_url(search_results: list) -> dict:
    """Extract the first URL from search results."""
    if search_results and len(search_results) > 0:
        return {"url": search_results[0]["url"]}
    raise ValueError("No search results to extract URL from")


# --- Function Node: DuckDuckGo Search ---
def duckduckgo_search(query: str, max_results: int = 5) -> dict:
    max_attempts = 5
    with DDGS() as ddgs:
        for attempt in range(max_attempts):
            try:
                results = ddgs.text(
                    keywords=query,
                    max_results=max_results
                )

                parsed = [
                    {
                        "title": r.get("title"),
                        "snippet": r.get("body"),
                        "url": r.get("href")
                    }
                    for r in results
                ]

                return {"search_results": parsed}

            except Exception as e:
                print(f"Retry due to: {e}")
                time.sleep(1.2 * (attempt + 1))

        raise RuntimeError("DuckDuckGo search failed after retries")


def scrape(url: str, timeout: int = 10, max_attempts: int = 5) -> dict:
    """
    Scrape textual content from a website with retries.

    Returns:
        { "page_content": str }
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; NodeAgents007/1.0)"
    }

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")

            for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
                tag.decompose()

            text = soup.get_text(separator=" ", strip=True)
            text = " ".join(text.split())

            return {"page_content": text}

        except Exception as e:
            print(f"[Scraper] Attempt {attempt}/{max_attempts} failed: {e}")
            time.sleep(1)

    raise RuntimeError(f"Failed to scrape {url} after {max_attempts} attempts")



# --- CrewAI Node: Summarize results ---
ollama_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434"
)

analyst_agent = Agent(
    name="AnalystAgent",
    role="Expert business analyst.",
    goal="Provide the best country for business based on text content.",
    backstory="You are a highly skilled business analyst.",
    llm=ollama_llm
)

def main():
    search_node = FunctionNode(
        name="DuckDuckGoSearchNode",
        adapter=PythonFnAdapter(duckduckgo_search),
        inputs=["query", "max_results"],
        outputs=["search_results"]
    )
    
    extract_url_node = FunctionNode(
        name="ExtractUrlNode",
        adapter=PythonFnAdapter(extract_first_url),
        inputs=["search_results"],
        outputs=["url"]
    )
    
    scrape_node = FunctionNode(
        name="ScrapeNode",
        adapter=PythonFnAdapter(scrape),
        inputs=["url"],
        outputs=["page_content"]
    )


    analyst_node = AgentNode(
        name="AnalystNode",
        adapter=CrewAIAdapter(
            analyst_agent,
            task_description="Analyze the provided text content and determine the best country for business. Explain your reasoning based on the information given.",
            expected_output="A single country recommendation with 2-3 bullet points explaining why it's the best choice."
        ),
        inputs=["page_content"],
        outputs=["summary"]
    )

    pipeline = Pipeline(nodes=[search_node, extract_url_node, scrape_node, analyst_node])

    context = {"query": "best country for business", "max_results": 5}
    result = pipeline.run(context)

    # Workaround for Rich FileProxy recursion issue
    time.sleep(0.1)
    sys.stdout = sys.__stdout__ 
    sys.stderr = sys.__stderr__

    print("\n✅ Final Pipeline Output:")
    print(result.get("summary"))



if __name__ == "__main__":
    main()