"""Function space formatter module."""

__all__ = ["PyFunctionSpaceFormatter"]


from cleer.formatters.formatter import Formatter


class PyFunctionSpaceFormatter(Formatter):
    """Ensures 2 newlines between function definitions.

    The whitespace between function definitions should be exactly 2 newlines
    (which appears as one blank line between the functions in the source).

    Accepts token types: `function_space`

    Examples
    --------

    ```python
    from cleer import PyFunctionSpaceFormatter

    formatter = PyFunctionSpaceFormatter()
    result = formatter.format("\\n\\n\\n\\n")
    ```
    """
    accepts_token_types = ["function_space"]


    def inspect(self, token: str) -> str | None:
        """Inspect whitespace between functions.

        Parameters
        ----------
        token : str
            String token to inspect (whitespace between functions).

        Examples
        --------

        ```python
        formatter = PyFunctionSpaceFormatter()
        message = formatter.inspect("\\n\\n\\n\\n")
        ```

        Returns
        -------
        str | None
            Error message if spacing is incorrect, `None` otherwise.
        """
        if token != "\n\n\n":
            return "Functions should have exactly 2 blank lines before and after themselves."

        return None


    def format(self, token: str) -> str:
        """Format whitespace between functions to exactly 2 blank lines.

        Parameters
        ----------
        token : str
            Token to format (whitespace between functions).

        Examples
        --------

        ```python
        formatter = PyFunctionSpaceFormatter()
        result = formatter.format("\\n\\n\\n\\n")
        ```

        Returns
        -------
        str
            Exactly 2 blank lines (3 newline characters).
        """
        return "\n\n\n"
