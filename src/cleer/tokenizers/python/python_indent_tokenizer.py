"""Python indent tokenizer module."""

__all__ = [
    "PythonIndentTokenizer"
]

import ast
import re

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonIndentTokenizer(Tokenizer):
    """Tokenizes indented code blocks with incorrect indentation.

    Emits tokens for each top-level statement that contains lines with
    incorrect indentation — either tabs or wrong number of spaces per
    indent level.

    Parameters
    ----------
    tab_size : int, default=4
        Expected number of spaces per indentation level.

    Examples
    --------

    ```python
    from cleer import PythonIndentTokenizer

    tokenizer = PythonIndentTokenizer()
    tokens = tokenizer.tokenize("def foo():\\n  pass\\n")
    ```
    """
    emits_token_type = "python_indent"
    _leading_ws = re.compile(r"^([ \t]*)")


    def __init__(self, tab_size: int=4):
        self._tab_size = tab_size


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize top-level code blocks with incorrect indentation.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each top-level code block that
            has incorrect indentation.

            ```python
            [
                {"token": "def foo():\\n  pass\\n", "index": 0, "length": 18}
            ]
            ```
        """
        tree = ast.parse(document)

        line_offsets = self._build_line_offsets(document)
        tokens = []

        for node in tree.body:
            if (
                not hasattr(node, "end_lineno")
                or node.end_lineno is None
            ):
                continue

            start_line = node.lineno

            if hasattr(node, "decorator_list") and node.decorator_list:
                start_line = node.decorator_list[0].lineno

            end_line = node.end_lineno

            if end_line <= start_line:
                continue

            start_index = line_offsets[start_line - 1]
            end_index = line_offsets[end_line] if end_line < len(line_offsets) else len(document)
            token = document[start_index:end_index]

            if self._has_bad_indent(token):
                tokens.append(
                    {
                        "token": token,
                        "index": start_index,
                        "length": len(token)
                    }
                )

        return tokens


    def _has_bad_indent(self, block: str) -> bool:
        for line in block.split("\n"):
            if not line.strip():
                continue

            leading = self._get_leading_whitespace(line)

            if not leading:
                continue

            if "\t" in leading:
                return True

            if len(leading) % self._tab_size != 0:
                return True

        if self._has_bad_docstring_indent(block):
            return True

        if self._has_bad_semantic_indent(block):
            return True

        return False


    def _has_bad_semantic_indent(self, block: str) -> bool:
        try:
            tree = ast.parse(block)
        except SyntaxError:
            return False

        lines = block.split("\n")
        indent_map: dict[int, int] = {}

        self._walk_for_indent_check(tree, 0, indent_map)

        for line_idx, expected_depth in indent_map.items():
            if line_idx >= len(lines):
                continue

            line = lines[line_idx]

            if not line.strip():
                continue

            leading = self._get_leading_whitespace(line)
            actual_indent = len(leading.replace("\t", " " * self._tab_size))
            expected_indent = expected_depth * self._tab_size

            if actual_indent != expected_indent:
                return True

        return False


    def _walk_for_indent_check(self, node, depth: int, indent_map: dict[int, int]):
        if hasattr(node, "lineno"):
            indent_map[node.lineno - 1] = depth

        if hasattr(node, "decorator_list"):
            for decorator in node.decorator_list:
                indent_map[decorator.lineno - 1] = depth

        child_depth = depth if isinstance(node, ast.Module) else depth + 1

        if hasattr(node, "body") and isinstance(node.body, list):
            for child in node.body:
                self._walk_for_indent_check(child, child_depth, indent_map)

        if isinstance(node, ast.Try):
            for handler in node.handlers:
                indent_map[handler.lineno - 1] = depth
                for child in handler.body:
                    self._walk_for_indent_check(child, child_depth, indent_map)

            if node.orelse:
                for child in node.orelse:
                    self._walk_for_indent_check(child, child_depth, indent_map)

            if node.finalbody:
                for child in node.finalbody:
                    self._walk_for_indent_check(child, child_depth, indent_map)

        elif isinstance(node, (ast.If, ast.For, ast.While)):
            if node.orelse:
                first_else = node.orelse[0]

                if (
                    isinstance(first_else, ast.If)
                    and len(node.orelse) == 1
                    and first_else.col_offset == node.col_offset
                ):
                    self._walk_for_indent_check(first_else, depth, indent_map)
                else:
                    for child in node.orelse:
                        self._walk_for_indent_check(
                            child,
                            child_depth,
                            indent_map
                        )

        elif (
            hasattr(node, "orelse")
            and isinstance(node.orelse, list)
        ):
            for child in node.orelse:
                self._walk_for_indent_check(child, child_depth, indent_map)


    def _has_bad_docstring_indent(self, block: str) -> bool:
        try:
            tree = ast.parse(block)
        except SyntaxError:
            return False

        for node in ast.walk(tree):
            body = getattr(node, "body", None)

            if not isinstance(body, list) or not body:
                continue

            depth = self._get_body_depth(node, tree)

            for i, child in enumerate(body):
                if not (
                    isinstance(child, ast.Expr)
                    and isinstance(child.value, ast.Constant)
                    and isinstance(child.value.value, str)
                ):
                    continue

                is_docstring = (
                    i == 0
                    or isinstance(body[i - 1], (ast.Assign, ast.AnnAssign))
                )

                if not is_docstring:
                    continue

                if child.end_lineno <= child.lineno:
                    continue

                expected_indent = depth * self._tab_size
                lines = block.split("\n")

                for line_num in range(child.lineno - 1, child.end_lineno):
                    if line_num >= len(lines):
                        break

                    line = lines[line_num]

                    if not line.strip():
                        continue

                    actual = len(self._get_leading_whitespace(line))

                    if actual != expected_indent:
                        return True

        return False


    def _get_body_depth(self, node, tree) -> int:
        if isinstance(node, ast.Module):
            return 0

        depth = 0

        for parent in ast.walk(tree):
            if parent is node:
                break

            body = getattr(parent, "body", None)

            if isinstance(body, list) and node in body:
                if not isinstance(parent, ast.Module):
                    depth += 1

                break

            for attr in (
                "handlers",
                "orelse",
                "finalbody"
            ):
                items = getattr(parent, attr, None)

                if isinstance(items, list) and node in items:
                    if not isinstance(parent, ast.Module):
                        depth += 1

                    break

        if not isinstance(node, ast.Module):
            depth += 1

        return depth


    def _get_leading_whitespace(self, line: str) -> str:
        match = self._leading_ws.match(line)

        if match:
            return match.group(1)

        return ""


    def _build_line_offsets(self, document: str) -> list[int]:
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
