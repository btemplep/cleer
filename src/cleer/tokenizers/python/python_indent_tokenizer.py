"""Python indent tokenizer module."""

__all__ = ["PythonIndentTokenizer"]


import ast
import re
from typing import List

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonIndentTokenizer(Tokenizer):
    """Tokenizes indented code blocks with incorrect indentation.

    Emits tokens for each top-level statement that contains lines with
    incorrect indentation — either tabs or wrong number of spaces per
    indent level.

    Parameters
    ----------
    tab_size : int, default=4
        Expected number of spaces per indentation level.

    Examples
    --------

    ```python
    from cleer import PythonIndentTokenizer

    tokenizer = PythonIndentTokenizer()
    tokens = tokenizer.tokenize("def foo():\\n  pass\\n")
    ```
    """
    emits_token_type = "python_indent"

    _leading_ws = re.compile(r"^([ \t]*)")


    def __init__(self, tab_size: int = 4):
        self._tab_size = tab_size


    def tokenize(self, document: str) -> List[TokenResult]:
        """Tokenize top-level code blocks with incorrect indentation.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        List[TokenResult]
            List of token results for each top-level code block that
            has incorrect indentation.

            ```python
            [
                {"token": "def foo():\\n  pass\\n", "index": 0, "length": 18}
            ]
            ```
        """
        tree = ast.parse(document)

        line_offsets = self._build_line_offsets(document)
        tokens = []

        for node in tree.body:
            if not hasattr(node, "end_lineno") or node.end_lineno is None:
                continue

            start_line = node.lineno

            if hasattr(node, "decorator_list") and node.decorator_list:
                start_line = node.decorator_list[0].lineno

            end_line = node.end_lineno

            if end_line <= start_line:
                continue

            start_index = line_offsets[start_line - 1]
            end_index = line_offsets[end_line] if end_line < len(line_offsets) else len(document)
            token = document[start_index:end_index]

            if self._has_bad_indent(token):
                tokens.append(
                    {
                        "token": token,
                        "index": start_index,
                        "length": len(token)
                    }
                )

        return tokens


    def _has_bad_indent(self, block: str) -> bool:
        """Check if a code block has any lines with incorrect indentation."""
        for line in block.split("\n"):
            if not line.strip():
                continue

            leading = self._get_leading_whitespace(line)

            if not leading:
                continue

            if "\t" in leading:
                return True

            if len(leading) % self._tab_size != 0:
                return True

        return False


    def _get_leading_whitespace(self, line: str) -> str:
        """Get the leading whitespace from a line."""
        match = self._leading_ws.match(line)

        if match:
            return match.group(1)

        return ""


    def _build_line_offsets(self, document: str) -> List[int]:
        """Build a list mapping line numbers (0-indexed) to character offsets."""
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
