"""Python max one space formatter module."""

__all__ = [
    "PythonMaxOneSpaceFormatter"
]

from cleer.formatters.formatter import Formatter


class PythonMaxOneSpaceFormatter(Formatter):
    """Replace runs of multiple spaces with a single space.

    Examples
    --------

    ```python
    from cleer import PythonMaxOneSpaceFormatter

    formatter = PythonMaxOneSpaceFormatter()
    result = formatter.format("   ")
    ```
    """
    accepts_token_types = ["python_max_one_space"]


    def inspect(self, token: str) -> str | None:
        """Inspect for multiple consecutive spaces.

        Parameters
        ----------
        token : str
            String token to inspect.

        Returns
        -------
        str | None
            Error message if multiple consecutive spaces found.
            Returns `None` if there is no violation.
        """
        if len(token) > 1:
            return "Only one consecutive space is allowed outside of indentation and string literals."

        return None


    def format(self, token: str) -> str:
        """Replace multiple spaces with a single space.

        Parameters
        ----------
        token : str
            Token to format (a run of 2+ spaces).

        Returns
        -------
        str
            A single space.
        """
        return " "
