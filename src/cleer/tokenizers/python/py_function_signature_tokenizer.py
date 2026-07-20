"""Function signature tokenizer module."""

__all__ = ["PyFunctionSignatureTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyFunctionSignatureTokenizer(Tokenizer):
    """Tokenizes Python function/method signatures.

    Each function definition line (the `def` line through the closing
    parenthesis and colon) is returned as a token, including its indent
    but no extra newlines.

    Emits token type: `function_signature`

    Examples
    --------

    ```python
    from cleer import PyFunctionSignatureTokenizer

    tokenizer = PyFunctionSignatureTokenizer()
    tokens = tokenizer.tokenize("def my_func(a, b, c):\\n    pass\\n")
    ```
    """
    emits_token_type = "function_signature"


    def _find_matching_paren(self, text: str, start: int) -> int:
        """Find the matching closing parenthesis."""
        depth = 1
        i = start + 1
        in_single = False
        in_double = False

        while i < len(text):
            if text[i] == "\\" and (in_single or in_double):
                i += 2
                continue

            if text[i:i + 3] in (
                "'''",
                '"""'
            ):
                quote = text[i:i + 3]
                end = text.find(quote, i + 3)
                if end != -1:
                    i = end + 3
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
        """Tokenize function signatures in a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyFunctionSignatureTokenizer()
        tokens = tokenizer.tokenize("def my_func(a, b, c):\\n    pass\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per function signature.

            ```python
            [
                {"token": "def my_func(a, b, c):", "index": 0, "length": 21}
            ]
            ```
        """
        tokens: List[dict] = []
        pattern = re.compile(r"^([ \t]*)(async\s+)?def\s+", re.MULTILINE)

        for match in pattern.finditer(document):
            start = match.start()
            paren_start = document.find("(", match.end())

            if paren_start == -1:
                continue

            paren_end = self._find_matching_paren(document, paren_start)
            if paren_end == -1:
                continue

            end = paren_end + 1
            if end < len(document) and document[end] == ":":
                end += 1
            elif end < len(document):
                rest = document[end:].lstrip()
                if rest.startswith("->"):
                    arrow_pos = document.find("->", end)
                    colon_pos = document.find(":", arrow_pos + 2)
                    if colon_pos != -1:
                        end = colon_pos + 1

            token_text = document[start:end]

            tokens.append(
                {
                    "token": token_text,
                    "index": start,
                    "length": len(token_text)
                }
            )

        return tokens
