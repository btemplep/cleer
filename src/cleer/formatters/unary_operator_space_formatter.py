"""Unary operator space formatter module."""

__all__ = ["UnaryOperatorSpaceFormatter"]


from cleer.formatters.formatter import Formatter


class UnaryOperatorSpaceFormatter(Formatter):
    """Removes spaces between unary operators and their operands.

    Accepts token types: `unary_operator`

    Examples
    --------

    ```python
    from cleer import UnaryOperatorSpaceFormatter

    formatter = UnaryOperatorSpaceFormatter()
    result = formatter.format("- 1")
    ```
    """
    accepts_token_types = ["unary_operator"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for spaces after unary operators.

        Parameters
        ----------
        token : str
            String token to inspect.

        Examples
        --------

        ```python
        formatter = UnaryOperatorSpaceFormatter()
        message = formatter.inspect("- 1")
        ```

        Returns
        -------
        str | None
            Error message if there is a space after the unary operator,
            `None` otherwise.
        """
        if self.format(token) != token:
            return "Unary operators should not have a space between the operator and the operand."

        return None


    def format(self, token: str) -> str:
        """Remove space between unary operator and operand.

        Parameters
        ----------
        token : str
            Token to format (operator possibly followed by spaces and operand).

        Examples
        --------

        ```python
        formatter = UnaryOperatorSpaceFormatter()
        result = formatter.format("- 1")
        ```

        Returns
        -------
        str
            Token with no space between operator and operand.
        """
        if len(token) > 1 and token[0] in "-+~":
            return token[0] + token[1:].lstrip()

        return token
