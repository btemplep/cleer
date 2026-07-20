"""File whitespace formatter module."""

__all__ = ["FileWhitespaceFormatter"]


from cleer.formatters.formatter import Formatter


class FileWhitespaceFormatter(Formatter):
    """Ensures proper whitespace at the start and end of a file.

    Removes all whitespace from the start of the file and ensures exactly
    one newline character at the end of the file.

    Accepts token types: `file`

    Examples
    --------

    ```python
    from cleer import FileWhitespaceFormatter

    formatter = FileWhitespaceFormatter()
    result = formatter.format("\\n\\nimport os\\n\\n\\n")
    ```
    """
    accepts_token_types = ["file"]


    def inspect(self, token: str) -> str | None:
        """Inspect a token for improper file whitespace.

        Parameters
        ----------
        token : str
            String token to inspect (whole file content).

        Examples
        --------

        ```python
        formatter = FileWhitespaceFormatter()
        message = formatter.inspect("\\nimport os\\n\\n")
        ```

        Returns
        -------
        str | None
            Error message if file whitespace is incorrect, `None` otherwise.
        """
        if token != token.lstrip():
            return "Files should have no leading whitespace."

        if not token.endswith("\n") or token.endswith("\n\n"):
            return "Files should end with one newline."

        return None


    def format(self, token: str) -> str:
        """Fix file whitespace.

        Removes leading whitespace and ensures exactly one trailing newline.

        Parameters
        ----------
        token : str
            Token to format (whole file content).

        Examples
        --------

        ```python
        formatter = FileWhitespaceFormatter()
        result = formatter.format("\\n\\nimport os\\n\\n\\n")
        ```

        Returns
        -------
        str
            Token with leading whitespace removed and exactly one trailing newline.
        """
        result = token.lstrip()
        result = result.rstrip("\n") + "\n"

        return result
