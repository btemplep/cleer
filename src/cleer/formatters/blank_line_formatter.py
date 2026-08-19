"""See [](#cleer.formatters.blank_line_formatter.BlankLineFormatter)"""

__all__ = [
    "BlankLineFormatter"
]

from cleer.formatters.formatter import Formatter, FormatterViolation


class BlankLineFormatter(Formatter):
    """Replace whitespace tokens with a fixed number of blank lines.

    A generic formatter for enforcing blank line counts in whitespace
    boundary tokens. Works with any tokenizer that emits pure blank
    line content between code structures.

    Parameters
    ----------
    num_blank_lines : int
        Number of blank lines to enforce. 0 means remove all blank
        lines (empty string replacement).
    message : str
        Error message for inspect violations.

    Examples
    --------

    ```python
    from cleer import BlankLineFormatter

    formatter = BlankLineFormatter(
        num_blank_lines=2,
        message="Expected 2 blank lines."
    )
    result = formatter.format("\\n\\n\\n\\n")
    ```
    """
    accepts_token_types = [
        "python_chain_boundary",
        "python_chain_boundary_after_return",
        "python_compound_end",
        "python_function_boundary",
        "python_nested_function_boundary",
        "python_decorator_boundary",
        "python_inner_max_blank_lines",
        "python_block_start"
    ]


    def __init__(self, num_blank_lines: int, message: str):
        self._num_blank_lines = num_blank_lines
        self._replacement = "\n" * num_blank_lines
        self._message = message


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect a whitespace token for incorrect blank lines.

        Parameters
        ----------
        token : str
            Whitespace token to inspect.

        Returns
        -------
        list[FormatterViolation]
            List of violations if the token doesn't match the expected
            replacement. Returns an empty list if there is no violation.
        """
        if token != self._replacement:
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": self._message
                }
            ]

        return []


    def format(self, token: str) -> str:
        """Replace the token with the configured number of blank lines.

        Parameters
        ----------
        token : str
            Whitespace token to format.

        Returns
        -------
        str
            The configured number of newline characters.
        """
        return self._replacement
