"""Import section tokenizer module."""

__all__ = ["PyImportSectionTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


IMPORT_LINE_PATTERN = re.compile(r"^[ \t]*(import |from [\w.]+ import )", re.MULTILINE)


class PyImportSectionTokenizer(Tokenizer):
    """Tokenizes contiguous sections of Python import statements.

    A section is defined as any contiguous block of lines that are either
    import statements or blank lines between import statements, including
    surrounding whitespace. The token includes the import section and any
    trailing whitespace up to but not including the next non-import line.

    Emits token type: `import_section`

    Examples
    --------

    ```python
    from cleer import PyImportSectionTokenizer

    tokenizer = PyImportSectionTokenizer()
    tokens = tokenizer.tokenize("import os\\nimport sys\\n\\nx = 1\\n")
    ```
    """
    emits_token_type = "import_section"


    def _is_import_line(self, line: str) -> bool:
        """Check if a line is an import statement or part of a multi-line import."""
        stripped = line.strip()

        return (
            stripped.startswith("import ")
            or stripped.startswith("from ")
            or stripped.startswith(")")
        )


    def _is_multiline_import_continuation(self, line: str, in_paren: bool) -> bool:
        """Check if a line is a continuation of a multi-line import."""
        if in_paren:
            return True

        stripped = line.strip()

        return stripped.endswith("\\")


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize contiguous import sections in a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyImportSectionTokenizer()
        tokens = tokenizer.tokenize("import os\\nimport sys\\n\\nx = 1\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per contiguous import section.

            ```python
            [
                {"token": "import os\\nimport sys\\n", "index": 0, "length": 20}
            ]
            ```
        """
        tokens: List[dict] = []
        lines = document.split("\n")
        i = 0
        doc_index = 0
        line_starts = []

        current_pos = 0
        for line in lines:
            line_starts.append(current_pos)
            current_pos += len(line) + 1

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if (
                (
                    stripped.startswith("import ")
                    or stripped.startswith("from ")
                )
                and line == line.lstrip()
            ):
                section_start = i
                start_index = line_starts[i]
                in_paren = "(" in line and ")" not in line

                i += 1

                while i < len(lines):
                    current_line = lines[i]
                    current_stripped = current_line.strip()

                    if in_paren:
                        if ")" in current_line:
                            in_paren = False

                        i += 1
                        continue

                    if (
                        current_stripped.startswith("import ")
                        or current_stripped.startswith("from ")
                    ):
                        if "(" in current_line and ")" not in current_line:
                            in_paren = True

                        i += 1
                        continue

                    if current_stripped == "":
                        peek = i + 1
                        while peek < len(lines) and lines[peek].strip() == "":
                            peek += 1

                        if peek < len(lines):
                            peek_stripped = lines[peek].strip()
                            if (
                                peek_stripped.startswith("import ")
                                or peek_stripped.startswith("from ")
                            ):
                                i += 1
                                continue

                    break

                end_index = line_starts[i] if i < len(lines) else len(document)
                section_text = document[start_index:end_index]

                if section_text.endswith("\n"):
                    tokens.append(
                        {
                            "token": section_text,
                            "index": start_index,
                            "length": len(section_text)
                        }
                    )
                else:
                    tokens.append(
                        {
                            "token": section_text,
                            "index": start_index,
                            "length": len(section_text)
                        }
                    )

            else:
                i += 1

        return tokens
