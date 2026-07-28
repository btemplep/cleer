"""Python decorator boundary formatter module."""

__all__ = ["PythonDecoratorBoundaryFormatter"]


from cleer.formatters.formatter import Formatter


class PythonDecoratorBoundaryFormatter(Formatter):
    """Remove blank lines between decorators and function definitions.

    Ensures there are no blank lines between consecutive decorators or
    between the last decorator and the function/method definition.

    Examples
    --------

    ```python
    from cleer import PythonDecoratorBoundaryFormatter

    formatter = PythonDecoratorBoundaryFormatter()
    result = formatter.format("\n\n")
    ```
    """
    accepts_token_types = ["python_decorator_boundary"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for blank lines between decorators and definitions.

        Parameters
        ----------
        token : str
            String token to inspect (whitespace between decorator and def).

        Returns
        -------
        str | None
            Error message if blank lines exist between decorator and definition.
            Returns `None` if there is no violation.
        """
        return "There should be no blank lines between decorators and function definitions."


    def format(self, token: str) -> str:
        """Remove blank lines between decorators and definitions.

        Parameters
        ----------
        token : str
            Token to format (whitespace between decorator and def).

        Returns
        -------
        str
            Empty string to remove all blank lines.
        """
        return ""
