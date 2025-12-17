class Pipeline:
    """Executes nodes in a defined order and manages shared context."""

    def __init__(self, nodes=None, start_node=None):
        """
        Build a simple linear pipeline, if nodes are provided: node1 -> node2 -> node3 -> ...
        Otherwise, an empty pipeline is created.

        Args:
            nodes (list[Node], optional): List of nodes to form a linear pipeline.
        """
        self.nodes = {}
        self.edges = {}

        if nodes and len(nodes) > 0:
            self.start_node = start_node or nodes[0].name
            self._build_linear_pipeline(nodes)


    def add_node(self, node):
        self.nodes[node.name] = node

    def add_edge(self, from_node, to_node, condition=None):
        """
        condition: None | callable(context) -> bool
        """
        self.edges.setdefault(from_node, []).append((condition, to_node))

    def run(self, initial_context=None, start_node=None):
        context = initial_context or {}
        current_node = start_node or self.start_node

        print("=== Starting pipeline ===")
        print("List of nodes in the pipeline:")
        for node_name in self.nodes:
            print(f"→ {node_name}")
        print("List of edges in the pipeline:")
        for from_node, edges in self.edges.items():
            for condition, to_node in edges:
                cond_str = "unconditional" if condition is None else "conditional"
                print(f"→ {from_node} --({cond_str})--> {to_node}")


        while current_node:
            node = self.nodes[current_node]
            print(f"→ Running node: {node.name}")
            context = node.run(context)

            next_node = None
            for condition, target in self.edges.get(current_node, []):
                if condition is None or condition(context):
                    next_node = target
                    break

            current_node = next_node

        print("=== Pipeline finished ===")
        return context

    def _build_linear_pipeline(self, nodes):
        for node in nodes:
            self.add_node(node)

        for i in range(len(nodes) - 1):
            self.add_edge(
                from_node=nodes[i].name,
                to_node=nodes[i + 1].name,
                condition=None  # unconditional edge
            )

        self.start_node = nodes[0].name