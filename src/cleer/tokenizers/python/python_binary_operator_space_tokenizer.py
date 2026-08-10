"""Python binary operator space tokenizer module."""

__all__ = [
    "PythonBinaryOperatorSpaceTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonBinaryOperatorSpaceTokenizer(Tokenizer):
    """Tokenizes the spacing around binary operators.

    Emits tokens for the segment between the left operand end and the
    right operand start for binary operations, comparisons, boolean
    operations, assignments, and augmented assignments.

    Excludes keyword arguments (handled separately by the kwargs tokenizer).
    Only handles single-line operations.

    Examples
    --------

    ```python
    from cleer import PythonBinaryOperatorSpaceTokenizer

    tokenizer = PythonBinaryOperatorSpaceTokenizer()
    tokens = tokenizer.tokenize("x  =  1\\n")
    ```
    """
    emits_token_type = "python_binary_operator_space"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize operator spacing segments.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each operator spacing segment.

            ```python
            [
                {"token": "  =  ", "index": 1, "length": 5}
            ]
            ```
        """
        tree = ast.parse(document)

        line_offsets = self._build_line_offsets(document)
        tokens = []

        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                self._add_binop(node, document, line_offsets, tokens)
            elif isinstance(node, ast.Compare):
                self._add_compare(node, document, line_offsets, tokens)
            elif isinstance(node, ast.BoolOp):
                self._add_boolop(node, document, line_offsets, tokens)
            elif isinstance(node, ast.Assign):
                self._add_assign(node, document, line_offsets, tokens)
            elif isinstance(node, ast.AugAssign):
                self._add_augassign(node, document, line_offsets, tokens)
            elif (
                isinstance(node, ast.AnnAssign)
                and node.value is not None
            ):
                self._add_annassign(node, document, line_offsets, tokens)

        tokens.sort(key=lambda t: t['index'])

        return tokens


    def _add_binop(
        self,
        node: ast.BinOp,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add token for a binary operation."""
        if node.left.end_lineno != node.right.lineno:
            return

        self._emit_segment(
            node.left.end_lineno,
            node.left.end_col_offset,
            node.right.lineno,
            node.right.col_offset,
            document,
            line_offsets,
            tokens
        )


    def _add_compare(
        self,
        node: ast.Compare,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add tokens for comparison operations."""
        left = node.left

        for comparator in node.comparators:
            if left.end_lineno == comparator.lineno:
                self._emit_segment(
                    left.end_lineno,
                    left.end_col_offset,
                    comparator.lineno,
                    comparator.col_offset,
                    document,
                    line_offsets,
                    tokens
                )

            left = comparator


    def _add_boolop(
        self,
        node: ast.BoolOp,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add tokens for boolean operations (and/or)."""
        for i in range(len(node.values) - 1):
            left = node.values[i]
            right = node.values[i + 1]

            if left.end_lineno != right.lineno:
                continue

            self._emit_segment(
                left.end_lineno,
                left.end_col_offset,
                right.lineno,
                right.col_offset,
                document,
                line_offsets,
                tokens
            )


    def _add_assign(
        self,
        node: ast.Assign,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add token for an assignment."""
        last_target = node.targets[-1]

        if last_target.end_lineno != node.value.lineno:
            return

        self._emit_segment(
            last_target.end_lineno,
            last_target.end_col_offset,
            node.value.lineno,
            node.value.col_offset,
            document,
            line_offsets,
            tokens
        )


    def _add_augassign(
        self,
        node: ast.AugAssign,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add token for an augmented assignment."""
        if node.target.end_lineno != node.value.lineno:
            return

        self._emit_segment(
            node.target.end_lineno,
            node.target.end_col_offset,
            node.value.lineno,
            node.value.col_offset,
            document,
            line_offsets,
            tokens
        )


    def _add_annassign(
        self,
        node: ast.AnnAssign,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add token for an annotated assignment with value."""
        if node.annotation.end_lineno != node.value.lineno:
            return

        self._emit_segment(
            node.annotation.end_lineno,
            node.annotation.end_col_offset,
            node.value.lineno,
            node.value.col_offset,
            document,
            line_offsets,
            tokens
        )


    def _emit_segment(
        self,
        left_end_line: int,
        left_end_col: int,
        right_line: int,
        right_col: int,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Emit a token for the segment between two operands."""
        start = line_offsets[left_end_line - 1] + left_end_col
        end = line_offsets[right_line - 1] + right_col

        if end <= start:
            return

        token = document[start:end]

        while token and token[0] in ")]}":
            token = token[1:]
            start += 1

        while token and token[-1] in "([{":
            token = token[:-1]
            end -= 1

        if not token or not token.strip():
            return

        stripped = token.strip()

        if not stripped:
            return

        expected = f" {stripped} "

        if token == expected:
            return

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
