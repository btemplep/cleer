"""Python compound chain tokenizer module."""

__all__ = ["PythonCompoundChainTokenizer"]


import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonCompoundChainTokenizer(Tokenizer):
    """Tokenizes full compound statement chains.

    Emits tokens for compound statements that have multiple parts
    (if/elif/else, try/except/finally, for/else, while/else). Each
    token spans from the first line of the chain through the last line
    of the final part's body, preserving original indentation.

    Single-part compounds (plain ``if`` with no elif/else) are not
    emitted.

    Examples
    --------

    ```python
    from cleer import PythonCompoundChainTokenizer

    tokenizer = PythonCompoundChainTokenizer()
    tokens = tokenizer.tokenize("if x:\\n    pass\\nelse:\\n    pass\\n")
    ```
    """
    emits_token_type = "python_compound_chain"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize compound statement chains.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each compound chain.
        """
        try:
            tree = ast.parse(document)
        except SyntaxError:
            return []

        lines = document.split("\n")
        line_offsets = self._build_line_offsets(document)
        tokens = []
        seen_ranges: set[tuple[int, int]] = set()

        self._walk(tree, lines, line_offsets, document, tokens, seen_ranges)

        tokens.sort(key=lambda t: t["index"])

        return tokens


    def _walk(self, node, lines, line_offsets, document, tokens, seen_ranges):
        """Walk AST to find compound chains."""
        for child in ast.iter_child_nodes(node):
            emitted = False

            if isinstance(child, ast.If):
                if child.orelse:
                    self._emit_if_chain(
                        child, lines, line_offsets, document, tokens, seen_ranges
                    )
                    emitted = True

            elif isinstance(child, ast.Try):
                self._emit_try_chain(
                    child, lines, line_offsets, document, tokens, seen_ranges
                )
                emitted = True

            elif isinstance(child, (ast.For, ast.AsyncFor, ast.While)):
                if child.orelse:
                    self._emit_simple_chain(
                        child, lines, line_offsets, document, tokens, seen_ranges
                    )
                    emitted = True

            elif isinstance(child, (ast.With, ast.AsyncWith)):
                pass

            if not emitted and isinstance(child, (
                ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try,
                ast.With, ast.AsyncWith
            )):
                self._walk(child, lines, line_offsets, document, tokens, seen_ranges)


    def _emit_if_chain(self, node, lines, line_offsets, document, tokens, seen_ranges):
        """Emit token for an if/elif/else chain."""
        start_line = node.lineno
        end_line = self._find_chain_end(node)

        self._emit(start_line, end_line, lines, line_offsets, document, tokens, seen_ranges)


    def _emit_try_chain(self, node, lines, line_offsets, document, tokens, seen_ranges):
        """Emit token for a try/except/else/finally chain."""
        start_line = node.lineno
        end_line = node.end_lineno

        self._emit(start_line, end_line, lines, line_offsets, document, tokens, seen_ranges)


    def _emit_simple_chain(self, node, lines, line_offsets, document, tokens, seen_ranges):
        """Emit token for a for/while with else."""
        start_line = node.lineno
        end_line = node.end_lineno

        self._emit(start_line, end_line, lines, line_offsets, document, tokens, seen_ranges)


    def _emit(self, start_line, end_line, lines, line_offsets, document, tokens, seen_ranges):
        """Emit a token for the given line range."""
        start_offset = line_offsets[start_line - 1]
        if end_line < len(line_offsets):
            end_offset = line_offsets[end_line]
        else:
            end_offset = len(document)

        token_range = (start_offset, end_offset)
        if token_range in seen_ranges:
            return

        seen_ranges.add(token_range)

        token = document[start_offset:end_offset]

        tokens.append({
            "token": token,
            "index": start_offset,
            "length": len(token)
        })


    def _find_chain_end(self, node: ast.If) -> int:
        """Find the end line of a full if/elif/else chain."""
        if node.orelse:
            last_else = node.orelse[-1]
            if isinstance(last_else, ast.If):
                return self._find_chain_end(last_else)
            else:
                return last_else.end_lineno
        else:
            return node.end_lineno


    def _build_line_offsets(self, document: str) -> list[int]:
        """Build a list mapping line numbers (0-indexed) to character offsets."""
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
