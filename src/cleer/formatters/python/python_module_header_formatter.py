"""Python module header formatter module."""

__all__ = ["PythonModuleHeaderFormatter"]


import ast

from cleer.formatters.formatter import Formatter


class PythonModuleHeaderFormatter(Formatter):
    """Enforce spacing in the module header block.

    The header block consists of (in order, each optional):
    - Module docstring
    - ``__all__`` assignment
    - Import statements

    Rules:
    - 1 blank line between adjacent header items
    - 2 blank lines between the last header item and the first
      module-level code (class, function, assignment, etc.)

    Examples
    --------

    ```python
    from cleer import PythonModuleHeaderFormatter

    formatter = PythonModuleHeaderFormatter()
    result = formatter.format('\"\"\"Doc.\"\"\"\\nimport os\\ndef foo():\\n    pass\\n')
    ```
    """
    accepts_token_types = ["file"]


    def inspect(self, token: str) -> str | None:
        """Inspect module header spacing.

        Parameters
        ----------
        token : str
            Entire document content.

        Returns
        -------
        str | None
            Error message if header spacing is incorrect.
            Returns `None` if there is no violation.
        """
        expected = self._fix_header(token)

        if token != expected:
            return "Module header should have 1 blank line between items and 2 blank lines before code."

        return None


    def format(self, token: str) -> str:
        """Fix module header spacing.

        Parameters
        ----------
        token : str
            Entire document content.

        Returns
        -------
        str
            Document with corrected header spacing.
        """
        return self._fix_header(token)


    def _fix_header(self, document: str) -> str:
        """Rebuild module header with correct spacing."""
        try:
            tree = ast.parse(document)
        except SyntaxError:
            return document

        if not tree.body:
            return document

        lines = document.split("\n")
        header_sections = self._identify_header_sections(tree)

        if not header_sections:
            return document

        last_header_end = header_sections[-1][1]
        first_code_line = self._find_first_code_line(tree, header_sections)

        result_parts = []

        for i, (start, end) in enumerate(header_sections):
            section_lines = lines[start:end]
            section_text = "\n".join(section_lines)

            while section_text.endswith("\n"):
                section_text = section_text[:-1]

            result_parts.append(section_text)

        header = "\n\n".join(result_parts)

        if first_code_line is not None:
            rest_start = self._find_rest_start(lines, last_header_end, first_code_line)
            rest_lines = lines[rest_start:]
            rest = "\n".join(rest_lines)

            return f"{header}\n\n\n{rest}"

        return f"{header}\n"


    def _identify_header_sections(self, tree: ast.Module) -> list:
        """Identify header sections as (start_line, end_line) 0-indexed tuples.

        Header items are (in order):
        - Module docstring (first Expr with string constant)
        - __all__ assignments
        - Import/ImportFrom statements

        Stops at the first non-header node.
        """
        sections = []
        i = 0
        body = tree.body

        if not body:
            return sections

        first = body[0]

        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            sections.append((first.lineno - 1, first.end_lineno))
            i = 1

        while i < len(body):
            node = body[i]

            if self._is_all_assignment(node):
                sections.append((node.lineno - 1, node.end_lineno))
                i += 1
            else:
                break

        import_start = None
        import_end = None

        while i < len(body):
            node = body[i]

            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if import_start is None:
                    import_start = node.lineno - 1

                import_end = node.end_lineno
                i += 1
            else:
                break

        if import_start is not None:
            sections.append((import_start, import_end))

        return sections


    def _find_first_code_line(self, tree: ast.Module, header_sections: list) -> int | None:
        """Find the first line of module code after the header.

        Returns 0-indexed line number, or None if no code follows.
        """
        if not header_sections:
            return None

        last_header_end = header_sections[-1][1]

        for node in tree.body:
            line = node.lineno - 1

            if hasattr(node, "decorator_list") and node.decorator_list:
                line = node.decorator_list[0].lineno - 1

            if line >= last_header_end:
                return line

        return None


    def _find_rest_start(self, lines: list, last_header_end: int, first_code_line: int) -> int:
        """Find the first non-blank line after the header.

        Looks between the last header section end and the first AST
        code node for comment lines that should be preserved.

        Returns the 0-indexed line number where the rest starts.
        """
        for i in range(last_header_end, first_code_line):
            if lines[i].strip():
                return i

        return first_code_line


    def _is_all_assignment(self, node) -> bool:
        """Check if a node is an __all__ assignment."""
        if not isinstance(node, ast.Assign):
            return False

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__all__":
                return True

        return False
