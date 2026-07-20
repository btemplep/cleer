"""Quote style formatter module."""

__all__ = ["QuoteStyleFormatter"]


from cleer.formatters.formatter import Formatter


class QuoteStyleFormatter(Formatter):
    """Enforces a consistent quote style for string literals.

    Can enforce either double quotes or single quotes for all strings.

    Accepts token types: `quotation`

    Parameters
    ----------
    style : str, default='"'
        The quote style to enforce. Either '"' for double quotes or
        "'" for single quotes.

    Examples
    --------

    ```python
    from cleer import QuoteStyleFormatter

    formatter = QuoteStyleFormatter(style='"')
    result = formatter.format("'hello'")
    ```
    """
    accepts_token_types = ["quotation"]


    def __init__(self, style: str='"') -> None:
        self._style = style
        self._other = "'" if style == '"' else '"'


    def _is_triple_quoted(self, token: str) -> bool:
        """Check if the token uses triple quotes."""

        return (
            (
                token.startswith('"""')
                and token.endswith('"""')
            )
            or (
                token.startswith("'''")
                and token.endswith("'''")
            )
        )


    def _get_quote_char(self, token: str) -> str:
        """Get the quote character used in the token."""
        if token.startswith('"""') or token.startswith('"'):
            return '"'

        return "'"


    def inspect(self, token: str) -> str | None:
        """Inspect a token for incorrect quote style.

        Parameters
        ----------
        token : str
            String token to inspect (string literal with quotes).

        Examples
        --------

        ```python
        formatter = QuoteStyleFormatter(style='"')
        message = formatter.inspect("'hello'")
        ```

        Returns
        -------
        str | None
            Error message if wrong quote style, `None` otherwise.
        """
        if not token:
            return None

        if self._is_triple_quoted(token):
            if not token.startswith(self._style * 3):
                return f"Multiline string should use {self._style}{self._style}{self._style} quotes."

            return None

        current_quote = self._get_quote_char(token)
        if current_quote != self._style:
            inner = token[1:-1]
            if self._style not in inner:
                return f"String should use {self._style} quotes."

        return None


    def format(self, token: str) -> str:
        """Convert string to the target quote style.

        Only converts if the string content does not contain the target
        quote character (to avoid escaping issues).

        Parameters
        ----------
        token : str
            Token to format (string literal with quotes).

        Examples
        --------

        ```python
        formatter = QuoteStyleFormatter(style='"')
        result = formatter.format("'hello'")
        ```

        Returns
        -------
        str
            Token with correct quote style, or unchanged if conversion
            would require escaping.
        """
        if not token:
            return token

        if self._is_triple_quoted(token):
            current_triple = token[:3]
            if current_triple == self._style * 3:
                return token

            inner = token[3:-3]
            target_triple = self._style * 3
            if target_triple not in inner:
                return target_triple + inner + target_triple

            return token

        current_quote = self._get_quote_char(token)
        if current_quote == self._style:
            return token

        inner = token[1:-1]
        if self._style in inner:
            return token

        return self._style + inner + self._style
