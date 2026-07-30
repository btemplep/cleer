"""Python binary operator space formatter module."""

__all__ = ["PythonBinaryOperatorSpaceFormatter"]


from cleer.formatters.formatter import Formatter


class PythonBinaryOperatorSpaceFormatter(Formatter):
    """Enforce exactly one space around binary operators.

    Takes a token that contains an operator with its surrounding
    whitespace and reformats it to have exactly one space on each side.

    Examples
    --------

    ```python
    from cleer import PythonBinaryOperatorSpaceFormatter

    formatter = PythonBinaryOperatorSpaceFormatter()
    result = formatter.format("  =  ")
    ```
    """
    accepts_token_types = ["python_binary_operator_space"]


    def inspect(self, token: str) -> str | None:
        """Inspect operator spacing.

        Parameters
        ----------
        token : str
            String token containing operator with surrounding whitespace.

        Returns
        -------
        str | None
            Error message if spacing is incorrect.
            Returns `None` if there is no violation.
        """
        stripped = token.strip()
        expected = f" {stripped} "

        if token != expected:
            return f"Binary operators should have exactly one space on each side."

        return None


    def format(self, token: str) -> str:
        """Enforce one space around the operator.

        Parameters
        ----------
        token : str
            Token to format (operator with surrounding whitespace).

        Returns
        -------
        str
            Operator with exactly one space on each side.
        """
        stripped = token.strip()

        return f" {stripped} "
