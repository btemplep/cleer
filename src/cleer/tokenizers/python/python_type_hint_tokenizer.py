"""See :class:`PythonTypeHintTokenizer`."""

__all__ = [
    "PythonTypeHintTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonTypeHintTokenizer(Tokenizer):
    """Tokenizes type annotations that may need structural formatting.

    Emits tokens spanning from the start of the line to the end of the
    annotation for each type annotation that contains subscripts or
    union operators. Simple name annotations are skipped.

    Examples
    --------

    ```python
    from cleer import PythonTypeHintTokenizer

    tokenizer = PythonTypeHintTokenizer()
    tokens = tokenizer.tokenize("x: dict[str, list[int]] = {}\\n")
    ```
    """
    emits_token_type = "python_type_hint"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize type annotations that need structural formatting.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each complex type annotation.
        """
        try:
            tree = ast.parse(document)
        except SyntaxError:
            return []

        line_offsets = self._build_line_offsets(document)
        tokens = []

        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign) and node.annotation:
                self._maybe_add(
                    node.annotation,
                    document,
                    line_offsets,
                    tokens
                )
            elif isinstance(node, ast.arg) and node.annotation:
                self._maybe_add(
                    node.annotation,
                    document,
                    line_offsets,
                    tokens
                )
            elif (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.returns
            ):
                self._maybe_add(
                    node.returns,
                    document,
                    line_offsets,
                    tokens
                )
            elif (
                isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Subscript)
            ):
                self._maybe_add(node.value, document, line_offsets, tokens)
            elif (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Subscript)
            ):
                self._maybe_add(node.value, document, line_offsets, tokens)

        tokens.sort(key=lambda t: t['index'])
        tokens = self._remove_overlaps(tokens)

        return tokens


    def _maybe_add(
        self,
        annotation: ast.expr,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add a token if the annotation is complex enough to format."""
        if not isinstance(annotation, (ast.Subscript, ast.BinOp)):
            return

        start = line_offsets[annotation.lineno - 1]
        end = (
            line_offsets[annotation.end_lineno - 1]
            + annotation.end_col_offset
        )

        if end > len(document):
            return

        token = document[start:end]

        tokens.append(
            {
                "token": token,
                "index": start,
                "length": len(token)
            }
        )


    def _build_line_offsets(self, document: str) -> list[int]:
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets


    def _remove_overlaps(self, tokens: list[TokenResult]) -> list[TokenResult]:
        if not tokens:
            return tokens

        result = []

        for tok in tokens:
            if (
                result
                and tok['index'] < result[-1]['index'] + result[-1]['length']
            ):
                if tok['length'] > result[-1]['length']:
                    result[-1] = tok

            else:
                result.append(tok)

        return result
