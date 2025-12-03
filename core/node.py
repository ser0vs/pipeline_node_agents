from abc import ABC, abstractmethod

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
    """Node wrapping an AI agent (e.g., CrewAI or local LLM)."""
    def run(self, context: dict) -> dict:
        # TODO: Implement later when integrating CrewAI/Ollama
        raise NotImplementedError("AgentNode execution is not yet implemented.")


class FunctionNode(Node):
    """Node executing a deterministic Python function via adapter."""
    def run(self, context: dict) -> dict:
        input_data = {key: context[key] for key in self.inputs if key in context}

        result = self.adapter.invoke(**input_data)

        context.update(result)
        print(f"[FunctionNode] {self.name} executed. Outputs: {result}")
        return context
