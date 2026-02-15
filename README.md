# Pipeline Node Agents

A lightweight Python framework for building modular AI pipelines with function nodes and agent nodes. Designed to work well with lightweight local LLMs by giving you full control over context and task complexity at each step.

## Usage Guide

### Requirements

- OS: Ubuntu 20.04 or later
- RAM: 8 GB minimum (16 GB recommended)
- Disk: 10 GB free space
- **curl** (any recent version)
- **Python 3.11 - 3.13**


### 1) Setup Ollama
- **Install Ollama** (if not already installed):
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```

- **Run Ollama in a separate terminal**:
    ```bash
    ollama serve
    ```

- **Install LLM** (default: `llama3.2:latest`):
    ```bash
    ollama pull llama3.2:latest
    ```

- **Make sure** the required LLM is installed using command:
    ```bash
    ollama list
    ```

Expected output:
```bash
NAME                ID              SIZE     MODIFIED
llama3.2:latest     9f1c3d6a5b8e    2.0 GB   1 minute ago
```

### 2) Install Package

- *(Optional, but recommended)* create python virtual environment:
    ```bash
    python3 -m venv .venv && source .venv/bin/activate
    ```

- Install package:
    ```bash
    pip install pipeline-node-agents
    ```


### 3) Verify Installation

```python
from pipeline_node_agents import greet

print(greet())
```

Expected output:
```
Hello, World! Pipeline Node Agents <version> is working.
```

### 4) Run Pipelines

#### Option 1: With defined model and logger (recommended)
```python
from crewai import LLM
from pipeline_node_agents import init_pipeline_logger, get_logger, TripPlannerPipeline

init_pipeline_logger(pipeline_name="trip_planner_pipeline", project_root=".")
logger = get_logger(__name__)

# Default model is llama3.2, change if needed
ollama_llm = LLM(model="ollama/llama3.2", base_url="http://localhost:11434")

pipeline = TripPlannerPipeline(ollama_llm=ollama_llm, logger=logger)
pipeline.run()
```

#### Option 2: Without logger
```python
from pipeline_node_agents import TripPlannerPipeline

# Default model is llama3.2
pipeline = TripPlannerPipeline()
pipeline.run()
```

#### Available tools configuration

As default, agent nodes work as pure LLMs (without tools). You can allow them to search for information by themselves. 

> **Note:** Usage of tools is not recommended for light-weight LLMs (<8 billion hyperparameters).

To enable tools for specific agents in `TripPlannerPipeline`:

1. Enable tools for local expert agent only:
    ```python
    pipeline = TripPlannerPipeline(local_expert_tools_enabled=True)
    ```

2. Enable tools for travel concierge agent only:
    ```python
    pipeline = TripPlannerPipeline(travel_concierge_tools_enabled=True)
    ```

3. Enable tools for both agents:
    ```python
    pipeline = TripPlannerPipeline(local_expert_tools_enabled=True, travel_concierge_tools_enabled=True)
    ```


#### Available pipelines

The following pipelines are included as examples:

- `ConditioningPipeline`: Randomly chooses whether to go to a park or cinema, and suggests either a film or a park in Vienna.

- `InputCheckerPipeline`: Takes text as input and returns true if the text is a list of populated places (cities). Can be run as a loop, returning to the input step as long as the input is invalid: `pipeline.run(loop=True)`

- `RandomMeanPipeline`: Simple pipeline without LLM usage that generates random numbers and calculates their mean.

- `RandomMeanPipelineCrewAI`: Generates random numbers and summarizes them using an LLM.

- `SearchAndSummarizePipeline`: Searches for the best country for business using DuckDuckGo and summarizes results using an LLM, returning the best country for business.

- `TripPlannerPipeline`: Takes a list of cities and trip dates as input, chooses the city based on weather conditions, and creates a full 7-day trip itinerary for the provided dates.

To run one of them, replace "TripPlannerPipeline" in the code example with a class from the list above.

Example with `SearchAndSummarizePipeline`:
```python
from pipeline_node_agents import SearchAndSummarizePipeline
pipeline = SearchAndSummarizePipeline()
pipeline.run()
```



## Maintenance Guide


### Creating a Custom Tool

The `tools/` directory provides utility classes for operations used by pipeline nodes. Tools are implemented as simple static methods within classes.

To create a custom tool, define a class with static methods:

```python
# filepath: pipeline_node_agents/src/pipeline_node_agents/tools/subtractor.py
class Subtractor:
    @staticmethod
    def subtract(a: float, b: float) -> float:
        """Subtract two numbers and return the difference."""
        return a - b
```

### Using Custom Tools in FunctionNode

Once created, integrate your tool into a `FunctionNode`:

```python
# main file
from pipeline_node_agents import PythonFnAdapter
from pipeline_node_agents.core.node import FunctionNode
from pipeline_node_agents.tools.subtractor import Subtractor

subtraction_node = FunctionNode(
    name="SubtractionNode",
    adapter=PythonFnAdapter(Subtractor.subtract),
    inputs=["number_a", "number_b"],
    output="difference"
)
```

### Using Custom Tools in AgentNode (example with CrewAI)

For agent nodes, tools must be wrapped using CrewAI's `@tool` decorator:
```python
# filepath: pipeline_node_agents/src/pipeline_node_agents/tools/subtractor_crewai.py
from crewai.tools import tool

class CrewAISubtractor:
    @staticmethod
    @tool("Subtract two numbers")
    def subtract(a: float, b: float) -> float:
        """Calculate the difference between two numbers."""
        return a - b
```


```python
# main file
from crewai import Agent
from pipeline_node_agents.core.node import AgentNode
from pipeline_node_agents.adapters.crewai_adapter import CrewAIAdapter
from pipeline_node_agents.core.tools.subtractor_crewai import CrewAISubtractor

agent = Agent(
    name="Calculator Agent",
    role="Math Assistant",
    goal="Perform calculations",
    backstory="A helpful math assistant",
    tools=[CrewAISubtractor.subtract],
    llm=ollama_llm
)

node = AgentNode(
    name="MyAgentNode",
    adapter=CrewAIAdapter(agent=agent, task_description="Perform the calculation"),
    inputs=["data"],
    output="result"
)
```

For other maintenance aspects such as creating nodes, building pipelines, and extending the framework, refer to the full [Maintenance Guide](docs/maintenance_guide.md).
