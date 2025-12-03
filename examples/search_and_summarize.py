import random, os, sys
import time, json

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



# --- Function Node 1: DuckDuckGo Search ---
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




# --- CrewAI Node 2: Summarize numbers ---
ollama_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434"
)

number_summary_agent = Agent(
    name="NumberSummaryAgent",
    role="Expert in weather data analysis",
    goal="Receive search results and return a brief summary",
    backstory="Expert in weather data analysis with years of experience.",
    llm=ollama_llm
)

def main():
    # Node 1: DuckDuckGo Search
    search_node = FunctionNode(
        name="DuckDuckGoSearchNode",
        adapter=PythonFnAdapter(duckduckgo_search),
        inputs=["query", "max_results"],
        outputs=["search_results"]
    )
    # Node 2: CrewAI summarization
    summary_node = AgentNode(
        name="NumberSummaryNode",
        adapter=CrewAIAdapter(number_summary_agent),
        inputs=["search_results"],
        outputs=["summary"]
    )

    pipeline = Pipeline(nodes=[search_node, summary_node])

    context = {"query": "weather today", "max_results": 5}
    result = pipeline.run(context)

    # Workaround for Rich FileProxy recursion issue
    time.sleep(0.1)
    sys.stdout = sys.__stdout__ 
    sys.stderr = sys.__stderr__

    print("\n✅ Final Pipeline Output:")
    print(result.get("summary"))


if __name__ == "__main__":
    main()