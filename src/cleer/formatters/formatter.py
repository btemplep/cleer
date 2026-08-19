"""See [](#cleer.formatters.formatter.Formatter) and [](#cleer.formatters.formatter.FormatterViolation)"""

__all__ = [
    "Formatter",
    "FormatterViolation"
]

from typing import TypedDict


class FormatterViolation(TypedDict):
    """Violation data returned directly from a Formatter's inspect method.

    Examples
    --------

    ```python
    {
        "start_index": 4,
        "length": 3,
        "message": "Lines should not have any trailing whitespace."
    }
    ```

    Attributes
    ----------
    start_index : int
        Start index of the violation within the token.
    length : int
        Length of the violating span within the token.
    message : str
        Message describing the violation.
    """
    start_index: int
    length: int
    message: str


class Formatter:
    """Formatter base class.

    Formatters are use by cleer to:
    - inspect tokens to see if they are formatted correctly
    - format tokens

    Formatters must implement the `inspect` and `format` methods
    """
    accepts_token_types: list[str] = []


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect a token for violations.

        Formatters must implement this method.

        Parameters
        ----------
        token : str
            String token to inspect.

        Returns
        -------
        list[FormatterViolation]
            List of formatter violations. An empty list mean no violations.
        """
        raise NotImplementedError("Formatter classes must implement the inspect method!")


    def format(self, token: str) -> str:
        """Format the given token.

        Formatters must implement this method.

        Parameters
        ----------
        token : str
            Token to format.

        Returns
        -------
        str
            Formatted token.
        """
        raise NotImplementedError("Formatter classes must implement the format method!")
