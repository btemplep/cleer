"""File tokenizer module."""

__all__ = [
    "FileTokenizer"
]

from cleer.tokenizers.tokenizer import Tokenizer


class FileTokenizer(Tokenizer):
    """Tokenizes a document as a single whole-file token.

    The entire document is returned as one token. If the document is an
    empty string, an empty list is returned.

    Emits token type: `file`

    Examples
    --------

    ```python
    from cleer import FileTokenizer

    tokenizer = FileTokenizer()
    tokens = tokenizer.tokenize("hello world\\ngoodbye world\\n")
    ```
    """
    emits_token_type = "file"


    def tokenize(self, document: str) -> list[dict]:
        """Tokenize a document as a single whole-file token.

        Returns the entire document as a single token with index 0 and
        length equal to the length of the document string.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = FileTokenizer()
        tokens = tokenizer.tokenize("hello\\nworld\\n")
        ```

        Returns
        -------
        list[TokenResult]
            List containing a single token result for the whole document,
            or an empty list if the document is empty.

            ```python
            [
                {
                    "token": "hello\\nworld\\n",
                    "index": 0,
                    "length": 12
                }
            ]
            ```
        """
        return [{
            "token": document,
            "index": 0,
            "length": len(document)
        }]
