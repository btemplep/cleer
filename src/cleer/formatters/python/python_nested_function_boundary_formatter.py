"""Python nested function boundary formatter module."""

__all__ = ["PythonNestedFunctionBoundaryFormatter"]


from cleer.formatters.formatter import Formatter


class PythonNestedFunctionBoundaryFormatter(Formatter):
    """Enforce blank lines before and after nested function definitions.

    Replaces the whitespace boundary token with the configured number
    of blank lines for nested functions inside other functions/methods.

    Parameters
    ----------
    blank_lines : int, default=1
        Number of blank lines to enforce before and after nested function
        definitions.

    Examples
    --------

    ```python
    from cleer import PythonNestedFunctionBoundaryFormatter

    formatter = PythonNestedFunctionBoundaryFormatter()
    result = formatter.format("\n\n\n")
    ```
    """
    accepts_token_types = ["python_nested_function_boundary"]


    def __init__(self, blank_lines: int = 1):
        self._blank_lines = blank_lines
        self._expected = "\n" * blank_lines


    def inspect(self, token: str) -> str | None:
        """Inspect a boundary token for improper blank lines around nested functions.

        Parameters
        ----------
        token : str
            String token to inspect (whitespace around nested functions).

        Returns
        -------
        str | None
            Error message if blank lines do not match the expected.
            Returns `None` if there is no violation.
        """
        if token != self._expected:
            return f"Expected {self._blank_lines} blank line(s) before and after nested function definition."

        return None


    def format(self, token: str) -> str:
        """Format the boundary to the configured number of blank lines.

        Parameters
        ----------
        token : str
            Token to format (whitespace around nested functions).

        Returns
        -------
        str
            The configured number of blank lines.
        """
        return self._expected
