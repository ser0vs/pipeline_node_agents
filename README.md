# Pipeline Node Agents

A lightweight Python framework for building modular AI pipelines with function nodes and agent nodes.

## Key Features

- **Modular architecture**: Compose pipelines from reusable function and agent nodes
- **Flexible flow control**: Support for linear pipelines, conditional branching, and loops
- **Adapter pattern**: Easy integration with different AI backends (CrewAI, LangChain, custom LLMs)
- **Nested pipelines**: Run sub-pipelines within nodes for complex workflows
- **Local LLM support**: Works with Ollama for fully offline AI pipelines

## Why This Framework?

- **Easy to maintain**: Clean separation between node logic, adapters, and pipeline orchestration
- **Easy to extend**: Add new adapters without modifying core pipeline logic
- **Easy to test**: Each node can be tested independently with mock adapters

## Project Structure

```
pipeline_node_agents/
├── src/
│   ├── core/
│   │   ├── node.py          # FunctionNode, AgentNode definitions
│   │   └── pipeline.py      # Pipeline orchestration
│   └── adapters/            # Adapters for different execution backends
├── examples/                # Example pipelines
├── pyproject.toml
└── README.md
```

## Requirements

- [Poetry](https://python-poetry.org/) for dependency management
- [Ollama](https://ollama.ai/) for local LLM support (optional, for AI agent nodes)

## Installation

1. **Install Poetry** (if not already installed):
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2. **Clone the repository and install dependencies**:
    ```bash
    cd pipeline_node_agents
    poetry lock
    poetry install --no-root
    ```

## Running Examples

1) Run Ollama
    ```bash
    ollama serve
    ```

> **Note:** Before the next step, make sure the corresponding model is installed using `ollama list` (as of December 3rd 2025, it's *llama3.2*)

2) Run an example:
    ```bash
    poetry run python3 examples/<example_name>.py
    ```
    e.g.
    ```bash
    poetry run python3 examples/random_mean_pipeline.py
    ```



## Usage

### Creating a Function Node

```python
from src.adapters.python_fn_adapter import PythonFnAdapter
from src.core.node import FunctionNode

def my_function(input_value: int) -> dict:
    return {"output_value": input_value * 2}

node = FunctionNode(
    name="MyNode",
    adapter=PythonFnAdapter(my_function),
    inputs=["input_value"],
    outputs=["output_value"]
)
```

### Creating an Agent Node

```python
from src.core.node import AgentNode

node = AgentNode(
    name="MyAgentNode",
    adapter=your_adapter,  # Use an appropriate adapter from src/adapters/
    inputs=["data"],
    outputs=["result"]
)
```

### Building a Pipeline

#### Option 1: Linear Pipeline (list of nodes)

For simple sequential pipelines, pass a list of nodes:

```python
from src.core.pipeline import Pipeline

pipeline = Pipeline(nodes=[node1, node2, node3])
result = pipeline.run(initial_context={"input_value": 5})
```

This creates edges: `node1 -> node2 -> node3`

#### Option 2: Graph-based Pipeline (start node + edges)

For pipelines with conditional branching or complex flows:

```python
from src.core.pipeline import Pipeline

# Create pipeline with a start node
pipeline = Pipeline(start_node=decision_node)

# Add additional nodes
pipeline.add_node(branch_a_node)
pipeline.add_node(branch_b_node)

# Add conditional edges
pipeline.add_edge(
    "DecisionNode",
    "BranchANode",
    condition=lambda ctx: ctx["choice"] == "A"
)
pipeline.add_edge(
    "DecisionNode",
    "BranchBNode",
    condition=lambda ctx: ctx["choice"] == "B"
)

result = pipeline.run(initial_context={"choice": "A"})
```

#### Merging Pipelines

You can merge an existing pipeline into another:

```python
sub_pipeline = Pipeline(nodes=[search_node, scrape_node, summarize_node])

main_pipeline = Pipeline(start_node=start_node)
main_pipeline.add_pipeline(sub_pipeline)
main_pipeline.add_edge("StartNode", "SearchNode")
```

#### Nested Pipelines

You can run a pipeline inside a function node for complex sub-workflows:

```python
def process_items(items: list[str]) -> dict:
    """Run a sub-pipeline for each item and aggregate results."""
    results = {}
    
    for item in items:
        # Define nodes for sub-pipeline
        # search_node = FunctionNode(...)
        # process_node = AgentNode(...)
        
        sub_pipeline = Pipeline(nodes=[search_node, process_node])
        result = sub_pipeline.run({"query": item})
        results[item] = result.get("output")
    
    return {"aggregated_results": results}

# Use the function as a node in the main pipeline
nested_node = FunctionNode(
    name="NestedPipelineNode",
    adapter=PythonFnAdapter(process_items),
    inputs=["items"],
    outputs=["aggregated_results"]
)

main_pipeline = Pipeline(nodes=[nested_node, final_node])
```

This pattern is useful when you need to dynamically run pipelines based on runtime data.

#### Edge Conditions

- **Unconditional edge**: `condition=None` (default) — always follows this edge
- **Conditional edge**: `condition=lambda ctx: <bool>` — follows edge only if condition returns `True`

When multiple edges exist from a node, the first edge whose condition evaluates to `True` is taken.

#### Creating Loops

To create loops, add an edge back to a previous node:

```python
pipeline.add_edge(
    "ProcessNode",
    "CheckNode",
    condition=lambda ctx: ctx["retry_count"] < 3
)
pipeline.add_edge(
    "CheckNode",
    "ProcessNode",
    condition=lambda ctx: not ctx["success"]
)
pipeline.add_edge(
    "CheckNode",
    "FinalNode",
    condition=lambda ctx: ctx["success"]
)
```

