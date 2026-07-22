"""Import statement tokenizer module."""

__all__ = ["PyImportStatementTokenizer"]


from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyImportStatementTokenizer(Tokenizer):
    """Tokenizes individual Python import statements.

    Each import statement is returned as a single token including its indent.
    Multi-line imports (using parentheses or backslash continuation) are
    included as a single token.

    Emits token type: `import_statement`

    Examples
    --------

    ```python
    from cleer import PyImportStatementTokenizer

    tokenizer = PyImportStatementTokenizer()
    tokens = tokenizer.tokenize("import os\\nfrom sys import path\\n")
    ```
    """
    emits_token_type = "import_statement"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize individual import statements in a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyImportStatementTokenizer()
        tokens = tokenizer.tokenize("import os\\nfrom sys import path, argv\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per import statement.

            ```python
            [
                {"token": "import os", "index": 0, "length": 9},
                {"token": "from sys import path, argv", "index": 10, "length": 26}
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

            if (
                stripped.startswith("import ")
                or stripped.startswith("from ")
            ):
                start_index = line_starts[i]
                end_line = i

                if "(" in line and ")" not in line:
                    end_line = i + 1
                    while end_line < len(lines):
                        if ")" in lines[end_line]:
                            break

                        end_line += 1

                elif line.rstrip().endswith("\\"):
                    end_line = i + 1
                    while end_line < len(lines):
                        if not lines[end_line].rstrip().endswith("\\"):
                            break

                        end_line += 1

                end_index = line_starts[end_line] + len(lines[end_line])
                token_text = document[start_index:end_index]

                tokens.append(
                    {
                        "token": token_text,
                        "index": start_index,
                        "length": len(token_text)
                    }
                )
                i = end_line + 1
            else:
                i += 1

        return tokens
