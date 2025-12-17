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
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter



def flip_coin() -> bool:
    """Flip a coin and return True (heads) or False (tails)."""
    choice = random.choice([True, False])
    # choice = False  # For testing purposes, always go to cinema
    print(f"[DecisionNode] Coin flip result: {'True -> Going to park!' if choice else 'False -> Going to cinema!'}")
    return {"decision": choice}


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


def scrape_website(url: str, timeout: int = 10, max_attempts: int = 5) -> dict:
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


# --- Function Node: Chunk Text ---
def chunk_text(page_content: str, chunk_size: int = 8000, overlap: int = 200) -> dict:
    chunks = []
    start = 0
    length = len(page_content)

    while start < length:
        end = start + chunk_size
        chunks.append(page_content[start:end])
        start = end - overlap

    return {"chunks": chunks}


# --- CrewAI Node: Summarize results ---
ollama_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434"
)

cinema_expert_agent = Agent(
    name="CinemaExpertAgent",
    role="Expert in cinema and film recommendations.",
    goal="Provide the best film recommendation based on text content.",
    backstory="You are a highly skilled cinema expert.",
    llm=ollama_llm
)

local_expert_agent = Agent(
    name="LocalExpertAgent",
    role="Local Expert in defined city.",
    goal="Provide the best recommendation where to go in defined city based on text content.",
    backstory="You are a highly skilled local expert of defined city.",
    llm=ollama_llm
)

def main():
    decision_node = FunctionNode(
        name="DecisionNode",
        adapter=PythonFnAdapter(flip_coin),
        inputs=[],
        outputs=["decision"]
    )


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
        adapter=PythonFnAdapter(scrape_website),
        inputs=["url"],
        outputs=["page_content"]
    )

    local_expert_node = AgentNode(
        name="LocalExpertNode",
        adapter=CrewAIAdapter(
            local_expert_agent,
            task_description="Recommend places based on provided context to go in defined city.",
            expected_output="2-3 top places of this city with short descriptions."
        ),
        inputs=["city", "type_of_place"],
        outputs=["summary"]
    )

    cinema_expert_node = AgentNode(
        name="CinemaExpertNode",
        adapter=CrewAIAdapter(
            cinema_expert_agent,
            task_description="Analyze the provided text content and recommend a film to go in cinema.",
            expected_output="A single film recommendation with 2-3 highlights of this film."
        ),
        inputs=["page_content"],
        outputs=["summary"]
    )


    main_pipeline = Pipeline(start_node=decision_node)
    main_pipeline.add_node(decision_node)
    main_pipeline.add_node(local_expert_node)
    main_pipeline.add_pipeline(Pipeline(nodes=[search_node, extract_url_node, scrape_node, cinema_expert_node]))

    main_pipeline.add_edge(
        "DecisionNode",
        "LocalExpertNode",
        condition=lambda ctx: ctx["decision"] is True
    )
    main_pipeline.add_edge(
        "DecisionNode",
        "DuckDuckGoSearchNode",
        condition=lambda ctx: ctx["decision"] is False
    )

    context = {"query": "imdb showtimes", "max_results": 5, "city": "Vienna", "type_of_place": "parks"}
    result = main_pipeline.run(context)

    time.sleep(0.1)
    sys.stdout = sys.__stdout__ 
    sys.stderr = sys.__stderr__

    print("\n✅ Final Pipeline Output:")
    print(result.get("summary"))



if __name__ == "__main__":
    main()