"""Docstring space tokenizer module."""

__all__ = ["PyDocstringSpaceTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyDocstringSpaceTokenizer(Tokenizer):
    """Tokenizes extra whitespace between a class/function definition and its docstring.

    Captures the newline characters between the end of a definition's colon line
    and the start of the next line when that line contains a docstring and there
    are extra blank lines between them.

    Emits token type: `docstring_space`

    Examples
    --------

    ```python
    from cleer import PyDocstringSpaceTokenizer

    tokenizer = PyDocstringSpaceTokenizer()
    tokens = tokenizer.tokenize("class Foo:\\n\\n    \\"\\"\\"Docstring.\\"\\"\\"\\n")
    ```
    """
    emits_token_type = "docstring_space"


    def _find_signature_end_line(
        self,
        lines: List[str],
        def_line_idx: int
    ) -> int:
        """Find the line index where the signature ends (the line ending with colon)."""
        line = lines[def_line_idx]

        if line.rstrip().endswith(":"):
            return def_line_idx

        paren_depth = 0
        i = def_line_idx

        while i < len(lines):
            for char in lines[i]:
                if char == "(":
                    paren_depth += 1
                elif char == ")":
                    paren_depth -= 1

            if paren_depth == 0:
                if lines[i].rstrip().endswith(":"):
                    return i

                j = i + 1
                while j < len(lines):
                    if lines[j].rstrip().endswith(":"):
                        return j

                    if (
                        lines[j].strip()
                        and not lines[j].strip().startswith("->")
                    ):
                        break

                    j += 1

                return i

            i += 1

        return def_line_idx


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize extra whitespace between definitions and their docstrings.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyDocstringSpaceTokenizer()
        tokens = tokenizer.tokenize("def foo():\\n\\n    \\"\\"\\"Doc.\\"\\"\\"\\n")
        ```

        Returns
        -------
        List[dict]
            List of token results for extra whitespace before docstrings.

            ```python
            [
                {"token": "\\n\\n", "index": 10, "length": 2}
            ]
            ```
        """
        tokens: List[dict] = []
        lines = document.split("\n")
        line_starts = []
        current_pos = 0

        for line in lines:
            line_starts.append(current_pos)
            current_pos += len(line) + 1

        def_pattern = re.compile(
            r"^([ \t]*)(async\s+)?def\s+|^([ \t]*)class\s+",
            re.MULTILINE
        )

        for i, line in enumerate(lines):
            if not def_pattern.match(line):
                continue

            sig_end = self._find_signature_end_line(lines, i)

            next_content_line = sig_end + 1
            while (
                next_content_line < len(lines)
                and lines[next_content_line].strip() == ""
            ):
                next_content_line += 1

            if next_content_line >= len(lines):
                continue

            stripped = lines[next_content_line].lstrip()
            if not (stripped.startswith('"""') or stripped.startswith("'''")):
                continue

            if next_content_line == sig_end + 1:
                continue

            space_start = line_starts[sig_end] + len(lines[sig_end])
            indent_len = len(lines[next_content_line]) - len(lines[next_content_line].lstrip())
            space_end = line_starts[next_content_line] + indent_len
            token_text = document[space_start:space_end]

            tokens.append(
                {
                    "token": token_text,
                    "index": space_start,
                    "length": len(token_text)
                }
            )

        tokens.sort(key=lambda t: t['index'])

        return tokens
