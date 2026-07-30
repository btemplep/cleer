"""Python function boundary tokenizer module."""

__all__ = ["PythonFunctionBoundaryTokenizer"]


import ast
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PythonFunctionBoundaryTokenizer(Tokenizer):
    """Tokenizes blank lines before and after top-level function/method definitions.

    Uses Python's AST to find function and method definitions that are
    top-level within a module or class body. Emits tokens for the
    whitespace block immediately before each function definition (or its
    first decorator).

    Nested functions (functions defined inside other functions) are
    excluded. Decorator lines are not treated as the boundary — the
    whitespace before the first decorator is the boundary.

    Only emits a boundary token when the function is not the first
    statement in its scope (module or class body).

    Examples
    --------

    ```python
    from cleer import PythonFunctionBoundaryTokenizer

    tokenizer = PythonFunctionBoundaryTokenizer()
    tokens = tokenizer.tokenize("import os\n\n\ndef foo():\n    pass\n")
    ```
    """
    emits_token_type = "python_function_boundary"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize blank line boundaries around top-level function/method definitions.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PythonFunctionBoundaryTokenizer()
        tokens = tokenizer.tokenize("import os\n\n\ndef foo():\n    pass\n")
        ```

        Returns
        -------
        List[dict]
            List of token results for each whitespace boundary before
            function definitions, or an empty list if none exist.

            ```python
            [
                {"token": "\n\n\n", "index": 9, "length": 3}
            ]
            ```
        """
        tree = ast.parse(document)

        lines = document.split("\n")
        line_offsets = self._build_line_offsets(document)
        boundaries = self._collect_boundaries(tree, lines, line_offsets, document)

        return boundaries


    def _build_line_offsets(self, document: str) -> List[int]:
        """Build a list mapping line numbers (0-indexed) to character offsets."""
        offsets = [0]
        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets


    def _collect_boundaries(
        self,
        tree: ast.Module,
        lines: List[str],
        line_offsets: List[int],
        document: str
    ) -> List[dict]:
        """Collect all function boundary tokens."""
        tokens = []
        seen_ranges = set()
        module_body = tree.body
        self._process_body(
            module_body,
            lines,
            line_offsets,
            document,
            tokens,
            seen_ranges
        )
        for node in module_body:
            if isinstance(node, ast.ClassDef):
                self._process_body(
                    node.body,
                    lines,
                    line_offsets,
                    document,
                    tokens,
                    seen_ranges
                )

        tokens.sort(key=lambda t: t["index"])

        return tokens


    def _process_body(
        self,
        body: list,
        lines: List[str],
        line_offsets: List[int],
        document: str,
        tokens: List[dict],
        seen_ranges: set
    ):
        """Process a body (module or class) for function boundaries."""
        for i, node in enumerate(body):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            if i == 0:
                continue

            start_line = self._get_start_line(node)
            prev_node = body[i - 1]
            prev_end_line = prev_node.end_lineno
            if prev_end_line is None:
                continue

            token = self._extract_boundary(
                document,
                lines,
                line_offsets,
                prev_end_line,
                start_line
            )
            if token is not None:
                token_range = (token["index"], token["length"])
                if token_range not in seen_ranges:
                    seen_ranges.add(token_range)
                    tokens.append(token)

            if i < len(body) - 1:
                next_node = body[i + 1]
                if not isinstance(next_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    end_line = node.end_lineno

                    if end_line is None:
                        continue

                    next_start_line = self._get_node_start_line(next_node)
                    after_token = self._extract_boundary(
                        document,
                        lines,
                        line_offsets,
                        end_line,
                        next_start_line
                    )

                    if after_token is not None:
                        token_range = (after_token["index"], after_token["length"])
                        if token_range not in seen_ranges:
                            seen_ranges.add(token_range)
                            tokens.append(after_token)

        last_func_idx = None
        for i in range(len(body) - 1, -1, -1):
            if isinstance(body[i], (ast.FunctionDef, ast.AsyncFunctionDef)):
                last_func_idx = i
                break

        if last_func_idx is not None and last_func_idx < len(body) - 1:
            func_node = body[last_func_idx]
            next_node = body[last_func_idx + 1]
            end_line = func_node.end_lineno
            if end_line is not None:
                next_start_line = self._get_node_start_line(next_node)
                after_token = self._extract_boundary(
                    document,
                    lines,
                    line_offsets,
                    end_line,
                    next_start_line
                )
                if after_token is not None:
                    token_range = (after_token["index"], after_token["length"])
                    if token_range not in seen_ranges:
                        seen_ranges.add(token_range)
                        tokens.append(after_token)


    def _get_start_line(self, func) -> int:
        """Get the effective start line of a function, including decorators.

        Returns 1-indexed line number.
        """
        if func.decorator_list:
            return func.decorator_list[0].lineno

        return func.lineno


    def _get_node_start_line(self, node) -> int:
        """Get the start line of any AST node, including decorators if applicable.

        Returns 1-indexed line number.
        """
        if hasattr(node, "decorator_list") and node.decorator_list:
            return node.decorator_list[0].lineno

        return node.lineno


    def _extract_boundary(
        self,
        document: str,
        lines: List[str],
        line_offsets: List[int],
        prev_end_line: int,
        next_start_line: int
    ) -> dict | None:
        """Extract the whitespace boundary between two nodes.

        Parameters
        ----------
        prev_end_line : int
            1-indexed line number where the previous node ends.
        next_start_line : int
            1-indexed line number where the next node starts.
        """
        prev_end_idx = prev_end_line
        next_start_idx = next_start_line - 1
        if prev_end_idx >= next_start_idx:
            return {
                "token": "",
                "index": line_offsets[next_start_idx],
                "length": 0
            }

        start_offset = line_offsets[prev_end_idx]
        end_offset = line_offsets[next_start_idx]
        token = document[start_offset:end_offset]

        return {
            "token": token,
            "index": start_offset,
            "length": len(token)
        }
