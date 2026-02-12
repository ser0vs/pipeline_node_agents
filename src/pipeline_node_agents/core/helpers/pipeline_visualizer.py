import traceback


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
    ) -> str:
        """
        Visualize a directed graph in CLI, including loops.
        Returns the visualization as a string.
        """
        try:
            main_path, visited, loop_edges = PipelineVisualizer._walk_main_path(edges, start_node)
            side_branches = PipelineVisualizer._find_side_branches(edges, main_path)
            main_line = PipelineVisualizer._render_main_line(main_path)
            lines = [main_line]
            lines.append(PipelineVisualizer._render_side_branches(edges, side_branches, main_line, visited))
            lines.append(PipelineVisualizer._render_main_loops(loop_edges, main_line))
            content = "\n".join(line for line in lines if line)
            max_width = max(len(line) for line in content.split("\n")) if content else 0
            frame_width = max_width + 4
            frame = "┌" + "─" * (frame_width - 2) + "┐\n"
            frame += "\n".join(f"│ {line.ljust(max_width)} │" for line in content.split("\n"))
            frame += "\n└" + "─" * (frame_width - 2) + "┘"
            return frame
        except Exception as e:
            return f"Error: {e}\n{traceback.format_exc()}\nUnable to visualize the pipeline due to unexpected error"



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

    @staticmethod
    def _walk_main_path(
        edges: dict[str, list[tuple[str, str]]],
        start_node: str,
    ) -> tuple[list[str], set[str], list[tuple[str, str]]]:
        """
        Follow the first outgoing edge from the start to build the main path.
        Detect a single loop edge if encountered.
        Returns (main_path, visited, loop_edges).
        """

        visited: set[str] = set()
        stack: list[str] = []
        main_path: list[str] = []
        loop_edges: list[tuple[str, str]] = []

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

        return main_path, visited, loop_edges

    @staticmethod
    def _find_side_branches(
        edges: dict[str, list[tuple[str, str]]],
        main_path: list[str],
    ) -> dict[str, list[str]]:
        """
        For each node in main path, collect additional children beyond the first.
        """
        side_branches: dict[str, list[str]] = {}
        for node in main_path:
            children = PipelineVisualizer._targets(edges, node)
            if len(children) > 1:
                side_branches[node] = children[1:]
        return side_branches

    @staticmethod
    def _render_main_line(main_path: list[str]) -> str:
        """
        Render the main path as a single CLI line.
        """
        return " -> ".join(main_path)

    @staticmethod
    def _render_side_branches(
        edges: dict[str, list[tuple[str, str]]],
        side_branches: dict[str, list[str]],
        main_line: str,
        visited: set[str],
    ) -> str:
        """
        Render side branches and their loop annotations as a string.
        """
        lines = []
        for node, branches in side_branches.items():
            base_offset = main_line.index(node) + len(node)
            indent = " " * base_offset

            for branch in branches:
                lines.append(f"{indent} |")
                branch_line, branch_loops = PipelineVisualizer._render_branch_with_loops(
                    branch, edges, visited
                )
                lines.append(f"{indent} ----> {branch_line}")

                for loop in branch_loops:
                    lines.append(f"{indent}        ↺ loop to {loop}")
        return "\n".join(lines)

    @staticmethod
    def _render_main_loops(
        loop_edges: list[tuple[str, str]],
        main_line: str,
    ) -> str:
        """
        Render loop edges detected on the main path as a string.
        """
        lines = []
        for src, target in loop_edges:
            offset = main_line.index(src) + len(src)
            indent = " " * offset
            lines.append(f"{indent} ↺ loop to {target}")
        return "\n".join(lines)



def main() -> None:
    test_cases = [
        (
            "Test 1: Simple linear pipeline",
            {
                "Start": [("c1", "A")],
                "A": [("c2", "B")],
                "B": [("c3", "C")],
                "C": [],
            },
            "Start",
        ),
        (
            "Test 2: Conditional branching without loops",
            {
                "Start": [("c1", "A")],
                "A": [("c2", "B"), ("c3", "X")],
                "B": [("c4", "C")],
                "C": [],
                "X": [("c5", "Y")],
                "Y": [],
            },
            "Start",
        ),
        (
            "Test 3: Loop on the main path",
            {
                "Start": [("c1", "A")],
                "A": [("c2", "B")],
                "B": [("c3", "C")],
                "C": [("c4", "A")],
            },
            "Start",
        ),
        (
            "Test 4: Loop inside a side branch",
            {
                "Start": [("c1", "A")],
                "A": [("c2", "B"), ("c3", "X")],
                "B": [],
                "X": [("c4", "Y")],
                "Y": [("c5", "X")],
            },
            "Start",
        ),
        (
            "Test 5: Cross-loop from branch back to main path",
            {
                "Start": [("c1", "A")],
                "A": [("c2", "B"), ("c3", "X")],
                "B": [("c4", "C")],
                "C": [],
                "X": [("c5", "A")],
            },
            "Start",
        ),
    ]

    for title, edges, start_node in test_cases:
        print("\n" + "=" * len(title))
        print(title)
        print("=" * len(title))
        print(PipelineVisualizer.visualize(edges, start_node))


if __name__ == "__main__":
    main()
