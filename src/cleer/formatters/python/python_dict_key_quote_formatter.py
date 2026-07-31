"""Python dict key quote formatter module."""

__all__ = ["PythonDictKeyQuoteFormatter"]


from cleer.formatters.formatter import Formatter


class PythonDictKeyQuoteFormatter(Formatter):
    """Enforce quote style for dict bracket subscript key lookups.

    Converts string literals used as dict bracket keys to the configured
    quote character.

    Parameters
    ----------
    quote : str, default="'"
        Quote character to use for dict key bracket lookups.

    Examples
    --------

    ```python
    from cleer import PythonDictKeyQuoteFormatter

    formatter = PythonDictKeyQuoteFormatter()
    result = formatter.format('"key"')
    ```
    """
    accepts_token_types = ["python_dict_key_quote"]


    def __init__(self, quote: str = "'"):
        self._quote = quote


    def inspect(self, token: str) -> str | None:
        """Inspect a dict key string token for incorrect quote style.

        Parameters
        ----------
        token : str
            String token to inspect (full string literal with quotes).

        Returns
        -------
        str | None
            Error message if wrong quote style is used.
            Returns `None` if there is no violation.
        """
        prefix, quote_char, content = self._parse_string(token)

        if prefix is None:
            return None

        if quote_char == self._quote:
            return None

        if self._quote in content:
            return None

        return f"Dict key bracket notation should use {self._quote} quotes."


    def format(self, token: str) -> str:
        """Format a dict key string token to use the correct quote style.

        Parameters
        ----------
        token : str
            Token to format (full string literal with quotes).

        Returns
        -------
        str
            String with corrected quote style, or unchanged if the
            target quote character exists in the string content.
        """
        prefix, quote_char, content = self._parse_string(token)

        if prefix is None:
            return token

        if quote_char == self._quote:
            return token

        if self._quote in content:
            return token

        new_content = content.replace("\\" + quote_char, quote_char)
        if self._quote in new_content:
            return token

        new_content = new_content.replace(self._quote, "\\" + self._quote)

        return prefix + self._quote + new_content + self._quote


    def _parse_string(self, token: str) -> tuple:
        """Parse a string token into prefix, quote, and content.

        Returns
        -------
        tuple
            (prefix, quote_char, content) or (None, None, None) if not parseable.
        """
        stripped = token

        prefix = ""
        while stripped and stripped[0] in "fFrRbBuU":
            prefix += stripped[0]
            stripped = stripped[1:]

        if not stripped:
            return (None, None, None)

        if stripped[0] in ("'", '"'):
            quote_char = stripped[0]
            content = stripped[1:-1]
        else:
            return (None, None, None)

        return (prefix, quote_char, content)
