"""Class var whitespace tokenizer module."""

__all__ = ["PyClassVarWhitespaceTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyClassVarWhitespaceTokenizer(Tokenizer):
    """Tokenizes whitespace between class declaration and first pass or class var.

    Captures the newlines between the class declaration line and the first
    body line when that body line is ``pass`` or a class variable (not a
    method or nested class).

    Emits token type: ``class_var_whitespace``

    Examples
    --------

    ```python
    from cleer import PyClassVarWhitespaceTokenizer

    tokenizer = PyClassVarWhitespaceTokenizer()
    tokens = tokenizer.tokenize("class Foo:\\n\\n    my_var = 1\\n")
    ```
    """
    emits_token_type = "class_var_whitespace"


    def _find_class_end(
        self,
        lines: List[str],
        class_line_idx: int,
        base_indent: int
    ) -> int:
        """Find the line index after the last line of a class body."""
        i = class_line_idx + 1

        while i < len(lines):
            line = lines[i]
            if line.strip() == "":
                i += 1
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent:
                break

            i += 1

        while i > class_line_idx + 1 and lines[i - 1].strip() == "":
            i -= 1

        return i


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize whitespace between class declaration and pass or class vars.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyClassVarWhitespaceTokenizer()
        tokens = tokenizer.tokenize("class Foo:\\n\\n    my_var = 1\\n")
        ```

        Returns
        -------
        List[dict]
            List of token results for whitespace before pass or class vars.

            ```python
            [{"token": "\\n\\n", "index": 10, "length": 2}]
            ```
        """
        tokens: List[dict] = []
        lines = document.split("\n")
        line_starts: List[int] = []
        current_pos = 0

        for line in lines:
            line_starts.append(current_pos)
            current_pos += len(line) + 1

        class_pattern = re.compile(r"^([ \t]*)class\s+")
        covered_lines: set = set()
        class_ranges: List[tuple] = []

        for i, line in enumerate(lines):
            if i in covered_lines:
                continue

            match = class_pattern.match(line)
            if match:
                base_indent = len(match.group(1))
                class_end = self._find_class_end(
                    lines,
                    i,
                    base_indent
                )
                class_ranges.append(
                    (
                        i,
                        class_end - 1
                    )
                )
                for j in range(i, class_end):
                    covered_lines.add(j)

        for class_start, class_end in class_ranges:
            first_member = class_start + 1
            while (
                first_member < len(lines)
                and lines[first_member].strip() == ""
            ):
                first_member += 1

            if first_member <= class_end:
                first_stripped = lines[first_member].lstrip()
                is_docstring = first_stripped.startswith('"""') or first_stripped.startswith("'''")
                is_method_or_class = (
                    first_stripped.startswith("def ")
                    or first_stripped.startswith("class ")
                )

                if not is_docstring and not is_method_or_class:
                    space_start = line_starts[class_start] + len(lines[class_start])
                    space_end = line_starts[first_member]
                    token_text = document[space_start:space_end]

                    if token_text and token_text != "\n":
                        tokens.append(
                            {
                                "token": token_text,
                                "index": space_start,
                                "length": len(token_text)
                            }
                        )

                elif is_docstring:
                    quote_char = first_stripped[:3]
                    if first_stripped.count(quote_char) >= 2 and len(first_stripped) > 3:
                        docstring_end_line = first_member
                    else:
                        docstring_end_line = first_member + 1
                        while docstring_end_line < len(lines):
                            if quote_char in lines[docstring_end_line]:
                                break

                            docstring_end_line += 1

                    if docstring_end_line <= class_end:
                        after_docstring = docstring_end_line + 1
                        while after_docstring < len(lines) and lines[after_docstring].strip() == "":
                            after_docstring += 1

                        if after_docstring <= class_end:
                            after_stripped = lines[after_docstring].lstrip()
                            after_is_method_or_class = (
                                after_stripped.startswith("def ")
                                or after_stripped.startswith("class ")
                            )

                            if not after_is_method_or_class:
                                space_start = line_starts[docstring_end_line] + len(lines[docstring_end_line])
                                space_end = line_starts[after_docstring]
                                token_text = document[space_start:space_end]

                                if token_text and token_text != "\n":
                                    tokens.append(
                                        {
                                            "token": token_text,
                                            "index": space_start,
                                            "length": len(token_text)
                                        }
                                    )

        tokens.sort(key=lambda t: t['index'])

        return tokens
