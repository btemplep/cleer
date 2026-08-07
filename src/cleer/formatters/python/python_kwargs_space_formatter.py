"""Python kwargs space formatter module."""

__all__ = [
    "PythonKwargsSpaceFormatter"
]

from cleer.formatters.formatter import Formatter


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


    def inspect(self, token: str) -> str | None:
        """Inspect kwarg = spacing.

        Parameters
        ----------
        token : str
            String token containing = with surrounding whitespace.

        Returns
        -------
        str | None
            Error message if spacing is incorrect.
            Returns `None` if there is no violation.
        """
        if token != "=":
            return "Keyword argument = should have no surrounding spaces."

        return None


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
