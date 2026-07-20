"""Import section space formatter module."""

__all__ = ["PyImportSectionSpaceFormatter"]


from cleer.formatters.formatter import Formatter


class PyImportSectionSpaceFormatter(Formatter):
    """Ensures 2 blank lines after the import section.

    The whitespace after the last import statement and before the next
    content should be exactly 3 newline characters (2 blank lines).

    Accepts token types: `import_section_space`

    Examples
    --------

    ```python
    from cleer import PyImportSectionSpaceFormatter

    formatter = PyImportSectionSpaceFormatter()
    result = formatter.format("\\n\\n\\n\\n")
    ```
    """
    accepts_token_types = ["import_section_space"]


    def inspect(self, token: str) -> str | None:
        """Inspect whitespace after import section.

        Parameters
        ----------
        token : str
            String token to inspect (whitespace after imports).

        Examples
        --------

        ```python
        formatter = PyImportSectionSpaceFormatter()
        message = formatter.inspect("\\n")
        ```

        Returns
        -------
        str | None
            Error message if spacing is incorrect, `None` otherwise.
        """
        if token != "\n\n\n":
            return "There should be exactly 2 blank lines after the import section."

        return None


    def format(self, token: str) -> str:
        """Format whitespace after import section to exactly 2 blank lines.

        Parameters
        ----------
        token : str
            Token to format (whitespace after imports).

        Examples
        --------

        ```python
        formatter = PyImportSectionSpaceFormatter()
        result = formatter.format("\\n")
        ```

        Returns
        -------
        str
            Exactly 2 blank lines (3 newline characters).
        """
        return "\n\n\n"
