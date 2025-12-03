import os, sys, random, time
from statistics import mean

# Ensure project root is on sys.path when running this file directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.node import FunctionNode
from adapters.python_fn_adapter import PythonFnAdapter
from core.pipeline import Pipeline


# --- Function Node 1: Generate random numbers ---
def generate_random_numbers(limit: int) -> dict:
    """Generates 10 random numbers between 0 and `limit`."""
    numbers = [random.uniform(0, limit) for _ in range(10)]
    time.sleep(1)
    return {"random_numbers": numbers}


# --- Function Node 2: Compute mean ---
def calculate_mean(random_numbers: list) -> dict:
    """Calculates the mean of 10 random numbers."""
    result = mean(random_numbers)
    time.sleep(3)
    return {"mean_value": result}


def main():
    # Create Function Nodes
    node1 = FunctionNode(
        name="RandomNumberGenerator",
        adapter=PythonFnAdapter(generate_random_numbers),
        inputs=["limit"],
        outputs=["random_numbers"]
    )

    node2 = FunctionNode(
        name="MeanCalculator",
        adapter=PythonFnAdapter(calculate_mean),
        inputs=["random_numbers"],
        outputs=["mean_value"]
    )

    # Build and run pipeline
    pipeline = Pipeline(nodes=[node1, node2])
    result = pipeline.run(initial_context={"limit": 5})

    print("\n✅ Final Pipeline Output:")
    print(result)


if __name__ == "__main__":
    main()