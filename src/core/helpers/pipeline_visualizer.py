class PipelineVisualizer:
    """
    A helper class to visualize directed graphs (pipelines) in CLI,
    including loops.

    Edge format:
        dict[str, list[tuple[str, str]]]
        FromNode -> [(condition, ToNode), ...]
    """

    @staticmethod
    def _targets(edges: dict[str, list[tuple[str, str]]], node: str) -> list[str]:
        """
        Extract target nodes, ignoring conditions.
        """
        return [to_node for _, to_node in edges.get(node, [])]

    @staticmethod
    def visualize(
        edges: dict[str, list[tuple[str, str]]],
        start_node: str
    ) -> None:
        """
        Visualize a directed graph in CLI, including loops.
        """

        visited = set()
        stack = []
        main_path = []
        loop_edges = []

        current = start_node

        while current:
            if current in stack:
                loop_edges.append((stack[-1], current))
                break

            if current in visited:
                break

            visited.add(current)
            stack.append(current)
            main_path.append(current)

            next_nodes = PipelineVisualizer._targets(edges, current)
            current = next_nodes[0] if next_nodes else None

        side_branches: dict[str, list[str]] = {}
        for node in main_path:
            children = PipelineVisualizer._targets(edges, node)
            if len(children) > 1:
                side_branches[node] = children[1:]

        main_line = " -> ".join(main_path)
        print(main_line)

        for node, branches in side_branches.items():
            base_offset = main_line.index(node) + len(node)
            indent = " " * base_offset

            for branch in branches:
                print(f"{indent} |")
                branch_line, branch_loops = PipelineVisualizer._render_branch_with_loops(
                    branch, edges, visited
                )
                print(f"{indent} ----> {branch_line}")

                for loop in branch_loops:
                    print(f"{indent}        ↺ loop to {loop}")

        for src, target in loop_edges:
            offset = main_line.index(src) + len(src)
            indent = " " * offset
            print(f"{indent} ↺ loop to {target}")

    @staticmethod
    def _render_branch_with_loops(
        start: str,
        edges: dict[str, list[tuple[str, str]]],
        global_visited: set,
    ) -> tuple[str, list[str]]:
        """
        Render a branch and explicitly mark loops.
        """

        path = []
        stack = []
        loops = []

        current = start

        while current:
            if current in stack:
                loops.append(current)
                break

            if current in global_visited:
                loops.append(current)
                break

            stack.append(current)
            path.append(current)

            next_nodes = PipelineVisualizer._targets(edges, current)
            current = next_nodes[0] if next_nodes else None

        return " -> ".join(path), loops
