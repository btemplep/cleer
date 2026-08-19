"""See [](#cleer.formatters.python.python_compound_chain_formatter.PythonCompoundChainFormatter)"""

__all__ = [
    "PythonCompoundChainFormatter"
]

import ast
import textwrap

from cleer.formatters.formatter import Formatter, FormatterViolation


class PythonCompoundChainFormatter(Formatter):
    """Format blank lines between parts of compound statement chains.

    Rules:
    - Between compound parts (if→elif, try→except, etc.): no blank line
    - Exception: after return/yield/exit → 1 blank line
    - Exception: after a compound statement (if/for/while/with/try) as
    the last statement → 1 blank line

    Examples
    --------

    ```python
    from cleer import PythonCompoundChainFormatter

    formatter = PythonCompoundChainFormatter()
    result = formatter.format("if x:\\n    pass\\n\\nelse:\\n    pass\\n")
    ```
    """
    accepts_token_types = ["python_compound_chain"]


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect compound chain for incorrect blank lines.

        Parameters
        ----------
        token : str
            Token containing the full compound chain.

        Returns
        -------
        list[FormatterViolation]
            List of violations. Empty if blank lines are correct.
        """
        formatted = self.format(token)

        if formatted != token:
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": "Compound statement chains (if/elif/else, try/except/finally) should have no blank lines between parts, "
                        "except after return/yield/exit statements."
                }
            ]

        return []


    def format(self, token: str) -> str:
        """Format blank lines between compound chain parts.

        Parameters
        ----------
        token : str
            Token containing the full compound chain with original
            indentation.

        Returns
        -------
        str
            Token with corrected blank lines between parts.
        """
        base_indent = self._get_base_indent(token)
        dedented = textwrap.dedent(token)

        try:
            tree = ast.parse(dedented)
        except SyntaxError:
            return token

        if not tree.body:
            return token

        node = tree.body[0]
        boundaries = self._find_boundaries(node)

        if not boundaries:
            return token

        lines = token.split("\n")
        result_lines = []
        i = 0

        while i < len(lines):
            result_lines.append(lines[i])

            boundary = self._boundary_at_line(boundaries, i, base_indent, lines)
            if boundary is not None:
                expected_blanks = boundary['expected_blanks']

                j = i + 1
                while j < len(lines) and lines[j].strip() == "":
                    j += 1

                actual_blanks = j - i - 1

                if actual_blanks != expected_blanks:
                    for _ in range(expected_blanks):
                        result_lines.append("")

                    i = j
                else:
                    i += 1

            else:
                i += 1

        return "\n".join(result_lines)


    def _get_base_indent(self, token: str) -> str:
        first_line = token.split("\n")[0]

        for i, ch in enumerate(first_line):
            if ch != " " and ch != "\t":
                return first_line[:i]

        return ""


    def _find_boundaries(self, node) -> list:
        boundaries = []

        for child in ast.walk(node):
            if isinstance(child, ast.If) and child.orelse:
                self._find_if_boundaries(child, boundaries)
            elif isinstance(child, ast.Try):
                self._find_try_boundaries(child, boundaries)
            elif isinstance(
                child,
                (
                    ast.For,
                    ast.AsyncFor,
                    ast.While
                )
            ):
                if child.orelse:
                    self._find_loop_boundaries(child, boundaries)

        return boundaries


    def _find_if_boundaries(self, node: ast.If, boundaries: list):
        if not node.orelse:
            return

        last_stmt = node.body[-1]
        body_end = last_stmt.end_lineno
        first_else = node.orelse[0]

        if isinstance(first_else, ast.If):
            connector_line = first_else.lineno
        else:
            connector_line = self._find_else_line(body_end, first_else.lineno, node)

        expected = 1 if self._needs_blank(last_stmt) else 0
        boundaries.append(
            {
                "body_end_line": body_end,
                "connector_line": connector_line,
                "expected_blanks": expected
            }
        )

        if isinstance(first_else, ast.If):
            self._find_if_boundaries(first_else, boundaries)


    def _find_try_boundaries(self, node: ast.Try, boundaries: list):
        if node.handlers:
            last_stmt = node.body[-1]
            body_end = last_stmt.end_lineno
            connector_line = node.handlers[0].lineno

            expected = 1 if self._needs_blank(last_stmt) else 0
            boundaries.append(
                {
                    "body_end_line": body_end,
                    "connector_line": connector_line,
                    "expected_blanks": expected
                }
            )

            for i in range(len(node.handlers) - 1):
                last_stmt = node.handlers[i].body[-1]
                body_end = last_stmt.end_lineno
                connector_line = node.handlers[i + 1].lineno

                expected = 1 if self._needs_blank(last_stmt) else 0
                boundaries.append(
                    {
                        "body_end_line": body_end,
                        "connector_line": connector_line,
                        "expected_blanks": expected
                    }
                )

        if node.orelse:
            if node.handlers:
                last_stmt = node.handlers[-1].body[-1]
                body_end = last_stmt.end_lineno
            else:
                last_stmt = node.body[-1]
                body_end = last_stmt.end_lineno

            connector_line = node.orelse[0].lineno

            expected = 1 if self._needs_blank(last_stmt) else 0
            boundaries.append(
                {
                    "body_end_line": body_end,
                    "connector_line": connector_line,
                    "expected_blanks": expected
                }
            )

        if node.finalbody:
            if node.orelse:
                last_stmt = node.orelse[-1]
                body_end = last_stmt.end_lineno
            elif node.handlers:
                last_stmt = node.handlers[-1].body[-1]
                body_end = last_stmt.end_lineno
            else:
                last_stmt = node.body[-1]
                body_end = last_stmt.end_lineno

            connector_line = node.finalbody[0].lineno

            expected = 1 if self._needs_blank(last_stmt) else 0
            boundaries.append(
                {
                    "body_end_line": body_end,
                    "connector_line": connector_line,
                    "expected_blanks": expected
                }
            )


    def _find_loop_boundaries(self, node, boundaries: list):
        if not node.orelse:
            return

        last_stmt = node.body[-1]
        body_end = last_stmt.end_lineno
        connector_line = node.orelse[0].lineno

        expected = 1 if self._needs_blank(last_stmt) else 0
        boundaries.append(
            {
                "body_end_line": body_end,
                "connector_line": connector_line,
                "expected_blanks": expected
            }
        )


    def _needs_blank(self, node) -> bool:
        if isinstance(node, ast.Return):
            return True

        if isinstance(node, ast.Expr):
            if isinstance(node.value, (ast.Yield, ast.YieldFrom)):
                return True

            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "exit"
            ):
                return True

        if isinstance(
            node,
            (
                ast.If,
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.With,
                ast.AsyncWith,
                ast.Try
            )
        ):
            return True

        return False


    def _find_else_line(self, body_end: int, first_else_line: int, node) -> int:
        return body_end + 1


    def _boundary_at_line(
        self,
        boundaries,
        line_idx,
        base_indent,
        lines
    ) -> dict | None:
        token_line_num = line_idx + 1

        for boundary in boundaries:
            if boundary['body_end_line'] == token_line_num:
                return boundary

        return None
