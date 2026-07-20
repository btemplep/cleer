"""Class var whitespace formatter module."""

__all__ = ["PyClassVarWhitespaceFormatter"]


from cleer.formatters.formatter import Formatter


class PyClassVarWhitespaceFormatter(Formatter):
    """Ensures no blank lines between class declaration and pass or class vars.

    The whitespace between a class declaration and the first body line
    should be exactly 1 newline character when the body starts with
    ``pass`` or a class variable.

    Accepts token types: ``class_var_whitespace``

    Examples
    --------

    ```python
    from cleer import PyClassVarWhitespaceFormatter

    formatter = PyClassVarWhitespaceFormatter()
    result = formatter.format("\\n\\n\\n")
    ```
    """
    accepts_token_types = ["class_var_whitespace"]


    def inspect(self, token: str) -> str | None:
        """Inspect whitespace between class declaration and pass or class var.

        Parameters
        ----------
        token : str
            String token to inspect (whitespace between class decl and body).

        Examples
        --------

        ```python
        formatter = PyClassVarWhitespaceFormatter()
        message = formatter.inspect("\\n\\n")
        ```

        Returns
        -------
        str | None
            Error message if spacing is incorrect, ``None`` otherwise.
        """
        if token != "\n":
            return "There should be no blank lines between class declaration and pass or class vars."

        return None


    def format(self, token: str) -> str:
        """Format whitespace to exactly 1 newline (no blank lines).

        Parameters
        ----------
        token : str
            Token to format (whitespace between class decl and body).

        Examples
        --------

        ```python
        formatter = PyClassVarWhitespaceFormatter()
        result = formatter.format("\\n\\n\\n")
        ```

        Returns
        -------
        str
            Exactly 1 newline character.
        """
        return "\n"
