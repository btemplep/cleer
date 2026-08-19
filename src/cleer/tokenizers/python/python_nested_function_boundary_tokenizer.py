"""See [](#cleer.tokenizers.python.python_nested_function_boundary_tokenizer.PythonNestedFunctionBoundaryTokenizer)"""

__all__ = [
    "PythonNestedFunctionBoundaryTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonNestedFunctionBoundaryTokenizer(Tokenizer):
    """Tokenizes blank lines before and after nested definitions inside functions.

    Uses Python's AST to find function and class definitions that are
    nested inside other functions or methods. Emits tokens for the
    whitespace block immediately before and after each nested definition.

    Only emits a boundary token when the nested definition is not the
    first or last statement in its enclosing scope.

    Examples
    --------

    ```python
    from cleer import PythonNestedFunctionBoundaryTokenizer

    tokenizer = PythonNestedFunctionBoundaryTokenizer()
    doc = "def outer():\n    x = 1\n\n\n\n    def inner():\n        pass\n\n\n\n    y = 2\n"
    tokens = tokenizer.tokenize(doc)
    ```
    """
    emits_token_type = "python_nested_function_boundary"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize blank line boundaries around nested function definitions.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each whitespace boundary before/after
            nested function definitions, or an empty list if none exist.

            ```python
            [
                {"token": "\n\n\n\n", "index": 18, "length": 4}
            ]
            ```
        """
        tree = ast.parse(document)
        line_offsets = self._build_line_offsets(document)
        tokens = []
        seen_ranges = set()
        self._walk_for_nested(
            tree,
            document,
            line_offsets,
            tokens,
            seen_ranges
        )
        tokens.sort(key=lambda t: t['index'])

        return tokens


    def _build_line_offsets(self, document: str) -> list[int]:
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets


    def _walk_for_nested(
        self,
        tree: ast.Module,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult],
        seen_ranges: set
    ):
        """Walk the AST to find all nested functions and their boundaries."""
        for node in ast.walk(tree):
            if not isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):
                continue

            self._process_body(
                node.body,
                document,
                line_offsets,
                tokens,
                seen_ranges
            )


    def _process_body(
        self,
        body: list,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult],
        seen_ranges: set
    ):
        """Process a function body for nested function/class boundaries."""
        target_types = (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
            ast.ClassDef
        )
        for i, node in enumerate(body):
            if not isinstance(node, target_types):
                continue

            if i > 0:
                prev_node = body[i - 1]
                prev_end_line = prev_node.end_lineno

                if prev_end_line is not None:
                    start_line = self._get_start_line(node)
                    token = self._extract_boundary(
                        document,
                        line_offsets,
                        prev_end_line,
                        start_line
                    )

                    if token is not None:
                        token_range = (
                            token['index'],
                            token['length']
                        )
                        if token_range not in seen_ranges:
                            seen_ranges.add(token_range)
                            tokens.append(token)

            if i < len(body) - 1:
                next_node = body[i + 1]
                if not isinstance(next_node, target_types):
                    end_line = node.end_lineno

                    if end_line is not None:
                        next_start_line = self._get_start_line(next_node)
                        token = self._extract_boundary(
                            document,
                            line_offsets,
                            end_line,
                            next_start_line
                        )

                        if token is not None:
                            token_range = (
                                token['index'],
                                token['length']
                            )
                            if token_range not in seen_ranges:
                                seen_ranges.add(token_range)
                                tokens.append(token)


    def _get_start_line(self, node) -> int:
        if hasattr(node, "decorator_list") and node.decorator_list:
            return node.decorator_list[0].lineno

        return node.lineno


    def _extract_boundary(
        self,
        document: str,
        line_offsets: list[int],
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
