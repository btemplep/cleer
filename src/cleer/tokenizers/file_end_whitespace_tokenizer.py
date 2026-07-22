"""File end whitespace tokenizer module."""

__all__ = ["FileEndWhitespaceTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


TRAILING_WHITESPACE_PATTERN = re.compile(
    r"(?<=\S)(\s+)$",
    re.DOTALL
)


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
    tokens = tokenizer.tokenize("import os\\n\\n\\n")
    ```
    """
    emits_token_type = "file_end_whitespace"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize trailing whitespace at the end of a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = FileEndWhitespaceTokenizer()
        tokens = tokenizer.tokenize("import os\\n\\n\\n")
        ```

        Returns
        -------
        List[dict]
            List containing a single token result for the trailing whitespace,
            or an empty list if the file ends with exactly one newline.

            ```python
            [
                {"token": "\\n\\n\\n", "index": 9, "length": 3}
            ]
            ```
        """
        if not document:
            return []

        match = TRAILING_WHITESPACE_PATTERN.search(document)

        if match is None:
            return [
                {
                    "token": "",
                    "index": len(document),
                    "length": 0
                }
            ]

        trailing = match.group(1)

        if trailing == "\n":
            return []

        return [
            {
                "token": trailing,
                "index": match.start(1),
                "length": len(trailing)
            }
        ]
