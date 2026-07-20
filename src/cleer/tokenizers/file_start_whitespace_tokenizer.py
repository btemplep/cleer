"""File start whitespace tokenizer module."""

__all__ = ["FileStartWhitespaceTokenizer"]


from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class FileStartWhitespaceTokenizer(Tokenizer):
    """Tokenizes leading whitespace at the start of a file.

    If the file starts with whitespace (spaces, tabs, newlines), a single
    token of type `file_start_whitespace` is emitted containing that leading
    whitespace. If the file does not start with whitespace, an empty list is
    returned.

    Examples
    --------

    ```python
    from cleer import FileStartWhitespaceTokenizer

    tokenizer = FileStartWhitespaceTokenizer()
    tokens = tokenizer.tokenize("\\n\\n  import os\\n")
    ```
    """
    emits_token_type = "file_start_whitespace"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize leading whitespace at the start of a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = FileStartWhitespaceTokenizer()
        tokens = tokenizer.tokenize("\\n  import os\\n")
        ```

        Returns
        -------
        List[dict]
            List containing a single token result for the leading whitespace,
            or an empty list if the document does not start with whitespace.

            ```python
            [
                {"token": "\\n  ", "index": 0, "length": 3}
            ]
            ```
        """
        if not document:
            return []

        stripped = document.lstrip()
        leading_length = len(document) - len(stripped)

        if leading_length == 0:
            return []

        leading = document[:leading_length]

        return [
            {
                "token": leading,
                "index": 0,
                "length": leading_length
            }
        ]
