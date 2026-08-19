"""See [](#cleer.tokenizers.python.python_comma_space_tokenizer.PythonCommaSpaceTokenizer)"""

__all__ = [
    "PythonCommaSpaceTokenizer"
]

import ast

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonCommaSpaceTokenizer(Tokenizer):
    """Tokenizes comma spacing in comma-separated sequences.

    Emits tokens for the segment from the end of one element through the
    comma to the start of the next element. The formatter can then enforce
    no space before the comma and one space after (or a newline for
    multi-line sequences).

    Handles: lists, tuples, dicts, sets, function calls, function
    definitions, and for-loop target unpacking.

    Examples
    --------

    ```python
    from cleer import PythonCommaSpaceTokenizer

    tokenizer = PythonCommaSpaceTokenizer()
    tokens = tokenizer.tokenize("x = [1 , 2 ,3]\\n")
    ```
    """
    emits_token_type = "python_comma_space"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize comma spacing segments between consecutive elements.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each comma spacing segment.

            ```python
            [
                {"token": " , ", "index": 6, "length": 3}
            ]
            ```
        """
        tree = ast.parse(document)

        line_offsets = self._build_line_offsets(document)
        tokens = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.List, ast.Set)):
                self._add_sequence_commas(
                    node.elts,
                    document,
                    line_offsets,
                    tokens
                )
            elif isinstance(node, ast.Tuple):
                if len(node.elts) > 1:
                    self._add_sequence_commas(
                        node.elts,
                        document,
                        line_offsets,
                        tokens
                    )

            elif isinstance(node, ast.Dict):
                self._add_dict_commas(node, document, line_offsets, tokens)
            elif isinstance(node, ast.Call):
                self._add_call_commas(node, document, line_offsets, tokens)
            elif isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):
                self._add_funcdef_commas(
                    node,
                    document,
                    line_offsets,
                    tokens
                )
            elif isinstance(node, ast.For):
                if (
                    isinstance(node.target, ast.Tuple)
                    and len(node.target.elts) > 1
                ):
                    self._add_sequence_commas(
                        node.target.elts,
                        document,
                        line_offsets,
                        tokens
                    )

        tokens.sort(key=lambda t: t['index'])

        return self._deduplicate(tokens)


    def _add_sequence_commas(
        self,
        elements: list,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add tokens for commas between elements in a sequence."""
        for i in range(len(elements) - 1):
            left = elements[i]
            right = elements[i + 1]

            start = (
                line_offsets[left.end_lineno - 1]
                + left.end_col_offset
            )
            end = line_offsets[right.lineno - 1] + right.col_offset
            token = document[start:end]

            if "," not in token:
                continue

            if self._is_correct(token):
                continue

            tokens.append(
                {
                    "token": token,
                    "index": start,
                    "length": len(token)
                }
            )


    def _add_dict_commas(
        self,
        node: ast.Dict,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add tokens for commas between dict entries."""
        entries = []

        for key, value in zip(node.keys, node.values):
            if value.end_lineno is not None:
                entries.append(value)

        for i in range(len(entries) - 1):
            left = entries[i]
            right_key_idx = i + 1
            right_key = node.keys[right_key_idx]

            if right_key is None:
                right = entries[right_key_idx]
            else:
                right = right_key

            start = (
                line_offsets[left.end_lineno - 1]
                + left.end_col_offset
            )
            end = line_offsets[right.lineno - 1] + right.col_offset
            token = document[start:end]

            if "," not in token:
                continue

            if self._is_correct(token):
                continue

            tokens.append(
                {
                    "token": token,
                    "index": start,
                    "length": len(token)
                }
            )


    def _add_call_commas(
        self,
        node: ast.Call,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add tokens for commas between function call arguments."""
        all_args = self._get_call_args_ordered(node)

        for i in range(len(all_args) - 1):
            left = all_args[i]
            right = all_args[i + 1]

            start = line_offsets[left[0] - 1] + left[1]
            end = line_offsets[right[2] - 1] + right[3]
            token = document[start:end]

            if "," not in token:
                continue

            if self._is_correct(token):
                continue

            tokens.append(
                {
                    "token": token,
                    "index": start,
                    "length": len(token)
                }
            )


    def _add_funcdef_commas(
        self,
        node,
        document: str,
        line_offsets: list[int],
        tokens: list[TokenResult]
    ):
        """Add tokens for commas between function definition parameters."""
        all_params = self._get_funcdef_params(node)

        for i in range(len(all_params) - 1):
            left = all_params[i]
            right = all_params[i + 1]

            start = line_offsets[left[0] - 1] + left[1]
            end = line_offsets[right[2] - 1] + right[3]
            token = document[start:end]

            if "," not in token:
                continue

            if (
                ", *," in token
                or ",*," in token
                or token.strip().startswith("*,")
            ):
                continue

            if ", /," in token or ",/," in token:
                continue

            if self._is_correct(token):
                continue

            tokens.append(
                {
                    "token": token,
                    "index": start,
                    "length": len(token)
                }
            )


    def _get_call_args_ordered(
        self,
        node: ast.Call
    ) -> list[tuple[int, int, int, int]]:
        """Get ordered (end_line, end_col, start_line, start_col) for all call args."""
        items = []

        for arg in node.args:
            items.append(
                (
                    arg.end_lineno,
                    arg.end_col_offset,
                    arg.lineno,
                    arg.col_offset
                )
            )

        for kw in node.keywords:
            items.append(
                (
                    kw.value.end_lineno,
                    kw.value.end_col_offset,
                    kw.lineno,
                    kw.col_offset
                )
            )

        items.sort(key=lambda x: (x[2], x[3]))

        return items


    def _get_funcdef_params(self, node) -> list[tuple[int, int, int, int]]:
        items = []
        args = node.args
        num_defaults = len(args.defaults)
        num_kw_defaults = len(args.kw_defaults)

        for i, arg in enumerate(args.posonlyargs + args.args):
            default_idx = i - (len(args.posonlyargs) + len(args.args) - num_defaults)
            if default_idx >= 0 and default_idx < num_defaults:
                default = args.defaults[default_idx]
                items.append(
                    (
                        default.end_lineno,
                        default.end_col_offset,
                        arg.lineno,
                        arg.col_offset
                    )
                )
            else:
                items.append(
                    (
                        arg.end_lineno,
                        arg.end_col_offset,
                        arg.lineno,
                        arg.col_offset
                    )
                )

        for i, arg in enumerate(args.kwonlyargs):
            if i < num_kw_defaults and args.kw_defaults[i] is not None:
                default = args.kw_defaults[i]
                items.append(
                    (
                        default.end_lineno,
                        default.end_col_offset,
                        arg.lineno,
                        arg.col_offset
                    )
                )
            else:
                items.append(
                    (
                        arg.end_lineno,
                        arg.end_col_offset,
                        arg.lineno,
                        arg.col_offset
                    )
                )

        if args.vararg:
            items.append(
                (
                    args.vararg.end_lineno,
                    args.vararg.end_col_offset,
                    args.vararg.lineno,
                    args.vararg.col_offset - 1
                )
            )

        if args.kwarg:
            items.append(
                (
                    args.kwarg.end_lineno,
                    args.kwarg.end_col_offset,
                    args.kwarg.lineno,
                    args.kwarg.col_offset - 2
                )
            )

        items.sort(key=lambda x: (x[2], x[3]))

        return items


    def _is_correct(self, token: str) -> bool:
        comma_idx = token.index(",")
        before = token[:comma_idx]
        after = token[comma_idx + 1:]

        if before.strip():
            return False

        if before != "":
            return False

        if "\n" in after:
            stripped_after = after.lstrip(" \t")
            if stripped_after[0] == "\n" if stripped_after else False:
                return False

            return True

        if after == " ":
            return True

        return False


    def _deduplicate(self, tokens: list[TokenResult]) -> list[TokenResult]:
        seen = set()
        result = []

        for token in tokens:
            if token['index'] not in seen:
                seen.add(token['index'])
                result.append(token)

        return result


    def _build_line_offsets(self, document: str) -> list[int]:
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
