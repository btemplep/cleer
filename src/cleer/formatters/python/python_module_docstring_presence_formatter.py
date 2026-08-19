"""See [](#cleer.formatters.python.python_module_docstring_presence_formatter.PythonModuleDocstringPresenceFormatter)"""

__all__ = [
    "PythonModuleDocstringPresenceFormatter"
]

import ast

from cleer.formatters.formatter import Formatter, FormatterViolation


class PythonModuleDocstringPresenceFormatter(Formatter):
    """Enforce that a module docstring exists at the top of the file.

    Receives the entire document (from `FileTokenizer`). If no module
    docstring is found as the first statement, inserts a placeholder
    docstring at the top.

    If a module docstring already exists, the document is returned
    unchanged.

    Examples
    --------

    ```python
    from cleer import PythonModuleDocstringPresenceFormatter

    formatter = PythonModuleDocstringPresenceFormatter()
    result = formatter.format("import os\\n")
    ```
    """
    accepts_token_types = ["file"]


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect whether a module docstring exists.

        Parameters
        ----------
        token : str
            Entire document content.

        Returns
        -------
        list[FormatterViolation]
            List of violations found, empty if no violations.
        """
        if self._has_module_docstring(token):
            return []

        return [
            {
                "start_index": 0,
                "length": len(token),
                "message": "Modules should have a docstring."
            }
        ]


    def format(self, token: str) -> str:
        """Insert a placeholder module docstring if missing.

        Parameters
        ----------
        token : str
            Entire document content.

        Returns
        -------
        str
            Document with a placeholder module docstring inserted if
            it was missing.
        """
        if self._has_module_docstring(token):
            return token

        return f'\"\"\"TODO: Add module docstring.\"\"\"\n\n{token}'


    def _has_module_docstring(self, document: str) -> bool:
        try:
            tree = ast.parse(document)
        except SyntaxError:
            return True

        if not tree.body:
            return False

        first_node = tree.body[0]

        return (
            isinstance(first_node, ast.Expr)
            and isinstance(first_node.value, ast.Constant)
            and isinstance(first_node.value.value, str)
        )
