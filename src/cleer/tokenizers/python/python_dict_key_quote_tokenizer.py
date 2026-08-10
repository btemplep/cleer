"""Python dict key quote tokenizer module."""

__all__ = [
    "PythonDictKeyQuoteTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonDictKeyQuoteTokenizer(Tokenizer):
    """Tokenizes string literals used in dict bracket subscript lookups.

    Uses Python's AST to find string constants used as keys in bracket
    subscript access (e.g., `my_dict['key']`). Emits the full source
    text of each such string including its quote characters.

    Examples
    --------

    ```python
    from cleer import PythonDictKeyQuoteTokenizer

    tokenizer = PythonDictKeyQuoteTokenizer()
    tokens = tokenizer.tokenize("x = my_dict['key']\\n")
    ```
    """
    emits_token_type = "python_dict_key_quote"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize string literals used as dict bracket subscript keys.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each dict key string.

            ```python
            [
                {"token": "'key'", "index": 12, "length": 5}
            ]
            ```
        """
        tree = ast.parse(document)

        line_offsets = self._build_line_offsets(document)
        tokens = self._collect_dict_keys(tree, document, line_offsets)

        tokens.sort(key=lambda t: t['index'])

        return tokens


    def _build_line_offsets(self, document: str) -> list[int]:
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets


    def _collect_dict_keys(
        self,
        tree: ast.Module,
        document: str,
        line_offsets: list[int]
    ) -> list[TokenResult]:
        """Collect string constants used as dict subscript keys."""
        tokens = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Subscript):
                continue

            slice_node = node.slice

            if not isinstance(slice_node, ast.Constant):
                continue

            if not isinstance(slice_node.value, str):
                continue

            end_lineno = slice_node.end_lineno
            end_col_offset = slice_node.end_col_offset

            if end_lineno is None or end_col_offset is None:
                continue

            start_index = line_offsets[slice_node.lineno - 1] + slice_node.col_offset
            end_index = line_offsets[end_lineno - 1] + end_col_offset
            token = document[start_index:end_index]

            if not token:
                continue

            tokens.append(
                {
                    "token": token,
                    "index": start_index,
                    "length": end_index - start_index
                }
            )

        return tokens
