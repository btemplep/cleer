"""See :class:`PythonCompoundEndTokenizer`."""

__all__ = [
    "PythonCompoundEndTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonCompoundEndTokenizer(Tokenizer):
    """Tokenizes missing blank lines after compound statement chains.

    Finds compound statements (if/elif/else, try/except/finally,
    for/else, while/else, with) and emits a token when there are 0
    blank lines between the end of the chain and the next statement.

    Only emits when there is no blank line. Does not reduce existing
    blank lines if there is already at least one.

    Examples
    --------

    ```python
    from cleer import PythonCompoundEndTokenizer

    tokenizer = PythonCompoundEndTokenizer()
    tokens = tokenizer.tokenize("if x:\\n    pass\\nnext_stmt\\n")
    ```
    """
    emits_token_type = "python_compound_end"
    _compound_types = (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.With,
        ast.AsyncWith,
        ast.Try
    )


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize missing blank lines after compound statement chains.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for locations where a blank line
            should be inserted after a compound statement.
        """
        try:
            tree = ast.parse(document)
        except SyntaxError:
            return []

        line_offsets = self._build_line_offsets(document)
        tokens = []
        seen: set[tuple[int, int]] = set()
        self._process_bodies(
            tree,
            document,
            line_offsets,
            tokens,
            seen
        )
        tokens.sort(key=lambda t: t['index'])

        return tokens


    def _process_bodies(
        self,
        tree,
        document: str,
        line_offsets: list[int],
        tokens: list,
        seen: set
    ):
        """Walk all bodies and check compound statements within them."""
        for node in ast.walk(tree):
            for attr in (
                "body",
                "orelse",
                "finalbody"
            ):
                body = getattr(node, attr, None)

                if not isinstance(body, list):
                    continue

                if attr == "orelse" and isinstance(node, ast.If):
                    if len(body) == 1 and isinstance(body[0], ast.If):
                        continue

                self._check_body(
                    body,
                    document,
                    line_offsets,
                    tokens,
                    seen
                )

            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    self._check_body(
                        handler.body,
                        document,
                        line_offsets,
                        tokens,
                        seen
                    )


    def _check_body(
        self,
        body: list,
        document: str,
        line_offsets: list[int],
        tokens: list,
        seen: set
    ):
        """Check each compound statement in a body for missing trailing blank."""
        lines = document.split("\n")

        for i, stmt in enumerate(body):
            if not isinstance(stmt, self._compound_types):
                continue

            if i >= len(body) - 1:
                compound_end_line = stmt.end_lineno

                if compound_end_line is None:
                    continue

                if compound_end_line < len(lines):
                    next_line = lines[compound_end_line]
                    if next_line.strip() and next_line.lstrip().startswith("#"):
                        start = line_offsets[compound_end_line]
                        end = start
                        token = ""
                        token_key = (start, 0)

                        if token_key not in seen:
                            seen.add(token_key)
                            tokens.append(
                                {
                                    "token": token,
                                    "index": start,
                                    "length": 0
                                }
                            )

                continue

            next_stmt = body[i + 1]
            compound_end_line = stmt.end_lineno

            if compound_end_line is None:
                continue

            next_start_line = next_stmt.lineno

            if (
                hasattr(next_stmt, "decorator_list")
                and next_stmt.decorator_list
            ):
                next_start_line = next_stmt.decorator_list[0].lineno

            if next_start_line <= compound_end_line + 1:
                start = line_offsets[compound_end_line]
                end = line_offsets[next_start_line - 1]
                token = document[start:end]

                token_key = (start, len(token))

                if token_key in seen:
                    continue

                seen.add(token_key)
                tokens.append(
                    {
                        "token": token,
                        "index": start,
                        "length": len(token)
                    }
                )
            elif compound_end_line < len(lines):
                next_line = lines[compound_end_line]
                if next_line.strip() and next_line.lstrip().startswith("#"):
                    start = line_offsets[compound_end_line]
                    token_key = (start, 0)

                    if token_key not in seen:
                        seen.add(token_key)
                        tokens.append(
                            {
                                "token": "",
                                "index": start,
                                "length": 0
                            }
                        )


    def _build_line_offsets(self, document: str) -> list[int]:
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
