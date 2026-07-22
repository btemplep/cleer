"""Import sort formatter module."""

__all__ = ["PyImportSortFormatter"]


from cleer.formatters.formatter import Formatter


class PyImportSortFormatter(Formatter):
    """Sorts import statements within a block alphabetically.

    Uses the full import path for sorting. Multi-line imports are kept
    together as a single unit.

    Accepts token types: `import_block`

    Examples
    --------

    ```python
    from cleer import PyImportSortFormatter

    formatter = PyImportSortFormatter()
    result = formatter.format("import sys\\nimport os\\n")
    ```
    """
    accepts_token_types = ["import_block"]


    def _parse_statements(self, token: str) -> list[str]:
        """Parse individual import statements from a block."""
        lines = token.split("\n")
        statements = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if (
                stripped.startswith("import ")
                or stripped.startswith("from ")
            ):
                statement_lines = [line]

                if "(" in line and ")" not in line:
                    i += 1
                    while i < len(lines):
                        statement_lines.append(lines[i])
                        if ")" in lines[i]:
                            break

                        i += 1

                elif line.rstrip().endswith("\\"):
                    i += 1
                    while i < len(lines):
                        statement_lines.append(lines[i])
                        if not lines[i].rstrip().endswith("\\"):
                            break

                        i += 1

                statements.append("\n".join(statement_lines))

            i += 1

        return statements


    def _get_sort_key(self, statement: str) -> str:
        """Get the sort key for an import statement."""
        first_line = statement.split("\n")[0].strip()
        if first_line.startswith("from "):
            parts = first_line.split()
            if len(parts) >= 2:
                return parts[1]

        elif first_line.startswith("import "):
            parts = first_line.split()
            if len(parts) >= 2:
                return parts[1].rstrip(",")

        return first_line


    def inspect(self, token: str) -> str | None:
        """Inspect a token for unsorted imports.

        Parameters
        ----------
        token : str
            String token to inspect (import block).

        Examples
        --------

        ```python
        formatter = PyImportSortFormatter()
        message = formatter.inspect("import sys\\nimport os\\n")
        ```

        Returns
        -------
        str | None
            Error message if imports are not sorted, `None` otherwise.
        """
        formatted = self.format(token)
        if formatted != token:
            return "Imports within an import block should be sorted alphabetically."

        return None


    def format(self, token: str) -> str:
        """Sort import statements alphabetically within a block.

        Parameters
        ----------
        token : str
            Token to format (import block).

        Examples
        --------

        ```python
        formatter = PyImportSortFormatter()
        result = formatter.format("import sys\\nimport os\\n")
        ```

        Returns
        -------
        str
            Token with imports sorted alphabetically.
        """
        statements = self._parse_statements(token)

        if len(statements) <= 1:
            return token

        sorted_statements = sorted(
            statements,
            key=self._get_sort_key
        )

        return "\n".join(sorted_statements)
