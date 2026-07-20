"""Binary operator tokenizer module."""

__all__ = ["BinaryOperatorTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


BINARY_OPS = [
    "**=",
    "//=",
    ">>=",
    "<<=",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "&=",
    "|=",
    "^=",
    "==",
    "!=",
    ">=",
    "<=",
    "**",
    "//",
    ">>",
    "<<",
    "->",
    "+",
    "-",
    "*",
    "/",
    "%",
    "&",
    "|",
    "^",
    "~",
    ">",
    "<",
    "="
]

BINARY_OP_PATTERN = re.compile(
    r"(\s*)"
    r"(\*\*=|//=|>>=|<<=|[+\-*/%&|^]=|==|!=|>=|<=|\*\*|//|>>|<<|->|[+\-*/%&|^><=])"
    r"(\s*)"
)


class BinaryOperatorTokenizer(Tokenizer):
    """Tokenizes Python binary operators with surrounding whitespace.

    Includes the binary operator and the whitespace immediately around it.
    Can exclude function signature and function call equals signs (kwargs).

    Emits token type: `binary_operator`

    Parameters
    ----------
    exclude_signature_equals : bool, default=True
        Exclude equals signs in function signature default kwargs.
    exclude_call_equals : bool, default=True
        Exclude equals signs in function call kwargs.

    Examples
    --------

    ```python
    from cleer import BinaryOperatorTokenizer

    tokenizer = BinaryOperatorTokenizer()
    tokens = tokenizer.tokenize("x = 1 + 2\\n")
    ```
    """
    emits_token_type = "binary_operator"


    def __init__(
        self,
        exclude_signature_equals: bool=True,
        exclude_call_equals: bool=True
    ):
        self._exclude_signature_equals = exclude_signature_equals
        self._exclude_call_equals = exclude_call_equals


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


    def _get_paren_depth(self, document: str, pos: int) -> int:
        """Get the parenthesis nesting depth at a position."""
        depth = 0
        i = 0
        in_single = False
        in_double = False

        while i < pos:
            if document[i] == "\\" and (in_single or in_double):
                i += 2
                continue

            if document[i] == "'" and not in_double:
                in_single = not in_single
            elif document[i] == '"' and not in_single:
                in_double = not in_double
            elif not in_single and not in_double:
                if document[i] == "(":
                    depth += 1
                elif document[i] == ")":
                    depth -= 1

            i += 1

        return depth


    def _is_in_function_signature(self, document: str, pos: int) -> bool:
        """Check if the position is inside a function signature."""
        line_start = document.rfind(
            "\n",
            0,
            pos
        ) + 1
        before = document[:pos]
        last_def = before.rfind("def ")

        if last_def == -1:
            return False

        paren_start = document.find("(", last_def)
        if paren_start == -1 or paren_start > pos:
            return False

        depth = 1
        i = paren_start + 1
        while i < len(document) and depth > 0:
            if document[i] == "(":
                depth += 1
            elif document[i] == ")":
                depth -= 1

            if depth == 0:
                if pos < i:
                    return True

            i += 1

        return False


    def _is_in_function_call(self, document: str, pos: int) -> bool:
        """Check if the equals sign is in a function call kwargs context."""
        before = document[:pos]

        paren_pos = -1
        depth = 0
        for i in range(
            pos - 1,
            -1,
            -1
        ):
            if document[i] == ")":
                depth += 1
            elif document[i] == "(":
                if depth == 0:
                    paren_pos = i
                    break

                depth -= 1

        if paren_pos == -1:
            return False

        j = paren_pos - 1
        while j >= 0 and document[j] in " \t":
            j -= 1

        if j >= 0 and (document[j].isalnum() or document[j] in "_."):
            return True

        return False


    def _is_decorator(self, document: str, pos: int) -> bool:
        """Check if the operator is in a decorator line."""
        line_start = document.rfind(
            "\n",
            0,
            pos
        ) + 1
        line = document[line_start:].split("\n")[0]

        return line.lstrip().startswith("@")


    def _is_annotated_assignment(self, document: str, pos: int) -> bool:
        """Check if the equals sign is in an annotated assignment (e.g. x: int=5)."""
        line_start = document.rfind(
            "\n",
            0,
            pos
        ) + 1
        line_before_eq = document[line_start:pos]

        depth = 0
        for char in line_before_eq:
            if char in "([{":
                depth += 1
            elif char in ")]}":
                depth -= 1
            elif char == ":" and depth == 0:
                return True

        return False


    def _is_unary_operator(
        self,
        document: str,
        op: str,
        pos: int
    ) -> bool:
        """Check if the operator is used as a unary operator."""
        if op not in (
            "+",
            "-",
            "~"
        ):
            return False

        before_pos = pos - 1
        while before_pos >= 0 and document[before_pos] in " \t":
            before_pos -= 1

        if before_pos < 0:
            return True

        char_before = document[before_pos]

        if char_before in "([{,=<>!&|^:+-*/%~\n":
            return True

        if char_before.isalpha() or char_before == "_":
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
            unary_keywords = {
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
            if word in unary_keywords:
                return True

        return False


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize binary operators with surrounding whitespace.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = BinaryOperatorTokenizer()
        tokens = tokenizer.tokenize("x = 1 + 2\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per binary operator with whitespace.

            ```python
            [
                {"token": " = ", "index": 1, "length": 3},
                {"token": " + ", "index": 5, "length": 3}
            ]
            ```
        """
        tokens: List[dict] = []
        covered = set()

        i = 0
        while i < len(document):
            if document[i] in (
                "'",
                '"'
            ):
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

            matched = False
            for op in BINARY_OPS:
                if document[i:i + len(op)] == op:
                    if self._is_unary_operator(
                        document,
                        op,
                        i
                    ):
                        break

                    if op == "=" and self._exclude_signature_equals:
                        if self._is_in_function_signature(document, i):
                            break

                    if op == "=" and self._exclude_call_equals:
                        if self._is_in_function_call(document, i):
                            break

                    if op == "=":
                        if self._is_annotated_assignment(document, i):
                            break

                    if op in (
                        "*",
                        "**"
                    ):
                        if self._get_paren_depth(document, i) > 0:
                            before_pos = i - 1
                            while before_pos >= 0 and document[before_pos] in " \t":
                                before_pos -= 1

                            if before_pos >= 0 and document[before_pos] in ",(":
                                break

                    ws_start = i
                    while ws_start > 0 and document[ws_start - 1] in " \t":
                        ws_start -= 1

                    ws_end = i + len(op)
                    while ws_end < len(document) and document[ws_end] in " \t":
                        ws_end += 1

                    token_text = document[ws_start:ws_end]

                    tokens.append(
                        {
                            "token": token_text,
                            "index": ws_start,
                            "length": len(token_text)
                        }
                    )
                    for ci in range(ws_start, ws_end):
                        covered.add(ci)

                    matched = True
                    i = ws_end
                    break

            if not matched:
                i += 1

        return tokens
