"""Pipeline Node Agents - A framework for building LLM-powered pipelines."""

from pipeline_node_agents.core.node import FunctionNode, AgentNode
from pipeline_node_agents.core.pipeline import Pipeline

__version__ = "0.1.1"
__all__ = ["FunctionNode", "AgentNode", "Pipeline", "greet"]


def greet(name: str = "World") -> str:
    """Simple greeting function to verify the package works."""
    return f"Hello, {name}! Pipeline Node Agents v{__version__} is working."
