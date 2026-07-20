"""Non-ascii whitespace tokenizer module."""

__all__ = ["NonAsciiWhitespaceTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


NON_ASCII_WHITESPACE_PATTERN = re.compile(r"[^\S\x00-\x7F]+")


class NonAsciiWhitespaceTokenizer(Tokenizer):
    """Tokenizes non-ascii whitespace characters in a document.

    Each contiguous sequence of non-ascii whitespace characters is returned
    as a token. ASCII whitespace characters (space, tab, newline, etc.) are
    not tokenized.

    Emits token type: `non_ascii_whitespace`

    Examples
    --------

    ```python
    from cleer import NonAsciiWhitespaceTokenizer

    tokenizer = NonAsciiWhitespaceTokenizer()
    tokens = tokenizer.tokenize("hello\u00a0world")
    ```
    """
    emits_token_type = "non_ascii_whitespace"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize non-ascii whitespace in a document.

        Each contiguous sequence of non-ascii whitespace characters becomes
        a token.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = NonAsciiWhitespaceTokenizer()
        tokens = tokenizer.tokenize("hello\\u00a0world\\u2003end")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per contiguous non-ascii whitespace sequence.

            ```python
            [
                {"token": "\\u00a0", "index": 5, "length": 1},
                {"token": "\\u2003", "index": 11, "length": 1}
            ]
            ```
        """
        tokens: List[dict] = []

        for match in NON_ASCII_WHITESPACE_PATTERN.finditer(document):
            tokens.append(
                {
                    "token": match.group(),
                    "index": match.start(),
                    "length": len(match.group())
                }
            )

        return tokens
