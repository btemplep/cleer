"""See :class:`LineTokenizer`."""

__all__ = [
    "LineTokenizer"
]

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class LineTokenizer(Tokenizer):
    """Tokenizes a document into individual lines.

    Splits the document on newlines and emits each line as a token.
    The newline character is not included in the token.

    Examples
    --------

    ```python
    from cleer import LineTokenizer

    tokenizer = LineTokenizer()
    tokens = tokenizer.tokenize("import os\nx = 1\n")
    ```
    """
    emits_token_type = "line"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize a document into individual lines.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = LineTokenizer()
        tokens = tokenizer.tokenize("import os\nx = 1\n")
        ```

        Returns
        -------
        list[TokenResult]
            List of token results for each line, or an empty list if
            the document is empty.

            ```python
            [
                {"token": "import os", "index": 0, "length": 9},
                {"token": "x = 1", "index": 10, "length": 5},
                {"token": "", "index": 16, "length": 0}
            ]
            ```
        """
        if not document:
            return []

        tokens = []
        index = 0
        for line in document.split("\n"):
            tokens.append(
                {
                    "token": line,
                    "index": index,
                    "length": len(line)
                }
            )
            index += len(line) + 1

        return tokens
