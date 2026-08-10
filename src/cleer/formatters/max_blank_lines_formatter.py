"""See :class:`MaxBlankLinesFormatter`."""

__all__ = [
    "MaxBlankLinesFormatter"
]

from cleer.formatters.formatter import Formatter, FormatterViolation


class MaxBlankLinesFormatter(Formatter):
    """Format runs of consecutive blank lines to a maximum.

    Replaces any run of consecutive blank lines that exceeds the configured
    maximum with exactly the maximum number of blank lines.

    Parameters
    ----------
    max_blank_lines : int, default=2
        The maximum number of consecutive blank lines allowed.

    Examples
    --------

    ```python
    from cleer import MaxBlankLinesFormatter

    formatter = MaxBlankLinesFormatter()
    result = formatter.format("\n\n\n\n\n")
    ```
    """
    accepts_token_types = ["whitespace"]


    def __init__(self, max_blank_lines: int=2):
        self._max_blank_lines = max_blank_lines
        self._replacement = "\n" * (max_blank_lines + 1)


    def _count_blank_lines(self, token: str) -> int:
        newline_count = token.count("\n")

        if newline_count <= 1:
            return 0

        return newline_count - 1


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect a token for too many consecutive blank lines.

        Parameters
        ----------
        token : str
            String token to inspect (whitespace block).

        Returns
        -------
        list[FormatterViolation]
            List of violations if there are more blank lines than allowed.
            Returns an empty list if there is no violation.
        """
        blank_lines = self._count_blank_lines(token)

        if blank_lines > self._max_blank_lines:
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": f"No more than {self._max_blank_lines} consecutive blank line(s) allowed."
                }
            ]

        return []


    def format(self, token: str) -> str:
        """Format a run of blank lines down to the maximum.

        Parameters
        ----------
        token : str
            Token to format (whitespace block).

        Returns
        -------
        str
            The token unchanged if within limits, or the maximum allowed
            number of consecutive blank lines with any trailing indentation
            preserved.
        """
        blank_lines = self._count_blank_lines(token)

        if blank_lines > self._max_blank_lines:
            last_newline = token.rfind("\n")
            trailing = token[last_newline + 1:]

            return self._replacement + trailing

        return token
