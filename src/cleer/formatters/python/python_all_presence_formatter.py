"""See :class:`PythonAllPresenceFormatter`."""

__all__ = [
    "PythonAllPresenceFormatter"
]

import ast

from cleer.formatters.formatter import Formatter, FormatterViolation


class PythonAllPresenceFormatter(Formatter):
    """Enforce that `__all__` exists in a module.

    Receives the entire document (from `FileTokenizer`). If no
    `__all__` assignment is found, inserts `__all__ = []` after the
    module docstring (if present) and before imports or other code.

    If `__all__` already exists, the document is returned unchanged.

    Examples
    --------

    ```python
    from cleer import PythonAllPresenceFormatter

    formatter = PythonAllPresenceFormatter()
    result = formatter.format("import os\\n")
    ```
    """
    accepts_token_types = ["file"]


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect whether `__all__` exists in the module.

        Parameters
        ----------
        token : str
            Entire document content.

        Returns
        -------
        list[FormatterViolation]
            List of violations. Empty if `__all__` exists.
        """
        if self._has_all(token):
            return []

        return [
            {
                "start_index": 0,
                "length": len(token),
                "message": "Modules should define __all__."
            }
        ]


    def format(self, token: str) -> str:
        """Insert `__all__ = []` if missing.

        Parameters
        ----------
        token : str
            Entire document content.

        Returns
        -------
        str
            Document with `__all__ = []` inserted if it was missing.
        """
        if self._has_all(token):
            return token

        return self._insert_all(token)


    def _has_all(self, document: str) -> bool:
        try:
            tree = ast.parse(document)
        except SyntaxError:
            return True

        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue

            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    return True

        return False


    def _insert_all(self, document: str) -> str:
        try:
            tree = ast.parse(document)
        except SyntaxError:
            return document

        if not tree.body:
            return "__all__ = []\n"

        insert_after_line = 0

        first_node = tree.body[0]
        if (
            isinstance(first_node, ast.Expr)
            and isinstance(first_node.value, ast.Constant)
            and isinstance(first_node.value.value, str)
        ):
            insert_after_line = first_node.end_lineno

        lines = document.split("\n")

        before = lines[:insert_after_line]
        after = lines[insert_after_line:]

        if before:
            result = "\n".join(before) + "\n\n__all__ = []\n\n" + "\n".join(after)
        else:
            result = "__all__ = []\n\n" + "\n".join(after)

        return result
