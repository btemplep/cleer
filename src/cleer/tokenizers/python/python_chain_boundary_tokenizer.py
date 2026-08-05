"""Python chain boundary tokenizer module."""

__all__ = ["PythonChainBoundaryTokenizer"]


import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonChainBoundaryTokenizer(Tokenizer):
    """Tokenizes blank lines between chain connectors in compound statements.

    Finds whitespace between the end of one block and the start of the
    next connector in a chain (if/elif/else, try/except/else/finally).

    When ``after_return=False`` (default), emits tokens for boundaries
    where the previous statement is NOT a return/yield/exit. These
    blank lines should be removed.

    When ``after_return=True``, emits tokens for boundaries where the
    previous statement IS a return/yield/exit and the blank lines are
    not exactly 1. These should be normalized to 1 blank.

    Parameters
    ----------
    after_return : bool, default=False
        If False, emit boundaries that should have 0 blank lines.
        If True, emit boundaries after return/yield/exit that should
        have exactly 1 blank line.

    Examples
    --------

    ```python
    from cleer import PythonChainBoundaryTokenizer

    tokenizer = PythonChainBoundaryTokenizer()
    tokens = tokenizer.tokenize("if x:\\n    pass\\n\\nelse:\\n    pass\\n")
    ```
    """
    emits_token_type = "python_chain_boundary"


    def __init__(self, after_return: bool = False):
        self._after_return = after_return

        if after_return:
            self.emits_token_type = "python_chain_boundary_after_return"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize blank lines between chain connectors.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for whitespace between chain parts.
        """
        try:
            tree = ast.parse(document)
        except SyntaxError:
            return []

        line_offsets = self._build_line_offsets(document)
        tokens = []
        seen: set[tuple[int, int]] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                self._check_if_chain(node, document, line_offsets, tokens, seen)
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
                self._check_for_while_else(node, document, line_offsets, tokens, seen)
            elif isinstance(node, ast.Try):
                self._check_try_chain(node, document, line_offsets, tokens, seen)

        tokens.sort(key=lambda t: t["index"])

        return tokens


    def _check_if_chain(
        self,
        node: ast.If,
        document: str,
        line_offsets: list[int],
        tokens: list,
        seen: set
    ):
        """Check boundaries in an if/elif/else chain."""
        if not node.orelse:
            return

        body_end_line = node.body[-1].end_lineno
        first_else = node.orelse[0]

        if isinstance(first_else, ast.If):
            connector_line = first_else.lineno
        else:
            connector_line = self._find_keyword_line(
                document,
                body_end_line,
                first_else.lineno
            )

        self._emit_boundary(
            node.body[-1],
            body_end_line,
            connector_line,
            document,
            line_offsets,
            tokens,
            seen
        )


    def _check_for_while_else(
        self,
        node,
        document: str,
        line_offsets: list[int],
        tokens: list,
        seen: set
    ):
        """Check boundary between for/while body and else."""
        if not node.orelse:
            return

        body_end_line = node.body[-1].end_lineno
        first_else = node.orelse[0]
        connector_line = self._find_keyword_line(
            document,
            body_end_line,
            first_else.lineno
        )

        self._emit_boundary(
            node.body[-1],
            body_end_line,
            connector_line,
            document,
            line_offsets,
            tokens,
            seen
        )


    def _check_try_chain(
        self,
        node: ast.Try,
        document: str,
        line_offsets: list[int],
        tokens: list,
        seen: set
    ):
        """Check boundaries in a try/except/else/finally chain."""
        if node.handlers:
            body_end_line = node.body[-1].end_lineno
            first_handler = node.handlers[0]
            connector_line = first_handler.lineno

            self._emit_boundary(
                node.body[-1],
                body_end_line,
                connector_line,
                document,
                line_offsets,
                tokens,
                seen
            )

            for i in range(len(node.handlers) - 1):
                prev_end = node.handlers[i].end_lineno
                next_handler = node.handlers[i + 1]

                self._emit_boundary(
                    node.handlers[i].body[-1],
                    prev_end,
                    next_handler.lineno,
                    document,
                    line_offsets,
                    tokens,
                    seen
                )

        if node.orelse:
            if node.handlers:
                prev_end = node.handlers[-1].end_lineno
                prev_last_stmt = node.handlers[-1].body[-1]
            else:
                prev_end = node.body[-1].end_lineno
                prev_last_stmt = node.body[-1]

            first_else = node.orelse[0]
            connector_line = self._find_keyword_line(
                document,
                prev_end,
                first_else.lineno
            )

            self._emit_boundary(
                prev_last_stmt,
                prev_end,
                connector_line,
                document,
                line_offsets,
                tokens,
                seen
            )

        if node.finalbody:
            if node.orelse:
                prev_end = node.orelse[-1].end_lineno
                prev_last_stmt = node.orelse[-1]
            elif node.handlers:
                prev_end = node.handlers[-1].end_lineno
                prev_last_stmt = node.handlers[-1].body[-1]
            else:
                prev_end = node.body[-1].end_lineno
                prev_last_stmt = node.body[-1]

            first_finally = node.finalbody[0]
            connector_line = self._find_keyword_line(
                document,
                prev_end,
                first_finally.lineno
            )

            self._emit_boundary(
                prev_last_stmt,
                prev_end,
                connector_line,
                document,
                line_offsets,
                tokens,
                seen
            )


    def _emit_boundary(
        self,
        last_stmt,
        body_end_line: int,
        connector_line: int,
        document: str,
        line_offsets: list[int],
        tokens: list,
        seen: set
    ):
        """Emit a boundary token if there are blank lines between body end and connector."""
        if connector_line <= body_end_line + 1:
            return

        start = line_offsets[body_end_line]
        end = line_offsets[connector_line - 1]
        token = document[start:end]

        if not token.strip():
            token_key = (start, len(token))

            if token_key in seen:
                return

            seen.add(token_key)

            is_after_return = self._is_return_yield_exit(last_stmt)

            if self._after_return:
                if not is_after_return:
                    return

                if token == "\n":
                    return

                tokens.append(
                    {
                        "token": token,
                        "index": start,
                        "length": len(token)
                    }
                )
            else:
                if is_after_return:
                    return

                tokens.append(
                    {
                        "token": token,
                        "index": start,
                        "length": len(token)
                    }
                )


    def _is_return_yield_exit(self, node) -> bool:
        """Check if a node is a return, yield, or exit() call."""
        if isinstance(node, ast.Return):
            return True

        if isinstance(node, ast.Expr):
            if isinstance(node.value, (ast.Yield, ast.YieldFrom)):
                return True

            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "exit"
            ):
                return True

        return False


    def _find_keyword_line(
        self,
        document: str,
        after_line: int,
        before_line: int
    ) -> int:
        """Find the keyword line (else/finally) between two lines.

        Parameters
        ----------
        after_line : int
            1-indexed end line of previous block.
        before_line : int
            1-indexed start line of the body after the keyword.

        Returns
        -------
        int
            1-indexed line number of the keyword.
        """
        lines = document.split("\n")

        for line_num in range(before_line - 1, after_line - 1, -1):
            line_idx = line_num - 1

            if line_idx < len(lines) and lines[line_idx].strip():
                return line_num

        return before_line - 1


    def _build_line_offsets(self, document: str) -> list[int]:
        """Build a list mapping line numbers (0-indexed) to character offsets."""
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
