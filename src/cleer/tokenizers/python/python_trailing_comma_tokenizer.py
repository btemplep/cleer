"""See :class:`PythonTrailingCommaTokenizer`."""

__all__ = [
    "PythonTrailingCommaTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonTrailingCommaTokenizer(Tokenizer):
    """Tokenizes trailing commas in comma-separated sequences.

    Emits tokens for trailing commas that should be removed (or
    positions where trailing commas should be added, based on config).

    By default, trailing commas are removed except for single-element
    tuples (which require them syntactically).

    Examples
    --------

    ```python
    from cleer import PythonTrailingCommaTokenizer

    tokenizer = PythonTrailingCommaTokenizer()
    tokens = tokenizer.tokenize("a = [1, 2, 3,]\\n")
    ```
    """
    emits_token_type = "python_trailing_comma"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize trailing commas that violate the style.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each trailing comma violation.

            ```python
            [
                {"token": ",", "index": 12, "length": 1}
            ]
            ```
        """
        tree = ast.parse(document)

        line_offsets = self._build_line_offsets(document)
        tokens = []

        for node in ast.walk(tree):
            if isinstance(node, ast.List):
                self._check_trailing(
                    node,
                    node.elts,
                    document,
                    line_offsets,
                    tokens
                )
            elif isinstance(node, ast.Set):
                self._check_trailing(
                    node,
                    node.elts,
                    document,
                    line_offsets,
                    tokens
                )
            elif isinstance(node, ast.Tuple):
                if len(node.elts) > 1:
                    self._check_trailing(
                        node,
                        node.elts,
                        document,
                        line_offsets,
                        tokens
                    )

            elif isinstance(node, ast.Dict):
                if node.values:
                    self._check_dict_trailing(
                        node,
                        document,
                        line_offsets,
                        tokens
                    )

            elif isinstance(node, ast.Call):
                self._check_call_trailing(
                    node,
                    document,
                    line_offsets,
                    tokens
                )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._check_funcdef_trailing(
                    node,
                    document,
                    line_offsets,
                    tokens
                )

        tokens.sort(key=lambda t: t['index'])

        return tokens


    def _check_trailing(
        self,
        container_node,
        elements: list,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Check for trailing comma in a sequence."""
        if not elements:
            return

        last = elements[-1]
        start = (
            line_offsets[last.end_lineno - 1]
            + last.end_col_offset
        )
        end = (
            line_offsets[container_node.end_lineno - 1]
            + container_node.end_col_offset
            - 1
        )

        if end <= start:
            return

        segment = document[start:end]
        comma_pos = segment.find(",")

        if comma_pos == -1:
            return

        abs_comma = start + comma_pos
        tokens.append(
            {
                "token": ",",
                "index": abs_comma,
                "length": 1
            }
        )


    def _check_dict_trailing(
        self,
        node: ast.Dict,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Check for trailing comma in a dict."""
        last_value = node.values[-1]
        start = (
            line_offsets[last_value.end_lineno - 1]
            + last_value.end_col_offset
        )
        end = (
            line_offsets[node.end_lineno - 1]
            + node.end_col_offset
            - 1
        )

        if end <= start:
            return

        segment = document[start:end]
        comma_pos = segment.find(",")

        if comma_pos == -1:
            return

        abs_comma = start + comma_pos
        tokens.append(
            {
                "token": ",",
                "index": abs_comma,
                "length": 1
            }
        )


    def _check_call_trailing(
        self,
        node: ast.Call,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Check for trailing comma in a function call."""
        all_args = (
            list(node.args)
            + [kw.value for kw in node.keywords]
        )

        if not all_args:
            return

        last = max(
            all_args,
            key=lambda a: (
                a.end_lineno,
                a.end_col_offset
            )
        )
        start = (
            line_offsets[last.end_lineno - 1]
            + last.end_col_offset
        )
        end = (
            line_offsets[node.end_lineno - 1]
            + node.end_col_offset
            - 1
        )

        if end <= start:
            return

        segment = document[start:end]
        comma_pos = segment.find(",")

        if comma_pos == -1:
            return

        abs_comma = start + comma_pos
        tokens.append(
            {
                "token": ",",
                "index": abs_comma,
                "length": 1
            }
        )


    def _check_funcdef_trailing(
        self,
        node,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Check for trailing comma in function definition params."""
        args = node.args
        all_params = args.posonlyargs + args.args + args.kwonlyargs

        if args.kwarg:
            all_params.append(args.kwarg)
        elif args.vararg:
            all_params.append(args.vararg)

        if not all_params:
            return

        num_defaults = len(args.defaults)
        if (
            num_defaults
            and not args.kwonlyargs
            and not args.vararg
            and not args.kwarg
        ):
            last_default = args.defaults[-1]
            last_end_line = last_default.end_lineno
            last_end_col = last_default.end_col_offset
        elif args.kwarg:
            last_end_line = args.kwarg.end_lineno
            last_end_col = args.kwarg.end_col_offset
        elif args.vararg and not args.kwonlyargs:
            last_end_line = args.vararg.end_lineno
            last_end_col = args.vararg.end_col_offset
        elif args.kwonlyargs:
            last_kw = args.kwonlyargs[-1]
            kw_idx = len(args.kwonlyargs) - 1
            if (
                kw_idx < len(args.kw_defaults)
                and args.kw_defaults[kw_idx] is not None
            ):
                last_default = args.kw_defaults[kw_idx]
                last_end_line = last_default.end_lineno
                last_end_col = last_default.end_col_offset
            else:
                last_end_line = last_kw.end_lineno
                last_end_col = last_kw.end_col_offset

        else:
            last_param = all_params[-1]
            last_end_line = last_param.end_lineno
            last_end_col = last_param.end_col_offset

        start = line_offsets[last_end_line - 1] + last_end_col

        func_line = line_offsets[node.lineno - 1]
        line_text = document[func_line:].split("\n")[0] if node.lineno == node.end_lineno else ""

        close_paren = document.find(")", start)

        if close_paren == -1:
            return

        segment = document[start:close_paren]
        comma_pos = segment.find(",")

        if comma_pos == -1:
            return

        abs_comma = start + comma_pos
        tokens.append(
            {
                "token": ",",
                "index": abs_comma,
                "length": 1
            }
        )


    def _build_line_offsets(self, document: str) -> list[int]:
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
