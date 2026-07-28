"""Python function boundary formatter module."""

__all__ = ["PythonFunctionBoundaryFormatter"]


from cleer.formatters.formatter import Formatter


class PythonFunctionBoundaryFormatter(Formatter):
    """Enforce blank lines before and after function/method definitions.

    Replaces the whitespace boundary token with the configured number
    of blank lines.

    Parameters
    ----------
    blank_lines : int, default=2
        Number of blank lines to enforce before and after function/method
        definitions.

    Examples
    --------

    ```python
    from cleer import PythonFunctionBoundaryFormatter

    formatter = PythonFunctionBoundaryFormatter()
    result = formatter.format("\n")
    ```
    """
    accepts_token_types = ["python_function_boundary"]


    def __init__(self, blank_lines: int = 2):
        self._blank_lines = blank_lines
        self._expected = "\n" * blank_lines


    def inspect(self, token: str) -> str | None:
        """Inspect a boundary token for improper blank lines.

        Parameters
        ----------
        token : str
            String token to inspect (whitespace between functions).

        Returns
        -------
        str | None
            Error message if blank lines do not match the expected.
            Returns `None` if there is no violation.
        """
        if token != self._expected:
            return f"Expected {self._blank_lines} blank line(s) before/after function or method definition."

        return None


    def format(self, token: str) -> str:
        """Format the boundary to the configured number of blank lines.

        Parameters
        ----------
        token : str
            Token to format (whitespace between functions).

        Returns
        -------
        str
            The configured number of blank lines.
        """
        return self._expected
