"""Class tokenizer module."""

__all__ = ["PyClassTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyClassTokenizer(Tokenizer):
    """Tokenizes whole Python class definitions.

    Each class definition is returned as a single token including its indent
    and full body. Does not include extra newlines on outside of class.

    Emits token type: `class`

    Examples
    --------

    ```python
    from cleer import PyClassTokenizer

    tokenizer = PyClassTokenizer()
    tokens = tokenizer.tokenize("class MyClass:\\n    def __init__(self):\\n        pass\\n")
    ```
    """
    emits_token_type = "class"


    def _find_class_end(
        self,
        lines: List[str],
        class_line_idx: int,
        base_indent: int
    ) -> int:
        """Find the last line of a class body."""
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

        return i - 1


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize whole class definitions in a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyClassTokenizer()
        tokens = tokenizer.tokenize("class Foo:\\n    x = 1\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per class definition.

            ```python
            [
                {"token": "class Foo:\\n    x = 1", "index": 0, "length": 20}
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

                start_index = line_starts[i]
                end_index = line_starts[class_end] + len(lines[class_end])
                token_text = document[start_index:end_index]

                tokens.append(
                    {
                        "token": token_text,
                        "index": start_index,
                        "length": len(token_text)
                    }
                )

                for j in range(i, class_end + 1):
                    covered_lines.add(j)

        return tokens
