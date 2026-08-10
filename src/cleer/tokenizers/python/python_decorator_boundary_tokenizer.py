"""Python decorator boundary tokenizer module."""

__all__ = [
    "PythonDecoratorBoundaryTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonDecoratorBoundaryTokenizer(Tokenizer):
    """Tokenizes whitespace between decorators and their function definitions.

    Uses Python's AST to find decorated function/method definitions and
    emits tokens for any whitespace between consecutive decorators and
    between the last decorator and the function definition.

    Examples
    --------

    ```python
    from cleer import PythonDecoratorBoundaryTokenizer

    tokenizer = PythonDecoratorBoundaryTokenizer()
    tokens = tokenizer.tokenize("@decorator\n\ndef foo():\n    pass\n")
    ```
    """
    emits_token_type = "python_decorator_boundary"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize whitespace between decorators and function definitions.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PythonDecoratorBoundaryTokenizer()
        tokens = tokenizer.tokenize("@decorator\n\ndef foo():\n    pass\n")
        ```

        Returns
        -------
        list[TokenResult]
            List of token results for whitespace gaps between decorators
            and their function definitions, or an empty list if none exist.

            ```python
            [
                {"token": "\n", "index": 11, "length": 1}
            ]
            ```
        """
        tree = ast.parse(document)

        lines = document.split("\n")
        line_offsets = self._build_line_offsets(document)
        tokens = []
        self._walk_for_decorated(
            tree,
            lines,
            line_offsets,
            document,
            tokens
        )
        tokens.sort(key=lambda t: t['index'])

        return tokens


    def _build_line_offsets(self, document: str) -> list[int]:
        """Build a list mapping line numbers (0-indexed) to character offsets."""
        offsets = [0]
        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets


    def _walk_for_decorated(
        self,
        tree: ast.Module,
        lines: list[str],
        line_offsets: list[int],
        document: str,
        tokens: list[TokenResult]
    ):
        """Walk the AST to find all decorated functions/methods."""
        for node in ast.walk(tree):
            if not isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef
                )
            ):
                continue

            if not node.decorator_list:
                continue

            decorators = node.decorator_list
            for i in range(len(decorators) - 1):
                self._check_gap(
                    decorators[i],
                    decorators[i + 1].lineno,
                    lines,
                    line_offsets,
                    document,
                    tokens
                )

            last_decorator = decorators[-1]
            self._check_gap(
                last_decorator,
                node.lineno,
                lines,
                line_offsets,
                document,
                tokens
            )


    def _check_gap(
        self,
        prev_node,
        next_line: int,
        lines: list[str],
        line_offsets: list[int],
        document: str,
        tokens: list[TokenResult]
    ):
        """Check for blank lines between a decorator and the next line.

        Parameters
        ----------
        prev_node : ast node
            The decorator or previous node.
        next_line : int
            1-indexed line number of the next decorator or def line.
        """
        prev_end_line = prev_node.end_lineno
        if prev_end_line is None:
            return

        prev_end_idx = prev_end_line
        next_start_idx = next_line - 1
        if prev_end_idx >= next_start_idx:
            return

        start_offset = line_offsets[prev_end_idx]
        end_offset = line_offsets[next_start_idx]
        token = document[start_offset:end_offset]
        if not token or token.strip() == "":
            if token:
                tokens.append(
                    {
                        "token": token,
                        "index": start_offset,
                        "length": len(token)
                    }
                )
