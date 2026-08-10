"""See :class:`PythonCommaSpaceFormatter`."""

__all__ = [
    "PythonCommaSpaceFormatter"
]

from cleer.formatters.formatter import Formatter, FormatterViolation


class PythonCommaSpaceFormatter(Formatter):
    """Enforce no space before comma, one space after (or newline).

    For single-line comma sequences, enforces `, ` (no space before,
    one space after). For multi-line sequences where the next element is
    on a new line, preserves the newline and indentation.

    Examples
    --------

    ```python
    from cleer import PythonCommaSpaceFormatter

    formatter = PythonCommaSpaceFormatter()
    result = formatter.format(" , ")
    ```
    """
    accepts_token_types = ["python_comma_space"]


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect comma spacing.

        Parameters
        ----------
        token : str
            String token containing comma with surrounding context.

        Returns
        -------
        list[FormatterViolation]
            List of violations. Empty if spacing is correct.
        """
        if "," not in token:
            return []

        comma_idx = token.index(",")
        before = token[:comma_idx]
        after = token[comma_idx + 1:]

        if (
            before != before.rstrip(" \t")
            or (
                after != " "
                and not after.startswith("\n")
            )
        ):
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": "There should be no space before a comma, and one space after."
                }
            ]

        return []


    def format(self, token: str) -> str:
        """Enforce correct comma spacing.

        Parameters
        ----------
        token : str
            Token to format (segment containing a comma).

        Returns
        -------
        str
            Correctly spaced comma segment.
        """
        if "," not in token:
            return token

        comma_idx = token.index(",")
        before = token[:comma_idx]
        after = token[comma_idx + 1:]

        before_fixed = before.rstrip(" \t")

        if "\n" in after:
            newline_idx = after.index("\n")

            return before_fixed + "," + after[newline_idx:]

        return before_fixed + ", "
