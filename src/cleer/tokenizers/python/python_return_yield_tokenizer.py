"""Python return/yield tokenizer module."""

__all__ = [
    "PythonReturnYieldTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonReturnYieldTokenizer(Tokenizer):
    """Tokenizes function definitions that contain return or yield.

    Emits a token for each top-level or nested function (including async
    functions) that contains at least one return or yield statement. The
    token spans the function definition including indentation and
    trailing blank lines.

    Examples
    --------

    ```python
    from cleer import PythonReturnYieldTokenizer

    tokenizer = PythonReturnYieldTokenizer()
    tokens = tokenizer.tokenize("def foo():\\n    x = 1\\n    return x\\n")
    ```
    """
    emits_token_type = "python_return_yield"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize functions containing return/yield statements.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results, one per function with return/yield.
        """
        tree = ast.parse(document)
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
        """Recursively find top-level functions with return/yield."""
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self._contains_return_yield(node):
                    start = line_offsets[node.lineno - 1]
                    end = self._get_end(node, line_offsets, document)
                    token = document[start:end]
                    results.append(
                        {
                            "token": token,
                            "index": start,
                            "length": len(token)
                        }
                    )

            elif isinstance(node, ast.ClassDef):
                self._walk(node.body, line_offsets, document, results)
            else:
                for field_name in (
                    "body",
                    "orelse",
                    "finalbody"
                ):
                    child = getattr(node, field_name, None)

                    if child and isinstance(child, list):
                        self._walk(child, line_offsets, document, results)

                handlers = getattr(node, "handlers", None)

                if handlers:
                    for handler in handlers:
                        if handler.body:
                            self._walk(
                                handler.body,
                                line_offsets,
                                document,
                                results
                            )


    def _contains_return_yield(self, func_node: ast.stmt) -> bool:
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return):
                return True

            if isinstance(node, (ast.Yield, ast.YieldFrom)):
                return True

        return False


    def _get_end(
        self,
        node: ast.stmt,
        line_offsets: list[int],
        document: str
    ) -> int:
        """Get the end of the function including trailing blank lines."""
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
