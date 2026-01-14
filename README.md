# Pipeline Node Agents

A lightweight Python framework for building modular AI pipelines with function nodes and agent nodes.

## Table of Contents

- [Key Features](#key-features)
- [Why This Framework?](#why-this-framework)
- [Requirements](#requirements)
- [Installation](#installation)
- [How to Run](#how-to-run)
  - [Option 1: Run an example directly](#option-1-run-an-example-directly)
  - [Option 2: Using Runner Scripts](#option-2-using-runner-scripts)
    - [Run a Single Pipeline](#run-a-single-pipeline)
    - [Run All Smoke Tests](#run-all-smoke-tests)
- [Maintenance Guide](#maintenance-guide)

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

## How to Run

> **Prerequisites:**
> 1. Start Ollama: `ollama serve`
> 2. Make sure the required model is installed using `ollama list` (as of December 3rd 2025, it's *llama3.2*)

### Option 1: Run an example directly

```bash
poetry run python3 examples/<example_name>.py
```

e.g.
```bash
poetry run python3 examples/random_mean_pipeline.py
```

### Option 2: Using Runner Scripts

> **Additional requirement:** All scripts in the `scripts/` folder must have execution permissions.
>
> If not, run:
> ```bash
> chmod +x scripts/*.sh
> ```

#### Run a Single Pipeline

```bash
./scripts/run_single_pipeline.sh <path_to_pipeline> <runs> [input_strings]
```

**Parameters:**
- `<path_to_pipeline>` - Path to the Python pipeline file
- `<runs>` - Number of times to run the pipeline
- `[input_strings]` - Optional: newline-separated inputs for interactive prompts

**Examples:**
```bash
# Run a simple pipeline 3 times
./scripts/run_single_pipeline.sh examples/random_mean_pipeline.py 3

# Run with single input
./scripts/run_single_pipeline.sh examples/input_checker_pipeline.py 2 "Munich, Vienna"

# Run with multiple inputs (use $'\n' to separate)
./scripts/run_single_pipeline.sh examples/trip_planner/pipeline.py 1 $'Paris, Rome\n15 June 2025\n22 June 2025'
```

#### Run All Smoke Tests

```bash
./scripts/run_smoke_pipelines.sh [number_of_runs_per_pipeline]
```

**Examples:**
```bash
# Run all example pipelines once
./scripts/run_smoke_pipelines.sh

# Run all example pipelines 3 times each
./scripts/run_smoke_pipelines.sh 3
```

Logs are automatically saved to `logs/` directory by the Python logging system.

## Maintenance Guide

For detailed maintenance instructions, including how to create nodes, build pipelines, and extend the framework, please refer to the [Maintenance Guide](docs/maintenance_guide.md).

