"""Python unary operator space tokenizer module."""

__all__ = ["PythonUnaryOperatorSpaceTokenizer"]


import ast


from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonUnaryOperatorSpaceTokenizer(Tokenizer):
    """Tokenizes unary negative operators that have space before the operand.

    Emits tokens for unary `-` expressions where there is whitespace
    between the `-` and its operand (e.g., `- x` should be `-x`).

    Examples
    --------

    ```python
    from cleer import PythonUnaryOperatorSpaceTokenizer

    tokenizer = PythonUnaryOperatorSpaceTokenizer()
    tokens = tokenizer.tokenize("x = - y\\n")
    ```
    """
    emits_token_type = "python_unary_operator_space"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize unary negative operators with incorrect spacing.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each unary negative with spacing.

            ```python
            [
                {"token": "- y", "index": 4, "length": 3}
            ]
            ```
        """
        tree = ast.parse(document)

        line_offsets = self._build_line_offsets(document)
        tokens = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.UnaryOp):
                continue

            if not isinstance(node.op, ast.USub):
                continue

            if node.lineno != node.operand.lineno:
                continue

            op_start = line_offsets[node.lineno - 1] + node.col_offset
            operand_end = line_offsets[node.operand.end_lineno - 1] + node.operand.end_col_offset

            token = document[op_start:operand_end]

            if token.startswith("-") and len(token) > 1 and token[1] == " ":
                tokens.append(
                    {
                        "token": token,
                        "index": op_start,
                        "length": len(token)
                    }
                )

        tokens.sort(key=lambda t: t["index"])

        return tokens


    def _build_line_offsets(self, document: str) -> list[int]:
        """Build a list mapping line numbers (0-indexed) to character offsets."""
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
