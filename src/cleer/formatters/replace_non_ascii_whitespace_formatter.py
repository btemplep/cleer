"""Replace non-ascii whitespace formatter module."""

__all__ = ["ReplaceNonAsciiWhitespaceFormatter"]


import re

from cleer.formatters.formatter import Formatter


NON_ASCII_WHITESPACE_PATTERN = re.compile(r"[^\S\x00-\x7F]")


class ReplaceNonAsciiWhitespaceFormatter(Formatter):
    """Replaces non-ascii whitespace characters with ascii spaces.

    Each non-ascii whitespace character in the token is replaced with
    a standard ascii space character.

    Accepts token types: `non_ascii_whitespace`

    Examples
    --------

    ```python
    from cleer import ReplaceNonAsciiWhitespaceFormatter

    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.format("\u00a0\u2003")
    ```
    """
    accepts_token_types = ["non_ascii_whitespace"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for non-ascii whitespace characters.

        Parameters
        ----------
        token : str
            String token to inspect.

        Examples
        --------

        ```python
        formatter = ReplaceNonAsciiWhitespaceFormatter()
        message = formatter.inspect("hello\\u00a0world")
        ```

        Returns
        -------
        str | None
            Error message if non-ascii whitespace is found, `None` otherwise.
        """
        if NON_ASCII_WHITESPACE_PATTERN.search(token):
            return "Files should not contain any non-ascii whitespace."

        return None


    def format(self, token: str) -> str:
        """Replace non-ascii whitespace characters with ascii spaces.

        Parameters
        ----------
        token : str
            Token to format.

        Examples
        --------

        ```python
        formatter = ReplaceNonAsciiWhitespaceFormatter()
        result = formatter.format("hello\\u00a0world")
        ```

        Returns
        -------
        str
            Token with non-ascii whitespace replaced by ascii spaces.
        """
        return NON_ASCII_WHITESPACE_PATTERN.sub(" ", token)
