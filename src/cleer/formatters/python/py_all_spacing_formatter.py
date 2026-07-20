"""All spacing formatter module."""

__all__ = ["PyAllSpacingFormatter"]


import re

from cleer.formatters.formatter import Formatter


ALL_PATTERN = re.compile(r"^__all__\s*=", re.MULTILINE)
MODULE_DOCSTRING_PATTERN = re.compile(r"^([ \t]*(?:\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\')[ \t]*\n)")


class PyAllSpacingFormatter(Formatter):
    """Ensures proper newline spacing around an existing ``__all__`` declaration.

    When ``__all__`` is present in a file, ensures:
    - One blank line between module docstring and ``__all__``
    - Two blank lines after ``__all__``

    Does nothing if ``__all__`` is not present in the file.

    Accepts token types: ``file``

    Examples
    --------

    ```python
    from cleer import PyAllSpacingFormatter

    formatter = PyAllSpacingFormatter()
    result = formatter.format("__all__ = []\\nimport os\\n")
    ```
    """
    accepts_token_types = ["file"]


    def inspect(self, token: str) -> str | None:
        """Inspect spacing around ``__all__`` if present.

        Parameters
        ----------
        token : str
            String token to inspect (whole file content).

        Examples
        --------

        ```python
        formatter = PyAllSpacingFormatter()
        message = formatter.inspect("__all__ = []\\nimport os\\n")
        ```

        Returns
        -------
        str | None
            Error message if spacing is incorrect, ``None`` otherwise.
        """
        if not ALL_PATTERN.search(token):
            return None

        formatted = self.format(token)
        if formatted != token:
            return "Spacing around '__all__' should be 1 blank line after docstring and 2 blank lines before next code."

        return None


    def format(self, token: str) -> str:
        """Format spacing around ``__all__`` if present.

        Parameters
        ----------
        token : str
            Token to format (whole file content).

        Examples
        --------

        ```python
        formatter = PyAllSpacingFormatter()
        result = formatter.format("__all__ = []\\nimport os\\n")
        ```

        Returns
        -------
        str
            Token with proper spacing around ``__all__``.
        """
        if not ALL_PATTERN.search(token):
            return token

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
            if all_start >= docstring_end:
                docstring = token[:docstring_end]
                between = token[docstring_end:all_start]
                if between != "\n":
                    before_all = docstring + "\n"

        return before_all + token[all_start:all_line_end] + after_all
