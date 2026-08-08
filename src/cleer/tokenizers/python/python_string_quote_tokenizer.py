"""Python string quote tokenizer module."""

__all__ = [
    "PythonStringQuoteTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonStringQuoteTokenizer(Tokenizer):
    """Tokenizes Python string literals excluding dict key bracket lookups.

    Uses Python's AST to find all string constants that are NOT used as
    dict bracket subscript keys. Emits the full source text of each
    string including its quote characters.

    This tokenizer pairs with `PythonStringQuoteFormatter` which enforces
    quote style for regular string literals and multiline/docstrings.

    Examples
    --------

    ```python
    from cleer import PythonStringQuoteTokenizer

    tokenizer = PythonStringQuoteTokenizer()
    tokens = tokenizer.tokenize("x = 'hello'\\n")
    ```
    """
    emits_token_type = "python_string_quote"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize Python string literals (excluding dict key lookups).

        Includes regular strings, f-strings, and t-strings.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each string literal.

            ```python
            [
                {"token": "'hello'", "index": 4, "length": 7}
            ]
            ```
        """
        tree = ast.parse(document)

        line_offsets = self._build_line_offsets(document)
        dict_key_positions = self._collect_dict_key_positions(tree)
        fstring_positions = self._collect_fstring_positions(tree)
        tokens = self._collect_strings(
            tree,
            document,
            line_offsets,
            dict_key_positions,
            fstring_positions
        )
        self._collect_fstrings(tree, document, line_offsets, tokens)

        tokens.sort(key=lambda t: t['index'])

        return tokens


    def _build_line_offsets(self, document: str) -> list[int]:
        """Build a list mapping line numbers (0-indexed) to character offsets."""
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets


    def _collect_dict_key_positions(self, tree: ast.Module) -> set[tuple[int, int]]:
        """Collect line/col positions of string constants used as dict subscript keys."""
        positions = set()

        for node in ast.walk(tree):
            if not isinstance(node, ast.Subscript):
                continue

            slice_node = node.slice

            if (
                isinstance(slice_node, ast.Constant)
                and isinstance(slice_node.value, str)
            ):
                positions.add((slice_node.lineno, slice_node.col_offset))

        return positions


    def _collect_fstring_positions(self, tree: ast.Module) -> set[tuple[int, int]]:
        """Collect line/col positions of constants that are children of f/t-strings."""
        positions = set()
        fstring_types = [ast.JoinedStr]

        if hasattr(ast, "TemplateStr"):
            fstring_types.append(ast.TemplateStr)

        for node in ast.walk(tree):
            if not isinstance(node, tuple(fstring_types)):
                continue

            for child in ast.walk(node):
                if child is node:
                    continue

                if (
                    isinstance(child, ast.Constant)
                    and hasattr(child, "lineno")
                ):
                    positions.add((child.lineno, child.col_offset))

        return positions


    def _collect_fstrings(
        self,
        tree: ast.Module,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Collect f-string and t-string tokens."""
        fstring_types = [ast.JoinedStr]

        if hasattr(ast, "TemplateStr"):
            fstring_types.append(ast.TemplateStr)

        for node in ast.walk(tree):
            if not isinstance(node, tuple(fstring_types)):
                continue

            end_lineno = node.end_lineno
            end_col_offset = node.end_col_offset

            if end_lineno is None or end_col_offset is None:
                continue

            start_index = line_offsets[node.lineno - 1] + node.col_offset
            end_index = line_offsets[end_lineno - 1] + end_col_offset
            token = document[start_index:end_index]

            if not token or not self._is_string_token(token):
                continue

            tokens.append(
                {
                    "token": token,
                    "index": start_index,
                    "length": end_index - start_index
                }
            )


    def _collect_strings(
        self,
        tree: ast.Module,
        document: str,
        line_offsets: list[int],
        dict_key_positions: set[tuple[int, int]],
        fstring_positions: set[tuple[int, int]]
    ) -> list[TokenResult]:
        """Collect all non-dict-key, non-fstring-child string constant tokens."""
        tokens = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue

            if not isinstance(node.value, str):
                continue

            position = (node.lineno, node.col_offset)

            if position in dict_key_positions:
                continue

            if position in fstring_positions:
                continue

            end_lineno = node.end_lineno
            end_col_offset = node.end_col_offset

            if end_lineno is None or end_col_offset is None:
                continue

            start_index = line_offsets[node.lineno - 1] + node.col_offset
            end_index = line_offsets[end_lineno - 1] + end_col_offset
            token = document[start_index:end_index]

            if not token or not self._is_string_token(token):
                continue

            tokens.append(
                {
                    "token": token,
                    "index": start_index,
                    "length": end_index - start_index
                }
            )

        return tokens


    def _is_string_token(self, token: str) -> bool:
        """Check if the extracted token looks like a string literal."""
        stripped = token.lstrip()

        if not stripped:
            return False

        for prefix in (
            "f",
            "F",
            "r",
            "R",
            "b",
            "B",
            "u",
            "U",
            "t",
            "T",
            "rb",
            "rB",
            "Rb",
            "RB",
            "br",
            "bR",
            "Br",
            "BR",
            "fr",
            "fR",
            "Fr",
            "FR",
            "rf",
            "rF",
            "Rf",
            "RF",
            "tr",
            "tR",
            "Tr",
            "TR",
            "rt",
            "rT",
            "Rt",
            "RT"
        ):
            if (
                stripped.startswith(prefix)
                and len(stripped) > len(prefix)
            ):
                after = stripped[len(prefix)]
                if after in ("'", '"'):
                    return True

        if stripped[0] in ("'", '"'):
            return True

        return False
