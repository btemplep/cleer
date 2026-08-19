"""See [](#cleer.formatters.python.python_kwargs_space_formatter.PythonKwargsSpaceFormatter)"""

__all__ = [
    "PythonKwargsSpaceFormatter"
]

from cleer.formatters.formatter import Formatter, FormatterViolation


class PythonKwargsSpaceFormatter(Formatter):
    """Enforce no spaces around = in keyword arguments and defaults.

    Examples
    --------

    ```python
    from cleer import PythonKwargsSpaceFormatter

    formatter = PythonKwargsSpaceFormatter()
    result = formatter.format(" = ")
    ```
    """
    accepts_token_types = ["python_kwargs_space"]


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect kwarg = spacing.

        Parameters
        ----------
        token : str
            String token containing = with surrounding whitespace.

        Returns
        -------
        list[FormatterViolation]
            List of violations. Empty if spacing is correct.
        """
        if token != "=":
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": "Keyword argument = should have no surrounding spaces."
                }
            ]

        return []


    def format(self, token: str) -> str:
        """Remove spaces around kwarg =.

        Parameters
        ----------
        token : str
            Token to format (= with surrounding whitespace).

        Returns
        -------
        str
            Just `=` with no surrounding spaces.
        """
        return "="
