"""Python import section formatter module."""

__all__ = ["PythonImportFormatter"]


import ast
import sys
from typing import List

from cleer.formatters.formatter import Formatter


STDLIB_MODULES = sys.stdlib_module_names


class PythonImportFormatter(Formatter):
    """Enforce import section formatting.

    Formats import sections with 4 sorted blocks separated by blank
    lines (stdlib, third-party, internal, current package). Flattens
    multi-name imports, sorts items alphabetically, and wraps lines
    longer than 80 characters.

    Parameters
    ----------
    internal_packages : List[str] | None, optional
        List of internal package names (private repos). By default, no
        packages are classified as internal.
    current_packages : List[str] | None, optional
        List of current project package names. By default, no packages
        are classified as current.

    Examples
    --------

    ```python
    from cleer import PythonImportFormatter

    formatter = PythonImportFormatter(
        current_packages=["my_package"]
    )
    ```
    """
    accepts_token_types = ["python_import"]


    def __init__(
        self,
        internal_packages: List[str] | None = None,
        current_packages: List[str] | None = None
    ):
        self._internal_packages = internal_packages or []
        self._current_packages = current_packages or []


    def inspect(self, token: str) -> str | None:
        """Inspect import section formatting.

        Parameters
        ----------
        token : str
            Import section token with surrounding whitespace.

        Returns
        -------
        str | None
            Error message if formatting is incorrect.
            Returns `None` if there is no violation.
        """
        expected = self._format_token(token)

        if token != expected:
            return "Import section should be sorted into blocks (stdlib, third-party, internal, current) with items sorted alphabetically."

        return None


    def format(self, token: str) -> str:
        """Reformat import section.

        Parameters
        ----------
        token : str
            Import section token with surrounding whitespace.

        Returns
        -------
        str
            Correctly formatted import section.
        """
        return self._format_token(token)


    def _format_token(self, token: str) -> str:
        """Format the import section token."""
        stripped = token.strip()

        if not stripped:
            return token

        try:
            tree = ast.parse(stripped)
        except SyntaxError:
            return token

        imports = self._extract_imports(tree)

        if not imports:
            return token

        stdlib = []
        third_party = []
        internal = []
        current = []

        for imp in imports:
            category = self._classify(imp)

            if category == "stdlib":
                stdlib.append(imp)
            elif category == "internal":
                internal.append(imp)
            elif category == "current":
                current.append(imp)
            else:
                third_party.append(imp)

        blocks = []

        for block_imports in [stdlib, third_party, internal, current]:
            if not block_imports:
                continue

            lines = self._format_block(block_imports)
            blocks.append("\n".join(lines))

        body = "\n\n".join(blocks)
        leading_newline = token.startswith("\n")
        prefix = "\n" if leading_newline else ""

        return f"{prefix}{body}\n\n"


    def _extract_imports(self, tree: ast.Module) -> list:
        """Extract flattened import entries from the AST.

        Each entry is a dict:
        - type: "import" or "from"
        - module: module name (for from imports)
        - level: relative import level
        - name: imported name
        - asname: alias or None
        """
        imports = []

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {
                            "type": "import",
                            "module": alias.name,
                            "level": 0,
                            "name": alias.name,
                            "asname": alias.asname,
                            "names": None
                        }
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                level = node.level

                names = []
                for alias in node.names:
                    names.append(
                        {
                            "name": alias.name,
                            "asname": alias.asname
                        }
                    )

                imports.append(
                    {
                        "type": "from",
                        "module": module,
                        "level": level,
                        "name": module,
                        "asname": None,
                        "names": names
                    }
                )

        return imports


    def _classify(self, imp: dict) -> str:
        """Classify an import into stdlib, third_party, internal, or current."""
        if imp["level"] > 0:
            return "current"

        root_module = imp["module"].split(".")[0]

        if root_module in STDLIB_MODULES:
            return "stdlib"

        if root_module in self._current_packages:
            return "current"

        if root_module in self._internal_packages:
            return "internal"

        return "third_party"


    def _format_block(self, imports: list) -> List[str]:
        """Format a block of imports into sorted lines."""
        lines = []

        for imp in imports:
            lines.extend(self._format_import(imp))

        lines.sort(key=self._sort_key_line)

        return lines


    def _sort_key_line(self, line: str) -> str:
        """Generate a sort key for a formatted import line.

        Strips the ``from`` or ``import`` keyword so sorting is by
        module name only.
        """
        stripped = line.lstrip(".")
        leading_dots = line[:len(line) - len(stripped)]

        if stripped.startswith("from "):
            return leading_dots + stripped[5:]

        if stripped.startswith("import "):
            return leading_dots + stripped[7:]

        return line


    def _format_import(self, imp: dict) -> List[str]:
        """Format a single import entry into one or more lines."""
        if imp["type"] == "import":
            line = f"import {imp['module']}"

            if imp["asname"]:
                line += f" as {imp['asname']}"

            return [line]

        prefix = "." * imp["level"]
        module = imp["module"]
        full_module = f"{prefix}{module}"

        names = sorted(imp["names"], key=lambda n: n["name"])
        name_parts = []

        for n in names:
            if n["asname"]:
                name_parts.append(f"{n['name']} as {n['asname']}")
            else:
                name_parts.append(n["name"])

        single_line = f"from {full_module} import {', '.join(name_parts)}"

        if len(single_line) <= 80:
            return [single_line]

        import_lines = [f"from {full_module} import ("]

        for i, part in enumerate(name_parts):
            if i < len(name_parts) - 1:
                import_lines.append(f"    {part},")
            else:
                import_lines.append(f"    {part}")

        import_lines.append(")")

        return ["\n".join(import_lines)]


    def _sort_key(self, imp: dict) -> str:
        """Generate a sort key for an import."""
        if imp["type"] == "import":
            return imp["module"]

        prefix = "." * imp["level"]

        return f"{prefix}{imp['module']}"
