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
from src.tools.scraper import Scraper
from src.tools.websearch import WebSearcher
from src.core.logger_bootstrap import init_pipeline_logger
from src.core.logging_config import get_logger

init_pipeline_logger(pipeline_name="conditioning_pipeline")
logger = get_logger(__name__)


def flip_coin() -> bool:
    """Flip a coin and return True (heads) or False (tails)."""
    choice = random.choice([True, False])
    logger.info(f"[DecisionNode] Coin flip result: {'True -> Going to park!' if choice else 'False -> Going to cinema!'}")
    return {"decision": choice}



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
        adapter=PythonFnAdapter(WebSearcher.duckduckgo_search),
        inputs=["query", "max_results"],
        outputs=["search_results"]
    )
    
    
    scrape_node = FunctionNode(
        name="ScrapeNode",
        adapter=PythonFnAdapter(Scraper.scrape),
        inputs=["search_results"],
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
    main_pipeline.add_pipeline(Pipeline(nodes=[search_node, scrape_node, cinema_expert_node]))

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

    # default query: imdb showtimes
    context = {"query": "imdb showtimes", "max_results": 5, "city": "Vienna", "type_of_place": "parks"}
    
    start_time = time.perf_counter()
    result = main_pipeline.run(context)
    elapsed_time = time.perf_counter() - start_time

    time.sleep(0.1)
    sys.stdout = sys.__stdout__ 
    sys.stderr = sys.__stderr__

    print("\n✅ Final Pipeline Output:")
    print(result.get("summary"))
    print(f"\n⏱️  Execution time: {elapsed_time:.2f} seconds")

    logger.info(f"✅Final Pipeline Output: {result.get('summary')}")
    logger.info(f"⏱️  Execution time: {elapsed_time:.2f} seconds")



if __name__ == "__main__":
    main()