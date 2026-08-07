"""Python __all__ tokenizer module."""

__all__ = [
    "PythonAllTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonAllTokenizer(Tokenizer):
    """Tokenizes the first `__all__` assignment in a module.

    Emits a token spanning the `__all__` assignment along with
    surrounding blank lines so the formatter can enforce correct spacing
    and formatting.

    Only the first `__all__` assignment is tokenized. Subsequent
    assignments are ignored.

    Examples
    --------

    ```python
    from cleer import PythonAllTokenizer

    tokenizer = PythonAllTokenizer()
    tokens = tokenizer.tokenize("__all__ = ['Foo', 'Bar']\\n")
    ```
    """
    emits_token_type = "python_all"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize the first `__all__` assignment with surrounding context.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List with at most one token result for the `__all__` block.

            ```python
            [
                {"token": "\\n__all__ = ['Foo']\\n\\n", "index": 20, "length": 22}
            ]
            ```
        """
        tree = ast.parse(document)
        line_offsets = self._build_line_offsets(document)
        all_node = self._find_first_all(tree)
        if all_node is None:
            return []

        prev_end, next_start = self._find_boundaries(
            tree,
            all_node,
            document,
            line_offsets
        )
        token = document[prev_end:next_start]

        return [{
            "token": token,
            "index": prev_end,
            "length": len(token)
        }]


    def _find_first_all(self, tree: ast.Module):
        """Find the first __all__ assignment node in the module body."""
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue

            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    return node

        return None


    def _find_boundaries(
        self,
        tree: ast.Module,
        all_node: ast.Assign,
        document: str,
        line_offsets: list[int]
    ):
        """Find the start and end boundaries including surrounding whitespace.

        Returns the character offset after the previous node's last line
        and the character offset of the next node's first line.
        """
        prev_node = None
        next_node = None
        found = False

        for node in tree.body:
            if node is all_node:
                found = True
                continue

            if not found:
                prev_node = node
            else:
                next_node = node
                break

        if prev_node is not None:
            prev_end_line = prev_node.end_lineno
            prev_end = line_offsets[prev_end_line]
        else:
            prev_end = 0

        if next_node is not None:
            next_start_line = next_node.lineno - 1
            next_start = line_offsets[next_start_line]
        else:
            next_start = len(document)

        return prev_end, next_start


    def _build_line_offsets(self, document: str) -> list[int]:
        """Build a list mapping line numbers (0-indexed) to character offsets."""
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
