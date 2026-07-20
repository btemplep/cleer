"""File end whitespace formatter module."""

__all__ = ["FileEndWhitespaceFormatter"]


from cleer.formatters.formatter import Formatter


class FileEndWhitespaceFormatter(Formatter):
    """Ensures exactly one trailing newline at the end of a file.

    Accepts `file_end_whitespace` tokens and formats them to a single
    newline character, ensuring the file ends with exactly one newline.

    Examples
    --------

    ```python
    from cleer import FileEndWhitespaceFormatter

    formatter = FileEndWhitespaceFormatter()
    result = formatter.format("\\n\\n\\n")
    ```
    """
    accepts_token_types = ["file_end_whitespace"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for improper trailing whitespace.

        Parameters
        ----------
        token : str
            String token to inspect (trailing whitespace from file).

        Examples
        --------

        ```python
        formatter = FileEndWhitespaceFormatter()
        message = formatter.inspect("\\n\\n\\n")
        ```

        Returns
        -------
        str | None
            Error message if trailing whitespace is not exactly one newline,
            `None` otherwise.
        """
        if token != "\n":
            return "Files should end with exactly one trailing newline."

        return None


    def format(self, token: str) -> str:
        """Format trailing whitespace to exactly one newline.

        Parameters
        ----------
        token : str
            Token to format (trailing whitespace from file).

        Examples
        --------

        ```python
        formatter = FileEndWhitespaceFormatter()
        result = formatter.format("\\n\\n\\n")
        ```

        Returns
        -------
        str
            A single newline character.
        """
        return "\n"
