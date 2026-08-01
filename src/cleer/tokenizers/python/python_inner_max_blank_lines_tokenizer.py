"""Python inner max blank lines tokenizer module."""

__all__ = ["PythonInnerMaxBlankLinesTokenizer"]


import ast
from typing import List, Set, Tuple

from cleer.tokenizers.tokenizer import Tokenizer


class PythonInnerMaxBlankLinesTokenizer(Tokenizer):
    """Tokenizes consecutive blank lines inside function/method bodies.

    Uses Python's AST to find function and method definitions, then
    finds runs of blank lines within their bodies that exceed a
    configurable maximum. Emits tokens containing only the blank line
    characters (no trailing newline from the previous statement).

    Parameters
    ----------
    max_blank_lines : int, default=1
        Maximum number of consecutive blank lines allowed inside
        function/method bodies. Only emits tokens for runs exceeding
        this limit.

    Examples
    --------

    ```python
    from cleer import PythonInnerMaxBlankLinesTokenizer

    tokenizer = PythonInnerMaxBlankLinesTokenizer()
    doc = "def foo():\\n    x = 1\\n\\n\\n\\n    y = 2\\n"
    tokens = tokenizer.tokenize(doc)
    ```
    """
    emits_token_type = "python_inner_max_blank_lines"


    def __init__(self, max_blank_lines: int = 1):
        self._max_blank_lines = max_blank_lines


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize excessive blank lines inside function/method bodies.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        List[dict]
            List of token results for blank line runs inside functions
            that exceed the max, or an empty list if none exist.

            ```python
            [
                {"token": "\\n\\n\\n", "index": 19, "length": 3}
            ]
            ```
        """
        tree = ast.parse(document)

        lines = document.split("\n")
        line_offsets = self._build_line_offsets(document)
        function_ranges = self._collect_function_body_ranges(
            tree,
            line_offsets,
            document
        )

        if not function_ranges:
            return []

        tokens = []
        seen_ranges: Set[Tuple[int, int]] = set()

        i = 0

        while i < len(lines):
            if lines[i].strip() != "":
                i += 1
                continue

            run_start = i

            while i < len(lines) and lines[i].strip() == "":
                i += 1

            run_length = i - run_start

            if run_length <= self._max_blank_lines:
                continue

            start = line_offsets[run_start]
            end = line_offsets[i] if i < len(line_offsets) else len(document)

            if not self._is_inside_function(start, end, function_ranges):
                continue

            token_range = (start, end - start)

            if token_range in seen_ranges:
                continue

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
        """Collect character ranges for all function/method bodies.

        Excludes regions inside class definitions so their internal
        spacing is not affected.
        """
        ranges = []
        class_ranges = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.body:
                cls_start_line = node.body[0].lineno
                cls_end_line = node.end_lineno

                if cls_end_line is None:
                    continue

                start_offset = line_offsets[cls_start_line - 1]
                end_offset = line_offsets[cls_end_line] if cls_end_line < len(line_offsets) else len(document)
                class_ranges.append((start_offset, end_offset))

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

        self._class_ranges = class_ranges

        return ranges


    def _is_inside_function(
        self,
        start: int,
        end: int,
        function_ranges: List[Tuple[int, int]]
    ) -> bool:
        """Check if a span falls inside a function body but not directly in a class body.

        A span inside a method (which is inside a class) is still
        considered inside a function. Only spans that are in a class body
        but not in any function body are excluded.
        """
        inside_function = False

        for range_start, range_end in function_ranges:
            if start >= range_start and end <= range_end:
                inside_function = True
                break

        if not inside_function:
            return False

        inside_class = False

        for range_start, range_end in self._class_ranges:
            if start >= range_start and end <= range_end:
                inside_class = True
                break

        if not inside_class:
            return True

        innermost_func = None

        for range_start, range_end in function_ranges:
            if start >= range_start and end <= range_end:
                if innermost_func is None or (range_end - range_start) < (innermost_func[1] - innermost_func[0]):
                    innermost_func = (range_start, range_end)

        innermost_class = None

        for range_start, range_end in self._class_ranges:
            if start >= range_start and end <= range_end:
                if innermost_class is None or (range_end - range_start) < (innermost_class[1] - innermost_class[0]):
                    innermost_class = (range_start, range_end)

        if innermost_func and innermost_class:
            func_size = innermost_func[1] - innermost_func[0]
            class_size = innermost_class[1] - innermost_class[0]

            return func_size < class_size

        return True
