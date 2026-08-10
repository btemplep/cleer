"""Python colon space tokenizer module."""

__all__ = [
    "PythonColonSpaceTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonColonSpaceTokenizer(Tokenizer):
    """Tokenizes the spacing around colons in type annotations and dicts.

    Emits tokens for the segment between the element before the colon
    and the element after (including the colon and surrounding whitespace).
    Handles type annotation colons and dict literal key-value colons.

    Does NOT handle function definition body colons or slice colons.

    Examples
    --------

    ```python
    from cleer import PythonColonSpaceTokenizer

    tokenizer = PythonColonSpaceTokenizer()
    tokens = tokenizer.tokenize("x : int = 1\\n")
    ```
    """
    emits_token_type = "python_colon_space"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize colon spacing segments.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each colon spacing segment.

            ```python
            [
                {"token": " : ", "index": 1, "length": 3}
            ]
            ```
        """
        tree = ast.parse(document)

        line_offsets = self._build_line_offsets(document)
        tokens = []

        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign):
                self._add_ann_assign(node, document, line_offsets, tokens)
            elif isinstance(node, ast.arg) and node.annotation:
                self._add_arg_annotation(
                    node,
                    document,
                    line_offsets,
                    tokens
                )
            elif isinstance(node, ast.Dict):
                self._add_dict_colons(node, document, line_offsets, tokens)

        tokens.sort(key=lambda t: t['index'])

        return tokens


    def _add_ann_assign(
        self,
        node: ast.AnnAssign,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add token for annotated assignment colon."""
        if node.target.end_lineno != node.annotation.lineno:
            return

        start = line_offsets[node.target.end_lineno - 1] + node.target.end_col_offset
        end = line_offsets[node.annotation.lineno - 1] + node.annotation.col_offset
        token = document[start:end]

        if token == ": ":
            return

        tokens.append(
            {
                "token": token,
                "index": start,
                "length": len(token)
            }
        )


    def _add_arg_annotation(
        self,
        node: ast.arg,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add token for function argument annotation colon."""
        arg_name_end_col = node.col_offset + len(node.arg)

        if node.lineno != node.annotation.lineno:
            return

        start = line_offsets[node.lineno - 1] + arg_name_end_col
        end = line_offsets[node.annotation.lineno - 1] + node.annotation.col_offset
        token = document[start:end]

        if token == ": ":
            return

        tokens.append(
            {
                "token": token,
                "index": start,
                "length": len(token)
            }
        )


    def _add_dict_colons(
        self,
        node: ast.Dict,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add tokens for dict literal key-value colons."""
        for key, value in zip(node.keys, node.values):
            if key is None:
                continue

            if key.end_lineno != value.lineno:
                continue

            start = line_offsets[key.end_lineno - 1] + key.end_col_offset
            end = line_offsets[value.lineno - 1] + value.col_offset
            token = document[start:end]

            if token == ": ":
                continue

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
