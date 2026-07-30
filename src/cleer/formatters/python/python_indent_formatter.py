"""Python indent formatter module."""

__all__ = ["PythonIndentFormatter"]


import ast
import re
from typing import Dict, List

from cleer.formatters.formatter import Formatter


class PythonIndentFormatter(Formatter):
    """Enforce spaces-only indentation at the correct indent level.

    Analyzes a code block using the AST to determine the expected indent
    level for each line, then replaces any tab-based indentation with the
    correct number of spaces.

    Parameters
    ----------
    tab_size : int, default=4
        Number of spaces per indentation level.

    Examples
    --------

    ```python
    from cleer import PythonIndentFormatter

    formatter = PythonIndentFormatter()
    result = formatter.format("def foo():\\n\\tpass\\n")
    ```
    """
    accepts_token_types = ["python_indent"]

    _leading_ws = re.compile(r"^([ \t]*)")


    def __init__(self, tab_size: int = 4):
        self._tab_size = tab_size


    def inspect(self, token: str) -> str | None:
        """Inspect a code block for incorrect indentation.

        Parameters
        ----------
        token : str
            String token to inspect (a code block).

        Returns
        -------
        str | None
            Error message if indentation is incorrect.
            Returns `None` if there is no violation.
        """
        for line in token.split("\n"):
            if not line.strip():
                continue

            leading = self._get_leading_whitespace(line)

            if not leading:
                continue

            if "\t" in leading:
                return f"Indentation should use spaces with {self._tab_size} spaces per level."

            if len(leading) % self._tab_size != 0:
                return f"Indentation should use spaces with {self._tab_size} spaces per level."

        return None


    def format(self, token: str) -> str:
        """Reformat indentation to use correct number of spaces per level.

        Uses the AST to determine what indent level each line should be
        at, then enforces that with spaces.

        Parameters
        ----------
        token : str
            Token to format (a code block starting at column 0).

        Returns
        -------
        str
            Code block with corrected indentation.
        """
        indent_map = self._build_indent_map(token)

        if not indent_map:
            if "\t" in token:
                return self._fallback_expand_tabs(token)

            return token

        lines = token.split("\n")
        result_lines = []

        for i, line in enumerate(lines):
            if not line.strip():
                result_lines.append("")
                continue

            if i in indent_map:
                indent_level = indent_map[i]
                content = line.lstrip()
                result_lines.append(" " * (indent_level * self._tab_size) + content)
            else:
                leading = self._get_leading_whitespace(line)
                if "\t" in leading:
                    expanded = leading.replace("\t", " " * self._tab_size)
                    content = line.lstrip()
                    result_lines.append(expanded + content)
                else:
                    result_lines.append(line)

        return "\n".join(result_lines)


    def _build_indent_map(self, token: str) -> Dict[int, int]:
        """Build a mapping of line index to indent level using the AST.

        Parameters
        ----------
        token : str
            Code block to parse.

        Returns
        -------
        dict
            Mapping of line index (0-based) to indent level.
        """
        try:
            tree = ast.parse(token)
        except SyntaxError:
            return {}

        indent_map: Dict[int, int] = {}
        self._walk_node(tree, 0, indent_map)

        return indent_map


    def _walk_node(self, node, depth: int, indent_map: Dict[int, int]):
        """Walk an AST node, recording indent levels for each line."""
        if hasattr(node, "lineno"):
            line_idx = node.lineno - 1
            indent_map[line_idx] = depth

        if hasattr(node, "decorator_list"):
            for decorator in node.decorator_list:
                indent_map[decorator.lineno - 1] = depth

        child_depth = depth if isinstance(node, ast.Module) else depth + 1

        if hasattr(node, "body") and isinstance(node.body, list):
            for child in node.body:
                self._walk_node(child, child_depth, indent_map)

        if isinstance(node, ast.Try):
            for handler in node.handlers:
                indent_map[handler.lineno - 1] = depth
                for child in handler.body:
                    self._walk_node(child, child_depth, indent_map)

            if node.orelse:
                first_else = node.orelse[0]
                else_line = first_else.lineno - 1
                lines = None
                if else_line > 0:
                    indent_map[else_line - 1] = depth
                for child in node.orelse:
                    self._walk_node(child, child_depth, indent_map)

            if node.finalbody:
                first_finally = node.finalbody[0]
                finally_line = first_finally.lineno - 1
                if finally_line > 0:
                    indent_map[finally_line - 1] = depth
                for child in node.finalbody:
                    self._walk_node(child, child_depth, indent_map)

        elif isinstance(node, (ast.If, ast.For, ast.While)):
            if node.orelse:
                first_else = node.orelse[0]

                if isinstance(first_else, ast.If):
                    self._walk_node(first_else, depth, indent_map)
                else:
                    else_keyword_line = first_else.lineno - 2
                    if else_keyword_line >= 0:
                        indent_map[else_keyword_line] = depth

                    for child in node.orelse:
                        self._walk_node(child, child_depth, indent_map)

        elif hasattr(node, "orelse") and isinstance(node.orelse, list):
            if node.orelse:
                for child in node.orelse:
                    self._walk_node(child, child_depth, indent_map)


    def _get_leading_whitespace(self, line: str) -> str:
        """Get the leading whitespace from a line."""
        match = self._leading_ws.match(line)

        if match:
            return match.group(1)

        return ""


    def _fallback_expand_tabs(self, token: str) -> str:
        """Simple tab expansion fallback when AST parsing fails."""
        lines = token.split("\n")
        result = []

        for line in lines:
            if not line.strip():
                result.append("")
            else:
                leading = self._get_leading_whitespace(line)
                if "\t" in leading:
                    expanded = leading.replace("\t", " " * self._tab_size)
                    result.append(expanded + line.lstrip())
                else:
                    result.append(line)

        return "\n".join(result)
