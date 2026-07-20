__all__ = ["MaxNewlinesFormatter"]


from cleer.formatters.formatter import Formatter


class MaxNewlinesFormatter(Formatter):
    """Reduces excessive consecutive newlines to a maximum of 3.

    Any token with more than 3 consecutive newline characters (representing
    more than 2 blank lines) is reduced to exactly 3 newlines (2 blank lines).

    Accepts token types: `max_newlines`

    Examples
    --------

    ```python
    from cleer import MaxNewlinesFormatter

    formatter = MaxNewlinesFormatter()
    result = formatter.format("\\n\\n\\n\\n\\n")
    ```
    """
    accepts_token_types = ["max_newlines"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for excessive consecutive newlines.

        Parameters
        ----------
        token : str
            String token to inspect.

        Examples
        --------

        ```python
        formatter = MaxNewlinesFormatter()
        message = formatter.inspect("\\n\\n\\n\\n")
        ```

        Returns
        -------
        str | None
            Error message if more than 3 consecutive newlines are found,
            `None` otherwise.
        """
        if len(token) > 3:
            return "There should be no more than 2 consecutive blank lines."

        return None


    def format(self, token: str) -> str:
        """Reduce consecutive newlines to exactly 3.

        Parameters
        ----------
        token : str
            Token to format.

        Examples
        --------

        ```python
        formatter = MaxNewlinesFormatter()
        result = formatter.format("\\n\\n\\n\\n\\n")
        ```

        Returns
        -------
        str
            Exactly 3 newline characters.
        """
        return "\n\n\n"
