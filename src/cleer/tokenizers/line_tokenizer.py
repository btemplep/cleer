"""Line tokenizer module."""

__all__ = ["LineTokenizer"]


from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class LineTokenizer(Tokenizer):
    """Tokenizes a document into individual lines.

    Each line is returned as a token, excluding the newline character itself.
    The newline character is not included in the token or its length.

    Emits token type: `line`

    Examples
    --------

    ```python
    from cleer import LineTokenizer

    tokenizer = LineTokenizer()
    tokens = tokenizer.tokenize("hello world\\ngoodbye world\\n")
    ```
    """
    emits_token_type = "line"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize a document into lines.

        Each line becomes a token. The newline character is not included
        in the token string or its length.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = LineTokenizer()
        tokens = tokenizer.tokenize("hello\\nworld\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per line.

            ```python
            [
                {"token": "hello", "index": 0, "length": 5},
                {"token": "world", "index": 6, "length": 5},
                {"token": "", "index": 12, "length": 0}
            ]
            ```
        """
        tokens: List[dict] = []
        index = 0

        lines = document.split("\n")
        for i, line in enumerate(lines):
            if i < len(lines) - 1 or line:
                tokens.append(
                    {
                        "token": line,
                        "index": index,
                        "length": len(line)
                    }
                )

            index += len(line) + 1

        return tokens
