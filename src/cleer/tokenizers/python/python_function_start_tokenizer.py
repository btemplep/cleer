"""Python function start tokenizer module."""

__all__ = ["PythonFunctionStartTokenizer"]


import ast
from typing import List

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonFunctionStartTokenizer(Tokenizer):
    """Tokenizes blank lines between function definition and first body line.

    Emits a token for the whitespace between the def/async def line and
    the first statement in the function body (docstring or code) when
    there are blank lines between them.

    Examples
    --------

    ```python
    from cleer import PythonFunctionStartTokenizer

    tokenizer = PythonFunctionStartTokenizer()
    tokens = tokenizer.tokenize("def foo():\\n\\n    pass\\n")
    ```
    """
    emits_token_type = "python_function_start"


    def tokenize(self, document: str) -> List[TokenResult]:
        """Tokenize blank lines between def and first body line.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        List[TokenResult]
            List of token results for whitespace gaps after def lines.
        """
        try:
            tree = ast.parse(document)
        except SyntaxError:
            return []

        line_offsets = self._build_line_offsets(document)
        tokens = []

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            if not node.body:
                continue

            def_end_line = node.lineno
            first_body_line = node.body[0].lineno

            if first_body_line > def_end_line + 1:
                start = line_offsets[def_end_line]
                end = line_offsets[first_body_line - 1]
                token = document[start:end]

                if not token.strip():
                    tokens.append(
                        {
                            "token": token,
                            "index": start,
                            "length": len(token)
                        }
                    )

            if len(node.body) >= 2:
                first_stmt = node.body[0]

                if (
                    isinstance(first_stmt, ast.Expr)
                    and isinstance(first_stmt.value, ast.Constant)
                    and isinstance(first_stmt.value.value, str)
                ):
                    docstring_end_line = first_stmt.end_lineno
                    second_body_line = node.body[1].lineno

                    if second_body_line > docstring_end_line + 1:
                        start = line_offsets[docstring_end_line]
                        end = line_offsets[second_body_line - 1]
                        token = document[start:end]

                        if not token.strip():
                            tokens.append(
                                {
                                    "token": token,
                                    "index": start,
                                    "length": len(token)
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
