"""Unary operator tokenizer module."""

__all__ = ["UnaryOperatorTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class UnaryOperatorTokenizer(Tokenizer):
    """Tokenizes unary operators that have spaces before their operands.

    Finds unary +, -, ~ operators that have whitespace between the operator
    and operand, so the space can be removed by a formatter.

    Emits token type: `unary_operator`

    Examples
    --------

    ```python
    from cleer import UnaryOperatorTokenizer

    tokenizer = UnaryOperatorTokenizer()
    tokens = tokenizer.tokenize("x = - 1\\n")
    ```
    """
    emits_token_type = "unary_operator"

    UNARY_CONTEXT_CHARS = set("([{,=<>!&|^:+-*/%~\n;")
    UNARY_KEYWORDS = {
        "return",
        "yield",
        "not",
        "and",
        "or",
        "in",
        "if",
        "else",
        "elif",
        "while",
        "assert",
        "lambda",
        "print",
        "raise"
    }


    def _is_in_string(self, document: str, pos: int) -> bool:
        """Check if a position is inside a string literal."""
        i = 0
        in_single = False
        in_double = False
        in_triple_single = False
        in_triple_double = False

        while i < pos:
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
                if document[i] == "\\":
                    i += 2
                    continue

                if document[i] == "'":
                    in_single = False

                i += 1
                continue

            if in_double:
                if document[i] == "\\":
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

            if document[i] == "'":
                in_single = True
                i += 1
                continue

            if document[i] == '"':
                in_double = True
                i += 1
                continue

            i += 1

        return (
            in_single
            or in_double
            or in_triple_single
            or in_triple_double
        )


    def _is_in_comment(self, document: str, pos: int) -> bool:
        """Check if a position is in a comment."""
        line_start = document.rfind(
            "\n",
            0,
            pos
        ) + 1
        line = document[line_start:pos]

        in_single = False
        in_double = False
        for char in line:
            if char == "'" and not in_double:
                in_single = not in_single
            elif char == '"' and not in_single:
                in_double = not in_double
            elif (
                char == "#"
                and not in_single
                and not in_double
            ):
                return True

        return False


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize unary operators with trailing whitespace.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = UnaryOperatorTokenizer()
        tokens = tokenizer.tokenize("x = - 1\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results for unary operators with spaces.

            ```python
            [
                {"token": "- 1", "index": 4, "length": 3}
            ]
            ```
        """
        tokens: List[dict] = []
        i = 0

        while i < len(document):
            if document[i] in "'\"":#
                if document[i:i + 3] in (
                    "'''",
                    '"""'
                ):
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

            if document[i] in "-+~":
                op_pos = i
                ws_start = i + 1
                ws_end = ws_start
                while ws_end < len(document) and document[ws_end] in " \t":
                    ws_end += 1

                if ws_end > ws_start and ws_end < len(document):
                    next_char = document[ws_end]
                    if (
                        next_char.isdigit()
                        or next_char == "("
                        or next_char.isalpha()
                        or next_char == "_"
                    ):
                        before_pos = op_pos - 1
                        while before_pos >= 0 and document[before_pos] in " \t":
                            before_pos -= 1

                        is_unary = False
                        if before_pos < 0:
                            is_unary = True
                        elif document[before_pos] in self.UNARY_CONTEXT_CHARS:
                            is_unary = True
                        elif document[before_pos].isalpha() or document[before_pos] == "_":
                            word_end = before_pos + 1
                            word_start = before_pos
                            while (
                                word_start > 0
                                and (
                                    document[word_start - 1].isalpha()
                                    or document[word_start - 1] == "_"
                                )
                            ):
                                word_start -= 1

                            word = document[word_start:word_end]
                            if word in self.UNARY_KEYWORDS:
                                is_unary = True

                        if is_unary:
                            token_end = ws_end
                            token_text = document[op_pos:token_end]
                            tokens.append(
                                {
                                    "token": token_text,
                                    "index": op_pos,
                                    "length": len(token_text)
                                }
                            )
                            i = token_end
                            continue

            i += 1

        return tokens
