"""Python inner max blank lines formatter module."""

__all__ = ["PythonInnerMaxBlankLinesFormatter"]


from cleer.formatters.formatter import Formatter


class PythonInnerMaxBlankLinesFormatter(Formatter):
    """Enforce max blank lines inside function/method bodies.

    Replaces excessive consecutive blank lines inside functions with the
    configured maximum.

    Parameters
    ----------
    max_blank_lines : int, default=1
        Maximum number of consecutive blank lines allowed inside
        function/method bodies.

    Examples
    --------

    ```python
    from cleer import PythonInnerMaxBlankLinesFormatter

    formatter = PythonInnerMaxBlankLinesFormatter()
    result = formatter.format("\n\n\n\n")
    ```
    """
    accepts_token_types = ["python_inner_max_blank_lines"]


    def __init__(self, max_blank_lines: int = 1):
        self._max_blank_lines = max_blank_lines
        self._expected = "\n" * (max_blank_lines + 1)


    def inspect(self, token: str) -> str | None:
        """Inspect for excessive blank lines inside a function body.

        Parameters
        ----------
        token : str
            String token to inspect (whitespace block inside a function).

        Returns
        -------
        str | None
            Error message if blank lines exceed the maximum.
            Returns `None` if there is no violation.
        """
        return f"No more than {self._max_blank_lines} consecutive blank line(s) allowed inside function bodies."


    def format(self, token: str) -> str:
        """Reduce blank lines to the configured maximum.

        Parameters
        ----------
        token : str
            Token to format (excessive blank lines inside a function).

        Returns
        -------
        str
            The maximum allowed blank lines.
        """
        return self._expected
