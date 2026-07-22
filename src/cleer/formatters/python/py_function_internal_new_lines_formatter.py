"""Function internal new lines formatter module."""

__all__ = ["PyFunctionInternalNewLinesFormatter"]


import re

from cleer.formatters.formatter import Formatter


BLOCK_KEYWORD_PATTERN = re.compile(r"^(\s*)(for |if |elif |else:|try:|except |except:|finally:|with |while |async for |async with )")
SIGNATURE_PATTERN = re.compile(r"^(\s*)(async\s+)?def\s+")
DOCSTRING_END_PATTERN = re.compile(r'^\s*("""|\'\'\')\s*$')


class PyFunctionInternalNewLinesFormatter(Formatter):
    """Ensures proper internal newlines within functions.

    Rules:
    - No more than one consecutive blank line within a function
    - No blank lines immediately after function signatures
    - No blank lines immediately after code block keywords (for, if, etc.)
    - No blank lines immediately after docstrings

    Accepts token types: `function`

    Examples
    --------

    ```python
    from cleer import PyFunctionInternalNewLinesFormatter

    formatter = PyFunctionInternalNewLinesFormatter()
    result = formatter.format("def func():\\n    x = 1\\n\\n\\n    return x\\n")
    ```
    """
    accepts_token_types = ["function"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for internal newline issues.

        Parameters
        ----------
        token : str
            String token to inspect (whole function).

        Examples
        --------

        ```python
        formatter = PyFunctionInternalNewLinesFormatter()
        message = formatter.inspect("def func():\\n    x = 1\\n\\n\\n    return x\\n")
        ```

        Returns
        -------
        str | None
            Error message if internal newline issues found, `None` otherwise.
        """
        formatted = self.format(token)
        if formatted != token:
            return "Functions should never have 2 new lines in a row."

        return None


    def format(self, token: str) -> str:
        """Fix internal newlines in a function.

        Reduces consecutive blank lines to at most one, and removes blank
        lines immediately after function signatures, code block keywords,
        and docstrings.

        Parameters
        ----------
        token : str
            Token to format (whole function).

        Examples
        --------

        ```python
        formatter = PyFunctionInternalNewLinesFormatter()
        result = formatter.format("def func():\\n    x = 1\\n\\n\\n    return x\\n")
        ```

        Returns
        -------
        str
            Token with properly formatted internal newlines.
        """
        while "\n\n\n" in token:
            token = token.replace("\n\n\n", "\n\n")

        lines = token.split("\n")
        result_lines = []
        in_docstring = False
        docstring_quote = None

        for i, line in enumerate(lines):
            stripped = line.strip()

            if in_docstring:
                result_lines.append(line)
                if docstring_quote in stripped and i > 0:
                    end_check = stripped
                    if (
                        end_check.endswith(docstring_quote)
                        and not end_check == docstring_quote + docstring_quote[:1]
                    ):
                        in_docstring = False
                        docstring_quote = None

                continue

            if stripped.startswith('"""') or stripped.startswith("'''"):
                quote = stripped[:3]
                if stripped.count(quote) == 1:
                    in_docstring = True
                    docstring_quote = quote

                result_lines.append(line)
                continue

            if stripped == "" and result_lines:
                prev_line = result_lines[-1]
                prev_stripped = prev_line.rstrip()

                if prev_stripped.endswith(":"):
                    is_sig = bool(SIGNATURE_PATTERN.match(prev_line))
                    is_block = bool(BLOCK_KEYWORD_PATTERN.match(prev_line))
                    if is_sig or is_block:
                        continue

                    if prev_line.strip() == "):":
                        is_multiline_sig = False
                        for back_idx in range(len(result_lines) - 2, -1, -1):
                            back_line = result_lines[back_idx]
                            if bool(SIGNATURE_PATTERN.match(back_line)):
                                is_multiline_sig = True
                                break

                            back_stripped = back_line.strip()
                            if back_stripped == "" or back_stripped.endswith(":"):
                                break

                        if is_multiline_sig:
                            continue

                if docstring_quote is None and not in_docstring:
                    prev_s = prev_line.strip()
                    if prev_s.endswith('"""') or prev_s.endswith("'''"):
                        continue

            result_lines.append(line)

        return "\n".join(result_lines)
