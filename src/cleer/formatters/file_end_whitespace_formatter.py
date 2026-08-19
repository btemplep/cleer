"""See [](#cleer.formatters.file_end_whitespace_formatter.FileEndWhitespaceFormatter)"""

__all__ = [
    "FileEndWhitespaceFormatter"
]

from cleer.formatters.formatter import Formatter, FormatterViolation


class FileEndWhitespaceFormatter(Formatter):
    """Format the number of blank lines at the end of a file.


    Parameters
    ----------
    blank_lines : int, default=1
        Number of blank lines to enforce at the end of a file.

    Examples
    --------
    ```python
    from cleer import FileEndWhitespaceFormatter

    formatter = FileEndWhitespaceFormatter()
    result = formatter.format("\n\n\n")
    ```
    """
    accepts_token_types = ["file_end_whitespace"]


    def __init__(self, blank_lines: int=1):
        self._blank_lines = blank_lines
        self._ending_token = "\n" * blank_lines


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect a token for improper trailing whitespace.

        Parameters
        ----------
        token : str
            String token to inspect (trailing whitespace from file).

        Returns
        -------
        list[FormatterViolation]
            List of violations if trailing whitespace does not match the expected.
            Returns an empty list if there is no violation.
        """
        if token != self._ending_token:
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": f"Files should end with {self._blank_lines} blank line(s)."
                }
            ]

        return []


    def format(self, token: str) -> str:
        """Format trailing whitespace.

        Parameters
        ----------
        token : str
            Token to format (trailing whitespace from file).

        Returns
        -------
        str
            The number configured number of blank lines.
        """
        return self._ending_token
