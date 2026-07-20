"""All module formatter module."""

__all__ = ["PyAllModuleFormatter"]


import re

from cleer.formatters.formatter import Formatter


ALL_PATTERN = re.compile(r"^__all__\s*=", re.MULTILINE)
MODULE_DOCSTRING_PATTERN = re.compile(r"^([ \t]*(?:\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\')[ \t]*\n)")


class PyAllModuleFormatter(Formatter):
    """Ensures all modules have an `__all__` variable declaration.

    If the token (whole file) does not contain an `__all__` declaration,
    the formatter adds an empty `__all__ = []` at the beginning of the file
    or after the module docstring if one exists. It also ensures there is
    exactly one blank line between the module docstring and `__all__`, and
    2 blank lines after the `__all__` declaration.

    This formatter should be placed in a group that only targets package
    source files (not tests or scripts).

    Accepts token types: ``file``

    Examples
    --------

    ```python
    from cleer import PyAllModuleFormatter

    formatter = PyAllModuleFormatter()
    result = formatter.format("import os\\n")
    ```
    """
    accepts_token_types = ["file"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for the presence of an `__all__` declaration.

        Parameters
        ----------
        token : str
            String token to inspect (whole file content).

        Examples
        --------

        ```python
        formatter = PyAllModuleFormatter()
        message = formatter.inspect("import os\\n")
        ```

        Returns
        -------
        str | None
            Error message if `__all__` is not found, `None` otherwise.
        """
        if not ALL_PATTERN.search(token):
            return "All modules should have an '__all__' declaration."

        return None


    def format(self, token: str) -> str:
        """Add an `__all__` declaration if not present and ensure proper spacing.

        Places `__all__` after the module docstring (if present) with one blank
        line between the docstring and `__all__`, and 2 blank lines after `__all__`.

        Parameters
        ----------
        token : str
            Token to format (whole file content).

        Examples
        --------

        ```python
        formatter = PyAllModuleFormatter()
        result = formatter.format("import os\\n")
        ```

        Returns
        -------
        str
            Token with `__all__` declaration properly placed.
        """
        if ALL_PATTERN.search(token):
            return self._ensure_all_spacing(token)

        docstring_match = MODULE_DOCSTRING_PATTERN.match(token)
        if docstring_match:
            docstring = docstring_match.group(1)
            rest = token[len(docstring):]
            rest = rest.lstrip("\n")

            return docstring + "\n__all__ = []\n\n\n" + rest

        return "__all__ = []\n\n\n" + token


    def _ensure_all_spacing(self, token: str) -> str:
        """Ensure proper spacing around __all__ when it already exists."""
        all_match = ALL_PATTERN.search(token)
        all_start = all_match.start()

        all_line_end = token.find("\n", all_start)
        if all_line_end == -1:
            all_line_end = len(token)

        if token[all_start:all_line_end].rstrip().endswith("["):
            bracket_content = token[all_line_end:]
            close_bracket = bracket_content.find("]")
            if close_bracket != -1:
                all_line_end = all_line_end + close_bracket + 1

        after_all = token[all_line_end:]
        if after_all.startswith("\n"):
            rest_after_newline = after_all[1:]
            stripped_rest = rest_after_newline.lstrip("\n")
            newlines_after = len(rest_after_newline) - len(stripped_rest)
            if newlines_after != 2:
                after_all = "\n\n\n" + stripped_rest

        elif after_all == "":
            after_all = "\n"
        else:
            after_all = "\n\n\n" + after_all.lstrip("\n")

        before_all = token[:all_start]
        docstring_match = MODULE_DOCSTRING_PATTERN.match(token)
        if docstring_match:
            docstring_end = docstring_match.end()
            if all_start > docstring_end or all_start == docstring_end:
                docstring = token[:docstring_end]
                between = token[docstring_end:all_start]
                if between != "\n":
                    before_all = docstring + "\n"

        return before_all + token[all_start:all_line_end] + after_all
