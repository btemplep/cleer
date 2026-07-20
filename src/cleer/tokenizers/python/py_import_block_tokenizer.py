"""Import block tokenizer module."""

__all__ = ["PyImportBlockTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyImportBlockTokenizer(Tokenizer):
    """Tokenizes blocks of Python imports separated by blank lines.

    Each block is a group of contiguous import statements with no blank
    lines between them. The token includes the indent but no extra
    surrounding newlines.

    Emits token type: `import_block`

    Examples
    --------

    ```python
    from cleer import PyImportBlockTokenizer

    tokenizer = PyImportBlockTokenizer()
    tokens = tokenizer.tokenize("import os\\nimport sys\\n\\nimport requests\\n")
    ```
    """
    emits_token_type = "import_block"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize blocks of imports in a document.

        Each contiguous group of import statements (no blank lines between)
        becomes a token.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyImportBlockTokenizer()
        tokens = tokenizer.tokenize("import os\\nimport sys\\n\\nimport requests\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per contiguous import block.

            ```python
            [
                {"token": "import os\\nimport sys", "index": 0, "length": 19},
                {"token": "import requests", "index": 21, "length": 14}
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

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if stripped.startswith("import ") or stripped.startswith("from "):
                block_start = i
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

                    break

                end_line = i - 1
                end_index = line_starts[end_line] + len(lines[end_line])
                block_text = document[start_index:end_index]

                tokens.append(
                    {
                        "token": block_text,
                        "index": start_index,
                        "length": len(block_text)
                    }
                )
            else:
                i += 1

        return tokens
