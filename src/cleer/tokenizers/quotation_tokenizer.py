"""Quotation tokenizer module."""

__all__ = ["QuotationTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


DICT_KEY_PATTERN = re.compile(r"\w\[")


class QuotationTokenizer(Tokenizer):
    """Tokenizes outermost string quotations in Python code.

    Returns string literals including their quote characters. Has the ability
    to exclude dictionary key notation like `my_dict['my_key']`.

    Emits token type: `quotation`

    Parameters
    ----------
    exclude_dict_keys : bool, default=True
        If True, excludes string literals used as dictionary keys in
        bracket notation.

    Examples
    --------

    ```python
    from cleer import QuotationTokenizer

    tokenizer = QuotationTokenizer()
    tokens = tokenizer.tokenize('x = "hello"\\n')
    ```
    """
    emits_token_type = "quotation"


    def __init__(self, exclude_dict_keys: bool=True):
        self._exclude_dict_keys = exclude_dict_keys


    def _is_dict_key_context(self, document: str, start: int) -> bool:
        """Check if the string at start position is in dict key bracket notation."""
        if start < 1:
            return False

        before = start - 1
        if document[before] == "[":
            if (
                before >= 1
                and (
                    document[before - 1].isalnum()
                    or document[before - 1] in "_]"
                )
            ):
                return True

        return False


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize string literals in a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = QuotationTokenizer()
        tokens = tokenizer.tokenize('x = "hello"\\ny = \\'world\\'\\n')
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per string literal.

            ```python
            [
                {"token": "\\"hello\\"", "index": 4, "length": 7},
                {"token": "\\'world\\'", "index": 16, "length": 7}
            ]
            ```
        """
        tokens: List[dict] = []
        i = 0

        while i < len(document):
            if document[i] == "#":
                newline = document.find("\n", i)
                if newline == -1:
                    break

                i = newline + 1
                continue

            if document[i] in (
                "'",
                '"'
            ):
                quote_char = document[i]

                if document[i:i + 3] == quote_char * 3:
                    end = document.find(quote_char * 3, i + 3)
                    if end != -1:
                        end += 3
                        if not (self._exclude_dict_keys and self._is_dict_key_context(document, i)):
                            token_text = document[i:end]
                            tokens.append(
                                {
                                    "token": token_text,
                                    "index": i,
                                    "length": len(token_text)
                                }
                            )

                        i = end
                        continue
                    else:
                        i += 3
                        continue

                end = i + 1
                while end < len(document):
                    if document[end] == "\\":
                        end += 2
                        continue

                    if document[end] == quote_char:
                        end += 1
                        break

                    if document[end] == "\n":
                        end += 1
                        break

                    end += 1

                if (
                    end <= len(document)
                    and end > i + 1
                    and document[end - 1] == quote_char
                ):
                    if not (self._exclude_dict_keys and self._is_dict_key_context(document, i)):
                        token_text = document[i:end]
                        tokens.append(
                            {
                                "token": token_text,
                                "index": i,
                                "length": len(token_text)
                            }
                        )

                    i = end
                    continue

                i = end
                continue

            i += 1

        return tokens
