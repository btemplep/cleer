"""Comma space formatter module."""

__all__ = ["CommaSpaceFormatter"]


from cleer.formatters.formatter import Formatter


class CommaSpaceFormatter(Formatter):
    """Ensures commas are followed by a space or a newline.

    Commas should have no space before them and either a space or a
    newline after them.

    Accepts token types: `comma`

    Examples
    --------

    ```python
    from cleer import CommaSpaceFormatter

    formatter = CommaSpaceFormatter()
    result = formatter.format(" ,")
    ```
    """
    accepts_token_types = ["comma"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for comma spacing.

        Parameters
        ----------
        token : str
            String token to inspect (comma with surrounding whitespace).

        Examples
        --------

        ```python
        formatter = CommaSpaceFormatter()
        message = formatter.inspect(" ,")
        ```

        Returns
        -------
        str | None
            Error message if comma spacing is incorrect, `None` otherwise.
        """
        formatted = self.format(token)
        if formatted != token:
            return "Commas should have no space before and a space or newline after"

        return None


    def format(self, token: str) -> str:
        """Format comma spacing.

        Removes space before comma and ensures a space or newline after.

        Parameters
        ----------
        token : str
            Token to format (comma with surrounding whitespace).

        Examples
        --------

        ```python
        formatter = CommaSpaceFormatter()
        result = formatter.format(" ,  ")
        ```

        Returns
        -------
        str
            Comma with no preceding space and followed by a space or newline.
        """
        if "\n" in token:
            comma_pos = token.index(",")
            after_comma = token[comma_pos + 1:]
            newline_pos = after_comma.find("\n")
            if newline_pos != -1:
                return "," + after_comma[newline_pos:]

        return ", "
