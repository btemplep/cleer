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
        in_triple_quote = False
        triple_char = ""

        for line in token.split("\n"):
            stripped = line.strip()

            if not in_triple_quote:
                count = stripped.count('"""')
                if count == 0:
                    count = stripped.count("'''")
                    if count % 2 == 1:
                        in_triple_quote = True
                        triple_char = "'''"
                elif count % 2 == 1:
                    in_triple_quote = True
                    triple_char = '"""'
            else:
                if triple_char in stripped:
                    in_triple_quote = False
                continue

            if not stripped:
                continue

            leading = self._get_leading_whitespace(line)

            if not leading:
                continue

            if (
                "\t" in leading
                or len(leading) % self._tab_size != 0
            ):
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
        indent_map, frozen_lines = self._build_indent_map(token)

        if not indent_map:
            if "\t" in token:
                return self._fallback_expand_tabs(token)

            return token

        lines = token.split("\n")
        result_lines = []
        current_shift = 0

        for i, line in enumerate(lines):
            if not line.strip():
                result_lines.append("")
                continue

            if i in frozen_lines:
                result_lines.append(line)
                continue

            if i in indent_map:
                indent_level = indent_map[i]
                new_indent = indent_level * self._tab_size
                old_indent = len(self._get_leading_whitespace(line).replace("\t", " " * self._tab_size))
                current_shift = new_indent - old_indent
                content = line.lstrip()
                result_lines.append(" " * new_indent + content)
            else:
                leading = self._get_leading_whitespace(line)
                old_indent = len(leading.replace("\t", " " * self._tab_size))
                new_indent = max(0, old_indent + current_shift)
                content = line.lstrip()
                result_lines.append(" " * new_indent + content)

        return "\n".join(result_lines)


    def _build_indent_map(self, token: str):
        """Build a mapping of line index to indent level using the AST.

        Parameters
        ----------
        token : str
            Code block to parse.

        Returns
        -------
        tuple[dict, set]
            Mapping of line index (0-based) to indent level, and a set
            of line indices that should not be modified (inside non-docstring
            multiline strings).
        """
        try:
            tree = ast.parse(token)
        except SyntaxError:
            return {}, set()

        indent_map: Dict[int, int] = {}
        frozen_lines: set = set()
        token_lines = token.split("\n")
        self._walk_node(tree, 0, indent_map, frozen_lines, token_lines)

        return indent_map, frozen_lines


    def _walk_node(
        self,
        node,
        depth: int,
        indent_map: Dict[int, int],
        frozen_lines: set,
        token_lines: List[str]
    ):
        """Walk an AST node, recording indent levels for each line."""
        if hasattr(node, "lineno"):
            line_idx = node.lineno - 1
            indent_map[line_idx] = depth

        if hasattr(node, "decorator_list"):
            for decorator in node.decorator_list:
                indent_map[decorator.lineno - 1] = depth

        child_depth = depth if isinstance(node, ast.Module) else depth + 1

        if hasattr(node, "body") and isinstance(node.body, list):
            for i, child in enumerate(node.body):
                is_docstring = self._is_body_docstring(i, node.body)

                if is_docstring:
                    self._map_docstring_lines(
                        child,
                        child_depth,
                        indent_map,
                        token_lines
                    )
                else:
                    self._freeze_multiline_strings(child, frozen_lines)

                self._walk_node(child, child_depth, indent_map, frozen_lines, token_lines)

        if isinstance(node, ast.Try):
            for handler in node.handlers:
                indent_map[handler.lineno - 1] = depth
                for child in handler.body:
                    self._freeze_multiline_strings(child, frozen_lines)
                    self._walk_node(child, child_depth, indent_map, frozen_lines, token_lines)

            if node.orelse:
                first_else = node.orelse[0]
                else_line = first_else.lineno - 1
                lines = None
                if else_line > 0:
                    indent_map[else_line - 1] = depth
                for child in node.orelse:
                    self._freeze_multiline_strings(child, frozen_lines)
                    self._walk_node(child, child_depth, indent_map, frozen_lines, token_lines)

            if node.finalbody:
                first_finally = node.finalbody[0]
                finally_line = first_finally.lineno - 1
                if finally_line > 0:
                    indent_map[finally_line - 1] = depth
                for child in node.finalbody:
                    self._freeze_multiline_strings(child, frozen_lines)
                    self._walk_node(child, child_depth, indent_map, frozen_lines, token_lines)

        elif isinstance(node, (ast.If, ast.For, ast.While)):
            if node.orelse:
                first_else = node.orelse[0]

                if (
                    isinstance(first_else, ast.If)
                    and len(node.orelse) == 1
                    and first_else.col_offset == node.col_offset
                ):
                    self._walk_node(first_else, depth, indent_map, frozen_lines, token_lines)
                else:
                    else_keyword_line = first_else.lineno - 2
                    if else_keyword_line >= 0:
                        indent_map[else_keyword_line] = depth

                    for child in node.orelse:
                        self._freeze_multiline_strings(child, frozen_lines)
                        self._walk_node(child, child_depth, indent_map, frozen_lines, token_lines)

        elif hasattr(node, "orelse") and isinstance(node.orelse, list):
            if node.orelse:
                for child in node.orelse:
                    self._freeze_multiline_strings(child, frozen_lines)
                    self._walk_node(child, child_depth, indent_map, frozen_lines, token_lines)


    def _freeze_multiline_strings(self, node, frozen_lines: set):
        """Mark lines inside non-docstring multiline strings as frozen."""
        for child in ast.walk(node):
            if not (
                isinstance(child, ast.Constant)
                and isinstance(child.value, str)
                and child.end_lineno > child.lineno
            ):
                continue

            if self._is_docstring(child, node):
                continue

            for line_idx in range(child.lineno, child.end_lineno):
                frozen_lines.add(line_idx)


    def _is_body_docstring(self, index: int, body: list) -> bool:
        """Check if a body node at the given index is a docstring.

        A docstring is either:
        - The first statement in a body (module/class/function docstring)
        - An Expr with string constant immediately after an Assign or
          AnnAssign (variable docstring)
        """
        node = body[index]

        if not (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            return False

        if index == 0:
            return True

        prev = body[index - 1]

        return isinstance(prev, (ast.Assign, ast.AnnAssign))


    def _map_docstring_lines(
        self,
        node,
        depth: int,
        indent_map: Dict[int, int],
        token_lines: List[str]
    ):
        """Map all lines of a docstring to the correct indent depth.

        The opening and closing triple-quote lines go to `depth`.
        Body lines are mapped so their base indent aligns with
        `depth`, preserving relative indentation within.

        Parameters
        ----------
        node : ast.AST
            The Expr node containing the docstring.
        depth : int
            Expected indent depth for this docstring.
        indent_map : Dict[int, int]
            Line index to depth mapping (mutated).
        token_lines : List[str]
            Lines of the token being processed.
        """
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        start_idx = node.lineno - 1
        end_idx = node.end_lineno - 1

        indent_map[start_idx] = depth
        indent_map[end_idx] = depth

        if end_idx <= start_idx + 1:
            return

        body_lines = token_lines[start_idx + 1:end_idx]

        min_indent = None

        for line in body_lines:
            if not line.strip():
                continue

            leading = self._get_leading_whitespace(line)
            indent = len(leading.replace("\t", " " * self._tab_size))

            if min_indent is None or indent < min_indent:
                min_indent = indent

        if min_indent is None:
            return

        expected_base = depth * self._tab_size

        for i, line in enumerate(body_lines):
            line_idx = start_idx + 1 + i

            if not line.strip():
                continue

            leading = self._get_leading_whitespace(line)
            actual_indent = len(leading.replace("\t", " " * self._tab_size))
            relative = actual_indent - min_indent
            target_indent = expected_base + relative
            target_depth = target_indent // self._tab_size

            indent_map[line_idx] = target_depth


    def _is_docstring(self, string_node, root_node) -> bool:
        """Check if a string constant is a docstring in any body."""
        for node in ast.walk(root_node):
            body = getattr(node, "body", None)

            if not isinstance(body, list) or not body:
                continue

            for i, child in enumerate(body):
                if not (
                    isinstance(child, ast.Expr)
                    and isinstance(child.value, ast.Constant)
                    and child.value is string_node
                ):
                    continue

                if i == 0:
                    return True

                prev = body[i - 1]

                if isinstance(prev, (ast.Assign, ast.AnnAssign)):
                    return True

        return False


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
