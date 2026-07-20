"""Type hint colon spacing formatter module."""

__all__ = ["PyTypeHintSpacingFormatter"]


from cleer.formatters.formatter import Formatter


class PyTypeHintSpacingFormatter(Formatter):
    """Formats type annotation colon spacing.

    Ensures no space before the colon and exactly one space after the
    colon in type annotations.

    Accepts token types: `type_hint_spacing`

    Examples
    --------

    ```python
    from cleer import PyTypeHintSpacingFormatter

    formatter = PyTypeHintSpacingFormatter()
    result = formatter.format(" :")
    ```
    """
    accepts_token_types = ["type_hint_spacing"]


    def inspect(self, token: str) -> str | None:
        """Inspect type annotation colon spacing.

        Parameters
        ----------
        token : str
            String token to inspect (colon with surrounding spaces).

        Examples
        --------

        ```python
        formatter = PyTypeHintSpacingFormatter()
        message = formatter.inspect(" :")
        ```

        Returns
        -------
        str | None
            Error message if spacing is wrong, `None` otherwise.
        """
        if token != ": ":
            return "Type annotation colons should have no space before and exactly one space after."

        return None


    def format(self, token: str) -> str:
        """Format type annotation colon spacing.

        Parameters
        ----------
        token : str
            Token to format (colon with surrounding spaces).

        Examples
        --------

        ```python
        formatter = PyTypeHintSpacingFormatter()
        result = formatter.format(" :  ")
        ```

        Returns
        -------
        str
            Correctly formatted colon: `: ` (no space before, one space after).
        """
        return ": "
