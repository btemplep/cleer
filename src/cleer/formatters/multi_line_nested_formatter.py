"""Multi-line nested formatter module."""

__all__ = ["MultiLineNestedFormatter"]


import re

from cleer.formatters.formatter import Formatter


class MultiLineNestedFormatter(Formatter):
    """Formats nested paired punctuation into multi-line format.

    Rules:
    - If more than 1 element, each element is on a new line with opening
      and closing brackets/braces on their own lines
    - If any nested paired punctuation has more than one element, each
      parent layer above is expanded to multi-line
    - No space between paired punctuation and inner items (excludes newlines)

    Accepts token types: `paired_punctuation`

    Examples
    --------

    ```python
    from cleer import MultiLineNestedFormatter

    formatter = MultiLineNestedFormatter()
    result = formatter.format('my_func([{"key": [1, 2]}])')
    ```
    """
    accepts_token_types = ["paired_punctuation"]


    def _find_matching_close(
        self,
        text: str,
        pos: int,
        open_char: str,
        close_char: str
    ) -> int:
        """Find matching close bracket, handling strings and nesting."""
        depth = 1
        i = pos + 1
        in_single = False
        in_double = False
        in_triple_single = False
        in_triple_double = False

        while i < len(text):
            remaining = text[i:]

            if in_triple_single:
                if remaining.startswith("'''"):
                    in_triple_single = False
                    i += 3
                    continue

                i += 1
                continue

            if in_triple_double:
                if remaining.startswith('"""'):
                    in_triple_double = False
                    i += 3
                    continue

                i += 1
                continue

            if in_single:
                if text[i] == "\\" and i + 1 < len(text):
                    i += 2
                    continue

                if text[i] == "'":
                    in_single = False

                i += 1
                continue

            if in_double:
                if text[i] == "\\" and i + 1 < len(text):
                    i += 2
                    continue

                if text[i] == '"':
                    in_double = False

                i += 1
                continue

            if remaining.startswith("'''"):
                in_triple_single = True
                i += 3
                continue

            if remaining.startswith('"""'):
                in_triple_double = True
                i += 3
                continue

            if text[i] == "'" and not in_double:
                in_single = True
                i += 1
                continue

            if text[i] == '"' and not in_single:
                in_double = True
                i += 1
                continue

            if text[i] == open_char:
                depth += 1
            elif text[i] == close_char:
                depth -= 1
                if depth == 0:
                    return i

            i += 1

        return -1


    def _split_elements(self, text: str) -> tuple[list[str], list[str]]:
        """Split text by commas and adjacent string literals at the top level."""
        elements = []
        separators = []
        depth = 0
        current = ""
        in_single = False
        in_double = False
        in_triple_single = False
        in_triple_double = False
        i = 0

        while i < len(text):
            remaining = text[i:]

            if in_triple_single:
                current += text[i]
                if remaining.startswith("'''"):
                    current += text[i + 1:i + 3]
                    in_triple_single = False
                    i += 3
                    continue

                i += 1
                continue

            if in_triple_double:
                current += text[i]
                if remaining.startswith('"""'):
                    current += text[i + 1:i + 3]
                    in_triple_double = False
                    i += 3
                    continue

                i += 1
                continue

            if in_single:
                current += text[i]
                if text[i] == "\\" and i + 1 < len(text):
                    current += text[i + 1]
                    i += 2
                    continue

                if text[i] == "'":
                    in_single = False

                i += 1
                continue

            if in_double:
                current += text[i]
                if text[i] == "\\" and i + 1 < len(text):
                    current += text[i + 1]
                    i += 2
                    continue

                if text[i] == '"':
                    in_double = False

                i += 1
                continue

            if remaining.startswith("'''"):
                in_triple_single = True
                current += "'''"
                i += 3
                continue

            if remaining.startswith('"""'):
                in_triple_double = True
                current += '"""'
                i += 3
                continue

            if (
                depth == 0
                and text[i] in (
                    "'",
                    '"',
                    "r",
                    "b",
                    "f"
                )
                and current.strip()
            ):
                is_string_start = False
                check_pos = i
                if (
                    text[i] in "rbf"
                    and check_pos + 1 < len(text)
                    and text[check_pos + 1] in (
                        "'",
                        '"'
                    )
                ):
                    is_string_start = True
                elif text[i] in (
                    "'",
                    '"'
                ):
                    is_string_start = True

                if is_string_start:
                    last_str_end = len(current.rstrip())
                    rstripped = current[:last_str_end]
                    if (
                        rstripped
                        and rstripped[-1] in (
                            "'",
                            '"'
                        )
                    ):
                        elements.append(current.strip())
                        separators.append("")
                        current = ""

                if text[i] in "rbf":
                    current += text[i]
                    i += 1
                    continue

            if text[i] == "'" and not in_double:
                in_single = True
                current += text[i]
                i += 1
                continue

            if text[i] == '"' and not in_single:
                in_double = True
                current += text[i]
                i += 1
                continue

            if text[i] in "([{":
                depth += 1
                current += text[i]
            elif text[i] in ")]}":
                depth -= 1
                current += text[i]
            elif text[i] == "," and depth == 0:
                elements.append(current.strip())
                separators.append(",")
                current = ""
            else:
                current += text[i]

            i += 1

        if current.strip():
            elements.append(current.strip())

        return elements, separators


    def _contains_generator(self, inner: str) -> bool:
        """Check if inner content of parens contains a generator expression."""
        depth = 0
        in_single = False
        in_double = False
        i = 0

        while i < len(inner):
            if inner[i] == "\\" and (in_single or in_double):
                i += 2
                continue

            if inner[i] == "'" and not in_double:
                in_single = not in_single
                i += 1
                continue

            if inner[i] == '"' and not in_single:
                in_double = not in_double
                i += 1
                continue

            if not in_single and not in_double:
                if inner[i] in "([{":
                    depth += 1
                elif inner[i] in ")]}":
                    depth -= 1
                elif depth == 0 and inner[i:].startswith("for "):
                    before = inner[:i].rstrip()
                    if before and not before.endswith(","):
                        return True

            i += 1

        return False


    def _get_bracket_nesting_depth(self, text: str) -> int:
        """Get the maximum square bracket nesting depth in text."""
        max_depth = 0
        depth = 0
        in_single = False
        in_double = False
        i = 0

        while i < len(text):
            if (
                text[i] == "\\"
                and (
                    in_single
                    or in_double
                )
                and i + 1 < len(text)
            ):
                i += 2
                continue

            if text[i] == "'" and not in_double:
                in_single = not in_single
                i += 1
                continue

            if text[i] == '"' and not in_single:
                in_double = not in_double
                i += 1
                continue

            if not in_single and not in_double:
                if text[i] == "[":
                    depth += 1
                    if depth > max_depth:
                        max_depth = depth

                elif text[i] == "]":
                    depth -= 1

            i += 1

        return max_depth


    def _needs_expansion(self, text: str) -> bool:
        """Check if any nested structure has more than 1 element or bracket nesting exceeds 2 levels."""
        if self._get_bracket_nesting_depth(text) > 2:
            return True

        pairs = {
            "(": ")",
            "[": "]",
            "{": "}"
        }
        i = 0
        in_single = False
        in_double = False

        while i < len(text):
            if (
                text[i] == "\\"
                and (
                    in_single
                    or in_double
                )
                and i + 1 < len(text)
            ):
                i += 2
                continue

            if text[i] == "'" and not in_double:
                in_single = not in_single
                i += 1
                continue

            if text[i] == '"' and not in_single:
                in_double = not in_double
                i += 1
                continue

            if (
                not in_single
                and not in_double
                and text[i] in pairs
            ):
                open_char = text[i]
                close_char = pairs[open_char]
                close_pos = self._find_matching_close(
                    text,
                    i,
                    open_char,
                    close_char
                )
                if close_pos != -1:
                    inner = text[i + 1:close_pos]
                    elements, _ = self._split_elements(inner)

                    is_func_call = (
                        open_char == "("
                        and i > 0
                        and (
                            text[i - 1].isalnum()
                            or text[i - 1] in "_)"
                        )
                    )
                    is_type_annotation = (
                        open_char == "["
                        and i > 0
                        and text[i - 1].isalnum()
                    )
                    min_elements = 3 if is_func_call else 2

                    if is_type_annotation:
                        bracket_depth = self._get_bracket_nesting_depth(text[i:close_pos + 1])
                        if bracket_depth <= 2:
                            i = close_pos + 1
                            continue

                    if len(elements) >= min_elements:
                        return True

                    if inner.strip():
                        if self._needs_expansion(inner):
                            return True

            i += 1

        return False


    def _exceeds_line_length(
        self,
        text: str,
        indent_level: int,
        base_indent: int=4,
        max_length: int=100
    ) -> bool:
        """Check if text would exceed max line length at given indent level."""
        indent_chars = indent_level * base_indent
        for line in text.split("\n"):
            if indent_chars + len(line) > max_length:
                return True

        return False


    def _format_nested(
        self,
        text: str,
        indent_level: int,
        base_indent: int=4
    ) -> str:
        """Recursively format nested paired punctuation."""
        pairs = {
            "(": ")",
            "[": "]",
            "{": "}"
        }
        result = ""
        i = 0
        indent = " " * (indent_level * base_indent)
        next_indent = " " * ((indent_level + 1) * base_indent)

        while i < len(text):
            if text[i] in (
                "'",
                '"'
            ):
                if text[i:i + 3] in (
                    "'''",
                    '"""'
                ):
                    quote = text[i:i + 3]
                    end = text.find(quote, i + 3)
                    if end != -1:
                        result += text[i:end + 3]
                        i = end + 3
                        continue

                else:
                    quote_char = text[i]
                    end = i + 1
                    while end < len(text):
                        if text[end] == "\\":
                            end += 1
                        elif text[end] == quote_char:
                            break

                        end += 1

                    result += text[i:end + 1]
                    i = end + 1
                    continue

            if text[i] in pairs:
                open_char = text[i]
                close_char = pairs[open_char]
                close_pos = self._find_matching_close(
                    text,
                    i,
                    open_char,
                    close_char
                )

                if close_pos != -1:
                    inner = text[i + 1:close_pos]
                    elements, separators = self._split_elements(inner)

                    is_func_call = (
                        open_char == "("
                        and i > 0
                        and (
                            text[i - 1].isalnum()
                            or text[i - 1] in "_)"
                        )
                    )
                    is_type_annotation = (
                        open_char == "["
                        and i > 0
                        and (
                            text[i - 1].isalnum()
                            or text[i - 1] == "_"
                        )
                    )
                    is_generator_expr = is_func_call and self._contains_generator(inner)
                    min_elements = 3 if is_func_call else 2

                    should_expand = len(elements) >= min_elements

                    if is_generator_expr:
                        should_expand = False

                    if is_type_annotation:
                        bracket_depth = self._get_bracket_nesting_depth(text[i:close_pos + 1])
                        if bracket_depth <= 2:
                            should_expand = False
                        elif bracket_depth > 2:
                            should_expand = True

                    if not should_expand:
                        if inner.strip() and self._needs_expansion(inner.strip()):
                            should_expand = True

                    if not should_expand and "\n" in inner:
                        if is_func_call and len(elements) == 1:
                            collapsed_single = result + open_char + elements[0].strip() + close_char
                            if not self._exceeds_line_length(
                                collapsed_single,
                                indent_level,
                                base_indent
                            ):
                                result += open_char + elements[0].strip() + close_char
                                i = close_pos + 1
                                continue

                        should_expand = True

                    if not should_expand and len(elements) > 1:
                        parts = []
                        for j, elem in enumerate(elements):
                            if j > 0:
                                if j - 1 < len(separators) and separators[j - 1] == "":
                                    parts.append(" ")
                                else:
                                    parts.append(", ")

                            parts.append(elem.strip())

                        collapsed = result + open_char + "".join(parts) + close_char
                        if self._exceeds_line_length(
                            collapsed,
                            indent_level,
                            base_indent
                        ):
                            should_expand = True

                    if should_expand:
                        has_trailing_comma = len(separators) > len(elements) - 1
                        is_single_item_set = (
                            open_char == "{"
                            and len(elements) == 1
                            and has_trailing_comma
                            and not self._has_top_level_colon(elements[0])
                        )
                        is_single_item_tuple = (
                            open_char == "("
                            and len(elements) == 1
                            and has_trailing_comma
                            and not is_func_call
                        )
                        preserve_trailing = is_single_item_set or is_single_item_tuple
                        result += open_char + "\n"
                        for j, elem in enumerate(elements):
                            formatted_elem = self._format_nested(
                                elem.strip(),
                                indent_level + 1,
                                base_indent
                            )
                            if j < len(elements) - 1:
                                if j < len(separators) and separators[j] == "":
                                    suffix = ""
                                else:
                                    suffix = ","

                            elif preserve_trailing:
                                suffix = ","
                            else:
                                suffix = ""

                            result += next_indent + formatted_elem + suffix + "\n"

                        result += indent + close_char
                    else:
                        parts = []
                        for j, elem in enumerate(elements):
                            if j > 0:
                                if j - 1 < len(separators) and separators[j - 1] == "":
                                    parts.append(" ")
                                else:
                                    parts.append(", ")

                            parts.append(elem.strip())

                        collapsed_inner = "".join(parts)

                        has_trailing_comma = len(separators) > len(elements) - 1
                        is_single_item_set = (
                            open_char == "{"
                            and len(elements) == 1
                            and has_trailing_comma
                            and not self._has_top_level_colon(elements[0])
                        )
                        is_single_item_tuple = (
                            open_char == "("
                            and len(elements) == 1
                            and has_trailing_comma
                            and not is_func_call
                        )
                        if is_single_item_set or is_single_item_tuple:
                            collapsed_inner += ","

                        inner_formatted = self._format_nested(
                            collapsed_inner,
                            indent_level,
                            base_indent
                        )
                        result += open_char + inner_formatted + close_char

                    i = close_pos + 1
                    continue

            result += text[i]
            i += 1

        return result


    def _get_base_indent(self, token: str) -> str:
        """Get the base indentation of the token."""
        first_line = token.split("\n")[0]
        match = re.match(r"^(\s*)", first_line)

        return match.group(1) if match else ""


    def _has_top_level_colon(self, text: str) -> bool:
        """Check if text contains a colon at the top level (not inside strings or brackets)."""
        depth = 0
        in_single = False
        in_double = False
        i = 0

        while i < len(text):
            if text[i] == "\\" and (in_single or in_double):
                i += 2
                continue

            if text[i] == "'" and not in_double:
                in_single = not in_single
            elif text[i] == '"' and not in_single:
                in_double = not in_double
            elif not in_single and not in_double:
                if text[i] in "([{":
                    depth += 1
                elif text[i] in ")]}":
                    depth -= 1
                elif text[i] == ":" and depth == 0:
                    return True

            i += 1

        return False


    def inspect(self, token: str) -> str | None:
        """Inspect a token for improperly nested paired punctuation.

        Parameters
        ----------
        token : str
            String token to inspect.

        Examples
        --------

        ```python
        formatter = MultiLineNestedFormatter()
        message = formatter.inspect('my_func([{"key": [1, 2]}])')
        ```

        Returns
        -------
        str | None
            Error message if formatting is needed, `None` otherwise.
        """
        formatted = self.format(token)
        if formatted != token:
            return (
                "Nested punctuation pairs ('()','[]', and '{}') should have one item per line if there are more than 2 items."
                " Direct parents are also expanded if any of their children are."
            )

        return None


    def format(self, token: str) -> str:
        """Format nested paired punctuation into multi-line format.

        Parameters
        ----------
        token : str
            Token to format.

        Examples
        --------

        ```python
        formatter = MultiLineNestedFormatter()
        result = formatter.format('my_func([{"key": [1, 2]}])')
        ```

        Returns
        -------
        str
            Token with properly formatted nested paired punctuation.
        """
        base_indent = self._get_base_indent(token)
        stripped = token.strip()

        if not any(c in stripped for c in "([{"):
            return token

        base_indent_level = len(base_indent) // 4 if base_indent else 0
        formatted = self._format_nested(stripped, base_indent_level)

        if base_indent:
            return base_indent + formatted

        return formatted
