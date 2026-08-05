"""Python __all__ formatter module."""

__all__ = ["PythonAllFormatter"]


import ast

from cleer.formatters.formatter import Formatter


class PythonAllFormatter(Formatter):
    """Enforce ``__all__`` formatting: sorted, one item per line, blank lines around.

    Enforces:
    - One blank line before and after ``__all__``
    - Items sorted alphabetically
    - One item per line (if there are any items)
    - Uses double quotes for items

    Parameters
    ----------
    quote : str, default='"'
        Quote character to use for ``__all__`` items.

    Examples
    --------

    ```python
    from cleer import PythonAllFormatter

    formatter = PythonAllFormatter()
    result = formatter.format("\\n__all__ = ['Foo', 'Bar']\\n\\n")
    ```
    """
    accepts_token_types = ["python_all"]


    def __init__(self, quote: str = '"'):
        self._quote = quote


    def inspect(self, token: str) -> str | None:
        """Inspect ``__all__`` formatting.

        Parameters
        ----------
        token : str
            String token containing ``__all__`` with surrounding blank lines.

        Returns
        -------
        str | None
            Error message if formatting is incorrect.
            Returns `None` if there is no violation.
        """
        expected = self._format_token(token)
        if token != expected:
            return "__all__ should be sorted alphabetically with one item per line and one blank line before and after."

        return None


    def format(self, token: str) -> str:
        """Reformat ``__all__``.

        Parameters
        ----------
        token : str
            Token to format (``__all__`` block with surrounding whitespace).

        Returns
        -------
        str
            Correctly formatted ``__all__`` block.
        """
        return self._format_token(token)


    def _format_token(self, token: str) -> str:
        """Format the __all__ token."""
        items = self._extract_items(token)

        if items is None:
            return token

        items.sort()

        leading_newline = token.startswith("\n")

        return self._build_all(items, leading_newline)


    def _extract_items(self, token: str) -> list[str] | None:
        """Extract the string items from __all__."""
        stripped = token.strip()

        if not stripped:
            return None

        try:
            tree = ast.parse(stripped)
        except SyntaxError:
            return None

        all_node = None
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue

            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    all_node = node
                    break

            if all_node:
                break

        if all_node is None:
            return None

        if not isinstance(all_node.value, ast.List):
            return None

        items = []
        for elt in all_node.value.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                items.append(elt.value)
            else:
                return None

        return items


    def _build_all(self, items: list[str], leading_newline: bool = True) -> str:
        """Build the formatted __all__ string."""
        q = self._quote
        prefix = "\n" if leading_newline else ""

        if not items:
            return f"{prefix}__all__ = []\n\n"

        lines = [f"    {q}{item}{q}" for item in items]
        items_str = ",\n".join(lines)

        return f"{prefix}__all__ = [\n{items_str}\n]\n\n"
