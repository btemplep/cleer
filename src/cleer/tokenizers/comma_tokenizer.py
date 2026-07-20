"""Comma tokenizer module."""

__all__ = ["CommaTokenizer"]


from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class CommaTokenizer(Tokenizer):
    """Tokenizes commas with all surrounding whitespace.

    Each comma is returned as a token that includes the comma character
    and any whitespace immediately surrounding it.

    Emits token type: `comma`

    Examples
    --------

    ```python
    from cleer import CommaTokenizer

    tokenizer = CommaTokenizer()
    tokens = tokenizer.tokenize("a ,b, c\\n")
    ```
    """
    emits_token_type = "comma"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize commas with surrounding whitespace.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = CommaTokenizer()
        tokens = tokenizer.tokenize("a, b,c\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per comma with whitespace.

            ```python
            [
                {"token": ", ", "index": 1, "length": 2},
                {"token": ",", "index": 4, "length": 1}
            ]
            ```
        """
        tokens: List[dict] = []
        i = 0
        in_single = False
        in_double = False
        in_triple_single = False
        in_triple_double = False

        while i < len(document):
            remaining = document[i:]

            if in_triple_single:
                if remaining.startswith("'''"):
                    in_triple_single = False
                    i += 3
                    continue

                i += 1
                continue

            if in_triple_double:
                if remaining.startswith('"""'):
                    in_triple_double = False
                    i += 3
                    continue

                i += 1
                continue

            if in_single:
                if document[i] == "\\" and i + 1 < len(document):
                    i += 2
                    continue

                if document[i] == "'":
                    in_single = False

                i += 1
                continue

            if in_double:
                if document[i] == "\\" and i + 1 < len(document):
                    i += 2
                    continue

                if document[i] == '"':
                    in_double = False

                i += 1
                continue

            if remaining.startswith("'''"):
                in_triple_single = True
                i += 3
                continue

            if remaining.startswith('"""'):
                in_triple_double = True
                i += 3
                continue

            if document[i] == "'" and not in_double:
                in_single = True
                i += 1
                continue

            if document[i] == '"' and not in_single:
                in_double = True
                i += 1
                continue

            if document[i] == "#":
                newline = document.find("\n", i)
                if newline == -1:
                    break

                i = newline + 1
                continue

            if document[i] == ",":
                ws_start = i
                while ws_start > 0 and document[ws_start - 1] in " \t":
                    ws_start -= 1

                ws_end = i + 1
                while ws_end < len(document) and document[ws_end] in " \t\n":
                    if document[ws_end] == "\n":
                        ws_end += 1
                        break

                    ws_end += 1

                after_ws = ws_end
                while after_ws < len(document) and document[after_ws] in " \t":
                    after_ws += 1

                if after_ws < len(document) and document[after_ws] in ")]}":
                    i = ws_end
                    continue

                token_text = document[ws_start:ws_end]
                tokens.append(
                    {
                        "token": token_text,
                        "index": ws_start,
                        "length": len(token_text)
                    }
                )

                i = ws_end
                continue

            i += 1

        return tokens
