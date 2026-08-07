"""Python colon space formatter module."""

__all__ = [
    "PythonColonSpaceFormatter"
]

from cleer.formatters.formatter import Formatter


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


    def inspect(self, token: str) -> str | None:
        """Inspect colon spacing.

        Parameters
        ----------
        token : str
            String token containing colon with surrounding whitespace.

        Returns
        -------
        str | None
            Error message if spacing is incorrect.
            Returns `None` if there is no violation.
        """
        if token != ": ":
            return "Colons should have no space before and one space after."

        return None


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
