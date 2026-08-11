"""See :class:`PythonColonSpaceFormatter`."""

__all__ = [
    "PythonColonSpaceFormatter"
]

from cleer.formatters.formatter import Formatter, FormatterViolation


class PythonColonSpaceFormatter(Formatter):
    """Enforce no space before colon, one space after.

    Examples
    --------

    ```python
    from cleer import PythonColonSpaceFormatter

    formatter = PythonColonSpaceFormatter()
    result = formatter.format(" : ")
    ```
    """
    accepts_token_types = ["python_colon_space"]


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect colon spacing.

        Parameters
        ----------
        token : str
            String token containing colon with surrounding whitespace.

        Returns
        -------
        list[FormatterViolation]
            List of violations. Empty if spacing is correct.
        """
        if token != ": ":
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": "Colons should have no space before and one space after."
                }
            ]

        return []


    def format(self, token: str) -> str:
        """Enforce no space before colon, one space after.

        Parameters
        ----------
        token : str
            Token to format (colon with surrounding whitespace).

        Returns
        -------
        str
            ``: `` (no space before, one space after).
        """
        return ": "
