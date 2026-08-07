"""Python string quote formatter module."""

__all__ = [
    "PythonStringQuoteFormatter"
]

from cleer.formatters.formatter import Formatter


class PythonStringQuoteFormatter(Formatter):
    """Enforce quote style for Python string literals and docstrings.

    Converts single-line string literals to use the configured quote
    character, and multiline/docstring literals to use the configured
    triple quote.

    Parameters
    ----------
    quote : str, default='"'
        Quote character to use for single-line string literals.
    multiline_quote : str, default='\"\"\"'
        Triple quote to use for multiline strings and docstrings.

    Examples
    --------

    ```python
    from cleer import PythonStringQuoteFormatter

    formatter = PythonStringQuoteFormatter()
    result = formatter.format("'hello'")
    ```
    """
    accepts_token_types = ["python_string_quote"]


    def __init__(
        self,
        quote: str='"',
        multiline_quote: str='"""'
    ):
        self._quote = quote
        self._multiline_quote = multiline_quote


    def inspect(self, token: str) -> str | None:
        """Inspect a string token for incorrect quote style.

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
        prefix, quote_char, content, is_multiline = self._parse_string(token)

        if prefix is None:
            return None

        if is_multiline:
            expected_quote = self._multiline_quote
        else:
            expected_quote = self._quote

        current_quote = quote_char

        if current_quote == expected_quote:
            return None

        if not is_multiline and expected_quote in content:
            return None

        if is_multiline:
            return f"Multiline strings should use {self._multiline_quote} quotes."

        return f"String literals should use {self._quote} quotes."


    def format(self, token: str) -> str:
        """Format a string token to use the correct quote style.

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
        prefix, quote_char, content, is_multiline = self._parse_string(token)

        if prefix is None:
            return token

        if is_multiline:
            target_quote = self._multiline_quote
        else:
            target_quote = self._quote

        if quote_char == target_quote:
            return token

        if not is_multiline and target_quote in content:
            return token

        if is_multiline and target_quote in content:
            return token

        new_content = content
        if not is_multiline:
            old_single = quote_char
            new_single = target_quote
            new_content = content.replace("\\" + old_single, old_single)
            if new_single in new_content:
                return token

            new_content = new_content.replace(new_single, "\\" + new_single)

        return prefix + target_quote + new_content + target_quote


    def _parse_string(self, token: str) -> tuple:
        """Parse a string token into prefix, quote, content, and multiline flag.

        Returns
        -------
        tuple
            (prefix, quote_char, content, is_multiline) or (None, None, None, None) if not parseable.
        """
        stripped = token

        prefix = ""
        while stripped and stripped[0] in "fFrRbBuUtT":
            prefix += stripped[0]
            stripped = stripped[1:]

        if not stripped:
            return (None, None, None, None)

        if stripped.startswith('"""') or stripped.startswith("'''"):
            quote_char = stripped[:3]
            is_multiline = True
            content = stripped[3:-3]
        elif stripped[0] in ("'", '"'):
            quote_char = stripped[0]
            is_multiline = False
            content = stripped[1:-1]
        else:
            return (None, None, None, None)

        return (prefix, quote_char, content, is_multiline)
