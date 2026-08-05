"""Python type hint formatter module."""

__all__ = ["PythonTypeHintFormatter"]


import re
from typing import Tuple

from cleer.formatters.formatter import Formatter


class PythonTypeHintFormatter(Formatter):
    """Format type annotations by flattening then selectively expanding.

    First flattens the type annotation to a single line. Then expands
    if any non-nested segment exceeds 40 characters or any section is
    more than 2 bracket levels deep.

    Parameters
    ----------
    max_length : int, default=40
        Maximum length for a non-nested segment before expansion.
    max_depth : int, default=2
        Maximum bracket nesting depth before expansion.

    Examples
    --------

    ```python
    from cleer import PythonTypeHintFormatter

    formatter = PythonTypeHintFormatter()
    result = formatter.format("    x: dict[str, list[int]]")
    ```
    """
    accepts_token_types = ["python_type_hint"]


    def __init__(self, max_length: int = 40, max_depth: int = 2):
        self._max_length = max_length
        self._max_depth = max_depth


    def inspect(self, token: str) -> str | None:
        """Inspect a type hint for formatting issues.

        Parameters
        ----------
        token : str
            Token containing prefix and type annotation.

        Returns
        -------
        str | None
            Error message if formatting is incorrect.
            Returns `None` if there is no violation.
        """
        formatted = self.format(token)

        if formatted != token:
            return "Type hint should be formatted according to length and depth rules."

        return None


    def format(self, token: str) -> str:
        """Format a type annotation token.

        Parameters
        ----------
        token : str
            Token from start of line through end of annotation.

        Returns
        -------
        str
            Formatted token with type hint flattened or expanded.
        """
        prefix, type_text = self._split_prefix(token)

        if not type_text:
            return token

        flat = self._flatten(type_text)

        if not self._needs_expansion(flat):
            return prefix + flat

        line_indent = len(token) - len(token.lstrip())
        expanded = self._expand(flat, line_indent)

        return prefix + expanded


    def _split_prefix(self, token: str) -> tuple[str, str]:
        """Split token into prefix and type expression.

        The prefix is everything before the type annotation starts.
        Handles patterns like `x: `, `    a: `, `) -> `, `x = `,
        and bare expressions.

        Parameters
        ----------
        token : str
            Full token text from start of line.

        Returns
        -------
        tuple[str, str]
            Prefix and type expression text.
        """
        first_line = token.split("\n")[0] if "\n" in token else token

        arrow_match = re.search(r"->\s*", first_line)

        if arrow_match:
            split_pos = arrow_match.end()

            return first_line[:split_pos], token[split_pos:]

        colon_match = re.search(r":\s*(?!:)", first_line)

        if colon_match:
            split_pos = colon_match.end()

            return first_line[:split_pos], token[split_pos:]

        equals_match = re.search(r"=\s*", first_line)

        if equals_match:
            split_pos = equals_match.end()

            return first_line[:split_pos], token[split_pos:]

        leading = re.match(r"^(\s*)", first_line)
        prefix = leading.group(1) if leading else ""

        return prefix, token[len(prefix):]


    def _flatten(self, type_text: str) -> str:
        """Flatten a type expression to a single line.

        Parameters
        ----------
        type_text : str
            Type expression possibly spanning multiple lines.

        Returns
        -------
        str
            Single-line type expression with normalized spacing.
        """
        result = re.sub(r"\s+", " ", type_text)
        result = re.sub(r"\s*,\s*", ", ", result)
        result = re.sub(r"\s*\[\s*", "[", result)
        result = re.sub(r"\s*\]", "]", result)
        result = re.sub(r"\|\s*", "| ", result)
        result = re.sub(r"\s*\|", " |", result)
        result = result.strip()

        return result


    def _needs_expansion(self, flat: str) -> bool:
        """Check if a flattened type needs expansion.

        Parameters
        ----------
        flat : str
            Flattened single-line type expression.

        Returns
        -------
        bool
            True if expansion is needed.
        """
        if len(flat) > self._max_length:
            return True

        if self._max_nesting_depth(flat) > self._max_depth:
            return True

        return False


    def _max_nesting_depth(self, text: str) -> int:
        """Get the maximum bracket nesting depth.

        Parameters
        ----------
        text : str
            Type expression text.

        Returns
        -------
        int
            Maximum nesting depth.
        """
        depth = 0
        max_depth = 0

        for char in text:
            if char == "[":
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == "]":
                depth -= 1

        return max_depth


    def _expand(self, flat: str, line_indent: int) -> str:
        """Expand a type expression at the appropriate nesting level.

        Expands at the shallowest level that either exceeds max_length
        or exceeds max_depth.

        Parameters
        ----------
        flat : str
            Flattened type expression.
        line_indent : int
            Leading whitespace of the line (base indentation).

        Returns
        -------
        str
            Expanded type expression.
        """
        segments = self._parse_segments(flat)

        return self._expand_segments(segments, line_indent)


    def _parse_segments(self, text: str) -> list:
        """Parse a type expression into a tree of segments.

        Parameters
        ----------
        text : str
            Flattened type expression.

        Returns
        -------
        list
            Tree structure: each element is either a string (text) or
            a list [name, [children]] where children are comma-separated
            segments that may themselves be trees.
        """
        result, _ = self._parse_at(text, 0)

        return result


    def _parse_at(self, text: str, pos: int) -> tuple[list, int]:
        """Parse segments starting at position.

        Returns
        -------
        tuple[list, int]
            Parsed segments and the position after parsing.
        """
        segments = []
        current = ""

        while pos < len(text):
            char = text[pos]

            if char == "[":
                name = current
                current = ""
                pos += 1
                children, pos = self._parse_children(text, pos)
                segments.append([name, children])
            elif char == "]":
                break
            else:
                current += char
                pos += 1

        if current:
            segments.append(current)

        return segments, pos


    def _parse_children(self, text: str, pos: int) -> tuple[list, int]:
        """Parse comma-separated children inside brackets.

        Returns
        -------
        tuple[list, int]
            List of children (each is a list of segments) and position
            after closing bracket.
        """
        children = []
        current_child = []
        current_text = ""
        depth = 0

        while pos < len(text):
            char = text[pos]

            if char == "[" and depth == 0:
                name = current_text
                current_text = ""
                pos += 1
                sub_children, pos = self._parse_children(text, pos)
                current_child.append([name, sub_children])
            elif char == "[":
                current_text += char
                depth += 1
                pos += 1
            elif char == "]" and depth > 0:
                current_text += char
                depth -= 1
                pos += 1
            elif char == "]" and depth == 0:
                if current_text:
                    current_child.append(current_text)

                children.append(current_child)
                pos += 1

                return children, pos
            elif char == "," and depth == 0:
                if current_text:
                    current_child.append(current_text)

                children.append(current_child)
                current_child = []
                current_text = ""
                pos += 1

                if pos < len(text) and text[pos] == " ":
                    pos += 1
            else:
                current_text += char
                pos += 1

        if current_text:
            current_child.append(current_text)

        if current_child:
            children.append(current_child)

        return children, pos


    def _expand_segments(self, segments: list, prefix_len: int) -> str:
        """Render segments, expanding where needed.

        Parameters
        ----------
        segments : list
            Parsed segment tree.
        prefix_len : int
            Column offset for indentation.

        Returns
        -------
        str
            Rendered type expression.
        """
        parts = []

        for seg in segments:
            if isinstance(seg, str):
                parts.append(seg)
            else:
                name, children = seg
                rendered = self._render_node(name, children, prefix_len)
                parts.append(rendered)

        return "".join(parts)


    def _render_node(
        self,
        name: str,
        children: list,
        base_indent: int
    ) -> str:
        """Render a subscript node, deciding whether to expand.

        Parameters
        ----------
        name : str
            The type name (e.g., "Dict", "List").
        children : list
            List of child segments.
        base_indent : int
            Current indentation column.

        Returns
        -------
        str
            Rendered subscript expression.
        """
        flat_children = []

        for child in children:
            flat_children.append(self._render_flat(child))

        flat = name + "[" + ", ".join(flat_children) + "]"

        if len(flat) <= self._max_length and self._max_nesting_depth(flat) <= self._max_depth:
            return flat

        inner_indent = base_indent + 4
        lines = []

        for i, child in enumerate(children):
            child_text = self._render_child_expanded(child, inner_indent)
            suffix = "," if i < len(children) - 1 else ""
            lines.append(" " * inner_indent + child_text + suffix)

        result = name + "[\n"
        result += "\n".join(lines) + "\n"
        result += " " * base_indent + "]"

        return result


    def _render_child_expanded(
        self,
        child: list,
        base_indent: int
    ) -> str:
        """Render a single child segment, recursively expanding if needed.

        Parameters
        ----------
        child : list
            List of segments for this child.
        base_indent : int
            Current indentation column.

        Returns
        -------
        str
            Rendered child text.
        """
        parts = []

        for seg in child:
            if isinstance(seg, str):
                parts.append(seg)
            else:
                name, sub_children = seg
                rendered = self._render_node(name, sub_children, base_indent)
                parts.append(rendered)

        return "".join(parts)


    def _render_flat(self, child: list) -> str:
        """Render a child as a flat single-line string.

        Parameters
        ----------
        child : list
            List of segments for this child.

        Returns
        -------
        str
            Flat rendered text.
        """
        parts = []

        for seg in child:
            if isinstance(seg, str):
                parts.append(seg)
            else:
                name, sub_children = seg
                flat_children = [self._render_flat(c) for c in sub_children]
                parts.append(name + "[" + ", ".join(flat_children) + "]")

        return "".join(parts)
