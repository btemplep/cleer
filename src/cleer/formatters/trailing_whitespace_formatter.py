"""Trailing whitespace formatter module."""

__all__ = ["TrailingWhitespaceFormatter"]


from cleer.formatters.formatter import Formatter


class TrailingWhitespaceFormatter(Formatter):
    """Removes trailing whitespace from a token.

    Trailing whitespace includes spaces and tabs at the end of the token string.

    Accepts token types: `line`

    Examples
    --------

    ```python
    from cleer import TrailingWhitespaceFormatter

    formatter = TrailingWhitespaceFormatter()
    result = formatter.format("hello world   ")
    ```
    """
    accepts_token_types = ["line"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for trailing whitespace.

        Parameters
        ----------
        token : str
            String token to inspect.

        Examples
        --------

        ```python
        formatter = TrailingWhitespaceFormatter()
        message = formatter.inspect("hello   ")
        ```

        Returns
        -------
        str | None
            Error message if trailing whitespace is found, `None` otherwise.
        """
        if token != token.rstrip(" \t"):
            return "Lines should not have any trailing whitespace."

        return None


    def format(self, token: str) -> str:
        """Remove trailing whitespace from the token.

        Parameters
        ----------
        token : str
            Token to format.

        Examples
        --------

        ```python
        formatter = TrailingWhitespaceFormatter()
        result = formatter.format("hello   ")
        ```

        Returns
        -------
        str
            Token with trailing whitespace removed.
        """
        return token.rstrip(" \t")
