import random, os, sys, time


import os
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
from src.core.logger_bootstrap import init_pipeline_logger
from src.core.logging_config import get_logger

init_pipeline_logger(pipeline_name="random_mean_pipeline")
logger = get_logger(__name__)


# --- Function Node 1: Generate random numbers ---
def generate_random_numbers(limit: int) -> dict:
    numbers = [random.uniform(0, limit) for _ in range(10)]
    return {"random_numbers": numbers}

# --- CrewAI Node 2: Summarize numbers ---
ollama_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434"
)

number_summary_agent = Agent(
    name="NumberSummaryAgent",
    role="Expert in statistics",
    goal="Receive a list of numbers and return a brief textual summary",
    backstory="Expert in statistics and data analysis with years of experience.",
    llm=ollama_llm
)

def main():
    # Node 1: Generate random numbers
    node1 = FunctionNode(
        name="RandomNumberGenerator",
        adapter=PythonFnAdapter(generate_random_numbers),
        inputs=["limit"],
        outputs=["random_numbers"]
    )

    # Node 2: CrewAI summarization
    node2 = AgentNode(
        name="NumberSummaryNode",
        adapter=CrewAIAdapter(number_summary_agent),
        inputs=["random_numbers"],
        outputs=["summary"]
    )

    pipeline = Pipeline(nodes=[node1, node2])

    context = {"limit": 5}

    start_time = time.perf_counter()
    result = pipeline.run(context)
    elapsed_time = time.perf_counter() - start_time

    print(f"\n⏱️  Execution time: {elapsed_time:.2f} seconds")

    time.sleep(0.1)
    sys.stdout = sys.__stdout__ 
    sys.stderr = sys.__stderr__

    print("\n✅ Final Pipeline Output:")
    print(result.get("summary"))

    logger.info(f"✅Final Pipeline Output:\n{result.get('summary')}")
    logger.info(f"⏱️  Execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()