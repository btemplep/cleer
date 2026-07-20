"""Binary operator space formatter module."""

__all__ = ["BinaryOperatorSpaceFormatter"]


import re

from cleer.formatters.formatter import Formatter


class BinaryOperatorSpaceFormatter(Formatter):
    """Ensures binary operators have a single space on both sides.

    Accepts token types: `binary_operator`

    Examples
    --------

    ```python
    from cleer import BinaryOperatorSpaceFormatter

    formatter = BinaryOperatorSpaceFormatter()
    result = formatter.format("  =  ")
    ```
    """
    accepts_token_types = ["binary_operator"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for binary operator spacing.

        Parameters
        ----------
        token : str
            String token to inspect (operator with surrounding whitespace).

        Examples
        --------

        ```python
        formatter = BinaryOperatorSpaceFormatter()
        message = formatter.inspect("=")
        ```

        Returns
        -------
        str | None
            Error message if spacing is incorrect, `None` otherwise.
        """
        if token != f" {token.strip()} ":
            return f"Binary operators should have a single space on both sides."

        return None


    def format(self, token: str) -> str:
        """Format binary operator to have a single space on both sides.

        Parameters
        ----------
        token : str
            Token to format (operator with surrounding whitespace).

        Examples
        --------

        ```python
        formatter = BinaryOperatorSpaceFormatter()
        result = formatter.format("  =  ")
        ```

        Returns
        -------
        str
            Operator with exactly one space on each side.
        """
        return f" {token.strip()} "
