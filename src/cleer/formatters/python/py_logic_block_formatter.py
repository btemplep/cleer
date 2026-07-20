"""Logic block multiline formatter module."""

__all__ = ["PyLogicBlockFormatter"]


import re

from cleer.formatters.formatter import Formatter


_ASSIGNMENT_PATTERN = re.compile(r"^(\s*\w[\w\.\[\]\'\"]*\s*=\s*)")
_CONDITION_PATTERN = re.compile(r"^(\s*(?:if|elif|while|assert|return|yield)\s+)")


class PyLogicBlockFormatter(Formatter):
    """Formats boolean logic expressions with `and`/`or` operators.

    Ensures logic blocks are formatted consistently:
    - If ≤2 statements and fits within 80 chars: single line, no outer parens
    - If >2 statements or exceeds 80 chars: multiline with parens, each
      statement on its own line with `and`/`or` at the start of continuation
      lines
    - Removes unnecessary outer parens around single statements
    - Removes extra inner parens wrapping single sub-expressions

    Accepts token types: `function`

    Parameters
    ----------
    max_line_length : int, default=80
        Maximum line length before triggering multiline formatting.

    Examples
    --------

    ```python
    from cleer.formatters.python import PyLogicBlockFormatter

    formatter = PyLogicBlockFormatter()
    result = formatter.format(some_function_token)
    ```
    """
    accepts_token_types = ["file"]


    def __init__(self, max_line_length: int=80) -> None:
        self._max_line_length = max_line_length


    def format(self, token: str) -> str:
        """Format logic block expressions in a function token.

        Parameters
        ----------
        token : str
            Function token to format.

        Examples
        --------

        ```python
        formatter = PyLogicBlockFormatter()
        result = formatter.format(function_token_str)
        ```

        Returns
        -------
        str
            Token with properly formatted logic blocks.
        """
        lines = token.split("\n")
        result_lines: list[str] = []
        i = 0

        while i < len(lines):
            block_lines, consumed = self._try_collect_logic_block(lines, i)
            if block_lines is not None:
                formatted = self._format_logic_block(block_lines)
                result_lines.extend(formatted)
                i += consumed
            else:
                result_lines.append(lines[i])
                i += 1

        return "\n".join(result_lines)


    def inspect(self, token: str) -> str | None:
        """Inspect a token for logic block formatting issues.

        Parameters
        ----------
        token : str
            String token to inspect.

        Examples
        --------

        ```python
        formatter = PyLogicBlockFormatter()
        message = formatter.inspect(function_token_str)
        ```

        Returns
        -------
        str | None
            Error message if logic block formatting is incorrect, `None` otherwise.
        """
        formatted = self.format(token)
        if formatted != token:
            return "Logic block expressions should follow multiline formatting rules."

        return None


    def _try_collect_logic_block(
        self,
        lines: list[str],
        start: int
    ) -> tuple[list[str] | None, int]:
        """Try to collect a logic block starting at the given line index.

        A logic block is either:
        - A single line with `and`/`or` at depth 0
        - A multiline expression in parens that uses `and`/`or`

        Parameters
        ----------
        lines : list[str]
            All lines of the token.
        start : int
            Index of the line to check.

        Returns
        -------
        tuple[list[str] | None, int]
            The collected block lines and number of lines consumed,
            or (None, 0) if no logic block found.
        """
        line = lines[start]
        stripped = line.lstrip()

        if (
            stripped.startswith("#")
            or stripped.startswith("def ")
            or stripped.startswith("class ")
        ):
            return None, 0

        if stripped.startswith("async def "):
            return None, 0

        prefix = self._get_logic_prefix(line)
        if prefix is None:
            return None, 0

        after_prefix = line[len(prefix):]
        rhs_start = after_prefix

        if self._has_logic_operator_at_depth_zero(rhs_start):
            depth = self._paren_depth_change(rhs_start)
            if depth == 0:
                return [line], 1

            block_lines = [line]
            consumed = 1
            j = start + 1
            while j < len(lines) and depth > 0:
                block_lines.append(lines[j])
                depth += self._paren_depth_change(lines[j])
                consumed += 1
                j += 1

            return block_lines, consumed

        unwrapped = self._unwrap_outer_parens(rhs_start.strip())
        if (
            unwrapped != rhs_start.strip()
            and self._has_logic_operator_at_depth_zero(unwrapped)
        ):
            return [line], 1

        open_depth = self._paren_depth_change(rhs_start)
        if open_depth > 0:
            block_lines = [line]
            consumed = 1
            depth = open_depth
            j = start + 1
            while j < len(lines) and depth > 0:
                block_lines.append(lines[j])
                depth += self._paren_depth_change(lines[j])
                consumed += 1
                j += 1

            full_text = "\n".join(block_lines)
            if self._has_logic_operator_at_depth_one(full_text, prefix):
                return block_lines, consumed

        return None, 0


    def _format_logic_block(self, block_lines: list[str]) -> list[str]:
        """Format a collected logic block according to the rules.

        Parameters
        ----------
        block_lines : list[str]
            The lines comprising the logic block.

        Returns
        -------
        list[str]
            The formatted lines for this logic block.
        """
        first_line = block_lines[0]
        indent = first_line[: len(first_line) - len(first_line.lstrip())]
        prefix = self._get_logic_prefix(first_line)
        if prefix is None:
            return block_lines

        is_condition = bool(_CONDITION_PATTERN.match(first_line))
        indent_level = len(indent) // 4
        max_length = 100 if indent_level > 3 else self._max_line_length
        full_text = "\n".join(block_lines)
        after_prefix = full_text[len(prefix):]

        trailing_colon = ""
        rhs_raw = after_prefix.strip()
        is_block_condition = bool(re.match(r"^\s*(?:if|elif|while)\s+", first_line))
        if is_block_condition:
            rhs_raw = self._strip_trailing_colon(rhs_raw)
            trailing_colon = ":"

        rhs = self._unwrap_outer_parens(rhs_raw)
        statements = self._split_statements(rhs)
        statements = [self._normalize_statement(s) for s in statements]
        statements = [self._strip_redundant_parens(s) for s in statements]

        if len(statements) == 1:
            single_line = prefix.rstrip() + " " + statements[0] + trailing_colon
            if len(single_line) <= max_length:
                return [single_line]

        if len(statements) <= 2:
            ops = self._extract_operators(rhs)
            joined = statements[0]
            for idx, stmt in enumerate(statements[1:]):
                op = ops[idx] if idx < len(ops) else "or"
                joined += " " + op + " " + stmt

            single_line = prefix.rstrip() + " " + joined + trailing_colon
            if len(single_line) <= max_length:
                return [single_line]

        ops = self._extract_operators(rhs)
        continuation_indent = indent + "    "
        result = [prefix.rstrip() + " ("]
        for idx, stmt in enumerate(statements):
            expanded_stmt = self._expand_statement(stmt, continuation_indent)
            if idx == 0:
                result.extend(
                    [
                        continuation_indent + l if i == 0 else l for i,
                        l in enumerate(expanded_stmt)
                    ]
                )
            else:
                op = ops[idx - 1] if idx - 1 < len(ops) else "or"
                first_line = continuation_indent + op + " " + expanded_stmt[0].lstrip()
                result.append(first_line)
                result.extend(expanded_stmt[1:])

        result.append(indent + ")" + trailing_colon)

        return result


    def _expand_statement(self, stmt: str, base_indent: str) -> list[str]:
        """Recursively expand a statement if it contains logic operators."""
        inner = self._unwrap_outer_parens(stmt.strip())
        sub_statements = self._split_statements(inner)

        if len(sub_statements) <= 1:
            return [stmt]

        sub_ops = self._extract_operators(inner)
        inner_indent = base_indent + "    "

        lines = ["("]
        for idx, sub in enumerate(sub_statements):
            expanded = self._expand_statement(sub, inner_indent)
            if idx == 0:
                lines.extend(
                    [
                        inner_indent + l if i == 0 else l for i,
                        l in enumerate(expanded)
                    ]
                )
            else:
                op = sub_ops[idx - 1] if idx - 1 < len(sub_ops) else "or"
                first_line = inner_indent + op + " " + expanded[0].lstrip()
                lines.append(first_line)
                lines.extend(expanded[1:])

        lines.append(base_indent + ")")

        return lines


    def _has_nested_logic(self, stmt: str) -> bool:
        """Check if a statement has nested and/or that needs expansion."""
        depth = 0
        i = 0
        in_single = False
        in_double = False

        while i < len(stmt):
            if stmt[i] == "\\" and (in_single or in_double):
                i += 2
                continue

            if stmt[i] == "'" and not in_double:
                in_single = not in_single
                i += 1
                continue

            if stmt[i] == '"' and not in_single:
                in_double = not in_double
                i += 1
                continue

            if not in_single and not in_double:
                if stmt[i] in "([{":
                    depth += 1
                elif stmt[i] in ")]}":
                    depth -= 1
                elif depth == 0:
                    remaining = stmt[i:]
                    if remaining.startswith(" and ") or remaining.startswith(" or "):
                        return True

            i += 1

        return False


    def _strip_trailing_colon(self, text: str) -> str:
        """Strip trailing colon from a condition expression.

        Handles both single-line `condition:` and multiline where the colon
        is at the end after closing parens.

        Parameters
        ----------
        text : str
            The expression text that may end with a colon.

        Returns
        -------
        str
            Text with trailing colon removed.
        """
        stripped = text.rstrip()
        if stripped.endswith(":"):
            return stripped[:-1].rstrip()

        return text


    def _normalize_statement(self, statement: str) -> str:
        """Collapse a multiline statement into a single line.

        Joins lines and collapses internal whitespace while preserving
        multiline content inside nested parentheses/brackets/braces that
        contain 3 or more comma-separated elements (since paired punctuation
        would re-expand them).

        Parameters
        ----------
        statement : str
            A statement that may span multiple lines.

        Returns
        -------
        str
            Single-line version of the statement, with multi-element paired
            punctuation content preserved as-is.
        """
        if "\n" not in statement:
            return statement.strip()

        result = []
        i = 0
        text = statement

        while i < len(text):
            if text[i] in "([{":
                close_map = {
                    "(": ")",
                    "[": "]",
                    "{": "}"
                }
                open_char = text[i]
                close_char = close_map[open_char]
                close_pos = self._find_close_in_text(
                    text,
                    i,
                    open_char,
                    close_char
                )
                if close_pos != -1:
                    inner = text[i + 1:close_pos]
                    if "\n" in inner and self._has_multiple_elements(inner):
                        result.append(text[i:close_pos + 1])
                        i = close_pos + 1
                    else:
                        collapsed = self._collapse_whitespace(inner)
                        result.append(open_char + collapsed + close_char)
                        i = close_pos + 1

                else:
                    result.append(text[i])
                    i += 1

            elif text[i] == "\n":
                j = i + 1
                while (
                    j < len(text)
                    and text[j] in (
                        " ",
                        "\t",
                        "\n"
                    )
                ):
                    j += 1

                result.append(" ")
                i = j
            elif text[i] in (
                " ",
                "\t"
            ):
                j = i + 1
                while (
                    j < len(text)
                    and text[j] in (
                        " ",
                        "\t"
                    )
                ):
                    j += 1

                if j < len(text) and text[j] == "\n":
                    i = j
                else:
                    result.append(" ")
                    i = j

            else:
                result.append(text[i])
                i += 1

        return "".join(result).strip()


    def _find_close_in_text(
        self,
        text: str,
        open_pos: int,
        open_char: str,
        close_char: str
    ) -> int:
        """Find the matching closing character in text."""
        depth = 1
        i = open_pos + 1
        in_single = False
        in_double = False

        while i < len(text):
            if text[i] == "\\" and (in_single or in_double):
                i += 2
                continue

            if text[i] == "'" and not in_double:
                in_single = not in_single
            elif text[i] == '"' and not in_single:
                in_double = not in_double
            elif not in_single and not in_double:
                if text[i] == open_char:
                    depth += 1
                elif text[i] == close_char:
                    depth -= 1
                    if depth == 0:
                        return i

            i += 1

        return -1


    def _has_multiple_elements(self, inner: str) -> bool:
        """Check if inner content has 2+ comma-separated elements at depth 0.

        Returns False for comprehension/generator expressions since those
        are handled differently by paired punctuation.
        """
        depth = 0
        has_comma = False
        in_single = False
        in_double = False
        has_for_keyword = False

        for i, ch in enumerate(inner):
            if ch == "\\" and (in_single or in_double):
                continue

            if ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '"' and not in_single:
                in_double = not in_double
            elif not in_single and not in_double:
                if ch in "([{":
                    depth += 1
                elif ch in ")]}":
                    depth -= 1
                elif depth == 0:
                    if ch == ",":
                        has_comma = True

                    remaining = inner[i:]
                    if (
                        remaining.startswith("for ")
                        or remaining.startswith("for\n")
                    ):
                        before_char = inner[i - 1] if i > 0 else " "
                        if before_char in (
                            " ",
                            "\n"
                        ):
                            has_for_keyword = True

        if has_for_keyword:
            return False

        return has_comma


    def _collapse_whitespace(self, text: str) -> str:
        """Collapse whitespace in text to single spaces."""
        result = []
        i = 0

        while i < len(text):
            if text[i] in (
                " ",
                "\t",
                "\n"
            ):
                j = i + 1
                while (
                    j < len(text)
                    and text[j] in (
                        " ",
                        "\t",
                        "\n"
                    )
                ):
                    j += 1

                if result and j < len(text):
                    result.append(" ")

                i = j
            else:
                result.append(text[i])
                i += 1

        return "".join(result)


    def _get_logic_prefix(self, line: str) -> str | None:
        """Get the prefix of a logic line (assignment target or condition keyword).

        Parameters
        ----------
        line : str
            The line to check.

        Returns
        -------
        str | None
            The prefix string including trailing space, or None if not a logic line.
        """
        m = _ASSIGNMENT_PATTERN.match(line)
        if m:
            return m.group(1)

        m = _CONDITION_PATTERN.match(line)
        if m:
            return m.group(1)

        return None


    def _has_logic_operator_at_depth_zero(self, text: str) -> bool:
        """Check if text contains `and`/`or` at paren/bracket depth 0.

        Parameters
        ----------
        text : str
            Text to check.

        Returns
        -------
        bool
            True if `and` or `or` found at depth 0.
        """
        depth = 0
        i = 0
        in_string = None

        while i < len(text):
            ch = text[i]

            if in_string:
                if ch == "\\" and i + 1 < len(text):
                    i += 2
                    continue

                if ch == in_string:
                    if text[i:i + 3] == in_string * 3:
                        i += 3
                    else:
                        i += 1

                    in_string = None
                    continue

                i += 1
                continue

            if ch in (
                "\"",
                "'"
            ):
                if text[i:i + 3] == ch * 3:
                    in_string = ch
                    i += 3
                else:
                    in_string = ch
                    i += 1

                continue

            if ch in (
                "(",
                "[",
                "{"
            ):
                depth += 1
            elif ch in (
                ")",
                "]",
                "}"
            ):
                depth -= 1

            if depth == 0:
                if (
                    text[i:i + 4] == " and"
                    and (
                        i + 4 >= len(text)
                        or not text[i + 4].isalnum()
                        and text[i + 4] != "_"
                    )
                ):
                    return True

                if (
                    text[i:i + 3] == " or"
                    and (
                        i + 3 >= len(text)
                        or not text[i + 3].isalnum()
                        and text[i + 3] != "_"
                    )
                ):
                    return True

            i += 1

        return False


    def _has_logic_operator_at_depth_one(self, text: str, prefix: str) -> bool:
        """Check if text has `and`/`or` at depth 1 (inside one layer of parens).

        This is used for multiline blocks that are already wrapped in parens.

        Parameters
        ----------
        text : str
            Full text of the block.
        prefix : str
            The logic prefix to skip past.

        Returns
        -------
        bool
            True if `and` or `or` found at depth 1.
        """
        after = text[len(prefix):]

        return self._has_logic_operator_at_depth_zero(self._unwrap_outer_parens(after.strip()))


    def _paren_depth_change(self, text: str) -> int:
        """Calculate net paren/bracket depth change for a line.

        Parameters
        ----------
        text : str
            Line of text.

        Returns
        -------
        int
            Net depth change (positive = more opens than closes).
        """
        depth = 0
        in_string = None
        i = 0

        while i < len(text):
            ch = text[i]

            if in_string:
                if ch == "\\" and i + 1 < len(text):
                    i += 2
                    continue

                if ch == in_string:
                    if text[i:i + 3] == in_string * 3:
                        i += 3
                    else:
                        i += 1

                    in_string = None
                    continue

                i += 1
                continue

            if ch in (
                "\"",
                "'"
            ):
                if text[i:i + 3] == ch * 3:
                    in_string = ch
                    i += 3
                else:
                    in_string = ch
                    i += 1

                continue

            if ch in (
                "(",
                "[",
                "{"
            ):
                depth += 1
            elif ch in (
                ")",
                "]",
                "}"
            ):
                depth -= 1

            i += 1

        return depth


    def _unwrap_outer_parens(self, text: str) -> str:
        """Remove outer parentheses from text if they wrap the entire expression.

        Parameters
        ----------
        text : str
            Text potentially wrapped in parens.

        Returns
        -------
        str
            Text with outer parens removed if they wrapped everything.
        """
        text = text.strip()
        if not text.startswith("("):
            return text

        depth = 0
        i = 0
        in_string = None

        while i < len(text):
            ch = text[i]

            if in_string:
                if ch == "\\" and i + 1 < len(text):
                    i += 2
                    continue

                if ch == in_string:
                    if text[i:i + 3] == in_string * 3:
                        i += 3
                    else:
                        i += 1

                    in_string = None
                    continue

                i += 1
                continue

            if ch in (
                "\"",
                "'"
            ):
                if text[i:i + 3] == ch * 3:
                    in_string = ch
                    i += 3
                else:
                    in_string = ch
                    i += 1

                continue

            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    if i == len(text) - 1:
                        return self._unwrap_outer_parens(text[1:-1].strip())

                    return text

            i += 1

        return text


    def _split_statements(self, rhs: str) -> list[str]:
        """Split a logic expression into statements by top-level `and`/`or`.

        Parameters
        ----------
        rhs : str
            The right-hand side expression (outer parens already removed).

        Returns
        -------
        list[str]
            Individual statements.
        """
        statements: list[str] = []
        current = ""
        depth = 0
        i = 0
        in_string = None
        text = rhs.strip()

        while i < len(text):
            ch = text[i]

            if in_string:
                if ch == "\\" and i + 1 < len(text):
                    current += ch + text[i + 1]
                    i += 2
                    continue

                if ch == in_string:
                    if text[i:i + 3] == in_string * 3:
                        current += text[i:i + 3]
                        i += 3
                    else:
                        current += ch
                        i += 1

                    in_string = None
                    continue

                current += ch
                i += 1
                continue

            if ch in (
                "\"",
                "'"
            ):
                if text[i:i + 3] == ch * 3:
                    in_string = ch
                    current += text[i:i + 3]
                    i += 3
                else:
                    in_string = ch
                    current += ch
                    i += 1

                continue

            if ch in (
                "(",
                "[",
                "{"
            ):
                depth += 1
                current += ch
                i += 1
                continue
            elif ch in (
                ")",
                "]",
                "}"
            ):
                depth -= 1
                current += ch
                i += 1
                continue

            if depth == 0:
                if text[i:i + 5] == " and " or (text[i:i + 4] == " and" and i + 4 == len(text)):
                    statements.append(current.strip())
                    current = ""
                    i += 5
                    continue
                elif text[i:i + 4] == " or " or (text[i:i + 3] == " or" and i + 3 == len(text)):
                    statements.append(current.strip())
                    current = ""
                    i += 4
                    continue
                elif i == 0 and text[0:4] == "and ":
                    current = ""
                    i += 4
                    continue
                elif i == 0 and text[0:3] == "or ":
                    current = ""
                    i += 3
                    continue

            current += ch
            i += 1

        if current.strip():
            statements.append(current.strip())

        return statements


    def _extract_operators(self, rhs: str) -> list[str]:
        """Extract the `and`/`or` operators between statements.

        Parameters
        ----------
        rhs : str
            The right-hand side expression (outer parens already removed).

        Returns
        -------
        list[str]
            List of operators (`"and"` or `"or"`) in order.
        """
        operators: list[str] = []
        depth = 0
        i = 0
        in_string = None
        text = rhs.strip()

        while i < len(text):
            ch = text[i]

            if in_string:
                if ch == "\\" and i + 1 < len(text):
                    i += 2
                    continue

                if ch == in_string:
                    if text[i:i + 3] == in_string * 3:
                        i += 3
                    else:
                        i += 1

                    in_string = None
                    continue

                i += 1
                continue

            if ch in (
                "\"",
                "'"
            ):
                if text[i:i + 3] == ch * 3:
                    in_string = ch
                    i += 3
                else:
                    in_string = ch
                    i += 1

                continue

            if ch in (
                "(",
                "[",
                "{"
            ):
                depth += 1
            elif ch in (
                ")",
                "]",
                "}"
            ):
                depth -= 1

            if depth == 0:
                if text[i:i + 5] == " and " or (text[i:i + 4] == " and" and i + 4 == len(text)):
                    operators.append("and")
                    i += 5
                    continue
                elif text[i:i + 4] == " or " or (text[i:i + 3] == " or" and i + 3 == len(text)):
                    operators.append("or")
                    i += 4
                    continue

            i += 1

        return operators


    def _strip_redundant_parens(self, statement: str) -> str:
        """Remove redundant outer parens from a single statement.

        Only removes parens if they wrap a single expression (no top-level
        comma or operator inside).

        Parameters
        ----------
        statement : str
            A single statement that may have redundant parens.

        Returns
        -------
        str
            Statement with redundant parens removed.
        """
        s = statement.strip()
        if not s.startswith("(") or not s.endswith(")"):
            return s

        depth = 0
        i = 0
        in_string = None

        while i < len(s):
            ch = s[i]

            if in_string:
                if ch == "\\" and i + 1 < len(s):
                    i += 2
                    continue

                if ch == in_string:
                    if s[i:i + 3] == in_string * 3:
                        i += 3
                    else:
                        i += 1

                    in_string = None
                    continue

                i += 1
                continue

            if ch in (
                "\"",
                "'"
            ):
                if s[i:i + 3] == ch * 3:
                    in_string = ch
                    i += 3
                else:
                    in_string = ch
                    i += 1

                continue

            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and i < len(s) - 1:
                    return s

            i += 1

        inner = s[1:-1].strip()
        if self._has_logic_operator_at_depth_zero(inner):
            return s

        if "," in inner:
            comma_depth = 0
            ci = 0
            c_in_string = None
            while ci < len(inner):
                c_ch = inner[ci]
                if c_in_string:
                    if c_ch == "\\" and ci + 1 < len(inner):
                        ci += 2
                        continue

                    if c_ch == c_in_string:
                        if inner[ci:ci + 3] == c_in_string * 3:
                            ci += 3
                        else:
                            ci += 1

                        c_in_string = None
                        continue

                    ci += 1
                    continue

                if c_ch in (
                    "\"",
                    "'"
                ):
                    if inner[ci:ci + 3] == c_ch * 3:
                        c_in_string = c_ch
                        ci += 3
                    else:
                        c_in_string = c_ch
                        ci += 1

                    continue

                if c_ch in (
                    "(",
                    "[",
                    "{"
                ):
                    comma_depth += 1
                elif c_ch in (
                    ")",
                    "]",
                    "}"
                ):
                    comma_depth -= 1
                elif c_ch == "," and comma_depth == 0:
                    return s

                ci += 1

        return inner
