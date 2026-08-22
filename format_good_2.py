""""""

__all__ = []

import json


my_thing = {}

other = {
    "start_index": 0,
    "length": len(token),
    "message": (
        "Compound statement chains (if/elif/else, try/except/finally) should have no blank lines between parts, "
        "except after return/yield/exit statements."
    )
}
end = (
    line_offsets[container_node.end_lineno - 1]
    + container_node.end_col_offset
    - 1
)
end = (
    line_offsets[container_node.end_lineno - 1]
    + container_node.end_col_offset
    - 120
)


class MyClass:


    def _build_punc_tree(self, nodes: list):
        """Build parent-child relationships among paired punc nodes."""
        sorted_nodes = sorted(
            nodes,
            key=lambda n: (n['_flat_start'], -n['_flat_end'], n['some_really_long_key_here_and_there'])
        )
        for n in shallowest_first:
            if n['_expand'] and n['_children']:
                if n['type'] not in (
                    "list",
                    "set",
                    "dict",
                    "tuple"
                ):
                    continue


    def _is_dict_subscript(self, node: ast.Subscript) -> bool:
        if isinstance(node.slice, ast.Tuple):
            return False

        if isinstance(node.value, ast.Name):
            name = node.value.id
            if (
                name[0].isupper()
                or name in (
                    "list",
                    "dict",
                    "set",
                    "tuple",
                    "frozenset",
                    "type"
                )
            ):
                return False

        else:
            if top_level_lines:
                ops_correct = all(line.startswith(f"{op_str} ") for line in top_level_lines[1:])

        if not op_texts or len(op_texts) != len(operands):
            if (
                not is_if_context
                and not is_assign_context
                and not is_return_context
            ):
                return flat if not should_expand else current_text

        else:
            if len(string_char) == 3 and line[i:i + 3] == string_char:
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
