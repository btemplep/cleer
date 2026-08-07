"""File end whitespace tokenizer module."""

__all__ = [
    "FileEndWhitespaceTokenizer"
]

import re

from cleer.tokenizers.tokenizer import Tokenizer


class FileEndWhitespaceTokenizer(Tokenizer):
    """Tokenizes trailing whitespace at the end of a file.

    Emits a single token of type `file_end_whitespace` for the trailing
    content after the last non-whitespace character. If the file ends with
    exactly one newline after the last content and nothing else, an empty
    list is returned. If it ends with multiple newlines, no newline, or
    extra whitespace, a token is emitted.

    Examples
    --------

    ```python
    from cleer import FileEndWhitespaceTokenizer

    tokenizer = FileEndWhitespaceTokenizer()
    tokens = tokenizer.tokenize("import os\n\n\n")
    ```
    """
    emits_token_type = "file_end_whitespace"
    trailing_whitespace_pattern = re.compile(r"\s*$")


    def tokenize(self, document: str) -> list[dict]:
        """Tokenize trailing whitespace at the end of a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = FileEndWhitespaceTokenizer()
        tokens = tokenizer.tokenize("import os\n\n\n")
        ```

        Returns
        -------
        list[dict]
            List containing a single token result for the trailing whitespace,
            or an empty list if the file ends with exactly one newline.

            ```python
            [
                {"token": "\n\n\n", "index": 9, "length": 3}
            ]
            ```
        """
        match = self.trailing_whitespace_pattern.search(document)
        trailing_ws = match.group()

        return [{
            "token": trailing_ws,
            "index": match.start(),
            "length": len(trailing_ws)
        }]
