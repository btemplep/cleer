"""Import entry sort formatter module."""

__all__ = ["PyImportEntrySortFormatter"]


import re

from cleer.formatters.formatter import Formatter


class PyImportEntrySortFormatter(Formatter):
    """Sorts entries within a from...import statement alphabetically.

    Multiple entries in a `from ... import` statement are sorted in
    alphabetical order.

    Accepts token types: `import_statement`

    Examples
    --------

    ```python
    from cleer import PyImportEntrySortFormatter

    formatter = PyImportEntrySortFormatter()
    result = formatter.format("from thing import c, a, b")
    ```
    """
    accepts_token_types = ["import_statement"]


    def _get_indent(self, token: str) -> str:
        """Get the leading indent of the token."""
        match = re.match(r"^(\s*)", token)

        return match.group(1) if match else ""


    def _is_from_import(self, token: str) -> bool:
        """Check if the token is a from...import statement."""
        return token.strip().startswith("from ")


    def _parse_items(
        self,
        token: str
    ) -> tuple[str | None, list[str] | None, bool]:
        """Parse items from a from...import statement."""
        stripped = token.strip()

        if "(" in stripped:
            match = re.match(r"from\s+([\w.]+)\s+import\s*\(", stripped)
            if match:
                module = match.group(1)
                content = stripped[stripped.index("(") + 1:stripped.rindex(")")]
                items = [item.strip().rstrip(",") for item in content.split(",") if item.strip().rstrip(",")]

                return module, items, True

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

                return module, items, False

        return None, None, False


    def inspect(self, token: str) -> str | None:
        """Inspect a token for unsorted import entries.

        Parameters
        ----------
        token : str
            String token to inspect (single import statement).

        Examples
        --------

        ```python
        formatter = PyImportEntrySortFormatter()
        message = formatter.inspect("from thing import c, a, b")
        ```

        Returns
        -------
        str | None
            Error message if import entries are not sorted, `None` otherwise.
        """
        if not self._is_from_import(token):
            return None

        formatted = self.format(token)
        if formatted != token:
            return "Entries within a single import statement should be sorted alphabetically."

        return None


    def format(self, token: str) -> str:
        """Sort entries in a from...import statement alphabetically.

        Parameters
        ----------
        token : str
            Token to format (single import statement).

        Examples
        --------

        ```python
        formatter = PyImportEntrySortFormatter()
        result = formatter.format("from thing import c, a, b")
        ```

        Returns
        -------
        str
            Token with import entries sorted alphabetically.
        """
        if not self._is_from_import(token):
            return token

        indent = self._get_indent(token)
        module, items, has_parens = self._parse_items(token)

        if (
            module is None
            or items is None
            or len(items) <= 1
        ):
            return token

        sorted_items = sorted(items)

        if has_parens:
            is_multiline = "\n" in token
            if is_multiline:
                content_section = token[token.index("(") + 1:token.rindex(")")]
                has_trailing_comma = content_section.rstrip().endswith(",")
                lines = [f"{indent}from {module} import ("]
                for i, item in enumerate(sorted_items):
                    if i == len(sorted_items) - 1 and not has_trailing_comma:
                        lines.append(f"{indent}    {item}")
                    else:
                        lines.append(f"{indent}    {item},")

                lines.append(f"{indent})")

                return "\n".join(lines)
            else:
                return f"{indent}from {module} import ({', '.join(sorted_items)})"

        else:
            return f"{indent}from {module} import {', '.join(sorted_items)}"
