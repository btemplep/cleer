"""See :class:`PythonTrailingCommaFormatter`."""

__all__ = [
    "PythonTrailingCommaFormatter"
]

from cleer.formatters.formatter import Formatter, FormatterViolation


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


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect for unwanted trailing comma.

        Parameters
        ----------
        token : str
            String token (always a single comma).

        Returns
        -------
        list[FormatterViolation]
            List of violations found, empty if no violations.
        """
        if token == ",":
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": "Trailing commas should be removed."
                }
            ]

        return []


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
