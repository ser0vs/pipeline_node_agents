import random, os, sys
import time, json, requests
import argparse

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

init_pipeline_logger(pipeline_name="input_checker_pipeline")
logger = get_logger(__name__)



def get_user_input(input_parameters: dict[str, str]) -> str:
    """
    Get string input fields from user.
    
    Args:
        input_parameters: dict mapping parameter names to their descriptions
        
    Returns:
        dict mapping parameter names to user-provided values
    """
    result = {}
    for name, description in input_parameters.items():
        value = input(description + ": ")
        result[name] = value
    return result

def get_validation_result(validation_summary: str) -> bool:
    is_valid = "false" not in validation_summary.lower()
    return is_valid


# --- CrewAI Node: Summarize results ---
ollama_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434"
)

input_validator_agent = Agent(
    name="GeographicalExpertAgent",
    role="Expert in geographical locations and settlements.",
    goal="Check whether the provided list of cities are real settlements on Earth.",
    backstory="You are a highly skilled geographical expert.",
    llm=ollama_llm
)

def main():
    parser = argparse.ArgumentParser(description="Input checker pipeline")
    parser.add_argument("--loop", type=lambda x: x.lower() == 'true', default=False, help="Enable loopback to UserInputNode if input is invalid (True/False)")
    args = parser.parse_args()

    user_input_node = FunctionNode(
        name="UserInputNode",
        adapter=PythonFnAdapter(get_user_input),
        inputs=["input_parameters"],
        output="list_of_cities"
    )

    input_validator_node = AgentNode(
        name="InputValidatorNode",
        adapter=CrewAIAdapter(
            input_validator_agent,
            task_description="Validate this statement: 'In the LIST_OF_CITIES all entries are populated places.' Say whether it is True or False.",
            expected_output="Brief explanation of the validation result. The last word MUST contain either 'True' or 'False' based on the validity of the statement."
        ),
        inputs=["list_of_cities"],
        output="validation_summary"
    )

    input_validation_result_node = FunctionNode(
        name="InputValidationResultNode",
        adapter=PythonFnAdapter(get_validation_result),
        inputs=["validation_summary"],
        output="is_valid"
    )

    main_pipeline = Pipeline(nodes=[user_input_node, input_validator_node, input_validation_result_node])
    
    if args.loop:
        main_pipeline.add_edge(
            "InputValidationResultNode",
            "UserInputNode",
            condition=lambda ctx: ctx.get("is_valid") == False
        )

    context = {"input_parameters": {"list_of_cities": "Enter list of cities"}}
    
    start_time = time.perf_counter()
    result = main_pipeline.run(context)
    elapsed_time = time.perf_counter() - start_time

    time.sleep(0.1)
    sys.stdout = sys.__stdout__ 
    sys.stderr = sys.__stderr__

    print("\n✅ Final Pipeline Output:")
    print("Validation summary:", result.get("validation_summary"))
    print(f"\n⏱️  Execution time: {elapsed_time:.2f} seconds\n")
    print("Is input valid:", result.get("is_valid"))
    
    logger.info(f"⏱️  Execution time: {elapsed_time:.2f} seconds")
    logger.info(f"✅Final Pipeline Output:\n validation_summary: {result.get('validation_summary')}\n is_valid: {result.get('is_valid')}")
    



if __name__ == "__main__":
    main()