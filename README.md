# Pipeline Node Agents

A framework for building pipelines with function nodes and AI agent nodes.

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

```python
from src.core.pipeline import Pipeline

pipeline = Pipeline(nodes=[node1, node2])
result = pipeline.run(initial_context={"input_value": 5})
```

