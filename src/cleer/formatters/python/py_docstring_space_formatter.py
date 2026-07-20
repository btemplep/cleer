"""Docstring space formatter module."""

__all__ = ["PyDocstringSpaceFormatter"]


from cleer.formatters.formatter import Formatter


class PyDocstringSpaceFormatter(Formatter):
    """Ensures no blank lines between class/function definition and its docstring.

    When a class or function has a docstring as its first content, there should
    be no blank lines between the definition line and the docstring.

    Accepts token types: `docstring_space`

    Examples
    --------

    ```python
    from cleer import PyDocstringSpaceFormatter

    formatter = PyDocstringSpaceFormatter()
    result = formatter.format("\\n\\n    ")
    ```
    """
    accepts_token_types = ["docstring_space"]


    def inspect(self, token: str) -> str | None:
        """Inspect whitespace between definition and docstring.

        Parameters
        ----------
        token : str
            String token to inspect (whitespace between definition and docstring).

        Examples
        --------

        ```python
        formatter = PyDocstringSpaceFormatter()
        message = formatter.inspect("\\n\\n    ")
        ```

        Returns
        -------
        str | None
            Error message if there are extra blank lines, `None` otherwise.
        """
        indentation = token.rsplit("\n", 1)[-1]
        expected = "\n" + indentation
        if token != expected:
            return "There should be no blank lines between a definition and its docstring."

        return None


    def format(self, token: str) -> str:
        """Format whitespace between definition and docstring to exactly one newline.

        Parameters
        ----------
        token : str
            Token to format (whitespace between definition and docstring).

        Examples
        --------

        ```python
        formatter = PyDocstringSpaceFormatter()
        result = formatter.format("\\n\\n    ")
        ```

        Returns
        -------
        str
            Single newline followed by the original indentation.
        """
        indentation = token.rsplit("\n", 1)[-1]

        return "\n" + indentation
