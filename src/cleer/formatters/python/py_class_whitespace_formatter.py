"""Class whitespace formatter module."""

__all__ = ["PyClassWhitespaceFormatter"]


from cleer.formatters.formatter import Formatter


class PyClassWhitespaceFormatter(Formatter):
    """Ensures 2 blank lines before and after class definitions.

    The whitespace before and after class definitions should be exactly
    3 newline characters (2 blank lines).

    Accepts token types: `class_whitespace`

    Examples
    --------

    ```python
    from cleer import PyClassWhitespaceFormatter

    formatter = PyClassWhitespaceFormatter()
    result = formatter.format("\\n\\n\\n\\n")
    ```
    """
    accepts_token_types = ["class_whitespace"]


    def inspect(self, token: str) -> str | None:
        """Inspect whitespace around a class.

        Parameters
        ----------
        token : str
            String token to inspect (whitespace before/after class).

        Examples
        --------

        ```python
        formatter = PyClassWhitespaceFormatter()
        message = formatter.inspect("\\n")
        ```

        Returns
        -------
        str | None
            Error message if spacing is incorrect, `None` otherwise.
        """
        if token != "\n\n\n":
            return "Classes should have exactly 2 blank lines before and after them."

        return None


    def format(self, token: str) -> str:
        """Format whitespace around class to exactly 2 blank lines.

        Parameters
        ----------
        token : str
            Token to format (whitespace before/after class).

        Examples
        --------

        ```python
        formatter = PyClassWhitespaceFormatter()
        result = formatter.format("\\n\\n\\n\\n")
        ```

        Returns
        -------
        str
            Exactly 2 blank lines (3 newline characters).
        """
        return "\n\n\n"
