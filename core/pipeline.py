class Pipeline:
    """Executes nodes in a defined order and manages shared context."""

    def __init__(self, nodes):
        self.nodes = nodes

    def run(self, initial_context=None):
        context = initial_context or {}
        print("=== Starting pipeline ===")
        for node in self.nodes:
            print(f"→ Running node: {node.name}")
            context = node.run(context)
        print("=== Pipeline finished ===")
        return context
