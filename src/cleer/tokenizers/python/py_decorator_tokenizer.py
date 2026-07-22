"""Decorator tokenizer module."""

__all__ = ["PyDecoratorTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyDecoratorTokenizer(Tokenizer):
    """Tokenizes individual Python decorator statements.

    Each decorator is returned as a single token including its indent,
    no extra newlines.

    Emits token type: `decorator`

    Examples
    --------

    ```python
    from cleer import PyDecoratorTokenizer

    tokenizer = PyDecoratorTokenizer()
    tokens = tokenizer.tokenize("@my_decorator(arg1, arg2, arg3)\\ndef func():\\n    pass\\n")
    ```
    """
    emits_token_type = "decorator"


    def _find_matching_paren(
        self,
        text: str,
        start: int
    ) -> int:
        """Find matching closing parenthesis."""
        depth = 1
        i = start + 1
        in_single = False
        in_double = False

        while i < len(text):
            if text[i] == "\\" and (in_single or in_double):
                i += 2
                continue

            if text[i] == "'" and not in_double:
                in_single = not in_single
                i += 1
                continue

            if text[i] == '"' and not in_single:
                in_double = not in_double
                i += 1
                continue

            if not in_single and not in_double:
                if text[i] == "(":
                    depth += 1
                elif text[i] == ")":
                    depth -= 1
                    if depth == 0:
                        return i

            i += 1

        return -1


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize decorator statements in a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyDecoratorTokenizer()
        tokens = tokenizer.tokenize("@app.route('/path')\\ndef handler():\\n    pass\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per decorator statement.

            ```python
            [
                {"token": "@app.route('/path')", "index": 0, "length": 19}
            ]
            ```
        """
        tokens: List[dict] = []
        pattern = re.compile(r"^([ \t]*)@", re.MULTILINE)

        for match in pattern.finditer(document):
            start = match.start()
            paren_start = None

            end_of_line = document.find("\n", start)
            if end_of_line == -1:
                end_of_line = len(document)

            line_content = document[start:end_of_line]

            paren_pos = line_content.find("(")
            if paren_pos != -1:
                abs_paren_pos = start + paren_pos
                paren_end = self._find_matching_paren(
                    document,
                    abs_paren_pos
                )
                if paren_end != -1:
                    end = paren_end + 1
                else:
                    end = end_of_line

            else:
                end = end_of_line

            token_text = document[start:end]

            tokens.append(
                {
                    "token": token_text,
                    "index": start,
                    "length": len(token_text)
                }
            )

        return tokens
