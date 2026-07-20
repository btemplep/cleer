"""Import section space tokenizer module."""

__all__ = ["PyImportSectionSpaceTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyImportSectionSpaceTokenizer(Tokenizer):
    """Tokenizes whitespace after the last import section in a Python file.

    Captures the newline characters between the end of the last import
    statement and the start of the next non-import content.

    Emits token type: `import_section_space`

    Examples
    --------

    ```python
    from cleer import PyImportSectionSpaceTokenizer

    tokenizer = PyImportSectionSpaceTokenizer()
    tokens = tokenizer.tokenize("import os\\n\\nclass Foo:\\n    pass\\n")
    ```
    """
    emits_token_type = "import_section_space"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize whitespace after the last import section.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyImportSectionSpaceTokenizer()
        tokens = tokenizer.tokenize("import os\\nimport sys\\n\\nx = 1\\n")
        ```

        Returns
        -------
        List[dict]
            List of token results for whitespace after the import section.

            ```python
            [
                {"token": "\\n\\n", "index": 20, "length": 2}
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

        import_pattern = re.compile(r"^(import |from [\w.]+ import )")
        last_import_line = -1
        in_paren = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            if in_paren:
                if ")" in line:
                    in_paren = False

                last_import_line = i
                continue

            if import_pattern.match(line):
                if "(" in line and ")" not in line:
                    in_paren = True

                last_import_line = i
                continue

        if last_import_line < 0:
            return tokens

        next_content = last_import_line + 1
        while next_content < len(lines) and lines[next_content].strip() == "":
            next_content += 1

        if next_content >= len(lines):
            return tokens

        space_start = line_starts[last_import_line] + len(lines[last_import_line])
        space_end = line_starts[next_content]
        token_text = document[space_start:space_end]

        if token_text and token_text != "\n\n\n":
            tokens.append(
                {
                    "token": token_text,
                    "index": space_start,
                    "length": len(token_text)
                }
            )

        return tokens
