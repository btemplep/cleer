"""See :class:`PythonUnaryOperatorSpaceFormatter`."""

__all__ = [
    "PythonUnaryOperatorSpaceFormatter"
]

from cleer.formatters.formatter import Formatter, FormatterViolation


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
    accepts_token_types = [
        "python_unary_operator_space"
    ]


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect unary negative spacing.

        Parameters
        ----------
        token : str
            String token containing unary - with operand.

        Returns
        -------
        list[FormatterViolation]
            List of violations. Empty if spacing is correct.
        """
        if (
            token.startswith("-")
            and len(token) > 1
            and token[1] == " "
        ):
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": "There should not be space between unary negative and its operand."
                }
            ]

        return []


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
