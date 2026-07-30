"""Python unary operator space formatter module."""

__all__ = ["PythonUnaryOperatorSpaceFormatter"]


from cleer.formatters.formatter import Formatter


class PythonUnaryOperatorSpaceFormatter(Formatter):
    """Remove space between unary negative and its operand.

    Examples
    --------

    ```python
    from cleer import PythonUnaryOperatorSpaceFormatter

    formatter = PythonUnaryOperatorSpaceFormatter()
    result = formatter.format("- x")
    ```
    """
    accepts_token_types = ["python_unary_operator_space"]


    def inspect(self, token: str) -> str | None:
        """Inspect unary negative spacing.

        Parameters
        ----------
        token : str
            String token containing unary - with operand.

        Returns
        -------
        str | None
            Error message if there is space between - and operand.
            Returns `None` if there is no violation.
        """
        if token.startswith("-") and len(token) > 1 and token[1] == " ":
            return "No space between unary negative and its operand."

        return None


    def format(self, token: str) -> str:
        """Remove space between unary negative and operand.

        Parameters
        ----------
        token : str
            Token to format (e.g., "- x").

        Returns
        -------
        str
            Token with no space after - (e.g., "-x").
        """
        return "-" + token[1:].lstrip()
