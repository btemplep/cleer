"""Python paired punctuation tokenizer module."""

__all__ = ["PythonPairedPunctuationTokenizer"]


import ast


from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonPairedPunctuationTokenizer(Tokenizer):
    """Tokenizes statements containing paired punctuation or logic conditions.

    Finds and emits full statement lines that contain paired punctuation
    (parentheses, brackets, braces) or logic conditions with `and`/`or`.

    Excludes `__all__` assignments, type hint annotations, and `for`
    loop unpacking variables.

    Examples
    --------

    ```python
    from cleer import PythonPairedPunctuationTokenizer

    tokenizer = PythonPairedPunctuationTokenizer()
    tokens = tokenizer.tokenize("say_hello(1, 2, 3)\\n")
    ```
    """
    emits_token_type = "python_paired_punctuation"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize statements containing paired punctuation.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results.
        """
        try:
            tree = ast.parse(document)
        except SyntaxError:
            return []

        lines = document.split("\n")
        line_offsets = self._compute_line_offsets(document)
        tokens = []
        seen_ranges = set()

        self._walk(tree, lines, line_offsets, document, tokens, seen_ranges)

        tokens.sort(key=lambda t: t["index"])

        return tokens


    def _walk(
        self,
        node,
        lines: list[str],
        line_offsets: list[int],
        document: str,
        tokens: list,
        seen_ranges: set
    ):
        """Walk AST to find paired punctuation regions."""
        for child in ast.iter_child_nodes(node):
            if self._is_excluded(child, node):
                continue

            emitted = False

            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if child.args.args or child.args.posonlyargs or child.args.kwonlyargs or child.args.vararg or child.args.kwarg:
                    self._emit_funcdef(
                        child, lines, line_offsets, document, tokens, seen_ranges
                    )
                    emitted = True

                if child.decorator_list:
                    for dec in child.decorator_list:
                        if isinstance(dec, ast.Call):
                            self._emit_decorator(
                                dec, lines, line_offsets, document, tokens, seen_ranges
                            )

                self._walk(child, lines, line_offsets, document, tokens, seen_ranges)

            elif isinstance(child, ast.ClassDef):
                if child.decorator_list:
                    for dec in child.decorator_list:
                        if isinstance(dec, ast.Call):
                            self._emit_decorator(
                                dec, lines, line_offsets, document, tokens, seen_ranges
                            )

                self._walk(child, lines, line_offsets, document, tokens, seen_ranges)

            elif isinstance(child, (ast.If, ast.While)):
                if self._is_logic_condition(child):
                    self._emit_condition(
                        child, lines, line_offsets, document, tokens, seen_ranges
                    )

                self._walk(child, lines, line_offsets, document, tokens, seen_ranges)

                if isinstance(child, ast.If) and child.orelse:
                    for orelse_child in child.orelse:
                        if isinstance(orelse_child, ast.If):
                            if self._is_logic_condition(orelse_child):
                                self._emit_condition(
                                    orelse_child, lines, line_offsets, document,
                                    tokens, seen_ranges
                                )
                            self._walk(
                                orelse_child, lines, line_offsets, document,
                                tokens, seen_ranges
                            )
                        else:
                            self._walk_single(
                                orelse_child, lines, line_offsets, document,
                                tokens, seen_ranges
                            )

            elif isinstance(child, ast.Expr) and isinstance(child.value, ast.Call):
                self._emit_statement(
                    child, lines, line_offsets, document, tokens, seen_ranges
                )

            elif isinstance(child, ast.Assign):
                if self._has_paired_punct_value(child):
                    self._emit_statement(
                        child, lines, line_offsets, document, tokens, seen_ranges
                    )
                    emitted = True

            elif isinstance(child, ast.AnnAssign):
                if child.value and self._node_has_paired_punct(child.value):
                    self._emit_statement(
                        child, lines, line_offsets, document, tokens, seen_ranges
                    )
                    emitted = True

            elif isinstance(child, ast.Return):
                if child.value and self._node_has_paired_punct(child.value):
                    self._emit_statement(
                        child, lines, line_offsets, document, tokens, seen_ranges
                    )
                    emitted = True

            elif isinstance(child, (ast.For, ast.AsyncFor)):
                self._walk(child, lines, line_offsets, document, tokens, seen_ranges)

            elif not emitted:
                self._walk(child, lines, line_offsets, document, tokens, seen_ranges)


    def _walk_single(
        self,
        node,
        lines: list[str],
        line_offsets: list[int],
        document: str,
        tokens: list,
        seen_ranges: set
    ):
        """Process a single node that may contain paired punctuation."""
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            self._emit_statement(
                node, lines, line_offsets, document, tokens, seen_ranges
            )
        elif isinstance(node, ast.Assign):
            if self._has_paired_punct_value(node):
                self._emit_statement(
                    node, lines, line_offsets, document, tokens, seen_ranges
                )
        elif isinstance(node, ast.Return):
            if node.value and self._node_has_paired_punct(node.value):
                self._emit_statement(
                    node, lines, line_offsets, document, tokens, seen_ranges
                )
        else:
            self._walk(node, lines, line_offsets, document, tokens, seen_ranges)


    def _is_excluded(self, child, parent) -> bool:
        """Check if a node should be excluded from tokenization."""
        if isinstance(child, ast.Assign):
            for target in child.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    return True

            if isinstance(child.value, ast.Subscript):
                return True

        if isinstance(child, ast.AnnAssign):
            if child.value is None:
                return True
            if isinstance(child.value, ast.Subscript):
                return True

        if isinstance(child, ast.Expr):
            if isinstance(child.value, ast.Subscript):
                return True

        return False


    def _is_logic_condition(self, node) -> bool:
        """Check if an if/while has a logic condition with and/or."""
        return isinstance(node.test, ast.BoolOp)


    def _has_paired_punct_value(self, node) -> bool:
        """Check if an assignment has a value with paired punctuation."""
        if isinstance(node, ast.Assign):
            value = node.value
        elif isinstance(node, ast.AnnAssign) and node.value:
            value = node.value
        else:
            return False

        return self._node_has_paired_punct(value)


    def _node_has_paired_punct(self, node) -> bool:
        """Check if an AST node contains paired punctuation."""
        if isinstance(node, (ast.Dict, ast.List, ast.Set, ast.Tuple, ast.Call)):
            return True

        if isinstance(node, ast.BoolOp):
            return True

        for child in ast.iter_child_nodes(node):
            if self._node_has_paired_punct(child):
                return True

        return False


    def _emit_funcdef(
        self,
        node,
        lines: list[str],
        line_offsets: list[int],
        document: str,
        tokens: list,
        seen_ranges: set
    ):
        """Emit a function definition line through its closing paren."""
        start_line = node.lineno - 1
        start_idx = line_offsets[start_line]

        end_line = self._find_funcdef_end(node, lines)
        if end_line + 1 < len(line_offsets):
            end_idx = line_offsets[end_line + 1]
        else:
            end_idx = len(document)

        token = document[start_idx:end_idx]

        if token.endswith("\n"):
            token = token[:-1]
            end_idx -= 1

        self._add_token(start_idx, token, tokens, seen_ranges)


    def _find_funcdef_end(self, node, lines: list[str]) -> int:
        """Find the line where the function def's colon is."""
        for line_idx in range(node.lineno - 1, min(node.end_lineno, len(lines))):
            line = lines[line_idx]
            stripped = line.rstrip()
            if stripped.endswith(":"):
                return line_idx

        return node.lineno - 1


    def _emit_decorator(
        self,
        dec_node,
        lines: list[str],
        line_offsets: list[int],
        document: str,
        tokens: list,
        seen_ranges: set
    ):
        """Emit a decorator call line."""
        start_line = dec_node.lineno - 1
        start_idx = line_offsets[start_line]

        end_line = dec_node.end_lineno - 1
        if end_line + 1 < len(line_offsets):
            end_idx = line_offsets[end_line + 1]
        else:
            end_idx = len(document)

        token = document[start_idx:end_idx]

        if token.endswith("\n"):
            token = token[:-1]
            end_idx -= 1

        self._add_token(start_idx, token, tokens, seen_ranges)


    def _emit_statement(
        self,
        node,
        lines: list[str],
        line_offsets: list[int],
        document: str,
        tokens: list,
        seen_ranges: set
    ):
        """Emit a full statement line."""
        start_line = node.lineno - 1
        start_idx = line_offsets[start_line]

        end_line = node.end_lineno - 1
        if end_line + 1 < len(line_offsets):
            end_idx = line_offsets[end_line + 1]
        else:
            end_idx = len(document)

        token = document[start_idx:end_idx]

        if token.endswith("\n"):
            token = token[:-1]
            end_idx -= 1

        self._add_token(start_idx, token, tokens, seen_ranges)


    def _emit_condition(
        self,
        node,
        lines: list[str],
        line_offsets: list[int],
        document: str,
        tokens: list,
        seen_ranges: set
    ):
        """Emit an if/elif/while condition line (up through the colon)."""
        start_line = node.lineno - 1
        start_idx = line_offsets[start_line]

        end_line = start_line
        for line_idx in range(start_line, len(lines)):
            stripped = lines[line_idx].rstrip()
            if stripped.endswith(":"):
                end_line = line_idx
                break

        if end_line + 1 < len(line_offsets):
            end_idx = line_offsets[end_line + 1]
        else:
            end_idx = len(document)

        token = document[start_idx:end_idx]

        if token.endswith("\n"):
            token = token[:-1]
            end_idx -= 1

        self._add_token(start_idx, token, tokens, seen_ranges)


    def _add_token(
        self,
        start_idx: int,
        token: str,
        tokens: list,
        seen_ranges: set
    ):
        """Add a token if it doesn't overlap with existing tokens."""
        end_idx = start_idx + len(token)
        token_range = (start_idx, end_idx)

        for seen_start, seen_end in seen_ranges:
            if start_idx < seen_end and end_idx > seen_start:
                return

        seen_ranges.add(token_range)
        tokens.append(
            {
                "token": token,
                "index": start_idx,
                "length": len(token)
            }
        )


    def _compute_line_offsets(self, document: str) -> list[int]:
        """Compute byte offsets for each line in the document."""
        offsets = [0]
        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
