"""Trailing whitespace formatter module."""

__all__ = [
    "TrailingWhitespaceFormatter"
]

from cleer.formatters.formatter import Formatter


class TrailingWhitespaceFormatter(Formatter):
    """Strip trailing whitespace from lines.

    Removes any trailing whitespace token by replacing it with an
    empty string.

    Examples
    --------

    ```python
    from cleer import TrailingWhitespaceFormatter

    formatter = TrailingWhitespaceFormatter()
    result = formatter.format("   ")
    ```
    """
    accepts_token_types = ["trailing_whitespace"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for trailing whitespace.

        Parameters
        ----------
        token : str
            String token to inspect (trailing whitespace from a line).

        Returns
        -------
        str | None
            Error message if trailing whitespace is present.
            Returns `None` if there is no violation.
        """
        return "Lines should not have any trailing whitespace."


    def format(self, token: str) -> str:
        """Remove trailing whitespace.

        Parameters
        ----------
        token : str
            Token to format (trailing whitespace from a line).

        Returns
        -------
        str
            Empty string.
        """
        return ""
