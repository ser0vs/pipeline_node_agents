from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    """Defines a unified interface for all adapters."""

    @abstractmethod
    def invoke(self, **kwargs) -> dict:
        """Executes the adapter and returns output as dict."""
        pass
