"""Python class boundary formatter module."""

__all__ = [
    "PythonClassBoundaryFormatter"
]

import ast

from cleer.formatters.formatter import Formatter


class PythonClassBoundaryFormatter(Formatter):
    """Enforce spacing rules inside class definitions.

    Rules:
    - No blank lines between class declaration, docstring, class vars,
    or pass.
    - 2 blank lines before any other members (methods, nested classes).

    Examples
    --------

    ```python
    from cleer import PythonClassBoundaryFormatter

    formatter = PythonClassBoundaryFormatter()
    result = formatter.format("class Foo:\\n\\n    x: int\\n\\n    def bar(self):\\n        pass\\n")
    ```
    """
    accepts_token_types = ["python_class_boundary"]


    def inspect(self, token: str) -> str | None:
        """Inspect class body spacing.

        Parameters
        ----------
        token : str
            Class definition token.

        Returns
        -------
        str | None
            Error message if spacing is incorrect.
            Returns `None` if there is no violation.
        """
        formatted = self.format(token)

        if formatted != token:
            return (
                "Class body spacing should have no blank lines between class declaration, docstring, class vars, or pass. "
                "There should be two blank lines between those and the first method."
            )

        return None


    def format(self, token: str) -> str:
        """Format class body spacing.

        Parameters
        ----------
        token : str
            Class definition token including trailing blank lines.

        Returns
        -------
        str
            Formatted class with correct internal spacing.
        """
        stripped = token.rstrip("\n")
        trailing_newlines = len(token) - len(stripped)

        indent = self._get_indent(stripped)
        dedented = self._dedent(stripped, indent)

        try:
            tree = ast.parse(dedented)
        except SyntaxError:
            return token

        if (
            not tree.body
            or not isinstance(tree.body[0], ast.ClassDef)
        ):
            return token

        class_node = tree.body[0]
        lines = stripped.split("\n")

        new_lines = self._rebuild_body(class_node, lines)

        result = "\n".join(new_lines) + "\n" * trailing_newlines

        return result


    def _rebuild_body(
        self,
        class_node: ast.ClassDef,
        lines: list[str]
    ) -> list[str]:
        """Rebuild class body with correct spacing.

        Parameters
        ----------
        class_node : ast.ClassDef
            The parsed class node.
        lines : list[str]
            Original lines of the class.

        Returns
        -------
        list[str]
            Lines with corrected spacing.
        """
        body = class_node.body
        class_line = class_node.lineno - 1

        header_end = self._find_header_end(body)

        result = []

        for line_idx in range(0, class_line + 1):
            result.append(lines[line_idx])

        for i, node in enumerate(body):
            node_start = node.lineno - 1
            node_end = node.end_lineno - 1
            is_header = i <= header_end

            if is_header:
                for line_idx in range(node_start, node_end + 1):
                    result.append(lines[line_idx])

            else:
                result.append("")
                result.append("")

                node_start_line = node_start

                if hasattr(node, "decorator_list") and node.decorator_list:
                    node_start_line = node.decorator_list[0].lineno - 1

                for line_idx in range(node_start_line, node_end + 1):
                    result.append(lines[line_idx])

        return result


    def _find_header_end(self, body: list) -> int:
        header_end = -1

        for i, node in enumerate(body):
            if self._is_header_node(node, i):
                header_end = i
            else:
                break

        return header_end


    def _is_header_node(self, node: ast.stmt, index: int) -> bool:
        if isinstance(node, ast.Pass):
            return True

        if index == 0 and isinstance(node, ast.Expr):
            if (
                isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                return True

        if isinstance(node, (ast.AnnAssign, ast.Assign)):
            return True

        return False


    def _get_indent(self, text: str) -> int:
        first_line = text.split("\n")[0]

        return len(first_line) - len(first_line.lstrip())


    def _dedent(self, text: str, indent: int) -> str:
        if indent == 0:
            return text

        lines = text.split("\n")
        dedented = []

        for line in lines:
            if line.strip():
                dedented.append(line[indent:])
            else:
                dedented.append(line)

        return "\n".join(dedented)
