"""Class whitespace tokenizer module."""

__all__ = ["PyClassWhitespaceTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyClassWhitespaceTokenizer(Tokenizer):
    """Tokenizes whitespace before and after Python class definitions.

    Captures the newlines between the end of a preceding block and the start
    of a class, and between the end of a class and the start of the next block.

    Emits token type: `class_whitespace`

    Examples
    --------

    ```python
    from cleer import PyClassWhitespaceTokenizer

    tokenizer = PyClassWhitespaceTokenizer()
    tokens = tokenizer.tokenize("x = 1\\n\\n\\nclass Foo:\\n    pass\\n\\n\\ny = 2\\n")
    ```
    """
    emits_token_type = "class_whitespace"


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
        """Tokenize whitespace around class definitions.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyClassWhitespaceTokenizer()
        tokens = tokenizer.tokenize("x = 1\\n\\nclass Foo:\\n    pass\\n\\ny = 2\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results for whitespace before/after classes.

            ```python
            [
                {"token": "\\n\\n", "index": 5, "length": 2},
                {"token": "\\n\\n", "index": 24, "length": 2}
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

        class_pattern = re.compile(r"^([ \t]*)class\s+")
        covered_lines = set()
        class_ranges = []

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
            prev_content_end = class_start - 1
            while (
                prev_content_end >= 0
                and lines[prev_content_end].strip() == ""
            ):
                prev_content_end -= 1

            if prev_content_end >= 0:
                space_start = line_starts[prev_content_end] + len(lines[prev_content_end])
                space_end = line_starts[class_start]
                token_text = document[space_start:space_end]

                if token_text:
                    tokens.append(
                        {
                            "token": token_text,
                            "index": space_start,
                            "length": len(token_text)
                        }
                    )

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

                if not is_docstring and is_method_or_class:
                    space_start = line_starts[class_start] + len(lines[class_start])
                    space_end = line_starts[first_member]
                    token_text = document[space_start:space_end]

                    if token_text and token_text != "\n\n\n":
                        tokens.append(
                            {
                                "token": token_text,
                                "index": space_start,
                                "length": len(token_text)
                            }
                        )

                else:
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

                            if after_is_method_or_class:
                                space_start = line_starts[docstring_end_line] + len(lines[docstring_end_line])
                                space_end = line_starts[after_docstring]
                                token_text = document[space_start:space_end]

                                if token_text and token_text != "\n\n\n":
                                    tokens.append(
                                        {
                                            "token": token_text,
                                            "index": space_start,
                                            "length": len(token_text)
                                        }
                                    )

            next_content_start = class_end + 1
            while (
                next_content_start < len(lines)
                and lines[next_content_start].strip() == ""
            ):
                next_content_start += 1

            if next_content_start < len(lines):
                space_start = line_starts[class_end] + len(lines[class_end])
                space_end = line_starts[next_content_start]
                token_text = document[space_start:space_end]

                if token_text:
                    tokens.append(
                        {
                            "token": token_text,
                            "index": space_start,
                            "length": len(token_text)
                        }
                    )

        tokens.sort(key=lambda t: t['index'])

        seen_indices: set = set()
        unique_tokens: List[dict] = []
        for t in tokens:
            if t['index'] not in seen_indices:
                seen_indices.add(t['index'])
                unique_tokens.append(t)

        return unique_tokens
