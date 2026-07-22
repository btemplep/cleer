"""Import parenthesis formatter module."""

__all__ = ["PyImportParenthesisFormatter"]


import re

from cleer.formatters.formatter import Formatter


class PyImportParenthesisFormatter(Formatter):
    """Wraps imports with more than 3 items into parenthesized multi-line format.

    Imports that have more than 3 items in an `import` or `from ... import`
    statement are reformatted with parentheses and each item on its own line.

    Accepts token types: `import_statement`

    Examples
    --------

    ```python
    from cleer import PyImportParenthesisFormatter

    formatter = PyImportParenthesisFormatter()
    result = formatter.format("from thing import a, b, c, d")
    ```
    """
    accepts_token_types = ["import_statement"]


    def _get_indent(self, token: str) -> str:
        """Get the leading indent of the token."""
        match = re.match(r"^(\s*)", token)

        return match.group(1) if match else ""


    def _parse_from_import(
        self,
        token: str
    ) -> tuple[str | None, list[str] | None]:
        """Parse a from...import statement into module and items."""
        stripped = token.strip()

        if "(" in stripped:
            match = re.match(
                r"from\s+([\w.]+)\s+import\s*\(\s*",
                stripped
            )
            if match:
                module = match.group(1)
                content = stripped[stripped.index("(") + 1:stripped.rindex(")")]
                items = [item.strip().rstrip(",") for item in content.split(",") if item.strip().rstrip(",")]

                return module, items

        else:
            match = re.match(
                r"from\s+([\w.]+)\s+import\s+(.+)",
                stripped,
                re.DOTALL
            )
            if match:
                module = match.group(1)
                items_str = match.group(2).replace("\\\n", " ")
                items = [item.strip().rstrip(",") for item in items_str.split(",") if item.strip().rstrip(",")]

                return module, items

        return None, None


    def _parse_plain_import(
        self,
        token: str
    ) -> list[str] | None:
        """Parse a plain import statement into items."""
        stripped = token.strip()
        match = re.match(r"import\s+(.+)", stripped, re.DOTALL)
        if match:
            items_str = match.group(1).replace("\\\n", " ")
            items = [item.strip().rstrip(",") for item in items_str.split(",") if item.strip().rstrip(",")]

            return items

        return None


    def inspect(self, token: str) -> str | None:
        """Inspect a token for imports needing parenthesization.

        Parameters
        ----------
        token : str
            String token to inspect (single import statement).

        Examples
        --------

        ```python
        formatter = PyImportParenthesisFormatter()
        message = formatter.inspect("from thing import a, b, c, d")
        ```

        Returns
        -------
        str | None
            Error message if import needs parenthesization, `None` otherwise.
        """
        formatted = self.format(token)
        if formatted != token:
            return "Import with more than 3 items should use parenthesized multi-line format."

        return None


    def format(self, token: str) -> str:
        """Format imports with more than 3 items into parenthesized multi-line.

        Parameters
        ----------
        token : str
            Token to format (single import statement).

        Examples
        --------

        ```python
        formatter = PyImportParenthesisFormatter()
        result = formatter.format("from thing import a, b, c, d")
        ```

        Returns
        -------
        str
            Token reformatted with parentheses if more than 3 items.
        """
        indent = self._get_indent(token)
        stripped = token.strip()

        if stripped.startswith("from "):
            module, items = self._parse_from_import(token)
            if module is None or items is None:
                return token

            if len(items) <= 3:
                return token

            if "(" in stripped:
                content_section = stripped[stripped.index("(") + 1:stripped.rindex(")")]
                has_trailing_comma = content_section.rstrip().endswith(",")
            else:
                has_trailing_comma = stripped.rstrip().endswith(",")

            lines = [f"{indent}from {module} import ("]
            for i, item in enumerate(items):
                if i == len(items) - 1 and not has_trailing_comma:
                    lines.append(f"{indent}    {item}")
                else:
                    lines.append(f"{indent}    {item},")

            lines.append(f"{indent})")

            return "\n".join(lines)
        elif stripped.startswith("import "):
            items = self._parse_plain_import(token)

            if len(items) <= 3:
                return token

            has_trailing_comma = stripped.rstrip().endswith(",")

            lines = [f"{indent}import ("]
            for i, item in enumerate(items):
                if i == len(items) - 1 and not has_trailing_comma:
                    lines.append(f"{indent}    {item}")
                else:
                    lines.append(f"{indent}    {item},")

            lines.append(f"{indent})")

            return "\n".join(lines)

        return token
