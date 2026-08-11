"""See :class:`TrailingWhitespaceFormatter`."""

__all__ = [
    "TrailingWhitespaceFormatter"
]

from cleer.formatters.formatter import Formatter, FormatterViolation


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


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect a token for trailing whitespace.

        Parameters
        ----------
        token : str
            String token to inspect (trailing whitespace from a line).

        Returns
        -------
        list[FormatterViolation]
            List of violations if trailing whitespace is present.
            Returns an empty list if there is no violation.
        """
        return [
            {
                "start_index": 0,
                "length": len(token),
                "message": "Lines should not have any trailing whitespace."
            }
        ]


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
