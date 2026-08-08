"""Python return/yield formatter module."""

__all__ = [
    "PythonReturnYieldFormatter"
]

import ast

from cleer.formatters.formatter import Formatter


class PythonReturnYieldFormatter(Formatter):
    """Enforce blank line spacing around return and yield statements.

    Receives an entire function definition as a token and walks its
    body at all nesting levels to enforce:

    - One blank line before return/yield unless it is the only
    statement in its code block.
    - At least one blank line after return/yield.

    Examples
    --------

    ```python
    from cleer import PythonReturnYieldFormatter

    formatter = PythonReturnYieldFormatter()
    ```
    """
    accepts_token_types = ["python_return_yield"]


    def inspect(self, token: str) -> str | None:
        """Inspect return/yield blank line spacing.

        Parameters
        ----------
        token : str
            Function definition source text with trailing blank lines.

        Returns
        -------
        str | None
            Error message if spacing is incorrect.
            Returns `None` if there is no violation.
        """
        expected = self._format_token(token)

        if token != expected:
            return "Return/yield should have a blank line before (unless only statement in block) and at least one blank line after."

        return None


    def format(self, token: str) -> str:
        """Reformat blank lines around return/yield.

        Parameters
        ----------
        token : str
            Function definition source text with trailing blank lines.

        Returns
        -------
        str
            Correctly formatted function text.
        """
        return self._format_token(token)


    def _format_token(self, token: str) -> str:
        """Format the function token."""
        stripped = token.rstrip("\n")
        trailing_newlines = len(token) - len(stripped)

        indent = self._get_indent(stripped)
        dedented = self._dedent(stripped, indent)

        try:
            tree = ast.parse(dedented)
        except SyntaxError:
            return token

        if not tree.body:
            return token

        func_node = tree.body[0]

        if not isinstance(
            func_node, (
                ast.FunctionDef,
                ast.AsyncFunctionDef
            )
        ):
            return token

        lines = stripped.split("\n")
        edits = []

        self._find_edits(func_node.body, lines, edits)

        if not edits:
            return token

        edits.sort(
            key=lambda e: (
                e[0],
                1 if e[1] == "add_after" else 0
            ),
            reverse=True
        )

        for line_idx, action in edits:
            if action == "add_before":
                lines.insert(line_idx, "")
            elif action == "add_after":
                lines.insert(line_idx + 1, "")

        result = "\n".join(lines) + "\n" * trailing_newlines

        return result


    def _get_indent(self, text: str) -> int:
        """Get the indentation level of the first line."""
        first_line = text.split("\n")[0]

        return len(first_line) - len(first_line.lstrip())


    def _dedent(self, text: str, indent: int) -> str:
        """Remove `indent` spaces from the start of each line."""
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


    def _find_edits(self, body: list, lines: list[str], edits: list):
        """Find required edits for return/yield in a body."""
        for i, node in enumerate(body):
            is_ry = self._is_return_yield(node)

            if is_ry:
                is_only = self._is_only_statement(body, i)
                line_idx = node.lineno - 1

                if not is_only:
                    if line_idx > 0 and lines[line_idx - 1].strip() != "":
                        edits.append((line_idx, "add_before"))

                end_line_idx = node.end_lineno - 1
                next_line_idx = end_line_idx + 1

                if (
                    next_line_idx < len(lines)
                    and lines[next_line_idx].strip() != ""
                ):
                    edits.append((end_line_idx, "add_after"))

            for field_name in (
                "body",
                "orelse",
                "finalbody"
            ):
                child = getattr(node, field_name, None)

                if child and isinstance(child, list):
                    self._find_edits(child, lines, edits)

            handlers = getattr(node, "handlers", None)

            if handlers:
                for handler in handlers:
                    if handler.body:
                        self._find_edits(handler.body, lines, edits)


    def _is_only_statement(self, body: list, index: int) -> bool:
        """Check if a return/yield is the only non-docstring statement in its block."""
        if len(body) == 1:
            return True

        if len(body) == 2 and index == 1:
            first = body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                return True

        return False


    def _is_return_yield(self, node: ast.stmt) -> bool:
        """Check if a node is a return or yield statement."""
        if isinstance(node, ast.Return):
            return True

        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, (ast.Yield, ast.YieldFrom))
        ):
            return True

        return False
