"""Python block start tokenizer module."""

__all__ = ["PythonBlockStartTokenizer"]


import ast


from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonBlockStartTokenizer(Tokenizer):
    """Tokenizes blank lines between block statements and first body line.

    Emits a token for the whitespace between a block statement (def,
    if, for, while, with, try, etc.) and the first statement in its
    body when there are blank lines between them.

    Also handles blank lines between a function docstring and the
    first code line.

    Examples
    --------

    ```python
    from cleer import PythonBlockStartTokenizer

    tokenizer = PythonBlockStartTokenizer()
    tokens = tokenizer.tokenize("def foo():\\n\\n    pass\\n")
    ```
    """
    emits_token_type = "python_block_start"

    _block_types = (
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.With,
        ast.AsyncWith,
        ast.Try,
    )


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize blank lines between block statements and first body line.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for whitespace gaps after block
            statement lines.
        """
        try:
            tree = ast.parse(document)
        except SyntaxError:
            return []

        line_offsets = self._build_line_offsets(document)
        tokens = []
        seen = set()

        for node in ast.walk(tree):
            if isinstance(node, self._block_types):
                self._check_body_start(node, node.body, line_offsets, document, tokens, seen)

                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._check_after_docstring(node, line_offsets, document, tokens, seen)

            if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While)):
                if node.orelse:
                    first_else = node.orelse[0]

                    if not isinstance(first_else, ast.If):
                        else_line = self._find_keyword_line(
                            document,
                            line_offsets,
                            node.body[-1].end_lineno,
                            first_else.lineno
                        )

                        self._check_body_start_at_line(
                            else_line,
                            node.orelse,
                            line_offsets,
                            document,
                            tokens,
                            seen
                        )

            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    self._check_body_start(
                        handler,
                        handler.body,
                        line_offsets,
                        document,
                        tokens,
                        seen
                    )

                if node.orelse:
                    else_line = self._find_keyword_line(
                        document,
                        line_offsets,
                        node.handlers[-1].end_lineno if node.handlers else node.body[-1].end_lineno,
                        node.orelse[0].lineno
                    )

                    self._check_body_start_at_line(
                        else_line,
                        node.orelse,
                        line_offsets,
                        document,
                        tokens,
                        seen
                    )

                if node.finalbody:
                    prev_end = node.orelse[-1].end_lineno if node.orelse else (
                        node.handlers[-1].end_lineno if node.handlers else node.body[-1].end_lineno
                    )
                    finally_line = self._find_keyword_line(
                        document,
                        line_offsets,
                        prev_end,
                        node.finalbody[0].lineno
                    )

                    self._check_body_start_at_line(
                        finally_line,
                        node.finalbody,
                        line_offsets,
                        document,
                        tokens,
                        seen
                    )

        tokens.sort(key=lambda t: t["index"])

        return tokens


    def _check_body_start(
        self,
        parent_node,
        body: list,
        line_offsets: list[int],
        document: str,
        tokens: list,
        seen: set
    ):
        """Check for blank lines between a block statement and its first body line."""
        if not body:
            return

        first_stmt = body[0]
        first_body_line = first_stmt.lineno

        colon_line = self._find_colon_line(
            parent_node.lineno, first_body_line, line_offsets, document
        )

        if first_body_line <= colon_line + 1:
            return

        start = line_offsets[colon_line]
        end = line_offsets[first_body_line - 1]
        token = document[start:end]

        if not token.strip():
            token_key = (start, len(token))

            if token_key not in seen:
                seen.add(token_key)
                tokens.append(
                    {
                        "token": token,
                        "index": start,
                        "length": len(token)
                    }
                )


    def _find_colon_line(
        self,
        start_lineno: int,
        body_lineno: int,
        line_offsets: list[int],
        document: str
    ) -> int:
        """Find the line number (1-indexed) of the colon ending the block header.

        Scans backwards from the body start to find the last non-blank
        line before the body, which is the line ending with ':'.
        """
        for line_num in range(body_lineno - 1, start_lineno - 1, -1):
            line_start = line_offsets[line_num - 1]
            if line_num < len(line_offsets):
                line_end = line_offsets[line_num]
            else:
                line_end = len(document)
            line_text = document[line_start:line_end]
            if line_text.strip():
                return line_num

        return start_lineno


    def _check_after_docstring(
        self,
        node,
        line_offsets: list[int],
        document: str,
        tokens: list,
        seen: set
    ):
        """Check for blank lines between function docstring and first code line."""
        if len(node.body) < 2:
            return

        first_stmt = node.body[0]

        if not (
            isinstance(first_stmt, ast.Expr)
            and isinstance(first_stmt.value, ast.Constant)
            and isinstance(first_stmt.value.value, str)
        ):
            return

        docstring_end_line = first_stmt.end_lineno
        second_body_line = node.body[1].lineno

        if second_body_line <= docstring_end_line + 1:
            return

        start = line_offsets[docstring_end_line]
        end = line_offsets[second_body_line - 1]
        token = document[start:end]

        if not token.strip():
            token_key = (start, len(token))

            if token_key not in seen:
                seen.add(token_key)
                tokens.append(
                    {
                        "token": token,
                        "index": start,
                        "length": len(token)
                    }
                )


    def _check_body_start_at_line(
        self,
        keyword_line: int,
        body: list,
        line_offsets: list[int],
        document: str,
        tokens: list,
        seen: set
    ):
        """Check for blank lines between a keyword line and first body line."""
        if not body:
            return

        first_body_line = body[0].lineno

        if first_body_line <= keyword_line + 1:
            return

        start = line_offsets[keyword_line]
        end = line_offsets[first_body_line - 1]
        token = document[start:end]

        if not token.strip():
            token_key = (start, len(token))

            if token_key not in seen:
                seen.add(token_key)
                tokens.append(
                    {
                        "token": token,
                        "index": start,
                        "length": len(token)
                    }
                )


    def _find_keyword_line(
        self,
        document: str,
        line_offsets: list[int],
        after_line: int,
        before_line: int
    ) -> int:
        """Find the keyword line (else/elif/except/finally) between two lines.

        Scans backward from before_line to find the line containing
        the keyword.

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
