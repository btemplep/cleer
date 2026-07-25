"""File start whitespace formatter module."""

__all__ = ["FileStartWhitespaceFormatter"]


from cleer.formatters.formatter import Formatter


class FileStartWhitespaceFormatter(Formatter):
    """Format the number of blank lines at the start of a file.

    Parameters
    ----------
    spaces : int, default=0
        Number of blank lines to enforce at the start of a file.

    Examples
    --------

    ```python
    from cleer import FileStartWhitespaceFormatter

    formatter = FileStartWhitespaceFormatter()
    result = formatter.format("\n\n\n")
    ```
    """
    accepts_token_types = ["file_start_whitespace"]


    def __init__(self, spaces: int = 0):
        self._spaces = spaces
        self._starting_token = "\n" * spaces


    def inspect(self, token: str) -> str | None:
        """Inspect a token for improper leading whitespace.

        Parameters
        ----------
        token : str
            String token to inspect (leading whitespace from file).

        Returns
        -------
        str | None
            Error message if leading whitespace does not match the expected.
            Returns `None` if there is no violation.
        """
        if token != self._starting_token:
            return f"Files should start with {self._spaces} blank line(s)."

        return None


    def format(self, token: str) -> str:
        """Format leading whitespace.

        Parameters
        ----------
        token : str
            Token to format (leading whitespace from file).

        Returns
        -------
        str
            The configured number of blank lines.
        """
        return self._starting_token
