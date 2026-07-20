"""Code block new lines formatter module."""

__all__ = ["PyCodeBlockNewLinesFormatter"]


import re

from cleer.formatters.formatter import Formatter


BLOCK_START_PATTERN = re.compile(
    r"^( *)(for |if |elif |else:|try:|except |except:|finally:|with |while )",
    re.MULTILINE
)

CONNECTED_KEYWORDS = {
    "elif",
    "else:",
    "except",
    "except:",
    "finally:"
}


class PyCodeBlockNewLinesFormatter(Formatter):
    """Ensures proper newlines around non-function/class code blocks.

    For code blocks including for, if/elif/else, try/except/finally, with,
    and while blocks:
    - A single newline after all code blocks
    - No newlines between connected blocks (if/elif/else, try/except/finally)
    - Nested blocks should only have one newline total after the outermost
      block, unless the next section is in the same code block

    Accepts token types: `function`

    Examples
    --------

    ```python
    from cleer import PyCodeBlockNewLinesFormatter

    formatter = PyCodeBlockNewLinesFormatter()
    result = formatter.format("if x:\\n    pass\\n\\n\\nprint(y)\\n")
    ```
    """
    accepts_token_types = [
        "function",
        "file"
    ]


    def _get_block_end(
        self,
        lines: list[str],
        start_idx: int,
        base_indent: int
    ) -> int:
        """Find the end index of a code block including connected blocks."""
        i = start_idx + 1
        while i < len(lines):
            line = lines[i]
            if line.strip() == "":
                peek = i + 1
                while peek < len(lines) and lines[peek].strip() == "":
                    peek += 1

                if peek < len(lines):
                    peek_line = lines[peek]
                    peek_stripped = peek_line.lstrip()
                    peek_indent = len(peek_line) - len(peek_stripped)
                    if peek_indent > base_indent:
                        i = peek
                        continue

                    if peek_indent == base_indent:
                        first_word = peek_stripped.split()[0] if peek_stripped.split() else ""
                        first_token = peek_stripped.split(":")[0] + ":" if ":" in peek_stripped else first_word
                        if first_word in CONNECTED_KEYWORDS or first_token in CONNECTED_KEYWORDS:
                            i = peek
                            continue

                    break
                else:
                    break

            else:
                stripped = line.lstrip()
                current_indent = len(line) - len(stripped)
                if current_indent <= base_indent:
                    first_word = stripped.split()[0] if stripped.split() else ""
                    first_token = stripped.split(":")[0] + ":" if ":" in stripped else first_word
                    if first_word in CONNECTED_KEYWORDS or first_token in CONNECTED_KEYWORDS:
                        i += 1
                        continue

                    break

            i += 1

        return i


    def _is_block_keyword_line(self, line: str) -> bool:
        """Check if a line starts a code block (non-function/class)."""
        stripped = line.lstrip()

        return bool(re.match(r"(for |if |elif |else:|try:|except |except:|finally:|with |while )", stripped))


    def _is_inside_function_or_class(self, lines: list[str], line_idx: int) -> bool:
        """Check if the line is inside a nested function or class definition.

        When processing a function token, we want to format blocks at the
        top level of that function but not blocks inside nested defs/classes.
        """
        line = lines[line_idx]
        if line.strip() == "":
            return False

        current_indent = len(line) - len(line.lstrip())
        if current_indent == 0:
            return False

        first_line = lines[0]
        first_stripped = first_line.lstrip()
        is_function_token = (
            first_stripped.startswith("def ")
            or first_stripped.startswith("async def ")
        )
        if is_function_token:
            token_base_indent = len(first_line) - len(first_stripped)
            body_indent = token_base_indent + 4

            if current_indent <= body_indent:
                return False

            for i in range(
                line_idx - 1,
                -1,
                -1
            ):
                check_line = lines[i]
                if check_line.strip() == "":
                    continue

                check_indent = len(check_line) - len(check_line.lstrip())
                if check_indent < current_indent and check_indent >= body_indent:
                    check_stripped = check_line.lstrip()
                    if (
                        check_stripped.startswith("def ")
                        or check_stripped.startswith("class ")
                        or check_stripped.startswith("async def ")
                    ):
                        return True

                    if check_indent == body_indent:
                        break

            return False

        for i in range(
            line_idx - 1,
            -1,
            -1
        ):
            check_line = lines[i]
            if check_line.strip() == "":
                continue

            check_indent = len(check_line) - len(check_line.lstrip())
            if check_indent < current_indent:
                check_stripped = check_line.lstrip()
                if check_stripped.startswith("def ") or check_stripped.startswith("class "):
                    return True

                if check_indent == 0:
                    break

        return False


    def inspect(self, token: str) -> str | None:
        """Inspect a token for code block newline issues.

        Parameters
        ----------
        token : str
            String token to inspect (whole file content).

        Examples
        --------

        ```python
        formatter = PyCodeBlockNewLinesFormatter()
        message = formatter.inspect("if x:\\n    pass\\n\\n\\nprint(y)\\n")
        ```

        Returns
        -------
        str | None
            Error message if code block newlines are incorrect, `None` otherwise.
        """
        formatted = self.format(token)
        if formatted != token:
            return "Code block should have newlines between them at the same level or higher."

        return None


    def format(self, token: str) -> str:
        """Format code block newlines.

        Parameters
        ----------
        token : str
            Token to format (whole file content).

        Examples
        --------

        ```python
        formatter = PyCodeBlockNewLinesFormatter()
        result = formatter.format("if x:\\n    pass\\n\\n\\nprint(y)\\n")
        ```

        Returns
        -------
        str
            Token with properly formatted code block newlines.
        """
        lines = token.split("\n")
        result_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            if (
                self._is_block_keyword_line(line)
                and not self._is_inside_function_or_class(lines, i)
            ):
                base_indent = len(line) - len(line.lstrip())
                block_end = self._get_block_end(
                    lines,
                    i,
                    base_indent
                )

                for j in range(i, min(block_end, len(lines))):
                    curr_line = lines[j]
                    if curr_line.strip() == "":
                        if j + 1 < len(lines) and j > i:
                            next_non_empty = j + 1
                            while (
                                next_non_empty < len(lines)
                                and lines[next_non_empty].strip() == ""
                            ):
                                next_non_empty += 1

                            next_line = lines[next_non_empty]
                            next_stripped = next_line.lstrip()
                            next_indent = len(next_line) - len(next_stripped)

                            first_word = next_stripped.split()[0] if next_stripped.split() else ""
                            if (
                                first_word in CONNECTED_KEYWORDS
                                or next_stripped.startswith("except")
                                or next_stripped.startswith("finally")
                            ):
                                continue

                            prev_non_empty = j - 1
                            while prev_non_empty >= i and lines[prev_non_empty].strip() == "":
                                prev_non_empty -= 1

                            if prev_non_empty >= i:
                                prev_line = lines[prev_non_empty]
                                prev_stripped = prev_line.rstrip()
                                if prev_stripped.endswith(":"):
                                    continue

                            result_lines.append(curr_line)

                    else:
                        if j > i and curr_line.strip():
                            curr_indent = len(curr_line) - len(curr_line.lstrip())
                            if curr_indent > base_indent and result_lines:
                                prev_result = result_lines[-1]
                                if prev_result.strip() != "":
                                    prev_indent = len(prev_result) - len(prev_result.lstrip()) if prev_result.strip() else 0
                                    if (
                                        prev_indent > curr_indent
                                        and not curr_line.lstrip().startswith(
                                            (
                                                "elif ",
                                                "else:",
                                                "except",
                                                "finally:"
                                            )
                                        )
                                    ):
                                        block_owner_idx = None
                                        for scan in range(
                                            j - 1,
                                            i - 1,
                                            -1
                                        ):
                                            scan_line = lines[scan]
                                            if scan_line.strip() == "":
                                                continue

                                            scan_indent = len(scan_line) - len(scan_line.lstrip())
                                            if scan_indent == curr_indent:
                                                if self._is_block_keyword_line(scan_line):
                                                    block_owner_idx = scan

                                                break

                                        if block_owner_idx is not None:
                                            has_exit_stmt = False
                                            for scan_body in range(block_owner_idx + 1, j):
                                                body_stripped = lines[scan_body].lstrip()
                                                if body_stripped.startswith(
                                                    (
                                                        "break",
                                                        "continue",
                                                        "return",
                                                        "raise"
                                                    )
                                                ):
                                                    has_exit_stmt = True
                                                    break

                                            if has_exit_stmt:
                                                result_lines.append("")

                        result_lines.append(curr_line)

                if block_end < len(lines):
                    peek = block_end
                    while peek < len(lines) and lines[peek].strip() == "":
                        peek += 1

                    if peek < len(lines):
                        next_line = lines[peek]
                        next_stripped = next_line.strip()
                        next_indent = len(next_line) - len(next_line.lstrip()) if next_stripped else 0
                        is_closing_paren = (
                            next_stripped.startswith(")")
                            or next_stripped.startswith("]")
                        )
                        if (
                            next_indent <= base_indent
                            and next_stripped != ""
                            and not is_closing_paren
                        ):
                            result_lines.append("")
                            i = peek
                            continue

                i = block_end
            else:
                result_lines.append(line)
                i += 1

        return self._ensure_indent_shrink_spacing("\n".join(result_lines))


    def _count_paren_depth_change(self, line: str) -> int:
        """Count net paren/bracket depth change on a line, skipping strings."""
        depth_change = 0
        i = 0
        in_single = False
        in_double = False

        while i < len(line):
            ch = line[i]

            if ch == "\\" and (in_single or in_double):
                i += 2
                continue

            if ch == "'" and not in_double:
                in_single = not in_single
                i += 1
                continue

            if ch == '"' and not in_single:
                in_double = not in_double
                i += 1
                continue

            if not in_single and not in_double:
                if ch in "([{":
                    depth_change += 1
                elif ch in ")]}":
                    depth_change -= 1

            i += 1

        return depth_change


    def _ensure_indent_shrink_spacing(self, text: str) -> str:
        """Ensure a blank line exists whenever indent level decreases in the body.

        Does not add blank lines between connected blocks (if/elif/else,
        try/except/finally).
        """
        lines = text.split("\n")
        result = []
        prev_indent = -1
        prev_was_blank = False
        in_docstring = False
        paren_depth = 0
        paren_open_indent = -1

        first_stripped = lines[0].lstrip() if lines else ""
        in_body = not (
            first_stripped.startswith("def ")
            or first_stripped.startswith("async def ")
        )

        for i, line in enumerate(lines):
            if not in_body:
                result.append(line)
                if line.rstrip().endswith(":"):
                    in_body = True
                    prev_indent = -1
                    prev_was_blank = False

                continue

            stripped = line.strip()

            if in_docstring:
                result.append(line)
                if '"""' in stripped or "'''" in stripped:
                    if stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                        in_docstring = False
                    elif stripped.endswith('"""') or stripped.endswith("'''"):
                        in_docstring = False

                prev_indent = len(line) - len(line.lstrip()) if stripped else prev_indent
                prev_was_blank = False
                continue

            if stripped.startswith('"""') or stripped.startswith("'''"):
                quote = stripped[:3]
                if stripped.count(quote) < 2:
                    in_docstring = True

                result.append(line)
                prev_indent = len(line) - len(line.lstrip())
                prev_was_blank = False
                continue

            if stripped == "":
                result.append(line)
                prev_was_blank = True
                continue

            curr_indent = len(line) - len(line.lstrip())

            is_connected = stripped.startswith(
                (
                    "elif ",
                    "else:",
                    "except ",
                    "except:",
                    "finally:"
                )
            )

            if (
                prev_indent > curr_indent
                and prev_indent >= 0
                and not prev_was_blank
                and paren_depth == 0
            ):
                if not is_connected or prev_indent - curr_indent > 4:
                    result.append("")

            depth_change = self._count_paren_depth_change(stripped)
            old_paren_depth = paren_depth
            paren_depth += depth_change

            result.append(line)
            if paren_depth == 0 and old_paren_depth > 0:
                prev_indent = paren_open_indent if paren_open_indent >= 0 else curr_indent
                paren_open_indent = -1
            elif paren_depth <= 0:
                prev_indent = curr_indent

            if paren_depth > 0 and old_paren_depth == 0:
                paren_open_indent = curr_indent

            prev_was_blank = False

        return "\n".join(result)
