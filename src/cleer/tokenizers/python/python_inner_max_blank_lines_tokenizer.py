"""Python inner max blank lines tokenizer module."""

__all__ = ["PythonInnerMaxBlankLinesTokenizer"]


import ast
import re
from typing import List, Set, Tuple

from cleer.tokenizers.tokenizer import Tokenizer


class PythonInnerMaxBlankLinesTokenizer(Tokenizer):
    """Tokenizes consecutive blank lines inside function/method bodies.

    Uses Python's AST to find function and method definitions, then
    finds whitespace blocks within their bodies that contain more than
    a configurable number of consecutive blank lines.

    Parameters
    ----------
    max_blank_lines : int, default=1
        Maximum number of consecutive blank lines allowed inside
        function/method bodies. Only emits tokens for whitespace blocks
        exceeding this limit.

    Examples
    --------

    ```python
    from cleer import PythonInnerMaxBlankLinesTokenizer

    tokenizer = PythonInnerMaxBlankLinesTokenizer()
    doc = "def foo():\n    x = 1\n\n\n\n    y = 2\n"
    tokens = tokenizer.tokenize(doc)
    ```
    """
    emits_token_type = "python_inner_max_blank_lines"


    def __init__(self, max_blank_lines: int = 1):
        self._max_blank_lines = max_blank_lines
        self._pattern = re.compile(
            r"\n{" + str(max_blank_lines + 2) + r",}"
        )


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize excessive blank lines inside function/method bodies.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        List[dict]
            List of token results for whitespace blocks inside functions
            that exceed the max blank lines, or an empty list if none exist.

            ```python
            [
                {"token": "\n\n\n\n", "index": 18, "length": 4}
            ]
            ```
        """
        tree = ast.parse(document)

        line_offsets = self._build_line_offsets(document)
        function_ranges = self._collect_function_body_ranges(tree, line_offsets, document)

        if not function_ranges:
            return []

        tokens = []
        seen_ranges: Set[Tuple[int, int]] = set()

        for match in self._pattern.finditer(document):
            start = match.start()
            end = match.end()

            if self._is_inside_function(start, end, function_ranges):
                token_range = (start, end - start)
                if token_range not in seen_ranges:
                    seen_ranges.add(token_range)
                    tokens.append(
                        {
                            "token": document[start:end],
                            "index": start,
                            "length": end - start
                        }
                    )

        tokens.sort(key=lambda t: t["index"])

        return tokens


    def _build_line_offsets(self, document: str) -> List[int]:
        """Build a list mapping line numbers (0-indexed) to character offsets."""
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets


    def _collect_function_body_ranges(
        self,
        tree: ast.Module,
        line_offsets: List[int],
        document: str
    ) -> List[Tuple[int, int]]:
        """Collect character ranges for all function/method bodies."""
        ranges = []

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            if not node.body:
                continue

            body_start_line = node.body[0].lineno
            body_end_line = node.end_lineno

            if body_end_line is None:
                continue

            start_offset = line_offsets[body_start_line - 1]
            end_offset = line_offsets[body_end_line] if body_end_line < len(line_offsets) else len(document)

            ranges.append((start_offset, end_offset))

        return ranges


    def _is_inside_function(
        self,
        start: int,
        end: int,
        function_ranges: List[Tuple[int, int]]
    ) -> bool:
        """Check if a span falls inside any function body range."""
        for range_start, range_end in function_ranges:
            if start >= range_start and end <= range_end:
                return True

        return False
