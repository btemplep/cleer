"""Paired punctuation tokenizer module."""

__all__ = ["PairedPunctuationTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PairedPunctuationTokenizer(Tokenizer):
    """Tokenizes statements containing paired punctuation.

    Finds any statement that has paired punctuation like (), {}, [].
    Pulls in the whole, highest level statement that has the paired
    punctuation with the indent, no external newlines.

    Emits token type: `paired_punctuation`

    Examples
    --------

    ```python
    from cleer import PairedPunctuationTokenizer

    tokenizer = PairedPunctuationTokenizer()
    tokens = tokenizer.tokenize("x = [1, 2, 3]\\ny = 4\\n")
    ```
    """
    emits_token_type = "paired_punctuation"


    def _find_statement_start(self, document: str, pos: int) -> int:
        """Find the start of the statement containing the paired punctuation."""
        line_start = document.rfind(
            "\n",
            0,
            pos
        )

        return line_start + 1 if line_start != -1 else 0


    def _is_comprehension(
        self,
        document: str,
        open_pos: int,
        close_pos: int
    ) -> bool:
        """Check if the content between brackets is a comprehension."""
        inner = document[open_pos + 1:close_pos]
        depth = 0
        in_single = False
        in_double = False
        in_triple_single = False
        in_triple_double = False
        i = 0

        while i < len(inner):
            remaining = inner[i:]

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
                if inner[i] == "\\" and i + 1 < len(inner):
                    i += 2
                    continue

                if inner[i] == "'":
                    in_single = False

                i += 1
                continue

            if in_double:
                if inner[i] == "\\" and i + 1 < len(inner):
                    i += 2
                    continue

                if inner[i] == '"':
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

            if inner[i] == "'" and not in_double:
                in_single = True
                i += 1
                continue

            if inner[i] == '"' and not in_single:
                in_double = True
                i += 1
                continue

            if inner[i] in "([{":
                depth += 1
            elif inner[i] in ")]}":
                depth -= 1
            elif depth == 0:
                if remaining.startswith("for ") or remaining.startswith("for\n"):
                    before = inner[:i].rstrip()
                    if before and not before.endswith(","):
                        return True

            i += 1

        return False


    def _find_matching_close(
        self,
        document: str,
        open_pos: int,
        open_char: str,
        close_char: str
    ) -> int:
        """Find the matching closing character, handling nesting and strings."""
        depth = 1
        i = open_pos + 1
        in_single_quote = False
        in_double_quote = False
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

            if in_single_quote:
                if document[i] == "\\" and i + 1 < len(document):
                    i += 2
                    continue

                if document[i] == "'":
                    in_single_quote = False

                i += 1
                continue

            if in_double_quote:
                if document[i] == "\\" and i + 1 < len(document):
                    i += 2
                    continue

                if document[i] == '"':
                    in_double_quote = False

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

            if document[i] == "'" and not in_double_quote:
                in_single_quote = True
                i += 1
                continue

            if document[i] == '"' and not in_single_quote:
                in_double_quote = True
                i += 1
                continue

            if document[i] == "#":
                newline_pos = document.find("\n", i)
                if newline_pos == -1:
                    i = len(document)
                else:
                    i = newline_pos + 1

                continue

            if document[i] == open_char:
                depth += 1
            elif document[i] == close_char:
                depth -= 1
                if depth == 0:
                    return i

            i += 1

        return -1


    def _is_logic_block(
        self,
        document: str,
        open_pos: int,
        close_pos: int
    ) -> bool:
        """Check if the content between parens is a logic block expression.

        A logic block is a parenthesized expression containing `and` or `or`
        operators at depth 0 (not inside nested brackets or strings).
        """
        inner = document[open_pos + 1:close_pos]
        depth = 0
        in_single = False
        in_double = False
        in_triple_single = False
        in_triple_double = False
        i = 0

        while i < len(inner):
            remaining = inner[i:]

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
                if inner[i] == "\\" and i + 1 < len(inner):
                    i += 2
                    continue

                if inner[i] == "'":
                    in_single = False

                i += 1
                continue

            if in_double:
                if inner[i] == "\\" and i + 1 < len(inner):
                    i += 2
                    continue

                if inner[i] == '"':
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

            if inner[i] == "'" and not in_double:
                in_single = True
                i += 1
                continue

            if inner[i] == '"' and not in_single:
                in_double = True
                i += 1
                continue

            if inner[i] in "([{":
                depth += 1
            elif inner[i] in ")]}":
                depth -= 1
            elif depth == 0:
                if (
                    remaining.startswith("and ")
                    or remaining.startswith("and\n")
                    or remaining.startswith("or ")
                    or remaining.startswith("or\n")
                ):
                    before_char = inner[i - 1] if i > 0 else " "
                    if before_char in (
                        " ",
                        "\n"
                    ):
                        return True

            i += 1

        return False


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize statements containing paired punctuation.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PairedPunctuationTokenizer()
        tokens = tokenizer.tokenize("x = [1, 2]\\nfunc(a, b)\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per statement with paired punctuation.

            ```python
            [
                {"token": "x = [1, 2]", "index": 0, "length": 10},
                {"token": "func(a, b)", "index": 11, "length": 10}
            ]
            ```
        """
        tokens: List[dict] = []
        covered_ranges = []
        pairs = [
            (
                "(",
                ")"
            ),
            (
                "[",
                "]"
            ),
            (
                "{",
                "}"
            )
        ]

        i = 0
        while i < len(document):
            char = document[i]

            if char in (
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
                        continue

                else:
                    end = i + 1
                    while end < len(document) and document[end] != char:
                        if document[end] == "\\":
                            end += 1

                        end += 1

                    i = end + 1
                    continue

            if char == "#":
                newline_pos = document.find("\n", i)
                if newline_pos == -1:
                    i = len(document)
                else:
                    i = newline_pos + 1

                continue

            open_char = None
            close_char = None
            for o, c in pairs:
                if char == o:
                    open_char = o
                    close_char = c
                    break

            if open_char is not None:
                already_covered = False
                for start, end in covered_ranges:
                    if start <= i <= end:
                        already_covered = True
                        break

                if not already_covered:
                    close_pos = self._find_matching_close(
                        document,
                        i,
                        open_char,
                        close_char
                    )
                    if close_pos != -1:
                        stmt_start = self._find_statement_start(document, i)
                        stmt_end = close_pos

                        after_close = close_pos + 1
                        while after_close < len(document) and document[after_close] == " ":
                            after_close += 1

                        if after_close < len(document) and document[after_close] == "\n":
                            stmt_end = after_close - 1
                        else:
                            end_of_line = document.find("\n", close_pos)
                            if end_of_line != -1:
                                stmt_end = end_of_line - 1
                            else:
                                stmt_end = len(document) - 1

                        stmt_end = close_pos
                        token_text = document[stmt_start:stmt_end + 1]

                        stripped_token = token_text.lstrip()
                        is_def = (
                            stripped_token.startswith("def ")
                            or stripped_token.startswith("async def ")
                        )
                        is_decorator = stripped_token.startswith("@")
                        is_multiline_logic = (
                            open_char == "("
                            and self._is_logic_block(
                                document,
                                i,
                                close_pos
                            )
                        )
                        is_comprehension = self._is_comprehension(
                            document,
                            i,
                            close_pos
                        )
                        is_type_subscript = (
                            open_char == "["
                            and i > 0
                            and (
                                document[i - 1].isalnum()
                                or document[i - 1] == "_"
                            )
                        )

                        if (
                            not is_def
                            and not is_decorator
                            and not is_comprehension
                            and not is_type_subscript
                            and not is_multiline_logic
                        ):
                            tokens.append(
                                {
                                    "token": token_text,
                                    "index": stmt_start,
                                    "length": len(token_text)
                                }
                            )
                            covered_ranges.append(
                                (
                                    stmt_start,
                                    stmt_end
                                )
                            )
                        elif is_comprehension or is_type_subscript:
                            covered_ranges.append(
                                (
                                    stmt_start,
                                    stmt_end
                                )
                            )
                        elif is_multiline_logic:
                            covered_ranges.append(
                                (
                                    i,
                                    i
                                )
                            )

            i += 1

        tokens.sort(key=lambda t: t['index'])

        return tokens
