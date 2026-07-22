"""Return yield new line formatter module."""

__all__ = ["PyReturnYieldNewLineFormatter"]


import re

from cleer.formatters.formatter import Formatter


class PyReturnYieldNewLineFormatter(Formatter):
    """Ensures proper newlines around return and yield statements.

    Rules:
    - Should have a newline between return or yield statements if there
      is a statement before it in the same block
    - Yield statements should have a newline after them if there is
      another statement in the same indent/block
    - Should have no newlines between return or yield statements if it
      is the only statement in a code block

    Accepts token types: `function`

    Examples
    --------

    ```python
    from cleer import PyReturnYieldNewLineFormatter

    formatter = PyReturnYieldNewLineFormatter()
    result = formatter.format("def func():\\n    x = 1\\n    return x\\n")
    ```
    """
    accepts_token_types = ["function"]


    def _get_block_indent(
        self,
        lines: list[str],
        line_idx: int
    ) -> int:
        """Get the indent level of the current block."""
        line = lines[line_idx]
        if line.strip():
            return len(line) - len(line.lstrip())

        return 0


    def _is_return_or_yield(self, line: str) -> bool:
        """Check if a line is a return or yield statement."""
        stripped = line.strip()

        return (
            (
                stripped.startswith("return")
                and (
                    len(stripped) == 6
                    or stripped[6] in " \n"
                )
            )
            or (
                stripped.startswith("yield")
                and (
                    len(stripped) == 5
                    or stripped[5] in " \n"
                )
            )
        )


    def _is_only_statement_in_block(
        self,
        lines: list[str],
        line_idx: int
    ) -> bool:
        """Check if this return/yield is the only statement in its block."""
        line = lines[line_idx]
        current_indent = len(line) - len(line.lstrip())

        in_docstring = False
        for i in range(line_idx - 1, -1, -1):
            check_line = lines[i]
            if check_line.strip() == "":
                continue

            check_indent = len(check_line) - len(check_line.lstrip())
            stripped = check_line.strip()

            if in_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    in_docstring = False

                continue

            if stripped == '"""' or stripped == "'''":
                in_docstring = True
                continue

            if (
                (
                    stripped.endswith('"""')
                    or stripped.endswith("'''")
                )
                and (
                    stripped.startswith('"""')
                    or stripped.startswith("'''")
                )
            ):
                continue

            if check_indent == current_indent:
                return False

            if check_indent < current_indent:
                break

        for i in range(line_idx + 1, len(lines)):
            check_line = lines[i]
            if check_line.strip() == "":
                continue

            check_indent = len(check_line) - len(check_line.lstrip())
            if check_indent == current_indent:
                return False

            if check_indent < current_indent:
                break

        return True


    def inspect(self, token: str) -> str | None:
        """Inspect a token for return/yield newline issues.

        Parameters
        ----------
        token : str
            String token to inspect (whole function).

        Examples
        --------

        ```python
        formatter = PyReturnYieldNewLineFormatter()
        message = formatter.inspect("def func():\\n    x = 1\\n    return x\\n")
        ```

        Returns
        -------
        str | None
            Error message if return/yield newlines are incorrect, `None` otherwise.
        """
        formatted = self.format(token)
        if formatted != token:
            return (
                "Return/yield statements should have a newline before them unless they are the only statement in a code block."
                "Yield statements should also have a newline after them, if there are more statements within the same code block."
            )

        return None


    def format(self, token: str) -> str:
        """Format return/yield statement newlines.

        Parameters
        ----------
        token : str
            Token to format (whole function).

        Examples
        --------

        ```python
        formatter = PyReturnYieldNewLineFormatter()
        result = formatter.format("def func():\\n    x = 1\\n    return x\\n")
        ```

        Returns
        -------
        str
            Token with properly formatted return/yield newlines.
        """
        lines = token.split("\n")
        result_lines = []

        for i, line in enumerate(lines):
            if self._is_return_or_yield(line):
                current_indent = len(line) - len(line.lstrip())
                is_only = self._is_only_statement_in_block(lines, i)

                if is_only:
                    if result_lines and result_lines[-1].strip() == "":
                        while result_lines and result_lines[-1].strip() == "":
                            result_lines.pop()

                    result_lines.append(line)
                else:
                    has_prev_statement = False
                    for j in range(i - 1, -1, -1):
                        if lines[j].strip() == "":
                            break

                        prev_indent = len(lines[j]) - len(lines[j].lstrip())
                        if prev_indent == current_indent:
                            has_prev_statement = True
                            break

                        if prev_indent < current_indent:
                            break

                    if has_prev_statement:
                        if not (result_lines and result_lines[-1].strip() == ""):
                            result_lines.append("")

                    result_lines.append(line)

                    if line.strip().startswith("yield"):
                        has_next = False
                        for j in range(i + 1, len(lines)):
                            if lines[j].strip() == "":
                                continue

                            next_indent = len(lines[j]) - len(lines[j].lstrip())
                            if next_indent == current_indent:
                                has_next = True

                            break

                        if has_next:
                            next_idx = i + 1
                            if next_idx < len(lines) and lines[next_idx].strip() != "":
                                result_lines.append("")

            else:
                result_lines.append(line)

        return "\n".join(result_lines)
