"""Trailing comma formatter module."""

__all__ = ["TrailingCommaFormatter"]


from cleer.formatters.formatter import Formatter


class TrailingCommaFormatter(Formatter):
    """Removes trailing commas before closing brackets/braces/parens.

    The last item in a multi-item structure should not have a trailing
    comma. If the first non-whitespace character after the comma is
    `)`, `]`, or `}`, the comma is removed.

    Accepts token types: `comma_plus`

    Examples
    --------

    ```python
    from cleer import TrailingCommaFormatter

    formatter = TrailingCommaFormatter()
    result = formatter.format(",\\n)")
    ```
    """
    accepts_token_types = ["comma_plus"]


    def _get_next_char(self, token: str) -> str:
        """Get the last character (first non-whitespace after comma)."""
        if not token:
            return ""

        return token[-1]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for trailing commas.

        Parameters
        ----------
        token : str
            String token to inspect (comma with following context).

        Examples
        --------

        ```python
        formatter = TrailingCommaFormatter()
        message = formatter.inspect(",\\n)")
        ```

        Returns
        -------
        str | None
            Error message if trailing comma found, `None` otherwise.
        """
        next_char = self._get_next_char(token)
        if next_char in ")]}":
            return "Trailing commas should not be used in lists, dictionaries, sets, tuples, etc."

        return None


    def format(self, token: str) -> str:
        """Remove trailing commas before closing brackets.

        Parameters
        ----------
        token : str
            Token to format (comma with following whitespace and next char).

        Examples
        --------

        ```python
        formatter = TrailingCommaFormatter()
        result = formatter.format(",\\n)")
        ```

        Returns
        -------
        str
            Token with comma removed if followed by closing bracket,
            unchanged otherwise.
        """
        next_char = self._get_next_char(token)
        if next_char in ")]}":
            whitespace = token[1:-1]

            return whitespace + next_char

        return token
