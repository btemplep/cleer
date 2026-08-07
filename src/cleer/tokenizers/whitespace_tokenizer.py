"""Whitespace tokenizer module."""

__all__ = [
    "WhitespaceTokenizer"
]

import re

from cleer.tokenizers.tokenizer import Tokenizer


class WhitespaceTokenizer(Tokenizer):
    """Tokenizes all blocks of only whitespace in a document.

    Scans a document and emits a token for every contiguous block that
    contains only whitespace characters (spaces, tabs, newlines, etc.).

    Examples
    --------

    ```python
    from cleer import WhitespaceTokenizer

    tokenizer = WhitespaceTokenizer()
    tokens = tokenizer.tokenize("import os\n\n\nx = 1\n")
    ```
    """
    emits_token_type = "whitespace"
    whitespace_pattern = re.compile(r"\s+")


    def tokenize(self, document: str) -> list[dict]:
        """Tokenize all blocks of whitespace in a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = WhitespaceTokenizer()
        tokens = tokenizer.tokenize("import os\n\n\nx = 1\n")
        ```

        Returns
        -------
        list[dict]
            List of token results for each whitespace block, or an empty
            list if no whitespace exists.

            ```python
            [
                {"token": "\n\n\n", "index": 9, "length": 3},
                {"token": " ", "index": 11, "length": 1},
                {"token": "\n", "index": 15, "length": 1}
            ]
            ```
        """
        tokens = []

        for match in self.whitespace_pattern.finditer(document):
            tokens.append(
                {
                    "token": match.group(),
                    "index": match.start(),
                    "length": len(match.group())
                }
            )

        return tokens
