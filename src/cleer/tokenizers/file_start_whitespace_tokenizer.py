"""File start whitespace tokenizer module."""

__all__ = [
    "FileStartWhitespaceTokenizer"
]

import re

from cleer.tokenizers.tokenizer import Tokenizer


class FileStartWhitespaceTokenizer(Tokenizer):
    """Tokenizes leading whitespace at the start of a file.

    Emits a single token of type `file_start_whitespace` for the leading
    whitespace before the first non-whitespace character. If the file has
    no leading whitespace, an empty list is returned.

    Examples
    --------

    ```python
    from cleer import FileStartWhitespaceTokenizer

    tokenizer = FileStartWhitespaceTokenizer()
    tokens = tokenizer.tokenize("\n\nimport os\n")
    ```
    """
    emits_token_type = "file_start_whitespace"
    leading_whitespace_pattern = re.compile(r"^\s*")


    def tokenize(self, document: str) -> list[dict]:
        """Tokenize leading whitespace at the start of a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = FileStartWhitespaceTokenizer()
        tokens = tokenizer.tokenize("\n\nimport os\n")
        ```

        Returns
        -------
        list[dict]
            List containing a single token result for the leading whitespace,
            or an empty list if the file has no leading whitespace.

            ```python
            [
                {"token": "\n\n", "index": 0, "length": 2}
            ]
            ```
        """
        match = self.leading_whitespace_pattern.search(document)
        leading_ws = match.group()

        if not leading_ws:
            return []

        return [
            {
                "token": leading_ws,
                "index": 0,
                "length": len(leading_ws)
            }
        ]
