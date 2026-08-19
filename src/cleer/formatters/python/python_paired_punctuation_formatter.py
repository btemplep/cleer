"""See [](#cleer.formatters.python.python_paired_punctuation_formatter.PythonPairedPunctuationFormatter)"""

__all__ = [
    "PythonPairedPunctuationFormatter"
]

import ast
import io
import re
import tokenize

from cleer.formatters.formatter import Formatter, FormatterViolation


class PythonPairedPunctuationFormatter(Formatter):
    """Format paired punctuation using AST for semantic understanding.

    Receives the entire file, parses it with AST, identifies all nodes
    that contain paired punctuation (calls, lists, dicts, logic expressions,
    etc.), and reformats them according to expansion/collapse rules.

    Processes nodes bottom-up so inner nodes are formatted before outer
    nodes make line-length decisions.

    Parameters
    ----------
    def_max_len : int, default=80
        Maximum flattened function definition length before expansion,
        excluding indent.
    def_max_line_len : int, default=100
        Maximum function definition length including indent before expansion.
    def_max_args : int, default=4
        Maximum number of function definition parameters before expansion.
    def_max_args_kw : int, default=2
        Maximum number of function definition parameters when defaults are
        present before expansion.
    call_max_len : int, default=60
        Maximum flattened call length before expansion, excluding indent.
        Also used for boolean expressions and individual chain segments.
    call_max_line_len : int, default=80
        Maximum call length including indent before expansion.
        Also used for boolean expressions.
    call_max_args : int, default=4
        Maximum number of call arguments before expansion.
        Also used for chain segments.
    call_max_args_kw : int, default=2
        Maximum number of call arguments when kwargs are present before
        expansion. Also used for chain segments.
    chain_call_max_len : int, default=80
        Maximum total flattened chain call length before expansion,
        excluding indent.
    chain_call_max_line_len : int, default=100
        Maximum total chain call length including indent before expansion.
    lst_max_len : int, default=30
        Maximum flattened container (list, set, tuple) literal length before
        expansion. Only includes the container itself.
    lst_max_line_len : int, default=80
        Maximum container length including indent before expansion.
    lst_max_num : int, default=3
        Maximum number of items in a list/set before expansion when inline
        within call arguments.
    annotation_max_len : int, default=40
        Maximum flattened type annotation length before expansion,
        excluding indent.
    annotation_max_line_len : int, default=80
        Maximum type annotation length including indent before expansion.
    annotation_max_depth : int, default=2
        Maximum bracket nesting depth in type annotations before expansion.
    """
    accepts_token_types = ["file"]


    def __init__(
        self,
        def_max_len: int=80,
        def_max_line_len: int=100,
        def_max_args: int=4,
        def_max_args_kw: int=2,
        call_max_len: int=60,
        call_max_line_len: int=80,
        call_max_args: int=4,
        call_max_args_kw: int=2,
        chain_call_max_len: int=80,
        chain_call_max_line_len: int=100,
        lst_max_len: int=30,
        lst_max_line_len: int=80,
        lst_max_num: int=3,
        annotation_max_len: int=40,
        annotation_max_line_len: int=80,
        annotation_max_depth: int=2,
        binop_max_len: int=60,
        binop_max_line_len: int=80,
        binop_max_operands: int=4
    ):
        self._def_max_len = def_max_len
        self._def_max_line_len = def_max_line_len
        self._def_max_args = def_max_args
        self._def_max_args_kw = def_max_args_kw
        self._call_max_len = call_max_len
        self._call_max_line_len = call_max_line_len
        self._call_max_args = call_max_args
        self._call_max_args_kw = call_max_args_kw
        self._chain_call_max_len = chain_call_max_len
        self._chain_call_max_line_len = chain_call_max_line_len
        self._lst_max_len = lst_max_len
        self._lst_max_line_len = lst_max_line_len
        self._lst_max_num = lst_max_num
        self._annotation_max_len = annotation_max_len
        self._annotation_max_line_len = annotation_max_line_len
        self._annotation_max_depth = annotation_max_depth
        self._binop_max_len = binop_max_len
        self._binop_max_line_len = binop_max_line_len
        self._binop_max_operands = binop_max_operands


    def inspect(self, token: str) -> list[FormatterViolation]:
        formatted = self.format(token)
        if formatted != token:
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": "Paired punctuation should be flattened first, then expanded based on length and argument thresholds. No space between openers/closers and inner values on the same line."
                }
            ]

        return []


    def format(self, token: str) -> str:
        """Format all paired punctuation in the document.

        Parameters
        ----------
        token : str
            The entire document.

        Returns
        -------
        str
            The reformatted document.
        """
        try:
            tree = ast.parse(token)
        except SyntaxError:
            return token

        self._line_offsets = self._build_line_offsets(token)
        nodes = self._collect_formattable_nodes(tree, token)

        if not nodes:
            return token

        doc = token

        for _ in range(10):
            try:
                tree = ast.parse(doc)
            except SyntaxError:
                break

            self._line_offsets = self._build_line_offsets(doc)
            nodes = self._collect_formattable_nodes(tree, doc)

            if not nodes:
                break

            nodes.sort(key=lambda n: (-n['depth'], -n['start']))

            changed = False

            for node_info in nodes:
                node = node_info['node']
                node_type = node_info['type']
                start = node_info['start']
                end = node_info['end']

                current_text = doc[start:end]
                indent = self._get_indent(doc, start)

                if node_type == "boolop":
                    formatted = self._format_boolop(node, current_text, indent)
                elif node_type == "if_boolop":
                    formatted = self._format_if_boolop(
                        node,
                        current_text,
                        indent,
                        node_info.get("parent_node")
                    )
                elif node_type == "assign_boolop":
                    formatted = self._format_assign_boolop(node, current_text, indent)
                elif node_type == "return_boolop":
                    formatted = self._format_return_boolop(node, current_text, indent)
                elif node_type == "call":
                    formatted = self._format_call(node, current_text, indent)
                elif node_type == "chain":
                    formatted = self._format_chain(node, current_text, indent)
                elif node_type in ("list", "set"):
                    formatted = self._format_container(
                        node,
                        current_text,
                        indent,
                        is_nested=node_info.get("is_nested", False)
                    )
                elif node_type == "dict":
                    formatted = self._format_dict(node, current_text, indent)
                elif node_type == "tuple":
                    formatted = self._format_tuple(node, current_text, indent)
                elif node_type == "funcdef":
                    formatted = self._format_funcdef(node, current_text, indent)
                elif node_type == "subscript":
                    formatted = self._format_subscript(node, current_text, indent)
                elif node_type == "dict_subscript":
                    formatted = self._format_dict_subscript(node, current_text, indent)
                elif node_type == "string_concat":
                    formatted = self._format_string_concat(node, current_text, indent)
                elif node_type == "binop":
                    formatted = self._format_binop(
                        node,
                        current_text,
                        indent,
                        node_info.get("parent_node")
                    )
                elif node_type == "compare":
                    formatted = self._format_binop(
                        node,
                        current_text,
                        indent,
                        node_info.get("parent_node")
                    )
                else:
                    continue

                if formatted != current_text:
                    size_diff = len(formatted) - len(current_text)
                    doc = doc[:start] + formatted + doc[end:]
                    changed = True

                    for other in nodes:
                        if other is node_info:
                            continue

                        if other['start'] > start:
                            other['start'] += size_diff
                            other['end'] += size_diff
                        elif other['end'] > start:
                            other['end'] += size_diff

            if not changed:
                break

        doc = self._collapse_inline_spaces(doc)
        doc = self._collapse_short_parens(doc)
        doc = self._normalize_paren_indent(doc)

        return doc


    def _collect_formattable_nodes(
        self,
        tree: ast.Module,
        document: str
    ) -> list[dict]:
        """Walk the AST and collect nodes that need formatting decisions."""
        nodes = []
        self._walk(
            tree,
            document,
            nodes,
            depth=0,
            parent=None
        )

        return nodes


    def _walk(
        self,
        node: ast.AST,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        for child in ast.iter_child_nodes(node):
            child._cleer_grandparent = parent

            if self._is_comprehension_node(child):
                continue

            self._walk(
                child,
                document,
                nodes,
                depth + 1,
                parent=node
            )

        if isinstance(node, ast.BoolOp):
            self._add_boolop(
                node,
                document,
                nodes,
                depth,
                parent
            )
        elif isinstance(node, ast.Assign):
            if isinstance(node.value, ast.BoolOp):
                self._add_assign_boolop(node, document, nodes, depth)
            elif (
                isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                self._add_string_concat(node, document, nodes, depth)

        elif isinstance(node, ast.Return):
            if node.value and isinstance(node.value, ast.BoolOp):
                self._add_return_boolop(node, document, nodes, depth)
            elif (
                node.value
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                self._add_string_concat(node, document, nodes, depth)

        elif isinstance(node, ast.Call):
            if self._is_chain_end(node, parent):
                self._add_chain(
                    node,
                    document,
                    nodes,
                    depth,
                    parent
                )
            else:
                self._add_call(
                    node,
                    document,
                    nodes,
                    depth,
                    parent
                )

        elif isinstance(node, (ast.List, ast.Set)):
            self._add_container(
                node,
                document,
                nodes,
                depth,
                parent
            )
        elif isinstance(node, ast.Dict):
            self._add_dict(
                node,
                document,
                nodes,
                depth,
                parent
            )
        elif isinstance(node, ast.Tuple):
            self._add_tuple(
                node,
                document,
                nodes,
                depth,
                parent
            )
        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef
            )
        ):
            self._add_funcdef(
                node,
                document,
                nodes,
                depth,
                parent
            )
        elif isinstance(node, ast.Subscript):
            self._add_subscript(
                node,
                document,
                nodes,
                depth,
                parent
            )
        elif isinstance(node, ast.BinOp):
            self._add_binop(
                node,
                document,
                nodes,
                depth,
                parent
            )
        elif isinstance(node, ast.Compare):
            self._add_compare(
                node,
                document,
                nodes,
                depth,
                parent
            )


    def _add_boolop(
        self,
        node: ast.BoolOp,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        if not hasattr(node, "lineno"):
            return

        if isinstance(parent, ast.BoolOp):
            return

        if isinstance(parent, ast.Assign):
            return

        if isinstance(parent, ast.Return):
            return

        if isinstance(parent, (ast.If, ast.While)):
            if node is parent.test:
                stmt_start = self._offset(document, parent.lineno, parent.col_offset)
                lines = document.split("\n")
                stmt_line_idx = parent.lineno - 1
                for li in range(stmt_line_idx, len(lines)):
                    if lines[li].rstrip().endswith(":"):
                        end = (
                            self._offset(document, li + 1, 0)
                            + len(lines[li].rstrip())
                        )
                        break

                else:
                    end = self._offset(document, node.end_lineno, node.end_col_offset)

                nodes.append(
                    {
                        "node": node,
                        "type": "if_boolop",
                        "start": stmt_start,
                        "end": end,
                        "depth": depth,
                        "parent_node": parent
                    }
                )

                return

        if (
            isinstance(parent, ast.UnaryOp)
            and isinstance(parent.op, ast.Not)
            and hasattr(node, "_cleer_grandparent")
            and isinstance(node._cleer_grandparent, (ast.If, ast.While))
            and parent is node._cleer_grandparent.test
        ):
            grandparent = node._cleer_grandparent
            stmt_start = self._offset(
                document,
                grandparent.lineno,
                grandparent.col_offset
            )
            lines = document.split("\n")
            stmt_line_idx = grandparent.lineno - 1
            for li in range(stmt_line_idx, len(lines)):
                if lines[li].rstrip().endswith(":"):
                    end = (
                        self._offset(document, li + 1, 0)
                        + len(lines[li].rstrip())
                    )
                    break

            else:
                end = self._offset(document, node.end_lineno, node.end_col_offset)

            nodes.append(
                {
                    "node": node,
                    "type": "if_boolop",
                    "start": stmt_start,
                    "end": end,
                    "depth": depth,
                    "parent_node": grandparent
                }
            )

            return

        start = self._offset(document, node.lineno, node.col_offset)
        end = self._offset(document, node.end_lineno, node.end_col_offset)

        nodes.append(
            {
                "node": node,
                "type": "boolop",
                "start": start,
                "end": end,
                "depth": depth
            }
        )


    def _add_assign_boolop(
        self,
        node: ast.Assign,
        document: str,
        nodes: list,
        depth: int
    ):
        """Add an assignment whose value is a BoolOp."""
        if not hasattr(node, "lineno"):
            return

        start = self._offset(document, node.lineno, node.col_offset)
        end = self._offset(document, node.end_lineno, node.end_col_offset)

        nodes.append(
            {
                "node": node,
                "type": "assign_boolop",
                "start": start,
                "end": end,
                "depth": depth
            }
        )


    def _add_return_boolop(
        self,
        node: ast.Return,
        document: str,
        nodes: list,
        depth: int
    ):
        """Add a return statement whose value is a BoolOp."""
        if not hasattr(node, "lineno"):
            return

        start = self._offset(document, node.lineno, node.col_offset)
        end = self._offset(document, node.end_lineno, node.end_col_offset)

        nodes.append(
            {
                "node": node,
                "type": "return_boolop",
                "start": start,
                "end": end,
                "depth": depth
            }
        )


    def _add_string_concat(
        self,
        node: ast.AST,
        document: str,
        nodes: list,
        depth: int
    ):
        """Add a statement containing implicit string concatenation."""
        if not hasattr(node, "lineno"):
            return

        start = self._offset(document, node.lineno, node.col_offset)
        end = self._offset(document, node.end_lineno, node.end_col_offset)

        text = document[start:end]
        if "(" not in text:
            return

        paren_start = text.find("(")
        paren_end = self._find_matching_paren(text, paren_start)
        if paren_end is None:
            return

        content = text[paren_start + 1:paren_end].strip()
        if not self._is_string_concat(content):
            return

        nodes.append(
            {
                "node": node,
                "type": "string_concat",
                "start": start,
                "end": end,
                "depth": depth
            }
        )


    def _add_chain(
        self,
        node: ast.Call,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        """Add a chained call node (outermost call of a chain)."""
        root = self._get_chain_root(node)
        if not hasattr(root, "lineno"):
            return

        start = self._offset(document, root.lineno, root.col_offset)
        end = self._offset(document, node.end_lineno, node.end_col_offset)

        nodes.append(
            {
                "node": node,
                "type": "chain",
                "start": start,
                "end": end,
                "depth": depth
            }
        )


    def _get_chain_root(self, node: ast.Call) -> ast.AST:
        current = node

        while True:
            if isinstance(current.func, ast.Attribute):
                if isinstance(current.func.value, ast.Call):
                    current = current.func.value
                else:
                    return current.func.value

            else:
                return current


    def _add_call(
        self,
        node: ast.Call,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        """Add a Call node for formatting."""
        if not node.args and not node.keywords:
            return

        if not hasattr(node, "lineno"):
            return

        if self._is_chained_method(node):
            return

        if self._is_chain_root(node, parent):
            return

        start = self._offset(document, node.lineno, node.col_offset)
        end = self._offset(document, node.end_lineno, node.end_col_offset)

        nodes.append(
            {
                "node": node,
                "type": "call",
                "start": start,
                "end": end,
                "depth": depth
            }
        )


    def _add_container(
        self,
        node: ast.AST,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        """Add a List or Set node for formatting."""
        if not hasattr(node, "lineno"):
            return

        elts = getattr(node, "elts", [])
        if not elts:
            return

        if isinstance(parent, (ast.For, ast.AsyncFor)):
            return

        if isinstance(parent, ast.Assign):
            for target in parent.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    return

        start = self._offset(document, node.lineno, node.col_offset)
        end = self._offset(document, node.end_lineno, node.end_col_offset)

        is_nested = isinstance(
            parent,
            (
                ast.Dict,
                ast.List,
                ast.Set,
                ast.Tuple
            )
        )

        nodes.append(
            {
                "node": node,
                "type": "list" if isinstance(node, ast.List) else "set",
                "start": start,
                "end": end,
                "depth": depth,
                "is_nested": is_nested
            }
        )


    def _add_dict(
        self,
        node: ast.Dict,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        """Add a Dict node for formatting."""
        if not hasattr(node, "lineno"):
            return

        if not node.keys:
            return

        start = self._offset(document, node.lineno, node.col_offset)
        end = self._offset(document, node.end_lineno, node.end_col_offset)

        nodes.append(
            {
                "node": node,
                "type": "dict",
                "start": start,
                "end": end,
                "depth": depth
            }
        )


    def _add_tuple(
        self,
        node: ast.Tuple,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        """Add a Tuple node for formatting."""
        if not hasattr(node, "lineno"):
            return

        if not node.elts:
            return

        if isinstance(parent, ast.Subscript):
            return

        start = self._offset(document, node.lineno, node.col_offset)
        end = self._offset(document, node.end_lineno, node.end_col_offset)

        nodes.append(
            {
                "node": node,
                "type": "tuple",
                "start": start,
                "end": end,
                "depth": depth
            }
        )


    def _add_funcdef(
        self,
        node: ast.AST,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        """Add a FunctionDef node for formatting (args only)."""
        if not hasattr(node, "lineno"):
            return

        args = node.args
        total_args = (
            len(args.posonlyargs)
            + len(args.args)
            + len(args.kwonlyargs)
            + (1 if args.vararg else 0)
            + (1 if args.kwarg else 0)
        )

        if total_args == 0:
            return

        start = self._offset(document, node.lineno, node.col_offset)
        body_start_line = node.body[0].lineno if node.body else node.end_lineno
        sig_end = self._find_colon_line(
            document,
            node.lineno,
            body_start_line
        )

        nodes.append(
            {
                "node": node,
                "type": "funcdef",
                "start": start,
                "end": sig_end,
                "depth": depth
            }
        )


    def _add_subscript(
        self,
        node: ast.Subscript,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        if not hasattr(node, "lineno"):
            return

        is_dict_sub = self._is_dict_subscript(node)

        if is_dict_sub:
            if (
                isinstance(parent, ast.Subscript)
                and self._is_dict_subscript(parent)
            ):
                return

            start = self._offset(document, node.lineno, node.col_offset)
            end = self._offset(document, node.end_lineno, node.end_col_offset)
            nodes.append(
                {
                    "node": node,
                    "type": "dict_subscript",
                    "start": start,
                    "end": end,
                    "depth": depth
                }
            )
        else:
            start = self._offset(document, node.lineno, node.col_offset)
            end = self._offset(document, node.end_lineno, node.end_col_offset)
            nodes.append(
                {
                    "node": node,
                    "type": "subscript",
                    "start": start,
                    "end": end,
                    "depth": depth
                }
            )


    def _add_binop(
        self,
        node: ast.BinOp,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        if not hasattr(node, "lineno"):
            return

        if isinstance(parent, ast.BinOp):
            return

        if isinstance(parent, ast.Compare):
            return

        if isinstance(parent, ast.BoolOp):
            return

        if (
            isinstance(parent, (ast.If, ast.While))
            and node is parent.test
        ):
            start = self._offset(document, parent.lineno, parent.col_offset)
            lines = document.split("\n")
            stmt_line_idx = parent.lineno - 1
            end = None
            for li in range(stmt_line_idx, len(lines)):
                if lines[li].rstrip().endswith(":"):
                    end = (
                        self._offset(document, li + 1, 0)
                        + len(lines[li].rstrip())
                    )
                    break

            if end is None:
                end = self._offset(document, node.end_lineno, node.end_col_offset)

            nodes.append(
                {
                    "node": node,
                    "type": "binop",
                    "start": start,
                    "end": end,
                    "depth": depth,
                    "parent_node": parent
                }
            )
        elif (
            isinstance(parent, ast.Assign)
            and node is parent.value
        ):
            start = self._offset(document, parent.lineno, parent.col_offset)
            end = self._offset(
                document,
                parent.end_lineno,
                parent.end_col_offset
            )
            nodes.append(
                {
                    "node": node,
                    "type": "binop",
                    "start": start,
                    "end": end,
                    "depth": depth,
                    "parent_node": parent
                }
            )
        elif (
            isinstance(parent, ast.Return)
            and node is parent.value
        ):
            start = self._offset(document, parent.lineno, parent.col_offset)
            end = self._offset(
                document,
                parent.end_lineno,
                parent.end_col_offset
            )
            nodes.append(
                {
                    "node": node,
                    "type": "binop",
                    "start": start,
                    "end": end,
                    "depth": depth,
                    "parent_node": parent
                }
            )
        elif isinstance(parent, ast.Expr) and node is parent.value:
            start = self._offset(document, parent.lineno, parent.col_offset)
            end = self._offset(
                document,
                parent.end_lineno,
                parent.end_col_offset
            )
            nodes.append(
                {
                    "node": node,
                    "type": "binop",
                    "start": start,
                    "end": end,
                    "depth": depth,
                    "parent_node": parent
                }
            )


    def _add_compare(
        self,
        node: ast.Compare,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        if not hasattr(node, "lineno"):
            return

        if isinstance(parent, ast.BoolOp):
            return

        if (
            isinstance(parent, (ast.If, ast.While))
            and node is parent.test
        ):
            start = self._offset(document, parent.lineno, parent.col_offset)
            lines = document.split("\n")
            stmt_line_idx = parent.lineno - 1
            end = None
            for li in range(stmt_line_idx, len(lines)):
                if lines[li].rstrip().endswith(":"):
                    end = (
                        self._offset(document, li + 1, 0)
                        + len(lines[li].rstrip())
                    )
                    break

            if end is None:
                end = self._offset(document, node.end_lineno, node.end_col_offset)

            nodes.append(
                {
                    "node": node,
                    "type": "compare",
                    "start": start,
                    "end": end,
                    "depth": depth,
                    "parent_node": parent
                }
            )
        elif (
            isinstance(parent, ast.Assign)
            and node is parent.value
        ):
            start = self._offset(document, parent.lineno, parent.col_offset)
            end = self._offset(
                document,
                parent.end_lineno,
                parent.end_col_offset
            )
            nodes.append(
                {
                    "node": node,
                    "type": "compare",
                    "start": start,
                    "end": end,
                    "depth": depth,
                    "parent_node": parent
                }
            )
        elif (
            isinstance(parent, ast.Return)
            and node is parent.value
        ):
            start = self._offset(document, parent.lineno, parent.col_offset)
            end = self._offset(
                document,
                parent.end_lineno,
                parent.end_col_offset
            )
            nodes.append(
                {
                    "node": node,
                    "type": "compare",
                    "start": start,
                    "end": end,
                    "depth": depth,
                    "parent_node": parent
                }
            )
        elif isinstance(parent, ast.Expr) and node is parent.value:
            start = self._offset(document, parent.lineno, parent.col_offset)
            end = self._offset(
                document,
                parent.end_lineno,
                parent.end_col_offset
            )
            nodes.append(
                {
                    "node": node,
                    "type": "compare",
                    "start": start,
                    "end": end,
                    "depth": depth,
                    "parent_node": parent
                }
            )


    def _is_dict_subscript(self, node: ast.Subscript) -> bool:
        if isinstance(node.slice, ast.Tuple):
            return False

        if isinstance(node.slice, ast.Subscript):
            if not self._is_dict_subscript(node.slice):
                return False

        return True


    def _format_boolop(
        self,
        node: ast.BoolOp,
        current_text: str,
        indent: str
    ) -> str:
        """Format a BoolOp (and/or expression).

        This handles standalone BoolOps (in assignments, returns, etc.)
        The parent context provides the wrapping parens.
        """
        if self._has_comment(current_text):
            return current_text

        op_str = "or" if isinstance(node.op, ast.Or) else "and"
        num_parts = len(node.values)

        flat = self._flatten(current_text)
        flat_len = len(flat)
        indent_len = len(indent)

        should_expand = (
            num_parts > 2
            or flat_len > self._call_max_len
            or flat_len + indent_len > self._call_max_line_len
        )

        if not should_expand:
            return flat

        inner_indent = indent + "    "
        parts = self._split_boolop_by_op(flat, op_str)

        if not parts:
            return flat

        lines = []
        for i, part in enumerate(parts):
            if i == 0:
                lines.append(f"{indent}{part}")
            else:
                lines.append(f"{indent}{op_str} {part}")

        return "\n".join(lines)


    def _get_boolop_parts(self, node: ast.BoolOp, current_text: str) -> list[str]:
        flat = self._flatten(current_text)
        op_str = "or" if isinstance(node.op, ast.Or) else "and"

        parts = []
        remaining = flat
        op_pattern = f" {op_str} "

        depth = 0
        in_string = False
        string_char = ""
        i = 0
        last_split = 0

        while i < len(remaining):
            ch = remaining[i]

            if not in_string:
                if ch in ('"', "'"):
                    if remaining[i:i + 3] in ('"""', "'''"):
                        in_string = True
                        string_char = remaining[i:i + 3]
                        i += 3
                        continue
                    else:
                        in_string = True
                        string_char = ch
                        i += 1
                        continue

                if ch in "([{":
                    depth += 1
                elif ch in ")]}":
                    depth -= 1
                elif (
                    depth == 0
                    and remaining[i:i + len(op_pattern)] == op_pattern
                ):
                    parts.append(remaining[last_split:i].strip())
                    i += len(op_pattern)
                    last_split = i
                    continue

            else:
                if (
                    len(string_char) == 3
                    and remaining[i:i + 3] == string_char
                ):
                    in_string = False
                    i += 3
                    continue
                elif (
                    len(string_char) == 1
                    and ch == string_char
                    and self._is_closing_quote(remaining, i)
                ):
                    in_string = False

            i += 1

        if last_split < len(remaining):
            parts.append(remaining[last_split:].strip())

        return parts


    def _is_subgroup_boolop(self, value_node: ast.AST, parent_op) -> bool:
        if isinstance(value_node, ast.BoolOp):
            return type(value_node.op) != type(parent_op)

        return False


    def _format_boolop_subgroup(
        self,
        node: ast.BoolOp,
        part_text: str,
        indent: str,
        parent_op: str
    ) -> str:
        """Format a sub-BoolOp (mixed precedence) with wrapping parens."""
        inner_op = "or" if isinstance(node.op, ast.Or) else "and"
        inner_indent = indent + "    "

        stripped = part_text.strip()
        if stripped.startswith("(") and stripped.endswith(")"):
            inner_content = stripped[1:-1].strip()
        else:
            inner_content = stripped

        inner_content = self._normalize_operators(inner_content)

        sub_parts = []
        remaining = inner_content
        op_pattern = f" {inner_op} "
        depth = 0
        in_string = False
        string_char = ""
        i = 0
        last_split = 0

        while i < len(remaining):
            ch = remaining[i]

            if not in_string:
                if ch in ('"', "'"):
                    in_string = True
                    string_char = ch
                    i += 1
                    continue

                if ch in "([{":
                    depth += 1
                elif ch in ")]}":
                    depth -= 1
                elif (
                    depth == 0
                    and remaining[i:i + len(op_pattern)] == op_pattern
                ):
                    sub_parts.append(remaining[last_split:i].strip())
                    i += len(op_pattern)
                    last_split = i
                    continue

            else:
                if (
                    ch == string_char
                    and self._is_closing_quote(remaining, i)
                ):
                    in_string = False

            i += 1

        if last_split < len(remaining):
            sub_parts.append(remaining[last_split:].strip())

        if len(sub_parts) <= 1:
            return f"({inner_content})"

        lines = ["("]
        for j, sp in enumerate(sub_parts):
            prefix = "" if j == 0 else f"{inner_op} "
            if self._is_subgroup_inner_boolop(sp):
                inner_sub = self._expand_inner_subgroup(sp, inner_indent, inner_op)
                lines.append(f"{inner_indent}{prefix}{inner_sub}")
            else:
                lines.append(f"{inner_indent}{prefix}{sp}")

        lines.append(f"{indent})")

        return "\n".join(lines)


    def _is_subgroup_inner_boolop(self, part: str) -> bool:
        stripped = part.strip()
        if (
            not stripped.startswith("(")
            or not stripped.endswith(")")
        ):
            return False

        inner = stripped[1:-1].strip()
        if " or " in inner or " and " in inner:
            return True

        return False


    def _expand_inner_subgroup(self, part: str, indent: str, op_str: str) -> str:
        stripped = part.strip()
        inner = stripped[1:-1].strip()
        inner_indent = indent + "    "

        inner_op = None
        if " or " in inner:
            inner_op = "or"
        elif " and " in inner:
            inner_op = "and"

        if not inner_op:
            return part

        sub_parts = self._split_boolop_by_op(inner, inner_op)

        if len(sub_parts) <= 1:
            return part

        lines = ["("]
        for j, sp in enumerate(sub_parts):
            if j == 0:
                lines.append(f"{inner_indent}{sp}")
            else:
                lines.append(f"{inner_indent}{inner_op} {sp}")

        lines.append(f"{indent})")

        return "\n".join(lines)


    def _call_should_expand_in_boolop(self, part: str) -> bool:
        paren_start = part.find("(")
        if paren_start == -1:
            return False

        paren_end = self._find_matching_paren(part, paren_start)
        if paren_end is None:
            return False

        args_str = part[paren_start + 1:paren_end]
        args = self._split_by_commas(args_str)

        if not args:
            return False

        has_kwargs = any(self._is_kwarg_str(a) for a in args)

        if has_kwargs and len(args) > self._call_max_args_kw:
            return True

        if len(args) > self._call_max_args:
            return True

        for a in args:
            stripped = a.strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                inner = stripped[1:-1].strip()
                if inner:
                    return True

            if stripped.startswith("[") and stripped.endswith("]"):
                inner = stripped[1:-1].strip()
                items = self._split_by_commas(inner)
                if len(items) > 1:
                    return True

        content_len = len(part)
        if content_len > self._call_max_len:
            any_complex = any("{" in a or "[" in a or "(" in a for a in args)
            if any_complex or has_kwargs:
                return True

        return False


    def _expand_call_in_boolop(self, part: str, indent: str) -> str:
        paren_start = part.find("(")
        if paren_start == -1:
            return part

        paren_end = self._find_matching_paren(part, paren_start)
        if paren_end is None:
            return part

        func_name = part[:paren_start]
        args_str = part[paren_start + 1:paren_end]
        suffix = part[paren_end + 1:]
        args = self._split_by_commas(args_str)

        inner_indent = indent + "    "
        lines = [f"{func_name}("]

        for i, arg in enumerate(args):
            comma = "," if i < len(args) - 1 else ""
            arg_stripped = arg.strip()
            if "{" in arg_stripped and "}" in arg_stripped:
                expanded_arg = self._try_expand_dict_arg(arg_stripped, inner_indent)
                if expanded_arg:
                    lines.append(f"{inner_indent}{expanded_arg}{comma}")
                else:
                    lines.append(f"{inner_indent}{arg_stripped}{comma}")

            else:
                lines.append(f"{inner_indent}{arg_stripped}{comma}")

        lines.append(f"{indent}){suffix}")

        return "\n".join(lines)


    def _try_expand_dict_arg(self, arg: str, indent: str) -> str | None:
        stripped = arg.strip()
        if (
            not stripped.startswith("{")
            or not stripped.endswith("}")
        ):
            return None

        inner = stripped[1:-1].strip()
        items = self._split_by_commas(inner)

        if not items or len(items) < 1:
            return None

        inner_indent = indent + "    "
        lines = ["{"]
        for i, item in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            lines.append(f"{inner_indent}{item.strip()}{comma}")

        lines.append(f"{indent}}}")

        return "\n".join(lines)


    def _format_if_boolop(
        self,
        node: ast.BoolOp,
        current_text: str,
        indent: str,
        parent_node: ast.AST
    ) -> str:
        """Format a BoolOp that is the condition of if/elif/while."""
        if self._has_comment(current_text):
            return current_text

        flat = self._flatten(current_text)
        flat_len = len(flat)
        indent_len = len(indent)

        op_str = "or" if isinstance(node.op, ast.Or) else "and"
        num_parts = len(node.values)

        should_expand = (
            num_parts > 2
            or flat_len > self._call_max_len
            or flat_len + indent_len > self._call_max_line_len
        )

        if not should_expand:
            return flat

        if "\n" in current_text:
            first_line = current_text.split("\n")[0].strip()
            last_line = current_text.split("\n")[-1].strip()
            if first_line.endswith("(") and last_line == "):":
                inner_indent = indent + "    "
                inner_text = "\n".join(current_text.split("\n")[1:-1])
                has_bad_indent = False
                paren_depth = 0
                for line in current_text.split("\n")[1:-1]:
                    stripped = line.strip()
                    if not stripped:
                        continue

                    if paren_depth == 0:
                        leading = len(line) - len(line.lstrip())
                        if leading != len(inner_indent):
                            has_bad_indent = True
                            break

                    if stripped.endswith("("):
                        paren_depth += 1

                    if stripped in (")", "),", "):", "),"):
                        paren_depth -= 1

                if has_bad_indent:
                    pass
                else:
                    has_bad_ops = (
                        "or(" in inner_text
                        or ")or " in inner_text
                        or "and(" in inner_text
                        or ")and " in inner_text
                    )
                    if not has_bad_ops:
                        for line in current_text.split("\n")[1:-1]:
                            stripped = line.strip()
                            if not stripped:
                                continue

                            if f" {op_str} " in stripped:
                                idx = stripped.find(f" {op_str} ")
                                after = stripped[idx + len(op_str) + 2:]
                                if after and not after.startswith("("):
                                    has_bad_ops = True
                                    break

                    if not has_bad_ops:
                        other_op = "and" if op_str == "or" else "or"
                        for line in current_text.split("\n")[1:-1]:
                            stripped = line.strip()
                            if not stripped:
                                continue

                            if f" {other_op} " in stripped:
                                if not stripped.startswith(f"{other_op} "):
                                    has_bad_ops = True
                                    break

                    if not has_bad_ops:
                        return current_text

        keyword = "if"
        if isinstance(parent_node, ast.While):
            keyword = "while"
        elif isinstance(parent_node, ast.If):
            lines = current_text.split("\n")
            first_stripped = lines[0].strip()
            if first_stripped.startswith("elif"):
                keyword = "elif"

        has_not = (
            isinstance(parent_node.test, ast.UnaryOp)
            and isinstance(parent_node.test.op, ast.Not)
        )
        keyword_prefix = f"{keyword} not" if has_not else keyword

        inner_indent = indent + "    "
        parts = self._get_boolop_parts(node, current_text)

        if not parts:
            return current_text

        condition_flat = self._flatten(current_text)
        condition_flat = self._collapse_paren_spaces(condition_flat)
        kw_end = (
            condition_flat.find(keyword_prefix)
            + len(keyword_prefix)
        )
        after_kw = condition_flat[kw_end:].strip()
        if after_kw.startswith("(") and after_kw.endswith("):"):
            after_kw = after_kw[1:-2].strip()

        if after_kw.endswith(":"):
            after_kw = after_kw[:-1].strip()

        after_kw = self._normalize_operators(after_kw)
        cond_parts = self._split_boolop_by_op(after_kw, op_str)

        if not cond_parts:
            return current_text

        result_lines = [f"{keyword_prefix} ("]

        for i, part in enumerate(cond_parts):
            prefix = "" if i == 0 else f"{op_str} "
            ast_value = node.values[i] if i < len(node.values) else None

            if (
                ast_value
                and self._is_subgroup_boolop(ast_value, node.op)
            ):
                sub_formatted = self._format_boolop_subgroup(
                    ast_value,
                    part,
                    inner_indent,
                    op_str
                )
                result_lines.append(f"{inner_indent}{prefix}{sub_formatted}")
            elif (
                ast_value
                and isinstance(ast_value, ast.Call)
                and self._call_should_expand_in_boolop(part)
            ):
                expanded = self._expand_call_in_boolop(part, inner_indent)
                result_lines.append(f"{inner_indent}{prefix}{expanded}")
            else:
                result_lines.append(f"{inner_indent}{prefix}{part}")

        result_lines.append(f"{indent}):")

        return "\n".join(result_lines)


    def _split_boolop_by_op(self, text: str, op_str: str) -> list[str]:
        parts = []
        op_pattern = f" {op_str} "
        depth = 0
        in_string = False
        string_char = ""
        i = 0
        last_split = 0

        while i < len(text):
            ch = text[i]

            if not in_string:
                if ch in ('"', "'"):
                    if text[i:i + 3] in ('"""', "'''"):
                        in_string = True
                        string_char = text[i:i + 3]
                        i += 3
                        continue
                    else:
                        in_string = True
                        string_char = ch
                        i += 1
                        continue

                if ch in "([{":
                    depth += 1
                elif ch in ")]}":
                    depth -= 1
                elif (
                    depth == 0
                    and text[i:i + len(op_pattern)] == op_pattern
                ):
                    parts.append(text[last_split:i].strip())
                    i += len(op_pattern)
                    last_split = i
                    continue

            else:
                if len(string_char) == 3 and text[i:i + 3] == string_char:
                    in_string = False
                    i += 3
                    continue
                elif (
                    len(string_char) == 1
                    and ch == string_char
                    and self._is_closing_quote(text, i)
                ):
                    in_string = False

            i += 1

        if last_split < len(text):
            parts.append(text[last_split:].strip())

        return parts


    def _format_assign_boolop(
        self,
        node: ast.Assign,
        current_text: str,
        indent: str
    ) -> str:
        """Format an assignment whose value is a BoolOp."""
        if self._has_comment(current_text):
            return current_text

        boolop = node.value
        op_str = "or" if isinstance(boolop.op, ast.Or) else "and"
        num_parts = len(boolop.values)

        flat = self._flatten(current_text)
        flat_len = len(flat)
        indent_len = len(indent)

        should_expand = (
            num_parts > 2
            or flat_len > self._call_max_len
            or flat_len + indent_len > self._call_max_line_len
        )

        if not should_expand:
            return flat

        if "\n" in current_text:
            first_line = current_text.split("\n")[0].strip()
            last_line = current_text.split("\n")[-1].strip()
            if first_line.endswith("(") and last_line == ")":
                has_unexpanded_inner = False
                inner_indent = indent + "    "
                for line in current_text.split("\n")[1:-1]:
                    stripped = line.strip()
                    if (
                        stripped.startswith(f"{op_str} (")
                        or stripped.startswith("(")
                    ):
                        paren_content = stripped[stripped.index("("):]
                        if (
                            paren_content.endswith(")")
                            and (
                                f" {op_str} " in paren_content
                                or " and " in paren_content
                                or " or " in paren_content
                            )
                            and len(paren_content) > self._call_max_len
                        ):
                            has_unexpanded_inner = True
                            break

                if not has_unexpanded_inner:
                    return current_text

        eq_pos = flat.find("=")
        if eq_pos == -1:
            return current_text

        prefix = flat[:eq_pos + 1].rstrip()
        value_text = flat[eq_pos + 1:].strip()

        if value_text.startswith("(") and value_text.endswith(")"):
            inner = value_text[1:-1].strip()
        else:
            inner = value_text

        inner_indent = indent + "    "
        parts = self._split_boolop_by_op(inner, op_str)

        if not parts:
            return current_text

        lines = [f"{prefix} ("]

        for i, part in enumerate(parts):
            op_prefix = "" if i == 0 else f"{op_str} "
            if (
                part.startswith("(")
                and part.endswith(")")
                and (
                    " and " in part
                    or " or " in part
                )
                and len(part) > self._call_max_len
            ):
                inner_op = "and" if " and " in part else "or"
                inner_content = part[1:-1].strip()
                sub_parts = self._split_boolop_by_op(inner_content, inner_op)
                if sub_parts and len(sub_parts) > 1:
                    sub_indent = inner_indent + "    "
                    lines.append(f"{inner_indent}{op_prefix}(")
                    for j, sp in enumerate(sub_parts):
                        sub_prefix = "" if j == 0 else f"{inner_op} "
                        lines.append(f"{sub_indent}{sub_prefix}{sp}")

                    lines.append(f"{inner_indent})")
                else:
                    lines.append(f"{inner_indent}{op_prefix}{part}")

            else:
                lines.append(f"{inner_indent}{op_prefix}{part}")

        lines.append(f"{indent})")

        return "\n".join(lines)


    def _format_return_boolop(
        self,
        node: ast.Return,
        current_text: str,
        indent: str
    ) -> str:
        """Format a return statement whose value is a BoolOp."""
        if self._has_comment(current_text):
            return current_text

        boolop = node.value
        op_str = "or" if isinstance(boolop.op, ast.Or) else "and"
        num_parts = len(boolop.values)

        flat = self._flatten(current_text)
        flat_len = len(flat)
        indent_len = len(indent)

        should_expand = (
            num_parts > 2
            or flat_len > self._call_max_len
            or flat_len + indent_len > self._call_max_line_len
        )

        if not should_expand:
            return flat

        if "\n" in current_text:
            first_line = current_text.split("\n")[0].strip()
            last_line = current_text.split("\n")[-1].strip()
            if first_line.endswith("(") and last_line == ")":
                inner_lines = current_text.split("\n")[1:-1]
                inner_indent = indent + "    "
                all_correct = all(l.strip().startswith(f"{op_str} ") or i == 0 for i, l in enumerate(inner_lines) if l.strip())
                indent_correct = all(l.startswith(inner_indent) and (l[len(inner_indent):len(inner_indent) + 1] != " ") for l in inner_lines if l.strip())
                if (
                    all_correct
                    and indent_correct
                    and len(inner_lines) >= num_parts
                ):
                    return current_text

        value_text = flat[len("return "):].strip()

        if value_text.startswith("(") and value_text.endswith(")"):
            inner = value_text[1:-1].strip()
        else:
            inner = value_text

        inner_indent = indent + "    "
        parts = self._split_boolop_by_op(inner, op_str)

        if not parts:
            return current_text

        lines = ["return ("]

        for i, part in enumerate(parts):
            if i == 0:
                lines.append(f"{inner_indent}{part}")
            else:
                lines.append(f"{inner_indent}{op_str} {part}")

        lines.append(f"{indent})")

        return "\n".join(lines)


    def _format_chain(self, node: ast.Call, current_text: str, indent: str) -> str:
        if self._has_comment(current_text):
            return current_text

        flat = self._flatten(current_text)
        flat = self._collapse_paren_spaces(flat)
        flat_len = len(flat)
        indent_len = len(indent)

        segments = self._get_chain_segments(node, indent)

        if not segments:
            return current_text

        any_needs_expand = False
        for seg in segments:
            if seg['args']:
                args_str = ", ".join(seg['args'])
                seg_len = len(seg['method']) + 1 + len(args_str) + 1
                if (
                    seg_len > self._call_max_len
                    or len(seg['args']) > self._call_max_args
                    or (
                        any(self._is_kwarg_str(a) for a in seg['args'])
                        and len(seg['args']) > self._call_max_args_kw
                    )
                ):
                    any_needs_expand = True
                    break

        should_expand = (
            any_needs_expand
            or flat_len > self._chain_call_max_len
            or flat_len + indent_len > self._chain_call_max_line_len
        )

        if not should_expand:
            return flat

        if "\n" in current_text:
            last_line = current_text.split("\n")[-1].strip()
            if last_line == ")":
                return current_text

        inner_indent = indent + "    "
        result_parts = []

        for i, seg in enumerate(segments):
            if i == 0:
                prefix = seg.get("prefix", "")
                if not seg['args']:
                    result_parts.append(f"{prefix}{seg['method']}()")
                else:
                    lines = [f"{prefix}{seg['method']}("]
                    for j, arg in enumerate(seg['args']):
                        comma = "," if j < len(seg['args']) - 1 else ""
                        lines.append(f"{inner_indent}{arg}{comma}")

                    lines.append(f"{indent})")
                    result_parts.append("\n".join(lines))

            else:
                method_call = f".{seg['method']}"
                if not seg['args']:
                    result_parts.append(f"{method_call}()")
                else:
                    lines = [f"{method_call}("]
                    for j, arg in enumerate(seg['args']):
                        comma = "," if j < len(seg['args']) - 1 else ""
                        lines.append(f"{inner_indent}{arg}{comma}")

                    lines.append(f"{indent})")
                    result_parts.append("\n".join(lines))

        return "".join(result_parts)


    def _get_chain_segments(
        self,
        node: ast.Call,
        indent: str=""
    ) -> list[dict]:
        """Extract chain segments from outermost to innermost call.

        Returns segments in order from first call to last. The first
        segment includes a 'prefix' key with any base expression
        (e.g., 'self.' or 'obj.').
        """
        inner_indent = indent + "    "
        segments = []
        current = node

        while True:
            if isinstance(current, ast.Call):
                if isinstance(current.func, ast.Attribute):
                    method_name = current.func.attr
                    args = [
                        a for a in self._get_call_arg_strs(current, inner_indent)
                    ]
                    segments.append(
                        {
                            "method": method_name,
                            "args": args,
                            "prefix": ""
                        }
                    )
                    current = current.func.value
                elif isinstance(current.func, ast.Name):
                    args = self._get_call_arg_strs(current, inner_indent)
                    segments.append(
                        {
                            "method": current.func.id,
                            "args": args,
                            "prefix": ""
                        }
                    )
                    break
                else:
                    break

            else:
                if segments:
                    segments[-1]['prefix'] = ast.unparse(current) + "."

                break

        segments.reverse()

        return segments


    def _get_call_arg_strs(
        self,
        node: ast.Call,
        indent: str=""
    ) -> list[str]:
        """Get string representations of a call's arguments from AST.

        Expands dicts and nested lists inline per formatting rules.
        """
        result = []
        inner_indent = indent + "    " if indent else "    "

        for arg in node.args:
            if isinstance(arg, ast.Dict) and arg.keys:
                expanded = self._expand_ast_dict(arg, indent)
                result.append(expanded)
            elif isinstance(arg, ast.List) and arg.elts:
                has_dict = any(isinstance(e, ast.Dict) and e.keys for e in arg.elts)
                if has_dict or len(arg.elts) > self._lst_max_num:
                    expanded = self._expand_ast_list(arg, indent)
                    result.append(expanded)
                else:
                    result.append(ast.unparse(arg))

            else:
                result.append(ast.unparse(arg))

        for kw in node.keywords:
            if kw.arg:
                if isinstance(kw.value, ast.Dict) and kw.value.keys:
                    expanded = self._expand_ast_dict(kw.value, indent)
                    result.append(f"{kw.arg}={expanded}")
                else:
                    result.append(f"{kw.arg}={ast.unparse(kw.value)}")

            else:
                result.append(f"**{ast.unparse(kw.value)}")

        return result


    def _expand_ast_dict(self, node: ast.Dict, indent: str) -> str:
        inner_indent = indent + "    " if indent else "        "
        items = []
        for k, v in zip(node.keys, node.values):
            items.append(f"{ast.unparse(k)}: {ast.unparse(v)}")

        lines = ["{"]
        for i, item in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            lines.append(f"{inner_indent}{item}{comma}")

        lines.append(f"{indent}    }}" if not indent else f"{indent}}}")

        return "\n".join(lines)


    def _expand_ast_list(self, node: ast.List, indent: str) -> str:
        inner_indent = indent + "    " if indent else "        "
        lines = ["["]

        for i, elt in enumerate(node.elts):
            comma = "," if i < len(node.elts) - 1 else ""
            if isinstance(elt, ast.Dict) and elt.keys:
                dict_expanded = self._expand_ast_dict(elt, inner_indent)
                lines.append(f"{inner_indent}{dict_expanded}{comma}")
            else:
                lines.append(f"{inner_indent}{ast.unparse(elt)}{comma}")

        lines.append(f"{indent}    ]" if not indent else f"{indent}]")

        return "\n".join(lines)


    def _format_call(self, node: ast.Call, current_text: str, indent: str) -> str:
        if self._has_comment(current_text):
            return current_text

        num_args = len(node.args) + len(node.keywords)
        if self._contains_ternary(node) and num_args <= 1:
            if "\n" not in current_text:
                return current_text

            flat = self._flatten(current_text)

            return flat

        if self._is_generator_call(node):
            flat = self._flatten(current_text)
            flat = self._collapse_paren_spaces(flat)

            return flat

        flat = self._flatten(current_text)
        flat = self._collapse_paren_spaces(flat)

        if self._has_string_concat_arg(flat):
            return self._format_call_with_string_concat(
                node,
                current_text,
                flat,
                indent
            )

        all_args = self._get_call_args(node, current_text)

        if not all_args:
            return current_text

        if (
            len(all_args) == 1
            and not self._is_kwarg_str(all_args[0])
            and self._is_single_string_arg(node)
        ):
            return flat

        if (
            len(all_args) == 1
            and not self._is_kwarg_str(all_args[0])
        ):
            flat_len = len(flat)
            if (
                not self._inner_would_expand(node, indent + "    ")
                and flat_len <= self._call_max_len
                and flat_len + len(indent) <= self._call_max_line_len
            ):
                return flat

        func_text = self._get_func_text(node, current_text)
        content_len = (
            len(func_text)
            + 1
            + len(", ".join(all_args))
            + 1
        )
        indent_len = len(indent)

        should_expand = (
            content_len > self._call_max_len
            or content_len + indent_len > self._call_max_line_len
            or len(all_args) > self._call_max_args
            or (
                any(self._is_kwarg_str(a) for a in all_args)
                and len(all_args) > self._call_max_args_kw
            )
            or self._any_arg_is_expanded(node)
        )

        if not should_expand:
            return flat

        if self._is_correctly_expanded(
            current_text,
            all_args,
            indent,
            "(",
            ")"
        ):
            return current_text

        inner_indent = indent + "    "
        expanded_args = self._get_expanded_args(node, current_text, inner_indent)
        lines = [f"{func_text}("]

        for i, arg in enumerate(expanded_args):
            comma = "," if i < len(expanded_args) - 1 else ""
            if "\n" in arg:
                arg_lines = arg.split("\n")
                for ai, al in enumerate(arg_lines):
                    if ai == 0:
                        lines.append(f"{inner_indent}{al}")
                    elif ai == len(arg_lines) - 1:
                        lines.append(f"{al}{comma}")
                    else:
                        lines.append(al)

            else:
                lines.append(f"{inner_indent}{arg}{comma}")

        lines.append(f"{indent})")

        return "\n".join(lines)


    def _format_container(
        self,
        node: ast.AST,
        current_text: str,
        indent: str,
        is_nested: bool=False
    ) -> str:
        """Format a list or set literal."""
        elts = getattr(node, "elts", [])
        if not elts:
            return current_text

        if self._has_comment(current_text):
            return current_text

        if self._is_comprehension_node(node):
            return self._flatten(current_text)

        flat = self._flatten(current_text)

        open_char = "[" if isinstance(node, ast.List) else "{"
        close_char = "]" if isinstance(node, ast.List) else "}"

        open_pos = flat.find(open_char)
        if open_pos == -1:
            return current_text

        close_pos = self._find_matching_paren(flat, open_pos)
        if close_pos is None:
            return current_text

        content = flat[open_pos + 1:close_pos]
        items = self._split_by_commas(content)

        if not items:
            return current_text

        content_len = (
            len(open_char)
            + len(", ".join(items))
            + len(close_char)
        )
        indent_len = len(indent)

        has_nested_children = any(isinstance(elt, (ast.Dict, ast.List, ast.Set, ast.Tuple)) and self._node_has_content(elt) for elt in elts)

        should_expand = (
            is_nested
            or has_nested_children
            or content_len > self._lst_max_len
            or content_len + indent_len > self._lst_max_line_len
        )

        if not should_expand:
            return flat

        if self._is_correctly_expanded(
            current_text,
            items,
            indent,
            open_char,
            close_char
        ):
            return current_text

        inner_indent = indent + "    "
        lines = [open_char]

        for i, item in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            ast_elt = elts[i] if i < len(elts) else None

            if (
                ast_elt
                and isinstance(ast_elt, ast.Dict)
                and ast_elt.keys
            ):
                expanded = self._expand_dict_inline(item, inner_indent)
                if expanded and "\n" in expanded:
                    exp_lines = expanded.split("\n")
                    lines.append(f"{inner_indent}{exp_lines[0]}")
                    for el in exp_lines[1:]:
                        lines.append(el)

                    if comma:
                        lines[-1] = lines[-1] + comma

                    continue

            lines.append(f"{inner_indent}{item}{comma}")

        lines.append(f"{indent}{close_char}")

        return "\n".join(lines)


    def _format_dict(self, node: ast.Dict, current_text: str, indent: str) -> str:
        if not node.keys:
            return current_text

        if self._has_comment(current_text):
            return current_text

        flat = self._flatten(current_text)
        flat_items = self._split_by_commas(
            flat[flat.find("{") + 1:self._find_matching_paren(flat, flat.find("{"))]
        )

        if not flat_items:
            return current_text

        if self._is_correctly_expanded(
            current_text,
            flat_items,
            indent,
            "{",
            "}"
        ):
            return current_text

        inner_indent = indent + "    "
        lines = ["{"]

        for i, item in enumerate(flat_items):
            comma = "," if i < len(flat_items) - 1 else ""
            lines.append(f"{inner_indent}{item}{comma}")

        lines.append(f"{indent}}}")

        return "\n".join(lines)


    def _format_tuple(self, node: ast.Tuple, current_text: str, indent: str) -> str:
        if "(" not in current_text:
            return current_text

        if self._has_comment(current_text):
            return current_text

        flat = self._flatten(current_text)
        flat = self._collapse_paren_spaces(flat)

        paren_start = flat.find("(")
        if paren_start < 0:
            return current_text

        paren_end = self._find_matching_paren(flat, paren_start)
        if paren_end is None:
            return current_text

        literal = flat[paren_start:paren_end + 1]

        if len(literal) <= self._lst_max_len:
            return flat

        items = self._split_by_commas(literal[1:-1])

        if not items:
            return flat

        if self._is_correctly_expanded(
            current_text,
            items,
            indent,
            "(",
            ")"
        ):
            return current_text

        inner_indent = indent + "    "
        lines = ["("]
        for i, item in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            lines.append(f"{inner_indent}{item.strip()}{comma}")

        lines.append(f"{indent})")

        return "\n".join(lines)


    def _format_call_with_string_concat(
        self,
        node: ast.Call,
        current_text: str,
        flat: str,
        indent: str
    ) -> str:
        """Format a call that has string concatenation as an argument.

        Wraps the concatenated strings in (...) and expands the call.
        """
        inner_indent = indent + "    "
        str_indent = inner_indent + "    "

        all_args = self._get_call_args(node, current_text)
        func_text = self._get_func_text(node, current_text)

        if not all_args:
            return current_text

        concat_idx = None
        for i, arg in enumerate(all_args):
            if self._is_string_concat(arg):
                concat_idx = i
                break

        if concat_idx is None:
            return current_text

        concat_arg = all_args[concat_idx]
        strings = self._split_concat_strings(concat_arg)

        if not strings:
            return current_text

        if len(all_args) == 1:
            str_lines = [f"{inner_indent}("]
            for s in strings:
                str_lines.append(f"{str_indent}{s}")

            str_lines.append(f"{inner_indent})")

            wrapped_lines = "\n".join(str_lines)

            if self._is_correctly_expanded_concat(current_text, indent):
                return current_text

            lines = [f"{func_text}("]
            lines.append(wrapped_lines)
            lines.append(f"{indent})")

            return "\n".join(lines)

        else:
            kwarg_prefix = ""
            if self._is_kwarg_str(all_args[concat_idx]):
                eq_pos = all_args[concat_idx].find("=")
                kwarg_prefix = all_args[concat_idx][:eq_pos + 1]

            wrapped_str_lines = [f"{kwarg_prefix}("]
            for s in strings:
                wrapped_str_lines.append(f"{str_indent}{s}")

            wrapped_str_lines.append(f"{inner_indent})")
            wrapped_arg = "\n".join(wrapped_str_lines)

            if self._is_correctly_expanded_concat(current_text, indent):
                return current_text

            lines = [f"{func_text}("]
            for i, arg in enumerate(all_args):
                comma = "," if i < len(all_args) - 1 else ""
                if i == concat_idx:
                    lines.append(f"{inner_indent}{wrapped_arg}{comma}")
                else:
                    lines.append(f"{inner_indent}{arg}{comma}")

            lines.append(f"{indent})")

            return "\n".join(lines)


    def _is_correctly_expanded_concat(self, text: str, indent: str) -> bool:
        lines = text.split("\n")
        if len(lines) < 3:
            return False

        inner_indent = indent + "    "
        str_indent = inner_indent + "    "

        first = lines[0].strip()
        last = lines[-1].strip()

        if not first.endswith("(") or last != ")":
            return False

        has_inner_paren = False
        for line in lines[1:-1]:
            stripped = line.strip()
            if stripped == "(":
                has_inner_paren = True
                expected_indent = inner_indent + "("
                if line.rstrip() != expected_indent.rstrip():
                    return False

                break

        if not has_inner_paren:
            return False

        return True


    def _split_concat_strings(self, content: str) -> list[str]:
        try:
            tokens = list(
                tokenize.generate_tokens(io.StringIO(content).readline)
            )
        except tokenize.TokenError:
            return []

        fstring_start = getattr(tokenize, "FSTRING_START", None)
        fstring_end = getattr(tokenize, "FSTRING_END", None)
        tstring_start = getattr(tokenize, "TSTRING_START", None)
        tstring_end = getattr(tokenize, "TSTRING_END", None)

        strings = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t.type == tokenize.STRING:
                strings.append(t.string)
                i += 1
            elif (
                fstring_start is not None
                and (
                    t.type == fstring_start
                    or (
                        tstring_start is not None
                        and t.type == tstring_start
                    )
                )
            ):
                end_type = (
                    tstring_end
                    if tstring_start is not None and t.type == tstring_start
                    else fstring_end
                )
                depth = 1
                j = i + 1
                while j < len(tokens) and depth > 0:
                    if tokens[j].type == t.type:
                        depth += 1
                    elif tokens[j].type == end_type:
                        depth -= 1

                    j += 1

                end_token = tokens[j - 1]
                start_line = t.start[0]
                start_col = t.start[1]
                end_line = end_token.end[0]
                end_col = end_token.end[1]
                lines = content.split("\n")
                if start_line == end_line:
                    string_text = lines[start_line - 1][start_col:end_col]
                else:
                    parts = [
                        lines[start_line - 1][start_col:]
                    ]
                    for line_idx in range(start_line, end_line - 1):
                        parts.append(lines[line_idx])

                    parts.append(lines[end_line - 1][:end_col])
                    string_text = "\n".join(parts)

                strings.append(string_text)
                i = j
            else:
                i += 1

        return strings


    def _format_funcdef(self, node: ast.AST, current_text: str, indent: str) -> str:
        if self._has_comment(current_text):
            return current_text

        flat = self._flatten(current_text)
        flat = self._collapse_paren_spaces(flat)
        flat_len = len(flat)

        args = node.args
        params = self._extract_params(node, current_text)

        if not params:
            return current_text

        should_expand = (
            flat_len > self._def_max_len
            or flat_len + len(indent) > self._def_max_line_len
            or len(params) > self._def_max_args
            or (
                any("=" in p for p in params)
                and len(params) > self._def_max_args_kw
            )
        )

        if not should_expand:
            return flat

        if self._is_correctly_expanded(
            current_text,
            params,
            indent,
            "(",
            ")"
        ):
            return current_text

        prefix = self._get_funcdef_prefix(current_text)
        suffix = self._get_funcdef_suffix(flat)
        inner_indent = indent + "    "
        lines = [f"{prefix}("]

        for i, param in enumerate(params):
            comma = "," if i < len(params) - 1 else ""
            lines.append(f"{inner_indent}{param}{comma}")

        lines.append(f"{indent}){suffix}")

        return "\n".join(lines)


    def _format_subscript(
        self,
        node: ast.Subscript,
        current_text: str,
        indent: str
    ) -> str:
        """Format a subscript (type annotation like Dict[str, int])."""
        if self._has_comment(current_text):
            return current_text

        flat = self._flatten(current_text)
        flat_len = len(flat)

        bracket_pos = flat.find("[")
        if bracket_pos == -1:
            return current_text

        close_pos = self._find_matching_paren(flat, bracket_pos)
        if close_pos is None:
            return current_text

        content = flat[bracket_pos + 1:close_pos]
        items = self._split_by_commas(content)

        if not items:
            return flat

        nesting_depth = self._subscript_nesting_depth(node)
        has_nested = any(isinstance(elt, ast.Subscript) and self._subscript_is_complex(elt) for elt in (node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]))

        should_expand = (
            has_nested
            or nesting_depth > self._annotation_max_depth
            or flat_len > self._annotation_max_len
            or flat_len + len(indent) > self._annotation_max_line_len
        )

        if not should_expand:
            return flat

        if self._is_correctly_expanded(
            current_text,
            items,
            indent,
            "[",
            "]"
        ):
            return current_text

        value_text = flat[:bracket_pos]
        inner_indent = indent + "    "
        lines = [f"{value_text}["]

        for i, item in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            lines.append(f"{inner_indent}{item}{comma}")

        lines.append(f"{indent}]")

        return "\n".join(lines)


    def _format_dict_subscript(
        self,
        node: ast.Subscript,
        current_text: str,
        indent: str
    ) -> str:
        if "\n" not in current_text:
            return current_text

        if self._has_comment(current_text):
            return current_text

        flat = self._flatten(current_text)

        bracket_pos = flat.find("[")
        if bracket_pos == -1:
            return current_text

        pos = bracket_pos
        while pos < len(flat):
            if flat[pos] != "[":
                break

            close_pos = self._find_matching_paren(flat, pos)
            if close_pos is None:
                return current_text

            content = flat[pos + 1:close_pos]
            if "\n" in content:
                return current_text

            pos = close_pos + 1

        return flat


    def _subscript_nesting_depth(self, node: ast.Subscript) -> int:
        depth = 1

        if isinstance(node.slice, ast.Tuple):
            children = node.slice.elts
        else:
            children = [node.slice]

        for child in children:
            if isinstance(child, ast.Subscript):
                child_depth = 1 + self._subscript_nesting_depth(child)
                depth = max(depth, child_depth)

        return depth


    def _format_string_concat(
        self,
        node: ast.AST,
        current_text: str,
        indent: str
    ) -> str:
        """Format a statement containing implicit string concatenation.

        Flattens first, then expands with one string per line inside parens.
        """
        if self._has_comment(current_text):
            return current_text

        flat = self._flatten(current_text)

        paren_start = flat.find("(")
        if paren_start == -1:
            return current_text

        paren_end = self._find_matching_paren(flat, paren_start)
        if paren_end is None:
            return current_text

        content = flat[paren_start + 1:paren_end].strip()

        if content.startswith("("):
            inner_end = self._find_matching_paren(content, 0)
            if inner_end is not None and inner_end == len(content) - 1:
                content = content[1:-1].strip()
                has_inner_parens = True
            else:
                has_inner_parens = False

        else:
            has_inner_parens = False

        strings = self._split_concat_strings(content)
        if len(strings) < 2:
            return current_text

        prefix = flat[:paren_start]
        suffix = flat[paren_end + 1:]
        inner_indent = indent + "    "

        if has_inner_parens:
            lines = [f"{prefix}("]
            lines.append(f"{inner_indent}(")
            str_indent = inner_indent + "    "
            for s in strings:
                lines.append(f"{str_indent}{s}")

            lines.append(f"{inner_indent})")
            lines.append(f"{indent}){suffix}")
        else:
            lines = [f"{prefix}("]
            for s in strings:
                lines.append(f"{inner_indent}{s}")

            lines.append(f"{indent}){suffix}")

        result = "\n".join(lines)

        if result == current_text:
            return current_text

        return result


    def _format_binop(
        self,
        node: ast.AST,
        current_text: str,
        indent: str,
        parent: ast.AST=None
    ) -> str:
        if self._has_comment(current_text):
            return current_text

        operands, operators = self._collect_binop_parts(node)
        if not operands or not operators:
            return current_text

        if (
            isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and not isinstance(node.left, ast.BinOp)
            and "\n" in current_text
        ):
            flat_check = self._flatten(current_text)
            flat_check_len = len(flat_check)
            if (
                flat_check_len <= self._binop_max_len
                and flat_check_len + len(indent) <= self._binop_max_line_len
                and len(operands) <= self._binop_max_operands
            ):
                return flat_check

            is_chain_left = (
                isinstance(node.left, ast.Call)
                and isinstance(node.left.func, ast.Attribute)
                and isinstance(node.left.func.value, ast.Call)
            )

            if not is_chain_left:
                lines = current_text.strip().split("\n")
                last_line = lines[-1].strip()
                if last_line.endswith(":"):
                    last_line = last_line[:-1].strip()

                for op in operators:
                    if (
                        last_line.startswith(f") {op} ")
                        or last_line.startswith(f"){op} ")
                    ):
                        return current_text

                    if last_line == f") {op}" or last_line == f"){op}":
                        return current_text

        flat = self._flatten(current_text)
        flat = self._normalize_binop_spaces(flat, operators)
        flat_len = len(flat)
        indent_len = len(indent)

        num_operands = len(operands)

        should_expand = (
            flat_len > self._binop_max_len
            or flat_len + indent_len > self._binop_max_line_len
            or num_operands > self._binop_max_operands
        )

        if not should_expand:
            if isinstance(parent, (ast.Assign, ast.Return)):
                if "=" in flat:
                    eq_pos = flat.find("=")
                    prefix = flat[:eq_pos + 1]
                    value = flat[eq_pos + 1:].strip()
                    if value.startswith("(") and value.endswith(")"):
                        inner = value[1:-1].strip()
                        flat = f"{prefix} {inner}"

                elif flat.startswith("return "):
                    value = flat[7:].strip()
                    if value.startswith("(") and value.endswith(")"):
                        inner = value[1:-1].strip()
                        flat = f"return {inner}"

            return flat

        is_if_context = isinstance(parent, (ast.If, ast.While))
        is_assign_context = isinstance(parent, ast.Assign)
        is_return_context = isinstance(parent, ast.Return)

        inner_indent = indent + "    "
        op_texts = self._extract_binop_operand_texts(flat, operators)

        if not op_texts or len(op_texts) != len(operands):
            return flat if not should_expand else current_text

        lines_out = []

        if is_if_context:
            keyword = "if" if isinstance(parent, ast.If) else "while"
            keyword_line = flat
            if keyword_line.startswith(keyword + " "):
                expr_text = keyword_line[len(keyword) + 1:]
            elif keyword_line.startswith(keyword + "("):
                expr_text = keyword_line[len(keyword):]
            else:
                expr_text = flat

            if expr_text.startswith("(") and expr_text.endswith("):"):
                expr_text = expr_text[1:-2]
            elif expr_text.endswith(":"):
                expr_text = expr_text[:-1]

            op_texts = self._extract_binop_operand_texts(
                expr_text.strip(),
                operators
            )
            if not op_texts or len(op_texts) != len(operands):
                return current_text

            lines_out.append(f"{keyword} (")
            for i, op_text in enumerate(op_texts):
                if i == 0:
                    lines_out.append(f"{inner_indent}{op_text}")
                else:
                    lines_out.append(f"{inner_indent}{operators[i - 1]} {op_text}")

            lines_out.append(f"{indent}):")
        elif is_assign_context:
            eq_pos = flat.find("=")
            if eq_pos == -1:
                return current_text

            prefix = flat[:eq_pos + 1].rstrip()
            value_text = flat[eq_pos + 1:].strip()

            if value_text.startswith("(") and value_text.endswith(")"):
                value_text = value_text[1:-1].strip()

            op_texts = self._extract_binop_operand_texts(value_text, operators)
            if not op_texts or len(op_texts) != len(operands):
                return current_text

            lines_out.append(f"{prefix} (")
            for i, op_text in enumerate(op_texts):
                if i == 0:
                    lines_out.append(f"{inner_indent}{op_text}")
                else:
                    lines_out.append(f"{inner_indent}{operators[i - 1]} {op_text}")

            lines_out.append(f"{indent})")
        elif is_return_context:
            if flat.startswith("return "):
                value_text = flat[7:].strip()
            else:
                return current_text

            if value_text.startswith("(") and value_text.endswith(")"):
                value_text = value_text[1:-1].strip()

            op_texts = self._extract_binop_operand_texts(value_text, operators)
            if not op_texts or len(op_texts) != len(operands):
                return current_text

            lines_out.append("return (")
            for i, op_text in enumerate(op_texts):
                if i == 0:
                    lines_out.append(f"{inner_indent}{op_text}")
                else:
                    lines_out.append(f"{inner_indent}{operators[i - 1]} {op_text}")

            lines_out.append(f"{indent})")
        else:
            op_texts = self._extract_binop_operand_texts(flat, operators)
            if not op_texts or len(op_texts) != len(operands):
                return current_text

            if flat.startswith("(") and flat.endswith(")"):
                inner_flat = flat[1:-1].strip()
                op_texts = self._extract_binop_operand_texts(inner_flat, operators)
                if not op_texts or len(op_texts) != len(operands):
                    return current_text

            lines_out.append("(")
            for i, op_text in enumerate(op_texts):
                if i == 0:
                    lines_out.append(f"{inner_indent}{op_text}")
                else:
                    lines_out.append(f"{inner_indent}{operators[i - 1]} {op_text}")

            lines_out.append(f"{indent})")

        result = "\n".join(lines_out)
        if result == current_text:
            return current_text

        return result


    def _collect_binop_parts(self, node: ast.AST) -> tuple[list, list]:
        operands = []
        operators = []

        if isinstance(node, ast.BinOp):
            self._flatten_binop_chain(node, operands, operators)
        elif isinstance(node, ast.Compare):
            if isinstance(node.left, ast.BinOp):
                self._flatten_binop_chain(node.left, operands, operators)
            else:
                operands.append(node.left)

            for op, comparator in zip(node.ops, node.comparators):
                operators.append(self._compare_op_str(op))
                operands.append(comparator)

        else:
            return [], []

        return operands, operators


    def _flatten_binop_chain(
        self,
        node: ast.BinOp,
        operands: list,
        operators: list
    ):
        if isinstance(node.left, ast.BinOp):
            self._flatten_binop_chain(node.left, operands, operators)
        else:
            operands.append(node.left)

        operators.append(self._binop_op_str(node.op))

        if isinstance(node.right, ast.BinOp):
            self._flatten_binop_chain(node.right, operands, operators)
        else:
            operands.append(node.right)


    def _binop_op_str(self, op: ast.operator) -> str:
        op_map = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.FloorDiv: "//",
            ast.Mod: "%",
            ast.Pow: "**",
            ast.MatMult: "@",
            ast.BitOr: "|",
            ast.BitAnd: "&",
            ast.BitXor: "^",
            ast.LShift: "<<",
            ast.RShift: ">>"
        }

        return op_map.get(type(op), "+")


    def _compare_op_str(self, op: ast.cmpop) -> str:
        op_map = {
            ast.Eq: "==",
            ast.NotEq: "!=",
            ast.Lt: "<",
            ast.LtE: "<=",
            ast.Gt: ">",
            ast.GtE: ">=",
            ast.Is: "is",
            ast.IsNot: "is not",
            ast.In: "in",
            ast.NotIn: "not in"
        }

        return op_map.get(type(op), "==")


    def _extract_binop_operand_texts(
        self,
        flat_expr: str,
        operators: list[str]
    ) -> list[str]:
        parts = []
        remaining = flat_expr.strip()

        for i, op in enumerate(operators):
            split_pos = self._find_binop_split(remaining, op)
            if split_pos == -1:
                return []

            parts.append(remaining[:split_pos].strip())
            remaining = remaining[split_pos + len(op):].strip()

        parts.append(remaining)

        return parts


    def _find_binop_split(self, text: str, op: str) -> int:
        depth = 0
        in_string = False
        string_char = ""
        i = 0

        while i < len(text):
            ch = text[i]

            if not in_string:
                if ch in ('"', "'"):
                    if text[i:i + 3] in ('"""', "'''"):
                        in_string = True
                        string_char = text[i:i + 3]
                        i += 3
                        continue
                    else:
                        in_string = True
                        string_char = ch

                elif ch in "([{":
                    depth += 1
                elif ch in ")]}":
                    depth -= 1
                elif depth == 0:
                    if text[i:i + len(op)] == op:
                        before = text[i - 1] if i > 0 else " "
                        after = text[i + len(op)] if i + len(op) < len(text) else " "
                        if len(op) >= 2:
                            if (
                                not before.isalnum()
                                and before != "_"
                                and not after.isalnum()
                                and after != "_"
                            ):
                                return i

                        else:
                            if before == " " and after == " ":
                                return i

            else:
                if len(string_char) == 3 and text[i:i + 3] == string_char:
                    in_string = False
                    i += 3
                    continue
                elif (
                    len(string_char) == 1
                    and ch == string_char
                    and (
                        i == 0
                        or text[i - 1] != "\\"
                    )
                ):
                    in_string = False

            i += 1

        return -1


    def _normalize_binop_spaces(self, flat: str, operators: list[str]) -> str:
        return flat


    def _build_line_offsets(self, document: str) -> list[int]:
        offsets = [0]
        self._line_byte_maps = {}
        line_idx = 0
        line_start = 0

        for i, ch in enumerate(document):
            if ch == "\n":
                line = document[line_start:i]
                if len(line.encode("utf-8")) != len(line):
                    byte_to_char = {}
                    byte_pos = 0
                    for ci, c in enumerate(line):
                        byte_to_char[byte_pos] = ci
                        byte_pos += len(c.encode("utf-8"))

                    byte_to_char[byte_pos] = len(line)
                    self._line_byte_maps[line_idx] = byte_to_char

                offsets.append(i + 1)
                line_idx += 1
                line_start = i + 1

        line = document[line_start:]
        if len(line.encode("utf-8")) != len(line):
            byte_to_char = {}
            byte_pos = 0
            for ci, c in enumerate(line):
                byte_to_char[byte_pos] = ci
                byte_pos += len(c.encode("utf-8"))

            byte_to_char[byte_pos] = len(line)
            self._line_byte_maps[line_idx] = byte_to_char

        return offsets


    def _offset(self, document: str, lineno: int, col_offset: int) -> int:
        line_start = self._line_offsets[lineno - 1]
        byte_map = self._line_byte_maps.get(lineno - 1)
        if byte_map is None:
            return line_start + col_offset

        char_offset = byte_map.get(col_offset)
        if char_offset is not None:
            return line_start + char_offset

        return line_start + col_offset


    def _get_indent(self, document: str, offset: int) -> str:
        line_start = document.rfind("\n", 0, offset) + 1
        indent = ""

        for ch in document[line_start:]:
            if ch in (" ", "\t"):
                indent += ch
            else:
                break

        return indent


    def _find_colon_line(
        self,
        document: str,
        start_line: int,
        body_start_line: int
    ) -> int:
        """Find the end of a function signature (up to and including ':')."""
        lines = document.split("\n")
        for line_idx in range(start_line - 1, body_start_line):
            line = lines[line_idx]
            stripped = line.rstrip()
            if stripped.endswith(":"):
                return (
                    self._offset(document, line_idx + 1, 0)
                    + len(stripped)
                )

        return self._offset(document, body_start_line, 0)


    def _flatten(self, text: str) -> str:
        if "\n" not in text:
            return text

        result = []
        i = 0
        in_string = False
        string_char = ""
        is_raw = False

        while i < len(text):
            if not in_string:
                prefix_start = i
                while (
                    i < len(text)
                    and text[i].lower() in ("f", "r", "b", "u")
                ):
                    i += 1

                if i < len(text) and text[i:i + 3] in ('"""', "'''"):
                    in_string = True
                    string_char = text[i:i + 3]
                    is_raw = any(text[j].lower() == "r" for j in range(prefix_start, i))
                    result.append(text[prefix_start:i + 3])
                    i += 3
                elif i < len(text) and text[i] in ('"', "'"):
                    in_string = True
                    string_char = text[i]
                    is_raw = any(text[j].lower() == "r" for j in range(prefix_start, i))
                    result.append(text[prefix_start:i + 1])
                    i += 1
                elif i < len(text) and text[i] == "#":
                    if prefix_start < i:
                        result.append(text[prefix_start:i])

                    nl_pos = text.find("\n", i)
                    if nl_pos == -1:
                        result.append(text[i:])
                        break

                    result.append(text[i:nl_pos + 1])
                    i = nl_pos + 1
                    indent_start = i
                    while i < len(text) and text[i] in (" ", "\t"):
                        i += 1

                    if indent_start < i:
                        result.append(text[indent_start:i])

                elif i < len(text) and text[i] in (" ", "\t", "\n", "\r"):
                    if prefix_start < i:
                        result.append(text[prefix_start:i])

                    has_newline = False
                    ws_start = i
                    while i < len(text) and text[i] in (" ", "\t", "\n", "\r"):
                        if text[i] == "\n":
                            has_newline = True

                        i += 1

                    if (
                        has_newline
                        and i < len(text)
                        and text[i] == "#"
                    ):
                        last_nl = text.rfind("\n", ws_start, i)
                        result.append(text[last_nl:i])
                    else:
                        if result and result[-1] != " ":
                            result.append(" ")

                elif i < len(text):
                    result.append(text[prefix_start:i + 1])
                    i += 1
                else:
                    if prefix_start < i:
                        result.append(text[prefix_start:i])

            else:
                if len(string_char) == 3 and text[i:i + 3] == string_char:
                    in_string = False
                    result.append(text[i:i + 3])
                    i += 3
                elif len(string_char) == 1 and text[i] == string_char:
                    if is_raw or self._is_closing_quote(text, i):
                        in_string = False
                        result.append(text[i])
                        i += 1
                    else:
                        result.append(text[i])
                        i += 1

                else:
                    result.append(text[i])
                    i += 1

        return "".join(result)


    def _is_closing_quote(self, s: str, i: int) -> bool:
        num_backslashes = 0
        j = i - 1

        while j >= 0 and s[j] == "\\":
            num_backslashes += 1
            j -= 1

        return num_backslashes % 2 == 0


    def _collapse_inline_spaces(self, doc: str) -> str:
        lines = doc.split("\n")
        result = []

        for line in lines:
            new_line = self._collapse_paren_spaces_line(line)
            result.append(new_line)

        return "\n".join(result)


    def _normalize_paren_indent(self, doc: str) -> str:
        lines = doc.split("\n")
        result = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.rstrip()

            if (
                stripped.endswith("(")
                and "=" in stripped
                and not self._is_call_paren(stripped.lstrip())
                and not self._is_keyword_paren(stripped.lstrip())
            ):
                base_indent = len(line) - len(line.lstrip())
                expected_inner = base_indent + 4

                close_idx = None
                inner_lines = []
                for j in range(
                    i + 1,
                    min(i + 20, len(lines))
                ):
                    j_stripped = lines[j].strip()
                    if j_stripped in (")", "),"):
                        close_idx = j
                        break

                    inner_lines.append(j)

                if close_idx is not None and inner_lines:
                    needs_fix = False
                    paren_depth = 0
                    brace_depth = 0
                    for j in inner_lines:
                        l = lines[j]
                        l_stripped = l.strip()
                        if not l_stripped:
                            continue

                        if paren_depth == 0 and brace_depth == 0:
                            actual = len(l) - len(l.lstrip())
                            if actual != expected_inner:
                                needs_fix = True
                                break

                        if l_stripped.endswith("("):
                            paren_depth += 1
                        elif l_stripped.endswith("{"):
                            brace_depth += 1

                        if l_stripped in (")", "),"):
                            paren_depth -= 1
                        elif l_stripped in ("}", "},"):
                            brace_depth -= 1

                    if needs_fix:
                        result.append(line)
                        paren_depth = 0
                        brace_depth = 0
                        for j in inner_lines:
                            l = lines[j]
                            l_stripped = l.strip()

                            if paren_depth > 0 or brace_depth > 0:
                                result.append(l)
                            elif l_stripped:
                                result.append(" " * expected_inner + l.lstrip())
                            else:
                                result.append(l)

                            if l_stripped.endswith("("):
                                paren_depth += 1
                            elif l_stripped.endswith("{"):
                                brace_depth += 1

                            if l_stripped in (")", "),"):
                                paren_depth -= 1
                            elif l_stripped in ("}", "},"):
                                brace_depth -= 1

                        result.append(lines[close_idx])
                        i = close_idx + 1
                        continue

            result.append(line)
            i += 1

        return "\n".join(result)


    def _collapse_short_parens(self, doc: str) -> str:
        lines = doc.split("\n")
        result = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.rstrip()

            if (
                stripped.endswith("(")
                and not stripped.endswith(":(")
                and not self._is_keyword_paren(stripped)
                and not self._is_call_paren(stripped)
            ):
                open_indent = len(line) - len(line.lstrip())
                close_idx = None
                content_lines = []

                for j in range(
                    i + 1,
                    min(i + 5, len(lines))
                ):
                    j_stripped = lines[j].strip()
                    if j_stripped in (")", "),"):
                        close_indent = len(lines[j]) - len(lines[j].lstrip())
                        if close_indent >= open_indent:
                            close_idx = j
                            break

                    elif (
                        "(" in j_stripped
                        or "{" in j_stripped
                        or "[" in j_stripped
                    ):
                        if j_stripped.count("(") != j_stripped.count(")"):
                            break

                        if j_stripped.count("[") != j_stripped.count("]"):
                            break

                        if j_stripped.count("{") != j_stripped.count("}"):
                            break

                    content_lines.append(j_stripped)

                if close_idx is not None and content_lines:
                    content = " ".join(content_lines)
                    close_suffix = lines[close_idx].strip()

                    if (
                        " or " not in content
                        and " and " not in content
                        and not any(c.startswith("f\"") or c.startswith("f'") or c.startswith("\"") or c.startswith("'") or c.startswith("b\"") or c.startswith("b'") for c in content_lines)
                        and not any("=" in c and not any(op in c for op in ["==", "!=", "<=", ">="]) for c in content_lines)
                        and not any(c.startswith(("+", "-", "*", "/", "%", "@", "|", "&", "^", "<<", ">>", "==", "!=", "<", ">", "<=", ">=", "is ", "in ", "not ")) for c in content_lines)
                    ):
                        collapsed = f"{stripped}{content}{close_suffix}"
                        if len(collapsed) <= 120:
                            if (
                                "," in content
                                and len(f"({content})") > self._lst_max_len
                            ):
                                result.append(line)
                                i += 1
                                continue

                            result.append(f"{line[:open_indent]}{stripped.lstrip()}{content}{close_suffix}")
                            i = close_idx + 1
                            continue

            result.append(line)
            i += 1

        return "\n".join(result)


    def _is_call_paren(self, stripped: str) -> bool:
        if not stripped.endswith("("):
            return False

        prefix = stripped[:-1].rstrip()
        if not prefix:
            return False

        if prefix[-1] in "_)":
            return True

        if prefix[-1].isalnum():
            keywords = (
                "in",
                "not",
                "and",
                "or",
                "is",
                "return",
                "yield",
                "assert",
                "del",
                "lambda"
            )
            for kw in keywords:
                if prefix == kw or prefix.endswith(f" {kw}"):
                    return False

            return True

        return False


    def _is_keyword_paren(self, stripped: str) -> bool:
        keywords = (
            "if ",
            "elif ",
            "while ",
            "def ",
            "class ",
            "if(",
            "elif("
        )

        for kw in keywords:
            if stripped.startswith(kw) or stripped == "if":
                return True

        return False


    def _collapse_paren_spaces_line(self, line: str) -> str:
        result = []
        i = 0
        in_string = False
        string_char = ""

        while i < len(line):
            ch = line[i]

            if not in_string:
                if ch == "#":
                    result.append(line[i:])
                    break

                if ch in ('"', "'"):
                    if line[i:i + 3] in ('"""', "'''"):
                        in_string = True
                        string_char = line[i:i + 3]
                        result.append(line[i:i + 3])
                        i += 3
                        continue
                    else:
                        in_string = True
                        string_char = ch

                if (
                    ch in "([{"
                    and i + 1 < len(line)
                    and line[i + 1] == " "
                ):
                    j = i + 1
                    while j < len(line) and line[j] == " ":
                        j += 1

                    if j < len(line) and line[j] == "#":
                        result.append(ch)
                        result.append(" ")
                        i = j
                        continue

                    result.append(ch)
                    i = j
                    continue

                if (
                    ch == " "
                    and i + 1 < len(line)
                    and line[i + 1] in ")]}"
                    and result
                    and result[-1] not in " \t"
                ):
                    i += 1
                    continue

                result.append(ch)
            else:
                if (
                    len(string_char) == 3
                    and line[i:i + 3] == string_char
                ):
                    in_string = False
                    result.append(line[i:i + 3])
                    i += 3
                    continue
                elif (
                    len(string_char) == 1
                    and ch == string_char
                    and self._is_closing_quote(line, i)
                ):
                    in_string = False

                result.append(ch)

            i += 1

        return "".join(result)


    def _collapse_paren_spaces(self, flat: str) -> str:
        result = []
        i = 0
        in_string = False
        string_char = ""

        while i < len(flat):
            ch = flat[i]

            if not in_string:
                if ch in ('"', "'"):
                    if flat[i:i + 3] in ('"""', "'''"):
                        in_string = True
                        string_char = flat[i:i + 3]
                        result.append(flat[i:i + 3])
                        i += 3
                        continue
                    else:
                        in_string = True
                        string_char = ch
                        result.append(ch)
                        i += 1
                        continue

                if (
                    ch in "([{"
                    and i + 1 < len(flat)
                    and flat[i + 1] == " "
                ):
                    result.append(ch)
                    i += 1
                    while i < len(flat) and flat[i] == " ":
                        i += 1

                    continue

                if (
                    ch == " "
                    and i + 1 < len(flat)
                    and flat[i + 1] in ")]}"
                ):
                    i += 1
                    continue

                result.append(ch)
            else:
                if len(string_char) == 3 and flat[i:i + 3] == string_char:
                    in_string = False
                    result.append(flat[i:i + 3])
                    i += 3
                    continue
                elif (
                    len(string_char) == 1
                    and ch == string_char
                    and self._is_closing_quote(flat, i)
                ):
                    in_string = False
                    result.append(ch)
                else:
                    result.append(ch)

            i += 1

        return "".join(result)


    def _contains_ternary(self, node: ast.Call) -> bool:
        for arg in node.args:
            if isinstance(arg, ast.IfExp):
                return True

        for kw in node.keywords:
            if isinstance(kw.value, ast.IfExp):
                return True

        return False


    def _any_arg_is_expanded(self, node: ast.Call) -> bool:
        for arg in node.args:
            if isinstance(arg, (ast.Dict, ast.List, ast.Set)):
                if self._node_has_content(arg):
                    return True

            if isinstance(arg, ast.Tuple):
                if len(arg.elts) > 1:
                    try:
                        unparsed = ast.unparse(arg)
                        if len(unparsed) > self._lst_max_len:
                            return True

                    except Exception:
                        pass

            if isinstance(arg, ast.Call):
                inner_args = arg.args + [kw.value for kw in arg.keywords]
                if len(inner_args) > 1:
                    return True

        for kw in node.keywords:
            if isinstance(kw.value, (ast.Dict, ast.List, ast.Set)):
                if self._node_has_content(kw.value):
                    return True

            if isinstance(kw.value, ast.Tuple):
                if len(kw.value.elts) > 1:
                    try:
                        unparsed = ast.unparse(kw.value)
                        if len(unparsed) > self._lst_max_len:
                            return True

                    except Exception:
                        pass

        return False


    def _is_chained_method(self, node: ast.Call) -> bool:
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Call):
                return True

        return False


    def _is_chain_root(self, node: ast.Call, parent: ast.AST) -> bool:
        if isinstance(parent, ast.Attribute):
            return True

        return False


    def _is_chain_end(self, node: ast.Call, parent: ast.AST) -> bool:
        if not isinstance(node.func, ast.Attribute):
            return False

        if not isinstance(node.func.value, ast.Call):
            return False

        if isinstance(parent, ast.Attribute):
            return False

        return True


    def _get_expanded_args(
        self,
        node: ast.Call,
        current_text: str,
        inner_indent: str
    ) -> list[str]:
        """Get arg strings, with inner expansions applied for dicts/lists/tuples."""
        flat_args = self._get_call_args(node, current_text)
        all_ast_args = (
            list(node.args)
            + [kw.value for kw in node.keywords]
        )

        result = []
        for i, arg_str in enumerate(flat_args):
            ast_arg = all_ast_args[i] if i < len(all_ast_args) else None

            if (
                ast_arg
                and isinstance(ast_arg, ast.Dict)
                and ast_arg.keys
            ):
                expanded = self._expand_dict_inline(arg_str, inner_indent)
                if expanded:
                    result.append(expanded)
                    continue

            elif (
                ast_arg
                and isinstance(ast_arg, ast.Tuple)
                and ast_arg.elts
            ):
                expanded = self._expand_tuple_inline(arg_str, inner_indent)
                if expanded:
                    result.append(expanded)
                    continue

            elif ast_arg and isinstance(ast_arg, (ast.List, ast.Set)):
                elts = getattr(ast_arg, "elts", [])
                if len(elts) > 1:
                    has_nested = any(isinstance(e, (ast.Dict, ast.List, ast.Set, ast.Call)) for e in elts)
                    if has_nested or len(elts) > self._lst_max_num:
                        expanded = self._expand_container_inline(
                            arg_str,
                            inner_indent,
                            ast_arg
                        )
                        if expanded:
                            result.append(expanded)
                            continue

            result.append(arg_str)

        return result


    def _expand_dict_inline(self, arg_str: str, indent: str) -> str | None:
        stripped = arg_str.strip()
        if (
            not stripped.startswith("{")
            or not stripped.endswith("}")
        ):
            return None

        inner = stripped[1:-1].strip()
        if not inner:
            return None

        items = self._split_by_commas(inner)
        if not items:
            return None

        inner_indent = indent + "    "
        lines = ["{"]
        for i, item in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            lines.append(f"{inner_indent}{item.strip()}{comma}")

        lines.append(f"{indent}}}")

        return "\n".join(lines)


    def _expand_tuple_inline(self, arg_str: str, indent: str) -> str | None:
        stripped = arg_str.strip()
        if (
            not stripped.startswith("(")
            or not stripped.endswith(")")
        ):
            return None

        if len(stripped) <= self._lst_max_len:
            return None

        inner = stripped[1:-1].strip()
        if not inner:
            return None

        items = self._split_by_commas(inner)
        if not items:
            return None

        inner_indent = indent + "    "
        lines = ["("]
        for i, item in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            lines.append(f"{inner_indent}{item.strip()}{comma}")

        lines.append(f"{indent})")

        return "\n".join(lines)


    def _expand_container_inline(
        self,
        arg_str: str,
        indent: str,
        node: ast.AST
    ) -> str | None:
        """Expand a list/set arg string into multi-line format."""
        stripped = arg_str.strip()
        if isinstance(node, ast.List):
            open_ch, close_ch = "[", "]"
        else:
            open_ch, close_ch = "{", "}"

        if (
            not stripped.startswith(open_ch)
            or not stripped.endswith(close_ch)
        ):
            return None

        inner = stripped[1:-1].strip()
        if not inner:
            return None

        items = self._split_by_commas(inner)
        if not items:
            return None

        inner_indent = indent + "    "
        lines = [open_ch]

        for i, item in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            item_stripped = item.strip()

            if (
                item_stripped.startswith("{")
                and item_stripped.endswith("}")
            ):
                inner_dict = item_stripped[1:-1].strip()
                if inner_dict:
                    dict_items = self._split_by_commas(inner_dict)
                    if dict_items:
                        dict_inner_indent = inner_indent + "    "
                        dict_lines = ["{"]
                        for j, di in enumerate(dict_items):
                            d_comma = "," if j < len(dict_items) - 1 else ""
                            dict_lines.append(f"{dict_inner_indent}{di.strip()}{d_comma}")

                        dict_lines.append(f"{inner_indent}}}")
                        expanded_item = "\n".join(dict_lines)
                        lines.append(f"{inner_indent}{expanded_item}{comma}")
                        continue

            lines.append(f"{inner_indent}{item_stripped}{comma}")

        lines.append(f"{indent}{close_ch}")

        return "\n".join(lines)


    def _is_generator_call(self, node: ast.Call) -> bool:
        if len(node.args) == 1 and not node.keywords:
            if isinstance(node.args[0], ast.GeneratorExp):
                return True

        return False


    def _normalize_operators(self, text: str) -> str:
        text = re.sub(r"\)or\(", ") or (", text)
        text = re.sub(r"\)or ", ") or ", text)
        text = re.sub(r" or\(", " or (", text)
        text = re.sub(r"\)and\(", ") and (", text)
        text = re.sub(r"\)and ", ") and ", text)
        text = re.sub(r" and\(", " and (", text)

        return text


    def _subscript_is_complex(self, node: ast.Subscript) -> bool:
        if isinstance(node.slice, ast.Tuple):
            if len(node.slice.elts) > 1:
                return any(isinstance(elt, ast.Subscript) for elt in node.slice.elts)

            return any(isinstance(elt, ast.Subscript) and self._subscript_is_complex(elt) for elt in node.slice.elts)

        if isinstance(node.slice, ast.Subscript):
            return True

        return False


    def _is_comprehension_node(self, node: ast.AST) -> bool:
        return isinstance(
            node,
            (
                ast.ListComp,
                ast.SetComp,
                ast.DictComp,
                ast.GeneratorExp
            )
        )


    def _has_string_concat_arg(self, flat: str) -> bool:
        paren_start = flat.find("(")
        if paren_start == -1:
            return False

        paren_end = self._find_matching_paren(flat, paren_start)
        if paren_end is None:
            return False

        content = flat[paren_start + 1:paren_end].strip()

        if content.startswith("("):
            inner_end = self._find_matching_paren(content, 0)
            if inner_end is not None and inner_end == len(content) - 1:
                content = content[1:-1].strip()

        return self._is_string_concat(content)


    def _is_string_concat(self, content: str) -> bool:
        try:
            tokens = list(
                tokenize.generate_tokens(io.StringIO(content).readline)
            )
        except tokenize.TokenError:
            return False

        fstring_start = getattr(tokenize, "FSTRING_START", None)
        fstring_end = getattr(tokenize, "FSTRING_END", None)
        tstring_start = getattr(tokenize, "TSTRING_START", None)
        tstring_end = getattr(tokenize, "TSTRING_END", None)

        string_tokens = []
        fstring_depth = 0
        i = 0
        while i < len(tokens):
            t = tokens[i]

            if (
                fstring_start is not None
                and (
                    t.type == fstring_start
                    or (
                        tstring_start is not None
                        and t.type == tstring_start
                    )
                )
            ):
                if fstring_depth == 0:
                    start_token = t

                fstring_depth += 1
                i += 1
            elif (
                fstring_end is not None
                and (
                    t.type == fstring_end
                    or (
                        tstring_end is not None
                        and t.type == tstring_end
                    )
                )
            ):
                fstring_depth -= 1
                if fstring_depth == 0:
                    fake = tokenize.TokenInfo(
                        type=tokenize.STRING,
                        string="",
                        start=start_token.start,
                        end=t.end,
                        line=""
                    )
                    string_tokens.append(fake)

                i += 1
            elif t.type == tokenize.STRING and fstring_depth == 0:
                string_tokens.append(t)
                i += 1
            else:
                i += 1

        if len(string_tokens) < 2:
            return False

        lines = content.split("\n")

        for i in range(len(string_tokens) - 1):
            cur = string_tokens[i]
            nxt = string_tokens[i + 1]

            if cur.end[0] == nxt.start[0]:
                between = content[cur.end[1]:nxt.start[1]]
                stripped = between.strip()
                if stripped == "" or stripped == "\\":
                    return True

            else:
                between_lines = lines[cur.end[0] - 1][cur.end[1]:]
                for line_idx in range(cur.end[0], nxt.start[0] - 1):
                    between_lines += "\n" + lines[line_idx]

                between_lines += "\n" + lines[nxt.start[0] - 1][:nxt.start[1]]
                stripped = between_lines.strip()
                if stripped == "" or stripped == "\\":
                    return True

        return False


    def _get_call_args(self, node: ast.Call, current_text: str) -> list[str]:
        flat = self._flatten(current_text)

        paren_start = flat.find("(")
        if paren_start == -1:
            return []

        paren_end = self._find_matching_paren(flat, paren_start)
        if paren_end is None:
            return []

        content = flat[paren_start + 1:paren_end]

        return self._split_by_commas(content)


    def _get_func_text(self, node: ast.Call, current_text: str) -> str:
        flat = self._flatten(current_text)
        paren_start = flat.find("(")

        if paren_start == -1:
            return flat

        return flat[:paren_start]


    def _has_comment(self, text: str) -> bool:
        return "#" in text and self._has_comment_full(text)


    def _has_comment_full(self, text: str) -> bool:
        in_string = False
        string_char = ""
        i = 0

        while i < len(text):
            ch = text[i]

            if not in_string:
                if ch == "#":
                    return True

                if ch in ('"', "'"):
                    if text[i:i + 3] in ('"""', "'''"):
                        in_string = True
                        string_char = text[i:i + 3]
                        i += 3
                        continue
                    else:
                        in_string = True
                        string_char = ch

            else:
                if (
                    len(string_char) == 3
                    and text[i:i + 3] == string_char
                ):
                    in_string = False
                    i += 3
                    continue
                elif (
                    len(string_char) == 1
                    and ch == string_char
                    and (
                        i == 0
                        or text[i - 1] != "\\"
                    )
                ):
                    in_string = False

            i += 1

        return False


    def _is_single_string_arg(self, node: ast.Call) -> bool:
        if len(node.args) != 1 or node.keywords:
            return False

        arg = node.args[0]

        if (
            isinstance(arg, ast.Constant)
            and isinstance(arg.value, str)
        ):
            return True

        if isinstance(arg, ast.JoinedStr):
            return True

        return False


    def _is_kwarg_str(self, arg: str) -> bool:
        depth = 0
        in_string = False
        string_char = ""
        i = 0

        while i < len(arg):
            ch = arg[i]

            if not in_string:
                if ch in ('"', "'"):
                    in_string = True
                    string_char = ch
                    i += 1
                    continue

                if ch in "([{":
                    depth += 1
                elif ch in ")]}":
                    depth -= 1
                elif ch == "=" and depth == 0:
                    if i > 0 and arg[i - 1] not in "!<>=":
                        if i + 1 < len(arg) and arg[i + 1] != "=":
                            return True

            else:
                if ch == string_char and self._is_closing_quote(arg, i):
                    in_string = False

            i += 1

        return False


    def _inner_would_expand(self, node: ast.Call, indent: str) -> bool:
        if not node.args:
            return False

        arg = node.args[0]

        if isinstance(arg, ast.Dict) and arg.keys:
            return True

        if isinstance(arg, (ast.List, ast.Set)):
            elts = getattr(arg, "elts", [])
            if not elts:
                return False

            has_nested = any(isinstance(e, (ast.Dict, ast.List, ast.Set, ast.Tuple)) and self._node_has_content(e) for e in elts)
            if has_nested:
                return True

            flat_inner = ", ".join(ast.unparse(e) for e in elts)
            if len(flat_inner) + 2 > self._lst_max_len:
                return True

            return False

        if isinstance(arg, ast.Call):
            inner_args = len(arg.args) + len(arg.keywords)
            if inner_args > self._call_max_args:
                return True

            if (
                inner_args > self._call_max_args_kw
                and any(kw for kw in arg.keywords)
            ):
                return True

            return False

        if isinstance(arg, ast.JoinedStr):
            return False

        if isinstance(arg, ast.Subscript):
            if (
                isinstance(arg.slice, ast.Tuple)
                and len(arg.slice.elts) > 2
            ):
                return True

        return False


    def _node_has_content(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Dict):
            return bool(node.keys)

        if isinstance(node, (ast.List, ast.Set, ast.Tuple)):
            return bool(node.elts)

        if isinstance(node, ast.Call):
            return bool(node.args or node.keywords)

        return False


    def _extract_items_from_source(
        self,
        current_text: str,
        node: ast.AST
    ) -> list[str]:
        """Extract comma-separated items from the source text of a node.

        Preserves inner formatting (multiline content within items).
        """
        if isinstance(node, (ast.List, ast.ListComp)):
            open_ch = "["
        elif isinstance(node, ast.Dict):
            open_ch = "{"
        elif isinstance(node, (ast.Set, ast.SetComp)):
            open_ch = "{"
        elif isinstance(node, ast.Subscript):
            open_ch = "["
        else:
            open_ch = "("

        start = current_text.find(open_ch)
        if start == -1:
            return []

        end = self._find_matching_paren(current_text, start)
        if end is None:
            return []

        content = current_text[start + 1:end]

        items = self._split_by_commas(content)

        return [self._normalize_item(item) for item in items if item.strip()]


    def _normalize_item(self, item: str) -> str:
        if "\n" not in item:
            return item.strip()

        lines = item.split("\n")
        if not lines:
            return item.strip()

        first = lines[0].strip()
        if len(lines) == 1:
            return first

        min_indent = None
        for line in lines[1:]:
            if line.strip():
                leading = len(line) - len(line.lstrip())
                if min_indent is None or leading < min_indent:
                    min_indent = leading

        if min_indent is None:
            return first

        result_lines = [first]
        for line in lines[1:]:
            if line.strip():
                result_lines.append(line[min_indent:] if len(line) > min_indent else line.lstrip())
            else:
                result_lines.append("")

        return "\n".join(result_lines)


    def _reindent(self, item: str, base_indent: str) -> str:
        if "\n" not in item:
            return item

        lines = item.split("\n")
        first = lines[0]

        result_lines = [first]
        for line in lines[1:]:
            if line.strip():
                result_lines.append(f"{base_indent}    {line}")
            else:
                result_lines.append("")

        return "\n".join(result_lines)


    def _is_correctly_expanded(
        self,
        current_text: str,
        flat_items: list[str],
        indent: str,
        open_char: str,
        close_char: str
    ) -> bool:
        """Check if current_text is already correctly expanded."""
        if "\n" not in current_text:
            return False

        inner_indent = indent + "    "
        lines = current_text.split("\n")

        if not lines:
            return False

        first_line = lines[0].rstrip()
        if not first_line.endswith(open_char):
            return False

        last_line = lines[-1].rstrip()
        expected_close = f"{indent}{close_char}"
        if last_line != expected_close:
            return False

        for line in lines[1:-1]:
            if line.strip():
                if not line.startswith(inner_indent):
                    return False

        first_content = next((l for l in lines[1:-1] if l.strip()), None)
        if (
            first_content is not None
            and first_content.startswith(inner_indent)
            and len(first_content) > len(inner_indent)
            and first_content[len(inner_indent)] == " "
        ):
            return False

        if flat_items and len(flat_items) > 1:
            content_lines = [l for l in lines[1:-1] if l.strip()]
            if len(content_lines) < len(flat_items):
                return False

        if len(lines) >= 3 and not lines[-2].strip():
            return False

        return True


    def _extract_params(self, node: ast.AST, current_text: str) -> list[str]:
        flat = self._flatten(current_text)
        paren_start = flat.find("(")

        if paren_start == -1:
            return []

        paren_end = self._find_matching_paren(flat, paren_start)
        if paren_end is None:
            return []

        content = flat[paren_start + 1:paren_end]

        return self._split_by_commas(content)


    def _get_funcdef_prefix(self, current_text: str) -> str:
        flat = self._flatten(current_text)
        paren_start = flat.find("(")

        if paren_start == -1:
            return flat

        return flat[:paren_start]


    def _get_funcdef_suffix(self, flat: str) -> str:
        paren_start = flat.find("(")
        if paren_start == -1:
            return ":"

        close_paren = self._find_matching_paren(flat, paren_start)
        if close_paren is None:
            return ":"

        after = flat[close_paren + 1:]

        return after


    def _get_subscript_value(self, current_text: str) -> str:
        flat = self._flatten(current_text)
        bracket_start = flat.find("[")

        if bracket_start == -1:
            return flat

        return flat[:bracket_start]


    def _find_matching_paren(self, s: str, start: int) -> int | None:
        open_ch = s[start]
        close_map = {
            "(": ")",
            "[": "]",
            "{": "}"
        }
        close_ch = close_map.get(open_ch)

        if close_ch is None:
            return None

        depth = 1
        in_string = False
        string_char = ""
        i = start + 1

        while i < len(s):
            ch = s[i]

            if not in_string:
                if ch in ('"', "'"):
                    if s[i:i + 3] in ('"""', "'''"):
                        in_string = True
                        string_char = s[i:i + 3]
                        i += 3
                        continue
                    else:
                        in_string = True
                        string_char = ch
                        i += 1
                        continue

                if ch == open_ch:
                    depth += 1
                elif ch == close_ch:
                    depth -= 1
                    if depth == 0:
                        return i

            else:
                if len(string_char) == 3 and s[i:i + 3] == string_char:
                    in_string = False
                    i += 3
                    continue
                elif (
                    len(string_char) == 1
                    and ch == string_char
                    and self._is_closing_quote(s, i)
                ):
                    in_string = False

            i += 1

        return None


    def _split_by_commas(self, content: str) -> list[str]:
        items = []
        current = ""
        depth = 0
        in_string = False
        string_char = ""
        i = 0

        while i < len(content):
            ch = content[i]

            if not in_string:
                if ch in ('"', "'"):
                    if content[i:i + 3] in ('"""', "'''"):
                        in_string = True
                        string_char = content[i:i + 3]
                        current += content[i:i + 3]
                        i += 3
                        continue
                    else:
                        in_string = True
                        string_char = ch
                        current += ch
                        i += 1
                        continue

                if ch in "([{":
                    depth += 1
                    current += ch
                elif ch in ")]}":
                    depth -= 1
                    current += ch
                elif ch == "," and depth == 0:
                    items.append(current.strip())
                    current = ""
                else:
                    current += ch

            else:
                if (
                    len(string_char) == 3
                    and content[i:i + 3] == string_char
                ):
                    in_string = False
                    current += content[i:i + 3]
                    i += 3
                    continue
                elif (
                    len(string_char) == 1
                    and ch == string_char
                    and self._is_closing_quote(content, i)
                ):
                    in_string = False
                    current += ch
                else:
                    current += ch

            i += 1

        if current.strip():
            items.append(current.strip())

        return items
