from abc import ABC, abstractmethod
from src.adapters.base_adapter import BaseAdapter
from src.core.logging_config import get_logger

logger = get_logger(__name__)

class Node(ABC):
    """Abstract base class for all nodes in the pipeline."""
    def __init__(self, name, inputs=None, outputs=None, adapter=None):
        self.name = name
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.adapter = adapter

    @abstractmethod
    def run(self, context: dict) -> dict:
        """Execute the node logic using given context."""
        pass


class AgentNode(Node):
    def __init__(self, name: str, adapter: BaseAdapter, inputs: list[str], outputs: list[str] = None):
        self.name = name
        self.adapter = adapter
        self.inputs = inputs
        self.outputs = outputs or []

    def run(self, context: dict) -> dict:
        input_data = {k: context[k] for k in self.inputs}
        
        result = self.adapter.invoke(**input_data)

        context.update(result)
        return context

class FunctionNode(Node):
    """Node executing a deterministic Python function via adapter."""
    def run(self, context: dict) -> dict:
        input_data = {key: context[key] for key in self.inputs if key in context}

        result = self.adapter.invoke(**input_data)

        context.update(result)
        logger.info(f"[FunctionNode] {self.name} executed. Outputs: {result}")
        return context
