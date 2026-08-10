"""Non-ASCII whitespace tokenizer module."""

__all__ = [
    "NonAsciiWhitespaceTokenizer"
]

import re

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class NonAsciiWhitespaceTokenizer(Tokenizer):
    """Tokenizes non-ASCII whitespace characters in a document.

    Scans a document and emits a token for every contiguous block of
    non-ASCII whitespace characters. This includes characters like
    non-breaking spaces, ideographic spaces, zero-width spaces, and
    other Unicode whitespace that is not a standard ASCII space, tab,
    newline, carriage return, or form feed.

    Examples
    --------

    ```python
    from cleer import NonAsciiWhitespaceTokenizer

    tokenizer = NonAsciiWhitespaceTokenizer()
    tokens = tokenizer.tokenize("import\u00a0os\n")
    ```
    """
    emits_token_type = "non_ascii_whitespace"
    non_ascii_ws_pattern = re.compile(r"[^\S\x00-\x7f]+")


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize all non-ASCII whitespace blocks in a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = NonAsciiWhitespaceTokenizer()
        tokens = tokenizer.tokenize("import\u00a0os\n")
        ```

        Returns
        -------
        list[TokenResult]
            List of token results for each non-ASCII whitespace block,
            or an empty list if none exist.

            ```python
            [
                {"token": "\u00a0", "index": 6, "length": 1}
            ]
            ```
        """
        tokens = []
        for match in self.non_ascii_ws_pattern.finditer(document):
            tokens.append(
                {
                    "token": match.group(),
                    "index": match.start(),
                    "length": len(match.group())
                }
            )

        return tokens
