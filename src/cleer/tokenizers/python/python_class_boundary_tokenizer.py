"""See [](#cleer.tokenizers.python.python_class_boundary_tokenizer.PythonClassBoundaryTokenizer)"""

__all__ = [
    "PythonClassBoundaryTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonClassBoundaryTokenizer(Tokenizer):
    """Tokenizes class definitions for internal spacing enforcement.

    Emits a token for each class definition spanning from the class
    declaration line through the end of the class body including
    trailing blank lines.

    Examples
    --------

    ```python
    from cleer import PythonClassBoundaryTokenizer

    tokenizer = PythonClassBoundaryTokenizer()
    tokens = tokenizer.tokenize("class Foo:\\n    pass\\n")
    ```
    """
    emits_token_type = "python_class_boundary"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize class definitions for spacing enforcement.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results, one per class definition.
        """
        try:
            tree = ast.parse(document)
        except SyntaxError:
            return []

        line_offsets = self._build_line_offsets(document)
        results = []
        self._walk(tree.body, line_offsets, document, results)
        results.sort(key=lambda e: e['index'])

        return results


    def _walk(
        self,
        body: list,
        line_offsets: list[int],
        document: str,
        results: list
    ):
        """Find class definitions at any scope."""
        for node in body:
            if isinstance(node, ast.ClassDef):
                start_line = node.lineno

                if node.decorator_list:
                    start_line = node.decorator_list[0].lineno

                start = line_offsets[start_line - 1]
                end = self._get_end(node, line_offsets, document)
                token = document[start:end]
                results.append(
                    {
                        "token": token,
                        "index": start,
                        "length": len(token)
                    }
                )
            elif isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):
                self._walk(node.body, line_offsets, document, results)


    def _get_end(
        self,
        node: ast.stmt,
        line_offsets: list[int],
        document: str
    ) -> int:
        """Get the end of the class including trailing blank lines."""
        if node.end_lineno >= len(line_offsets):
            end_offset = len(document)
        else:
            end_offset = line_offsets[node.end_lineno]

        while (
            end_offset < len(document)
            and document[end_offset] == "\n"
        ):
            end_offset += 1

        return end_offset


    def _build_line_offsets(self, document: str) -> list[int]:
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
