"""Python paired punctuation formatter module."""

__all__ = ["PythonPairedPunctuationFormatter"]

import ast
import re

from cleer.formatters.formatter import Formatter


class PythonPairedPunctuationFormatter(Formatter):
    """Format paired punctuation using AST for semantic understanding.

    Receives the entire file, parses it with AST, identifies all nodes
    that contain paired punctuation (calls, lists, dicts, logic expressions,
    etc.), and reformats them according to expansion/collapse rules.

    Processes nodes bottom-up so inner nodes are formatted before outer
    nodes make line-length decisions.

    Parameters
    ----------
    max_line : int, default=80
        Maximum line length before expansion is triggered.
    max_call_flat : int, default=60
        Maximum flat call length (excluding indent) before expansion.
    max_funcdef_flat : int, default=80
        Maximum flat function def length (excluding indent) before expansion.
    """
    accepts_token_types = ["file"]


    def __init__(
        self,
        max_line: int=80,
        max_call_flat: int=60,
        max_funcdef_flat: int=80
    ):
        self._MAX_LINE = max_line
        self._MAX_CALL_FLAT = max_call_flat
        self._MAX_FUNCDEF_FLAT = max_funcdef_flat


    def inspect(self, token: str) -> str | None:
        formatted = self.format(token)
        if formatted != token:
            return "Paired punctuation formatting incorrect."

        return None


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

        nodes = self._collect_formattable_nodes(tree, token)

        if not nodes:
            return token

        nodes.sort(key=lambda n: (-n['depth'], -n['start']))

        doc = token
        applied = set()

        for node_info in nodes:
            node = node_info['node']
            node_type = node_info['type']
            start = node_info['start']
            end = node_info['end']

            key = (node.lineno, node.col_offset, node_type)
            if key in applied:
                continue

            current_text = doc[start:end]
            indent = self._get_indent(doc, start)

            if node_type == "boolop":
                formatted = self._format_boolop(
                    node, current_text, indent
                )
            elif node_type == "if_boolop":
                formatted = self._format_if_boolop(
                    node, current_text, indent,
                    node_info.get("parent_node")
                )
            elif node_type == "assign_boolop":
                formatted = self._format_assign_boolop(
                    node, current_text, indent
                )
            elif node_type == "return_boolop":
                formatted = self._format_return_boolop(
                    node, current_text, indent
                )
            elif node_type == "call":
                formatted = self._format_call(
                    node, current_text, indent
                )
            elif node_type == "chain":
                formatted = self._format_chain(
                    node, current_text, indent
                )
            elif node_type in ("list", "set"):
                formatted = self._format_container(
                    node, current_text, indent,
                    is_nested=node_info.get("is_nested", False)
                )
            elif node_type == "dict":
                formatted = self._format_dict(
                    node, current_text, indent
                )
            elif node_type == "tuple":
                formatted = self._format_tuple(
                    node, current_text, indent
                )
            elif node_type == "funcdef":
                formatted = self._format_funcdef(
                    node, current_text, indent
                )
            elif node_type == "subscript":
                formatted = self._format_subscript(
                    node, current_text, indent
                )
            else:
                continue

            if formatted != current_text:
                size_diff = len(formatted) - len(current_text)
                doc = doc[:start] + formatted + doc[end:]

                applied.add(key)

                for other in nodes:
                    if other is node_info:
                        continue

                    if other['start'] > start:
                        other['start'] += size_diff
                        other['end'] += size_diff
                    elif other['end'] > start:
                        other['end'] += size_diff

        return doc


    def _collect_formattable_nodes(
        self,
        tree: ast.Module,
        document: str
    ) -> list[dict]:
        """Walk the AST and collect nodes that need formatting decisions."""
        nodes = []
        self._walk(tree, document, nodes, depth=0, parent=None)

        return nodes


    def _walk(
        self,
        node: ast.AST,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        """Recursively walk the AST collecting formattable nodes."""
        for child in ast.iter_child_nodes(node):
            self._walk(child, document, nodes, depth + 1, parent=node)

        if isinstance(node, ast.BoolOp):
            self._add_boolop(node, document, nodes, depth, parent)
        elif isinstance(node, ast.Assign):
            if isinstance(node.value, ast.BoolOp):
                self._add_assign_boolop(node, document, nodes, depth)
        elif isinstance(node, ast.Return):
            if node.value and isinstance(node.value, ast.BoolOp):
                self._add_return_boolop(node, document, nodes, depth)
        elif isinstance(node, ast.Call):
            if self._is_chain_end(node, parent):
                self._add_chain(node, document, nodes, depth, parent)
            else:
                self._add_call(node, document, nodes, depth, parent)
        elif isinstance(node, (ast.List, ast.Set)):
            self._add_container(node, document, nodes, depth, parent)
        elif isinstance(node, ast.Dict):
            self._add_dict(node, document, nodes, depth, parent)
        elif isinstance(node, ast.Tuple):
            self._add_tuple(node, document, nodes, depth, parent)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._add_funcdef(node, document, nodes, depth, parent)
        elif isinstance(node, ast.Subscript):
            self._add_subscript(node, document, nodes, depth, parent)


    def _add_boolop(
        self,
        node: ast.BoolOp,
        document: str,
        nodes: list,
        depth: int,
        parent: ast.AST=None
    ):
        """Add a BoolOp node for formatting."""
        if not hasattr(node, 'lineno'):
            return

        if isinstance(parent, ast.BoolOp):
            return

        if isinstance(parent, (ast.If, ast.While)):
            if node is parent.test:
                stmt_start = self._offset(
                    document, parent.lineno, parent.col_offset
                )
                lines = document.split("\n")
                stmt_line_idx = parent.lineno - 1
                for li in range(stmt_line_idx, len(lines)):
                    if lines[li].rstrip().endswith(":"):
                        end = self._offset(document, li + 1, 0) + len(lines[li].rstrip())
                        break
                else:
                    end = self._offset(
                        document, node.end_lineno, node.end_col_offset
                    )

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
        if not hasattr(node, 'lineno'):
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
        if not hasattr(node, 'lineno'):
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
        if not hasattr(root, 'lineno'):
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
        """Walk down the chain to find the root (first call)."""
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

        if not hasattr(node, 'lineno'):
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
        if not hasattr(node, 'lineno'):
            return

        elts = getattr(node, 'elts', [])
        if not elts:
            return

        if isinstance(parent, (ast.For, ast.AsyncFor)):
            return

        start = self._offset(document, node.lineno, node.col_offset)
        end = self._offset(document, node.end_lineno, node.end_col_offset)

        is_nested = isinstance(
            parent, (ast.Dict, ast.List, ast.Set, ast.Tuple)
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
        if not hasattr(node, 'lineno'):
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
        if not hasattr(node, 'lineno'):
            return

        if not node.elts:
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
        if not hasattr(node, 'lineno'):
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
        sig_end = self._find_colon_line(document, node.lineno, body_start_line)

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
        """Add a Subscript node for formatting (type annotations like Dict[...])."""
        if not hasattr(node, 'lineno'):
            return

        if not isinstance(node.slice, ast.Tuple):
            return

        if not node.slice.elts:
            return

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
        op_str = "or" if isinstance(node.op, ast.Or) else "and"
        num_parts = len(node.values)

        flat = self._flatten(current_text)
        flat_len = len(flat)
        indent_len = len(indent)

        should_expand = (
            num_parts > 2
            or flat_len > 60
            or flat_len + indent_len > self._MAX_LINE
        )

        if not should_expand:
            if "\n" not in current_text:
                return current_text

            return flat

        if "\n" in current_text:
            return current_text

        return current_text


    def _is_correctly_expanded_boolop(
        self,
        text: str,
        indent: str,
        op_str: str
    ) -> bool:
        """Check if a BoolOp is already correctly expanded."""
        if "\n" not in text:
            return False

        inner_indent = indent + "    "
        lines = text.split("\n")

        for line in lines:
            if not line.strip():
                continue

            if not line.startswith(inner_indent):
                return False

            content = line[len(inner_indent):]
            if not (
                content == content.lstrip()
                or content.startswith(f"{op_str} ")
                or content.startswith("and ")
                or content.startswith("or ")
                or content.startswith("    ")
            ):
                return False

        return True


    def _get_boolop_parts(
        self,
        node: ast.BoolOp,
        current_text: str
    ) -> list[str]:
        """Get the source text for each operand of a BoolOp."""
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
                if len(string_char) == 3 and remaining[i:i + 3] == string_char:
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
        """Check if a BoolOp value is a sub-BoolOp with different operator."""
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
                if ch == string_char and self._is_closing_quote(remaining, i):
                    in_string = False

            i += 1

        if last_split < len(remaining):
            sub_parts.append(remaining[last_split:].strip())

        if len(sub_parts) <= 1:
            return f"({inner_content})"

        lines = ["("]
        for j, sp in enumerate(sub_parts):
            if j == 0:
                lines.append(f"{inner_indent}{sp}")
            else:
                lines.append(f"{inner_indent}{inner_op} {sp}")

        lines.append(f"{indent})")

        return "\n".join(lines)


    def _format_if_boolop(
        self,
        node: ast.BoolOp,
        current_text: str,
        indent: str,
        parent_node: ast.AST
    ) -> str:
        """Format a BoolOp that is the condition of if/elif/while."""
        flat = self._flatten(current_text)
        flat_len = len(flat)
        indent_len = len(indent)

        op_str = "or" if isinstance(node.op, ast.Or) else "and"
        num_parts = len(node.values)

        should_expand = (
            num_parts > 2
            or flat_len > 60
            or flat_len + indent_len > self._MAX_LINE
        )

        if not should_expand:
            return flat

        if "\n" in current_text:
            first_line = current_text.split("\n")[0].strip()
            last_line = current_text.split("\n")[-1].strip()
            if first_line.endswith("(") and last_line == "):":
                return current_text

        keyword = "if"
        if isinstance(parent_node, ast.While):
            keyword = "while"
        elif isinstance(parent_node, ast.If):
            lines = current_text.split("\n")
            first_stripped = lines[0].strip()
            if first_stripped.startswith("elif"):
                keyword = "elif"

        inner_indent = indent + "    "
        parts = self._get_boolop_parts(node, current_text)

        if not parts:
            return current_text

        condition_flat = self._flatten(current_text)
        condition_flat = self._collapse_paren_spaces(condition_flat)
        kw_end = condition_flat.find(keyword) + len(keyword)
        after_kw = condition_flat[kw_end:].strip()
        if after_kw.startswith("(") and after_kw.endswith("):"):
            after_kw = after_kw[1:-2].strip()

        if after_kw.endswith(":"):
            after_kw = after_kw[:-1].strip()

        after_kw = self._normalize_operators(after_kw)
        cond_parts = self._split_boolop_by_op(after_kw, op_str)

        if not cond_parts:
            return current_text

        result_lines = [f"{keyword} ("]

        for i, part in enumerate(cond_parts):
            if i == 0:
                result_lines.append(f"{inner_indent}{part}")
            else:
                if self._is_subgroup_boolop(node.values[i], node.op):
                    sub_formatted = self._format_boolop_subgroup(
                        node.values[i], part, inner_indent, op_str
                    )
                    result_lines.append(f"{inner_indent}{op_str} {sub_formatted}")
                else:
                    result_lines.append(f"{inner_indent}{op_str} {part}")

        result_lines.append(f"{indent}):")

        return "\n".join(result_lines)


    def _split_boolop_by_op(self, text: str, op_str: str) -> list[str]:
        """Split a boolean expression by its top-level operator."""
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
        boolop = node.value
        op_str = "or" if isinstance(boolop.op, ast.Or) else "and"
        num_parts = len(boolop.values)

        flat = self._flatten(current_text)
        flat_len = len(flat)
        indent_len = len(indent)

        should_expand = (
            num_parts > 2
            or flat_len > 60
            or flat_len + indent_len > self._MAX_LINE
        )

        if not should_expand:
            return flat

        if "\n" in current_text:
            first_line = current_text.split("\n")[0].strip()
            last_line = current_text.split("\n")[-1].strip()
            if first_line.endswith("(") and last_line == ")":
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
            if i == 0:
                lines.append(f"{inner_indent}{part}")
            else:
                lines.append(f"{inner_indent}{op_str} {part}")

        lines.append(f"{indent})")

        return "\n".join(lines)


    def _format_return_boolop(
        self,
        node: ast.Return,
        current_text: str,
        indent: str
    ) -> str:
        """Format a return statement whose value is a BoolOp."""
        boolop = node.value
        op_str = "or" if isinstance(boolop.op, ast.Or) else "and"
        num_parts = len(boolop.values)

        flat = self._flatten(current_text)
        flat_len = len(flat)
        indent_len = len(indent)

        should_expand = (
            num_parts > 2
            or flat_len > 60
            or flat_len + indent_len > self._MAX_LINE
        )

        if not should_expand:
            return flat

        if "\n" in current_text:
            first_line = current_text.split("\n")[0].strip()
            last_line = current_text.split("\n")[-1].strip()
            if first_line.endswith("(") and last_line == ")":
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


    def _format_chain(
        self,
        node: ast.Call,
        current_text: str,
        indent: str
    ) -> str:
        """Format a chained method call.

        Rules:
        - Flatten first
        - Expand all (except 0-arg calls) if any call meets expansion
          criteria or total > 80 chars
        """
        flat = self._flatten(current_text)
        flat = self._collapse_paren_spaces(flat)
        flat_len = len(flat)
        indent_len = len(indent)

        segments = self._get_chain_segments(node)

        if not segments:
            return current_text

        any_needs_expand = False
        for seg in segments:
            if seg['args']:
                args_str = ", ".join(seg['args'])
                seg_len = len(seg['method']) + 1 + len(args_str) + 1
                if (
                    seg_len > self._MAX_CALL_FLAT
                    or len(seg['args']) > 4
                    or (
                        any(self._is_kwarg_str(a) for a in seg['args'])
                        and len(seg['args']) > 2
                    )
                ):
                    any_needs_expand = True
                    break

        should_expand = (
            any_needs_expand
            or flat_len > self._MAX_LINE
            or flat_len + indent_len > self._MAX_LINE
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
                if not seg['args']:
                    result_parts.append(f"{seg['method']}()")
                else:
                    args_str = ", ".join(seg['args'])
                    seg_flat_len = len(seg['method']) + 1 + len(args_str) + 1
                    if seg_flat_len <= self._MAX_CALL_FLAT and not any(self._is_kwarg_str(a) for a in seg['args']):
                        result_parts.append(f"{seg['method']}({args_str})")
                    else:
                        lines = [f"{seg['method']}("]
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
                    args_str = ", ".join(seg['args'])
                    result_parts.append(f"{method_call}(\n{inner_indent}{args_str}\n{indent})")

        return "".join(result_parts)


    def _get_chain_segments(self, node: ast.Call) -> list[dict]:
        """Extract chain segments from outermost to innermost call."""
        segments = []
        current = node

        while True:
            if isinstance(current, ast.Call):
                if isinstance(current.func, ast.Attribute):
                    method_name = current.func.attr
                    args = [
                        a for a in self._get_call_arg_strs(current)
                    ]
                    segments.append(
                        {
                            "method": method_name,
                            "args": args
                        }
                    )
                    current = current.func.value
                elif isinstance(current.func, ast.Name):
                    args = self._get_call_arg_strs(current)
                    segments.append(
                        {
                            "method": current.func.id,
                            "args": args
                        }
                    )
                    break
                else:
                    break
            else:
                break

        segments.reverse()

        return segments


    def _get_call_arg_strs(self, node: ast.Call) -> list[str]:
        """Get string representations of a call's arguments from AST."""
        result = []

        for arg in node.args:
            result.append(ast.unparse(arg))

        for kw in node.keywords:
            if kw.arg:
                result.append(f"{kw.arg}={ast.unparse(kw.value)}")
            else:
                result.append(f"**{ast.unparse(kw.value)}")

        return result


    def _format_call(
        self,
        node: ast.Call,
        current_text: str,
        indent: str
    ) -> str:
        """Format a function call."""
        if self._contains_ternary(node):
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
            if self._is_correctly_expanded(current_text, [], indent, "(", ")"):
                return current_text

            return current_text

        all_args = self._get_call_args(node, current_text)

        if not all_args:
            return current_text

        if len(all_args) == 1 and not self._is_kwarg_str(all_args[0]):
            if not self._inner_would_expand(node, indent + "    "):
                return flat

        func_text = self._get_func_text(node, current_text)
        content_len = len(func_text) + 1 + len(", ".join(all_args)) + 1
        indent_len = len(indent)

        should_expand = (
            content_len > self._MAX_CALL_FLAT
            or content_len + indent_len > self._MAX_LINE
            or len(all_args) > 4
            or (
                any(self._is_kwarg_str(a) for a in all_args)
                and len(all_args) > 2
            )
            or self._any_arg_is_expanded(node)
        )

        if not should_expand:
            return flat

        if self._is_correctly_expanded(current_text, all_args, indent, "(", ")"):
            return current_text

        inner_indent = indent + "    "
        expanded_args = self._get_expanded_args(node, current_text, inner_indent)
        lines = [f"{func_text}("]

        for i, arg in enumerate(expanded_args):
            comma = "," if i < len(expanded_args) - 1 else ""
            if "\n" in arg:
                arg_lines = arg.split("\n")
                lines.append(f"{inner_indent}{arg_lines[0]}{comma}")
                for al in arg_lines[1:]:
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
        elts = getattr(node, 'elts', [])
        if not elts:
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

        content_len = len(open_char) + len(", ".join(items)) + len(close_char)
        indent_len = len(indent)

        has_nested_children = any(
            isinstance(elt, (ast.Dict, ast.List, ast.Set, ast.Tuple))
            and self._node_has_content(elt)
            for elt in elts
        )

        should_expand = (
            is_nested
            or has_nested_children
            or content_len > 30
            or content_len + indent_len > self._MAX_LINE
        )

        if not should_expand:
            return flat

        if self._is_correctly_expanded(current_text, items, indent, open_char, close_char):
            return current_text

        inner_indent = indent + "    "
        lines = [open_char]

        for i, item in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            lines.append(f"{inner_indent}{item}{comma}")

        lines.append(f"{indent}{close_char}")

        return "\n".join(lines)


    def _format_dict(
        self,
        node: ast.Dict,
        current_text: str,
        indent: str
    ) -> str:
        """Format a dict literal — always expand if has content."""
        if not node.keys:
            return current_text

        flat = self._flatten(current_text)
        flat_items = self._split_by_commas(
            flat[flat.find("{") + 1:self._find_matching_paren(flat, flat.find("{"))]
        )

        if not flat_items:
            return current_text

        if self._is_correctly_expanded(current_text, flat_items, indent, "{", "}"):
            return current_text

        inner_indent = indent + "    "
        lines = ["{"]

        for i, item in enumerate(flat_items):
            comma = "," if i < len(flat_items) - 1 else ""
            lines.append(f"{inner_indent}{item}{comma}")

        lines.append(f"{indent}}}")

        return "\n".join(lines)


    def _format_tuple(
        self,
        node: ast.Tuple,
        current_text: str,
        indent: str
    ) -> str:
        """Format a tuple — generally don't expand unless it's a container."""
        return current_text


    def _format_funcdef(
        self,
        node: ast.AST,
        current_text: str,
        indent: str
    ) -> str:
        """Format a function definition signature."""
        flat = self._flatten(current_text)
        flat = self._collapse_paren_spaces(flat)
        flat_len = len(flat)

        args = node.args
        params = self._extract_params(node, current_text)

        if not params:
            return current_text

        should_expand = (
            flat_len > self._MAX_FUNCDEF_FLAT
            or flat_len + len(indent) > 100
            or len(params) > 4
            or (
                any("=" in p for p in params)
                and len(params) > 2
            )
        )

        if not should_expand:
            return flat

        if self._is_correctly_expanded(current_text, params, indent, "(", ")"):
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
        if not isinstance(node.slice, ast.Tuple):
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
            return current_text

        has_nested = any(
            isinstance(elt, ast.Subscript)
            and self._subscript_is_complex(elt)
            for elt in node.slice.elts
        )

        should_expand = (
            has_nested
            or flat_len > 40
            or flat_len + len(indent) > self._MAX_LINE
        )

        if not should_expand:
            return flat

        if self._is_correctly_expanded(current_text, items, indent, "[", "]"):
            return current_text

        value_text = flat[:bracket_pos]
        inner_indent = indent + "    "
        lines = [f"{value_text}["]

        for i, item in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            lines.append(f"{inner_indent}{item}{comma}")

        lines.append(f"{indent}]")

        return "\n".join(lines)


    def _offset(self, document: str, lineno: int, col_offset: int) -> int:
        """Convert a line number and column offset to a character offset."""
        line_start = 0
        for i in range(lineno - 1):
            line_start = document.index("\n", line_start) + 1

        return line_start + col_offset


    def _get_indent(self, document: str, offset: int) -> str:
        """Get the indentation at a given offset."""
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
                return self._offset(document, line_idx + 1, 0) + len(stripped)

        return self._offset(document, body_start_line, 0)


    def _flatten(self, text: str) -> str:
        """Flatten multiline text to single line, preserving strings."""
        result = []
        i = 0
        in_string = False
        string_char = ""
        is_raw = False

        while i < len(text):
            if not in_string:
                prefix_start = i
                while i < len(text) and text[i].lower() in ("f", "r", "b", "u"):
                    i += 1

                if i < len(text) and text[i:i + 3] in ('"""', "'''"):
                    in_string = True
                    string_char = text[i:i + 3]
                    is_raw = any(
                        text[j].lower() == "r"
                        for j in range(prefix_start, i)
                    )
                    result.append(text[prefix_start:i + 3])
                    i += 3
                elif i < len(text) and text[i] in ('"', "'"):
                    in_string = True
                    string_char = text[i]
                    is_raw = any(
                        text[j].lower() == "r"
                        for j in range(prefix_start, i)
                    )
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

                    if has_newline and i < len(text) and text[i] == "#":
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
        """Check if the quote at position i is a closing quote."""
        num_backslashes = 0
        j = i - 1

        while j >= 0 and s[j] == "\\":
            num_backslashes += 1
            j -= 1

        return num_backslashes % 2 == 0


    def _collapse_paren_spaces(self, flat: str) -> str:
        """Remove spaces after ( [ { and before ) ] } outside strings."""
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

                if ch in "([{" and i + 1 < len(flat) and flat[i + 1] == " ":
                    result.append(ch)
                    i += 1
                    while i < len(flat) and flat[i] == " ":
                        i += 1

                    continue

                if ch == " " and i + 1 < len(flat) and flat[i + 1] in ")]}":
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
        """Check if a call contains a ternary (IfExp) as a direct arg."""
        for arg in node.args:
            if isinstance(arg, ast.IfExp):
                return True

        for kw in node.keywords:
            if isinstance(kw.value, ast.IfExp):
                return True

        return False


    def _any_arg_is_expanded(self, node: ast.Call) -> bool:
        """Check if any argument of a call is a multiline-expanded node."""
        for arg in node.args:
            if isinstance(arg, (ast.Dict, ast.List, ast.Set)):
                if self._node_has_content(arg):
                    return True

            if isinstance(arg, ast.Call):
                inner_args = arg.args + [kw.value for kw in arg.keywords]
                if len(inner_args) > 1:
                    return True

        for kw in node.keywords:
            if isinstance(kw.value, (ast.Dict, ast.List, ast.Set)):
                if self._node_has_content(kw.value):
                    return True

        return False


    def _is_chained_method(self, node: ast.Call) -> bool:
        """Check if this call is an inner link of a method chain."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Call):
                return True

        return False


    def _is_chain_root(self, node: ast.Call, parent: ast.AST) -> bool:
        """Check if this call is the root of a method chain."""
        if isinstance(parent, ast.Attribute):
            return True

        return False


    def _is_chain_end(self, node: ast.Call, parent: ast.AST) -> bool:
        """Check if this call is the outermost (last) call in a chain.

        True if: this call is a method on another call result, AND
        is NOT itself used as the value of another Attribute.
        """
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
        """Get arg strings, with inner expansions applied."""
        return self._get_call_args(node, current_text)


    def _is_generator_call(self, node: ast.Call) -> bool:
        """Check if a call has a single generator expression arg."""
        if len(node.args) == 1 and not node.keywords:
            if isinstance(node.args[0], ast.GeneratorExp):
                return True

        return False


    def _normalize_operators(self, text: str) -> str:
        """Ensure 'and' and 'or' keywords have spaces around them."""
        import re

        text = re.sub(r"\)or\(", ") or (", text)
        text = re.sub(r"\)or ", ") or ", text)
        text = re.sub(r" or\(", " or (", text)
        text = re.sub(r"\)and\(", ") and (", text)
        text = re.sub(r"\)and ", ") and ", text)
        text = re.sub(r" and\(", " and (", text)

        return text


    def _subscript_is_complex(self, node: ast.Subscript) -> bool:
        """Check if a subscript is complex enough to trigger parent expansion.

        Complex means: has multiple type params AND at least one is itself
        a subscript, OR has a single param that is a complex subscript.
        """
        if isinstance(node.slice, ast.Tuple):
            if len(node.slice.elts) > 1:
                return any(
                    isinstance(elt, ast.Subscript)
                    for elt in node.slice.elts
                )

            return any(
                isinstance(elt, ast.Subscript)
                and self._subscript_is_complex(elt)
                for elt in node.slice.elts
            )

        if isinstance(node.slice, ast.Subscript):
            return True

        return False


    def _is_comprehension_node(self, node: ast.AST) -> bool:
        """Check if a node is a comprehension (ListComp, SetComp, etc.)."""
        return isinstance(
            node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
        )


    def _has_string_concat_arg(self, flat: str) -> bool:
        """Check if a flattened call has a string concatenation argument.

        Uses the tokenize module to detect adjacent STRING tokens.
        """
        import tokenize
        import io

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
        """Check if content is implicit string concatenation using tokenize."""
        import tokenize
        import io

        try:
            tokens = list(
                tokenize.generate_tokens(io.StringIO(content).readline)
            )
        except tokenize.TokenError:
            return False

        string_tokens = [
            t for t in tokens
            if t.type == tokenize.STRING
        ]

        if len(string_tokens) < 2:
            return False

        for i in range(len(string_tokens) - 1):
            cur = string_tokens[i]
            nxt = string_tokens[i + 1]

            between = content[cur.end[1]:nxt.start[1]]
            if cur.end[0] == nxt.start[0]:
                stripped = between.strip()
                if stripped == "" or stripped == "\\":
                    return True

        return False


    def _get_call_args(
        self,
        node: ast.Call,
        current_text: str
    ) -> list[str]:
        """Extract the argument strings from a call node."""
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
        """Get the function name/expression part of a call."""
        flat = self._flatten(current_text)
        paren_start = flat.find("(")

        if paren_start == -1:
            return flat

        return flat[:paren_start]


    def _is_kwarg_str(self, arg: str) -> bool:
        """Check if an arg string is a keyword argument."""
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
        """Check if a single-arg call's inner argument would expand."""
        if not node.args:
            return False

        arg = node.args[0]

        if isinstance(arg, (ast.Dict, ast.List, ast.Set)):
            elts = getattr(arg, 'elts', None) or getattr(arg, 'keys', None)
            if elts:
                return True

        if isinstance(arg, ast.Call):
            inner_args = len(arg.args) + len(arg.keywords)
            if inner_args > 4:
                return True

            if inner_args > 2 and any(kw for kw in arg.keywords):
                return True

            return False

        if isinstance(arg, ast.JoinedStr):
            return False

        if isinstance(arg, ast.Subscript):
            if isinstance(arg.slice, ast.Tuple) and len(arg.slice.elts) > 2:
                return True

        return False


    def _node_has_content(self, node: ast.AST) -> bool:
        """Check if a container node has any content."""
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
        """Normalize an item's internal whitespace while preserving structure."""
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
        """Re-indent a potentially multiline item to the given base indent.

        The first line is returned without leading indent (caller adds it).
        Subsequent lines get base_indent prepended to their relative indent.
        """
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
        if last_line != expected_close and not last_line.endswith(f"{indent}{close_char}"):
            return False

        for line in lines[1:-1]:
            if line.strip():
                if not line.startswith(inner_indent):
                    return False

        return True


    def _extract_params(
        self,
        node: ast.AST,
        current_text: str
    ) -> list[str]:
        """Extract parameter strings from a function def."""
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
        """Get the def/async def + name part before the opening paren."""
        flat = self._flatten(current_text)
        paren_start = flat.find("(")

        if paren_start == -1:
            return flat

        return flat[:paren_start]


    def _get_funcdef_suffix(self, flat: str) -> str:
        """Get the return annotation + colon after the closing paren."""
        paren_start = flat.find("(")
        if paren_start == -1:
            return ":"

        close_paren = self._find_matching_paren(flat, paren_start)
        if close_paren is None:
            return ":"

        after = flat[close_paren + 1:]

        return after


    def _get_subscript_value(self, current_text: str) -> str:
        """Get the value part before [ in a subscript."""
        flat = self._flatten(current_text)
        bracket_start = flat.find("[")

        if bracket_start == -1:
            return flat

        return flat[:bracket_start]


    def _find_matching_paren(self, s: str, start: int) -> int | None:
        """Find the matching closing bracket for an opener at start."""
        open_ch = s[start]
        close_map = {"(": ")", "[": "]", "{": "}"}
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
        """Split content by top-level commas."""
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
                if len(string_char) == 3 and content[i:i + 3] == string_char:
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
