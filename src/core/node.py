from abc import ABC, abstractmethod
from src.adapters.base_adapter import BaseAdapter


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
    def __init__(self, name: str, adapter: BaseAdapter, inputs: list[str], outputs: list[str], messages_template: list[dict] | None = None):
        self.name = name
        self.adapter = adapter
        self.inputs = inputs
        self.outputs = outputs
        self.messages_template = messages_template

    def run(self, context: dict) -> dict:
        input_data = {k: context[k] for k in self.inputs}
        
        if self.messages_template:
            result = self.adapter.invoke(messages_template=self.messages_template, **input_data)
        else:
            result = self.adapter.invoke(**input_data)

        context.update(result)
        return context

class FunctionNode(Node):
    """Node executing a deterministic Python function via adapter."""
    def run(self, context: dict) -> dict:
        input_data = {key: context[key] for key in self.inputs if key in context}

        result = self.adapter.invoke(**input_data)

        context.update(result)
        print(f"[FunctionNode] {self.name} executed. Outputs: {result}")
        return context
