__all__ = ["MaxNewlinesTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


MAX_NEWLINES_PATTERN = re.compile(r"\n{4,}")


class MaxNewlinesTokenizer(Tokenizer):
    """Tokenizes sequences of 4 or more consecutive newline characters.

    A sequence of 4+ newlines represents 3+ blank lines between content,
    which exceeds the maximum of 2 blank lines. Sequences of exactly 3
    newlines (2 blank lines) are acceptable and are not tokenized.

    Emits token type: `max_newlines`

    Examples
    --------

    ```python
    from cleer import MaxNewlinesTokenizer

    tokenizer = MaxNewlinesTokenizer()
    tokens = tokenizer.tokenize("hello\n\n\n\nworld")
    ```
    """
    emits_token_type = "max_newlines"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize sequences of 4 or more consecutive newlines in a document.

        Each contiguous run of 4+ newline characters becomes a token.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = MaxNewlinesTokenizer()
        tokens = tokenizer.tokenize("hello\\n\\n\\n\\nworld\\n\\n\\n\\n\\nend")
        ```

        Returns
        -------
        List[dict]
            List of token results, one per excessive newline sequence.

            ```python
            [
                {"token": "\\n\\n\\n\\n", "index": 5, "length": 4},
                {"token": "\\n\\n\\n\\n\\n", "index": 14, "length": 5}
            ]
            ```
        """
        tokens: List[dict] = []

        for match in MAX_NEWLINES_PATTERN.finditer(document):
            tokens.append(
                {
                    "token": match.group(),
                    "index": match.start(),
                    "length": len(match.group())
                }
            )

        return tokens
