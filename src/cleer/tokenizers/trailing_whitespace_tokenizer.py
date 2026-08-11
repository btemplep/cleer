"""See :class:`TrailingWhitespaceTokenizer`."""

__all__ = [
    "TrailingWhitespaceTokenizer"
]

import re

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class TrailingWhitespaceTokenizer(Tokenizer):
    """Tokenizes trailing whitespace at the end of lines.

    Scans a document and emits a token for each occurrence of trailing
    whitespace (spaces or tabs) before a newline character.

    Examples
    --------

    ```python
    from cleer import TrailingWhitespaceTokenizer

    tokenizer = TrailingWhitespaceTokenizer()
    tokens = tokenizer.tokenize("import os   \nx = 1\n")
    ```
    """
    emits_token_type = "trailing_whitespace"
    trailing_ws_pattern = re.compile(r"[ \t]+(?=\n)")


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize trailing whitespace before newlines in a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = TrailingWhitespaceTokenizer()
        tokens = tokenizer.tokenize("import os   \nx = 1  \n")
        ```

        Returns
        -------
        list[TokenResult]
            List of token results for each trailing whitespace occurrence,
            or an empty list if none exist.

            ```python
            [
                {"token": "   ", "index": 9, "length": 3},
                {"token": "  ", "index": 17, "length": 2}
            ]
            ```
        """
        tokens = []

        for match in self.trailing_ws_pattern.finditer(document):
            tokens.append(
                {
                    "token": match.group(),
                    "index": match.start(),
                    "length": len(match.group())
                }
            )

        return tokens
