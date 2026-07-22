"""Function call kwargs equals tokenizer module."""

__all__ = ["PyFunctionCallKwargsEqualsTokenizer"]


import re
from typing import List

from loguru import logger

from cleer.tokenizers.tokenizer import Tokenizer


class PyFunctionCallKwargsEqualsTokenizer(Tokenizer):
    """Tokenizes equals signs in function call kwargs.

    Finds equals signs used for keyword arguments in function calls,
    including any surrounding whitespace.

    Emits token type: `kwargs_equals`

    Examples
    --------

    ```python
    from cleer import PyFunctionCallKwargsEqualsTokenizer

    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    tokens = tokenizer.tokenize("result = func(x = 1, y = 2)\\n")
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


    def _is_function_call(
        self,
        document: str,
        paren_pos: int
    ) -> bool:
        """Check if a parenthesis is part of a function call."""
        j = paren_pos - 1
        while j >= 0 and document[j] in " \t":
            j -= 1

        if (
            j >= 0
            and (
                document[j].isalnum()
                or document[j] in "_."
            )
        ):
            return True

        return False


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize equals signs in function call kwargs.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyFunctionCallKwargsEqualsTokenizer()
        tokens = tokenizer.tokenize("func(x = 1, y = 2)\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per equals sign with whitespace.

            ```python
            [
                {"token": " = ", "index": 6, "length": 3},
                {"token": " = ", "index": 14, "length": 3}
            ]
            ```
        """
        tokens: List[dict] = []

        i = 0
        while i < len(document):
            if document[i] in ("'", '"'):
                if document[i:i + 3] in ("'''", '"""'):
                    quote = document[i:i + 3]
                    end = document.find(quote, i + 3)
                    if end != -1:
                        i = end + 3
                    else:
                        i += 3

                    continue
                else:
                    quote_char = document[i]
                    end = i + 1
                    while end < len(document):
                        if document[end] == "\\":
                            end += 2
                            continue

                        if document[end] == quote_char:
                            end += 1
                            break

                        end += 1

                    i = end
                    continue

            if document[i] == "#":
                newline = document.find("\n", i)
                if newline == -1:
                    break

                i = newline + 1
                continue

            if document[i] == "(":
                if self._is_function_call(document, i):
                    line_start = document.rfind("\n", 0, i) + 1
                    line = document[line_start:].split("\n")[0]
                    stripped = line.lstrip()
                    if (
                        stripped.startswith("def ")
                        or stripped.startswith("async def ")
                    ):
                        i += 1
                        continue

                    paren_end = self._find_matching_paren(document, i)
                    if paren_end != -1:
                        inner = document[i + 1:paren_end]
                        inner_start = i + 1

                        j = 0
                        depth = 0
                        in_single = False
                        in_double = False

                        while j < len(inner):
                            if inner[j] == "\\" and (in_single or in_double):
                                j += 2
                                continue

                            if inner[j:j + 3] in ("'''", '"""'):
                                quote = inner[j:j + 3]
                                end = inner.find(quote, j + 3)
                                if end != -1:
                                    j = end + 3
                                else:
                                    j += 3

                                continue

                            if inner[j] == "'" and not in_double:
                                in_single = not in_single
                                j += 1
                                continue

                            if inner[j] == '"' and not in_single:
                                in_double = not in_double
                                j += 1
                                continue

                            if not in_single and not in_double:
                                if inner[j] in "([{":
                                    depth += 1
                                elif inner[j] in ")]}":
                                    depth -= 1
                                elif inner[j] == "=" and depth == 0:
                                    if j + 1 < len(inner) and inner[j + 1] == "=":
                                        j += 2
                                        continue

                                    if j > 0 and inner[j - 1] in "!<>":
                                        j += 1
                                        continue

                                    before = j - 1
                                    while before >= 0 and inner[before] in " \t":
                                        before -= 1

                                    if (
                                        before >= 0
                                        and (
                                            inner[before].isalnum()
                                            or inner[before] == "_"
                                        )
                                    ):
                                        ws_start = j
                                        while ws_start > 0 and inner[ws_start - 1] in " \t":
                                            ws_start -= 1

                                        ws_end = j + 1
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

                                        j = ws_end
                                        continue

                            j += 1

                        i = paren_end + 1
                        continue

            i += 1

        return tokens
