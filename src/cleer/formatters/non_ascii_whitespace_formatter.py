"""Non-ASCII whitespace formatter module."""

__all__ = [
    "NonAsciiWhitespaceFormatter"
]

from cleer.formatters.formatter import Formatter


class NonAsciiWhitespaceFormatter(Formatter):
    """Remove non-ASCII whitespace characters.

    Replaces any non-ASCII whitespace token with ASCII spaces,
    preserving the length of the original token.

    Examples
    --------

    ```python
    from cleer import NonAsciiWhitespaceFormatter

    formatter = NonAsciiWhitespaceFormatter()
    result = formatter.format("\u00a0")
    ```
    """
    accepts_token_types = ["non_ascii_whitespace"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for non-ASCII whitespace.

        Parameters
        ----------
        token : str
            String token to inspect (non-ASCII whitespace).

        Returns
        -------
        str | None
            Error message if non-ASCII whitespace is present.
            Returns `None` if there is no violation.
        """
        return "Non-ASCII whitespace characters should not exist."


    def format(self, token: str) -> str:
        """Replace non-ASCII whitespace with spaces.

        Parameters
        ----------
        token : str
            Token to format (non-ASCII whitespace).

        Returns
        -------
        str
            ASCII spaces matching the length of the original token.
        """
        return " " * len(token)
