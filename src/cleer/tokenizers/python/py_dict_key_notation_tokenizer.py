"""Dict key notation tokenizer module."""

__all__ = ["PyDictKeyNotationTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


DICT_KEY_PATTERN = re.compile(r"(?<=[\w\]\)])\[(['\"])")


class PyDictKeyNotationTokenizer(Tokenizer):
    """Tokenizes string literals used in dictionary bracket key notation.

    Finds patterns like `my_dict['my_key']` and returns the string literal
    (including quotes) as a token.

    Emits token type: `quotation`

    Examples
    --------

    ```python
    from cleer import PyDictKeyNotationTokenizer

    tokenizer = PyDictKeyNotationTokenizer()
    tokens = tokenizer.tokenize("my_dict['my_key']\\n")
    ```
    """
    emits_token_type = "quotation"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize string literals in dict key bracket notation.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyDictKeyNotationTokenizer()
        tokens = tokenizer.tokenize("x = my_dict['key']\\ny = other['name']\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per dict key string literal.

            ```python
            [
                {"token": "'key'", "index": 12, "length": 5},
                {"token": "'name'", "index": 28, "length": 6}
            ]
            ```
        """
        tokens: List[dict] = []

        for match in DICT_KEY_PATTERN.finditer(document):
            quote_char = match.group(1)
            string_start = match.start(1)

            end = string_start + 1
            while end < len(document):
                if document[end] == "\\":
                    end += 2
                    continue

                if document[end] == quote_char:
                    end += 1
                    break

                end += 1

            if end <= len(document) and document[end - 1] == quote_char:
                token_text = document[string_start:end]
                tokens.append(
                    {
                        "token": token_text,
                        "index": string_start,
                        "length": len(token_text)
                    }
                )

        return tokens
