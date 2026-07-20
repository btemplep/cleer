"""File start whitespace formatter module."""

__all__ = ["FileStartWhitespaceFormatter"]


from cleer.formatters.formatter import Formatter


class FileStartWhitespaceFormatter(Formatter):
    """Removes leading whitespace from the start of a file.

    Accepts `file_start_whitespace` tokens and formats them to an empty
    string, effectively removing any leading whitespace from the file.

    Examples
    --------

    ```python
    from cleer import FileStartWhitespaceFormatter

    formatter = FileStartWhitespaceFormatter()
    result = formatter.format("\\n\\n  ")
    ```
    """
    accepts_token_types = ["file_start_whitespace"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for leading file whitespace.

        Parameters
        ----------
        token : str
            String token to inspect (leading whitespace from file).

        Examples
        --------

        ```python
        formatter = FileStartWhitespaceFormatter()
        message = formatter.inspect("\\n  ")
        ```

        Returns
        -------
        str | None
            Error message if leading whitespace exists, `None` otherwise.
        """
        if token:
            return "Files should have no leading whitespace."

        return None


    def format(self, token: str) -> str:
        """Remove leading whitespace from the start of a file.

        Parameters
        ----------
        token : str
            Token to format (leading whitespace from file).

        Examples
        --------

        ```python
        formatter = FileStartWhitespaceFormatter()
        result = formatter.format("\\n\\n  ")
        ```

        Returns
        -------
        str
            An empty string.
        """
        return ""
