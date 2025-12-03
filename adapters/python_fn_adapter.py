from adapters.base_adapter import BaseAdapter

class PythonFnAdapter(BaseAdapter):
    """Adapter for wrapping simple Python functions."""

    def __init__(self, fn):
        self.fn = fn

    def invoke(self, **kwargs) -> dict:
        result = self.fn(**kwargs)
        if not isinstance(result, dict):
            raise ValueError("Function must return a dictionary of outputs.")
        return result