"""See [](#cleer.formatters.python.python_max_one_space_formatter.PythonMaxOneSpaceFormatter)"""

__all__ = [
    "PythonMaxOneSpaceFormatter"
]

from cleer.formatters.formatter import Formatter, FormatterViolation


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


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect for multiple consecutive spaces.

        Parameters
        ----------
        token : str
            String token to inspect.

        Returns
        -------
        list[FormatterViolation]
            List of violations found, empty if no violations.
        """
        if len(token) > 1:
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": "Only one consecutive space is allowed outside of indentation and string literals."
                }
            ]

        return []


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
