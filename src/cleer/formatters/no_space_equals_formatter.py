"""No space equals formatter module."""

__all__ = ["NoSpaceEqualsFormatter"]


from cleer.formatters.formatter import Formatter


class NoSpaceEqualsFormatter(Formatter):
    """Ensures equals signs in kwargs have no surrounding spaces.

    Used for both function signature default kwargs and function call kwargs.

    Accepts token types: `kwargs_equals`

    Examples
    --------

    ```python
    from cleer import NoSpaceEqualsFormatter

    formatter = NoSpaceEqualsFormatter()
    result = formatter.format(" = ")
    ```
    """
    accepts_token_types = ["kwargs_equals"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for spacing around equals sign.

        Parameters
        ----------
        token : str
            String token to inspect (equals sign with surrounding whitespace).

        Examples
        --------

        ```python
        formatter = NoSpaceEqualsFormatter()
        message = formatter.inspect(" = ")
        ```

        Returns
        -------
        str | None
            Error message if spacing exists around equals, `None` otherwise.
        """
        if token != "=":
            return "Equals sign in kwargs should have no surrounding spaces."

        return None


    def format(self, token: str) -> str:
        """Remove spaces around equals sign.

        Parameters
        ----------
        token : str
            Token to format (equals sign with possible whitespace).

        Examples
        --------

        ```python
        formatter = NoSpaceEqualsFormatter()
        result = formatter.format(" = ")
        ```

        Returns
        -------
        str
            Equals sign with no surrounding spaces.
        """
        return "="
