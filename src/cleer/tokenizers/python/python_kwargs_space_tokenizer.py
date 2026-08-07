"""Python kwargs space tokenizer module."""

__all__ = [
    "PythonKwargsSpaceTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonKwargsSpaceTokenizer(Tokenizer):
    """Tokenizes the spacing around = in keyword arguments and function defaults.

    Emits tokens for the segment between a keyword argument name and its
    value in function calls, and between a parameter name and its default
    value in function definitions.

    Examples
    --------

    ```python
    from cleer import PythonKwargsSpaceTokenizer

    tokenizer = PythonKwargsSpaceTokenizer()
    tokens = tokenizer.tokenize("foo(x = 1)\\n")
    ```
    """
    emits_token_type = "python_kwargs_space"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize = spacing in kwargs and function defaults.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each kwarg = segment.

            ```python
            [
                {"token": " = ", "index": 5, "length": 3}
            ]
            ```
        """
        tree = ast.parse(document)

        line_offsets = self._build_line_offsets(document)
        tokens = []

        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg is not None:
                self._add_keyword(node, document, line_offsets, tokens)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._add_defaults(node, document, line_offsets, tokens)

        tokens.sort(key=lambda t: t['index'])

        return tokens


    def _add_keyword(
        self,
        node: ast.keyword,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add token for a call keyword argument."""
        arg_end_col = node.col_offset + len(node.arg)
        val_start_col = node.value.col_offset

        if node.lineno != node.value.lineno:
            return

        start = line_offsets[node.lineno - 1] + arg_end_col
        end = line_offsets[node.value.lineno - 1] + val_start_col
        token = document[start:end]

        if token == "=":
            return

        tokens.append(
            {
                "token": token,
                "index": start,
                "length": len(token)
            }
        )


    def _add_defaults(
        self,
        node,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add tokens for function definition default values."""
        args = node.args

        num_defaults = len(args.defaults)
        if num_defaults:
            default_args = args.args[-num_defaults:]
            for arg, default in zip(default_args, args.defaults):
                self._emit_default(
                    arg,
                    default,
                    document,
                    line_offsets,
                    tokens
                )

        for arg, default in zip(args.kwonlyargs, args.kw_defaults):
            if default is not None:
                self._emit_default(
                    arg,
                    default,
                    document,
                    line_offsets,
                    tokens
                )

        if args.posonlyargs:
            num_pos_defaults = len(args.defaults) - len(args.args) + len(args.posonlyargs)
            if num_pos_defaults > 0:
                pos_defaults = args.defaults[:num_pos_defaults]
                pos_args = args.posonlyargs[-num_pos_defaults:]
                for arg, default in zip(pos_args, pos_defaults):
                    self._emit_default(
                        arg,
                        default,
                        document,
                        line_offsets,
                        tokens
                    )


    def _emit_default(
        self,
        arg: ast.arg,
        default: ast.expr,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Emit a token for a parameter default = segment."""
        if arg.end_lineno != default.lineno:
            return

        start = line_offsets[arg.end_lineno - 1] + arg.end_col_offset
        end = line_offsets[default.lineno - 1] + default.col_offset
        token = document[start:end]

        if token == "=":
            return

        tokens.append(
            {
                "token": token,
                "index": start,
                "length": len(token)
            }
        )


    def _build_line_offsets(self, document: str) -> list[int]:
        """Build a list mapping line numbers (0-indexed) to character offsets."""
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
