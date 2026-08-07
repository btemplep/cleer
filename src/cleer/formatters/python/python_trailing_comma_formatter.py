"""Python trailing comma formatter module."""

__all__ = [
    "PythonTrailingCommaFormatter"
]

from cleer.formatters.formatter import Formatter


class PythonTrailingCommaFormatter(Formatter):
    """Remove trailing commas from comma-separated sequences.

    By default removes trailing commas. Single-element tuples are
    excluded from tokenization (they require the trailing comma
    syntactically).

    Examples
    --------

    ```python
    from cleer import PythonTrailingCommaFormatter

    formatter = PythonTrailingCommaFormatter()
    result = formatter.format(",")
    ```
    """
    accepts_token_types = ["python_trailing_comma"]


    def inspect(self, token: str) -> str | None:
        """Inspect for unwanted trailing comma.

        Parameters
        ----------
        token : str
            String token (always a single comma).

        Returns
        -------
        str | None
            Error message if trailing comma should be removed.
            Returns `None` if there is no violation.
        """
        if token == ",":
            return "Trailing commas should be removed."

        return None


    def format(self, token: str) -> str:
        """Remove the trailing comma.

        Parameters
        ----------
        token : str
            Token to format (a trailing comma).

        Returns
        -------
        str
            Empty string (comma removed).
        """
        return ""
