"""Type hint colon spacing tokenizer module."""

__all__ = ["PyTypeHintSpacingTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


_KEYWORDS = frozenset(
    [
        "if",
        "else",
        "elif",
        "for",
        "while",
        "with",
        "try",
        "except",
        "finally",
        "class",
        "def",
        "return",
        "yield",
        "async",
        "await",
        "raise",
        "pass",
        "break",
        "continue",
        "lambda",
        "assert",
        "del",
        "import",
        "from",
        "as",
        "global",
        "nonlocal",
        "and",
        "or",
        "not",
        "in",
        "is",
        "match",
        "case"
    ]
)

_TYPE_HINT_PATTERN = re.compile(
    r"(\w[\w.]*)"
    r"(\s*)"
    r"(:)"
    r"(\s*)"
    r"(?=[^\s:\]\}=])"
)


class PyTypeHintSpacingTokenizer(Tokenizer):
    """Tokenizes type annotation colons with incorrect spacing.

    Finds variable and parameter type annotations where the colon spacing
    is wrong. The rule is: no space before the colon, exactly one space
    after the colon.

    Does NOT match dictionary literals, slice notation, function/class
    definition colons, or control flow statement colons.

    Emits token type: `type_hint_spacing`

    Examples
    --------

    ```python
    from cleer import PyTypeHintSpacingTokenizer

    tokenizer = PyTypeHintSpacingTokenizer()
    tokens = tokenizer.tokenize("x :int = 5\\n")
    ```
    """
    emits_token_type = "type_hint_spacing"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize type annotation colons with incorrect spacing.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyTypeHintSpacingTokenizer()
        tokens = tokenizer.tokenize("x :int = 5\\nname:str = 'hello'\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results for colons with bad spacing.

            ```python
            [
                {"token": " :", "index": 1, "length": 2},
                {"token": ":", "index": 14, "length": 1}
            ]
            ```
        """
        tokens: List[dict] = []
        lines = document.split("\n")
        offset = 0

        for line in lines:
            self._process_line(line, offset, document, tokens)
            offset += len(line) + 1

        return tokens


    def _process_line(
        self,
        line: str,
        line_offset: int,
        document: str,
        tokens: List[dict]
    ) -> None:
        """Process a single line looking for type annotation colons.

        Parameters
        ----------
        line : str
            The line text to process.
        line_offset : int
            The character offset of this line in the full document.
        document : str
            The full document string.
        tokens : List[dict]
            List to append found tokens to.
        """
        stripped = line.lstrip()

        if stripped.startswith("#"):
            return

        for match in _TYPE_HINT_PATTERN.finditer(line):
            identifier = match.group(1)
            space_before = match.group(2)
            space_after = match.group(4)

            if space_before == "" and space_after == " ":
                continue

            colon_pos = match.start(3)

            if self._is_keyword(identifier):
                continue

            if self._is_in_string(document, line_offset + colon_pos):
                continue

            if self._is_in_comment(line, colon_pos):
                continue

            if self._is_dict_or_slice(line, colon_pos):
                continue

            if self._is_block_end_colon(line, colon_pos):
                continue

            token_start = match.start(2)
            token_end = match.start(3) + 1 + len(space_after)
            token_text = line[token_start:token_end]

            abs_start = line_offset + token_start

            tokens.append(
                {
                    "token": token_text,
                    "index": abs_start,
                    "length": len(token_text)
                }
            )


    def _is_keyword(self, identifier: str) -> bool:
        """Check if the identifier is a Python keyword.

        Parameters
        ----------
        identifier : str
            The identifier preceding the colon.

        Returns
        -------
        bool
            True if the identifier is a keyword.
        """
        base = identifier.split(".")[-1]

        return base in _KEYWORDS


    def _is_in_string(self, document: str, pos: int) -> bool:
        """Check if a position is inside a string literal.

        Parameters
        ----------
        document : str
            The full document.
        pos : int
            Position to check.

        Returns
        -------
        bool
            True if position is inside a string.
        """
        i = 0
        while i < pos:
            if document[i:i + 3] in ("'''", '"""'):
                quote = document[i:i + 3]
                end = document.find(quote, i + 3)
                if end == -1:
                    return True

                if pos < end + 3:
                    return True

                i = end + 3
                continue

            if document[i] in ("'", '"'):
                quote_char = document[i]
                j = i + 1
                while j < len(document):
                    if document[j] == "\\":
                        j += 2
                        continue

                    if document[j] == quote_char:
                        break

                    if document[j] == "\n":
                        break

                    j += 1

                if pos <= j:
                    return True

                i = j + 1
                continue

            i += 1

        return False


    def _is_in_comment(self, line: str, pos: int) -> bool:
        """Check if a position in a line is inside a comment.

        Parameters
        ----------
        line : str
            The line to check.
        pos : int
            Position within the line.

        Returns
        -------
        bool
            True if position is inside a comment.
        """
        i = 0
        in_single = False
        in_double = False

        while i < pos:
            if line[i] == "\\" and (in_single or in_double):
                i += 2
                continue

            if line[i] == "'" and not in_double:
                in_single = not in_single
            elif line[i] == '"' and not in_single:
                in_double = not in_double
            elif (
                line[i] == "#"
                and not in_single
                and not in_double
            ):
                return True

            i += 1

        return False


    def _is_dict_or_slice(
        self,
        line: str,
        colon_pos: int
    ) -> bool:
        """Check if the colon is inside dict braces or slice brackets.

        Parameters
        ----------
        line : str
            The line to check.
        colon_pos : int
            Position of the colon in the line.

        Returns
        -------
        bool
            True if the colon is inside {} or [] context.
        """
        brace_depth = 0
        bracket_depth = 0
        paren_depth = 0
        i = 0
        in_single = False
        in_double = False

        while i < colon_pos:
            if line[i] == "\\" and (in_single or in_double):
                i += 2
                continue

            if line[i] == "'" and not in_double:
                in_single = not in_single
            elif line[i] == '"' and not in_single:
                in_double = not in_double
            elif not in_single and not in_double:
                if line[i] == "{":
                    brace_depth += 1
                elif line[i] == "}":
                    brace_depth -= 1
                elif line[i] == "[":
                    bracket_depth += 1
                elif line[i] == "]":
                    bracket_depth -= 1
                elif line[i] == "(":
                    paren_depth += 1
                elif line[i] == ")":
                    paren_depth -= 1

            i += 1

        if brace_depth > 0:
            return True

        if bracket_depth > 0:
            return True

        return False


    def _is_block_end_colon(
        self,
        line: str,
        colon_pos: int
    ) -> bool:
        """Check if this colon ends a block statement.

        Parameters
        ----------
        line : str
            The line to check.
        colon_pos : int
            Position of the colon in the line.

        Returns
        -------
        bool
            True if the colon appears to end a block (def, class, if, etc.).
        """
        after = line[colon_pos + 1:].strip()
        if after == "" or after.startswith("#"):
            stripped = line.lstrip()
            if re.match(
                r"(if|elif|else|for|while|with|try|except|finally|class|def|async\s+def|async\s+for|async\s+with|case|match)\b",
                stripped
            ):
                return True

        return False


    def _will_expand_multiline(
        self,
        line: str,
        colon_pos: int
    ) -> bool:
        """Check if the type annotation after the colon has nesting > 2 levels.

        Parameters
        ----------
        line : str
            The line to check.
        colon_pos : int
            Position of the colon in the line.

        Returns
        -------
        bool
            True if the annotation would be expanded to multiline (nesting > 2).
        """
        after_colon = line[colon_pos + 1:].lstrip()
        max_depth = 0
        depth = 0

        for char in after_colon:
            if char == "[":
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == "]":
                depth -= 1
            elif char in ("=", "\n"):
                break

        return max_depth > 2
