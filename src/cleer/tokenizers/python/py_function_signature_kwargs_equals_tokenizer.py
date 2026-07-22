"""Function signature kwargs equals tokenizer module."""

__all__ = ["PyFunctionSignatureKwargsEqualsTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyFunctionSignatureKwargsEqualsTokenizer(Tokenizer):
    """Tokenizes equals signs in function signature default kwargs.

    Finds equals signs used for default parameter values in function
    definitions, including any surrounding whitespace.

    Emits token type: `kwargs_equals`

    Examples
    --------

    ```python
    from cleer import PyFunctionSignatureKwargsEqualsTokenizer

    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    tokens = tokenizer.tokenize("def func(x, y=5, z=None):\\n    pass\\n")
    ```
    """
    emits_token_type = "kwargs_equals"


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

            if text[i:i + 3] in ("'''", '"""'):
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
        """Tokenize equals signs in function signature default kwargs.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
        tokens = tokenizer.tokenize("def func(x, y=5):\\n    pass\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per equals sign with whitespace.

            ```python
            [
                {"token": " = ", "index": 15, "length": 3}
            ]
            ```
        """
        tokens: List[dict] = []
        def_pattern = re.compile(
            r"(async\s+)?def\s+\w+\s*\(",
            re.MULTILINE
        )

        for match in def_pattern.finditer(document):
            paren_start = document.find("(", match.start())

            paren_end = self._find_matching_paren(document, paren_start)
            if paren_end == -1:
                continue

            inner = document[paren_start + 1:paren_end]
            inner_start = paren_start + 1

            i = 0
            depth = 0
            in_single = False
            in_double = False
            has_annotation = False

            while i < len(inner):
                if inner[i] == "\\" and (in_single or in_double):
                    i += 2
                    continue

                if inner[i:i + 3] in ("'''", '"""'):
                    quote = inner[i:i + 3]
                    end = inner.find(quote, i + 3)
                    if end != -1:
                        i = end + 3
                    else:
                        i += 3

                    continue

                if inner[i] == "'" and not in_double:
                    in_single = not in_single
                    i += 1
                    continue

                if inner[i] == '"' and not in_single:
                    in_double = not in_double
                    i += 1
                    continue

                if not in_single and not in_double:
                    if inner[i] in "([{":
                        depth += 1
                    elif inner[i] in ")]}":
                        depth -= 1
                    elif inner[i] == "," and depth == 0:
                        has_annotation = False
                        i += 1
                        continue
                    elif inner[i] == ":" and depth == 0:
                        has_annotation = True
                    elif inner[i] == "=" and depth == 0:
                        if i + 1 < len(inner) and inner[i + 1] == "=":
                            i += 2
                            continue

                        if i > 0 and inner[i - 1] in "!<>":
                            i += 1
                            continue

                        if has_annotation:
                            i += 1
                            continue

                        ws_start = i
                        while ws_start > 0 and inner[ws_start - 1] in " \t":
                            ws_start -= 1

                        ws_end = i + 1
                        while ws_end < len(inner) and inner[ws_end] in " \t":
                            ws_end += 1

                        abs_start = inner_start + ws_start
                        token_text = document[abs_start:inner_start + ws_end]
                        tokens.append(
                            {
                                "token": token_text,
                                "index": abs_start,
                                "length": len(token_text)
                            }
                        )
                        i = ws_end
                        continue

                i += 1

        return tokens
