# Pipeline Node Agents

A flexible framework for building AI agent pipelines using a modular node-based architecture.

## Overview

This project provides a pipeline system where tasks are executed as a sequence of **nodes**. Each node performs a specific function and passes its output to the next node in the pipeline.

### Key Features

- **Node Architecture**: Break down complex workflows into discrete, reusable function nodes
- **Adapter Pattern**: Easily integrate any existing AI agents or functions using adapters (e.g., `PythonFnAdapter`)
- **Pipeline Orchestration**: Chain nodes together to create sophisticated multi-step agent workflows
- **Extensible Design**: Add custom adapters to wrap LLMs, APIs, or any external services

## Project Structure

```
├── core/           # Core pipeline and node implementations
├── adapters/       # Adapters for integrating various functions/agents
└── examples/       # Example pipelines
```

## Running Examples

```bash
cd examples
python3 <name_of_example>.py
```

For example:
```bash
cd examples
python3 random_mean_pipeline.py
```
