"""See [](#cleer.formatters.python.python_module_header_formatter.PythonModuleHeaderFormatter)"""

__all__ = [
    "PythonModuleHeaderFormatter"
]

import ast

from cleer.formatters.formatter import Formatter, FormatterViolation


class PythonModuleHeaderFormatter(Formatter):
    """Enforce spacing in the module header block.

    The header block consists of (in order, each optional):
    - Module docstring
    - `__version__` assignment
    - `__all__` assignment
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


    def inspect(self, token: str) -> list[FormatterViolation]:
        """Inspect module header spacing.

        Parameters
        ----------
        token : str
            Entire document content.

        Returns
        -------
        list[FormatterViolation]
            List of violations found, empty if no violations.
        """
        expected = self._fix_header(token)

        if token != expected:
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": "Module header should have 1 blank line between items and 2 blank lines before code."
                }
            ]

        return []


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

        all_ranges = []
        for section in header_sections:
            all_ranges.extend(section)

        last_header_end = max(end for _, end in all_ranges)
        first_code_line = self._find_first_code_line(tree, last_header_end)

        result_parts = []

        all_section_lines = set()
        for section in header_sections:
            for start, end in section:
                for line_num in range(start, end):
                    all_section_lines.add(line_num)

        for section in header_sections:
            if len(section) > 1:
                first_start = section[0][0]
                last_end = section[-1][1]
                section_lines = []
                for line_num in range(first_start, last_end):
                    if line_num in all_section_lines:
                        is_this_section = any(start <= line_num < end for start, end in section)
                        if is_this_section:
                            section_lines.append(lines[line_num])

                    elif lines[line_num].strip() == "":
                        section_lines.append(lines[line_num])

                section_text = "\n".join(section_lines)
            else:
                section_lines = []
                for start, end in section:
                    section_lines.extend(lines[start:end])

                section_text = "\n".join(section_lines)

            while section_text.endswith("\n"):
                section_text = section_text[:-1]

            result_parts.append(section_text)

        header = "\n\n".join(result_parts)

        if first_code_line is not None:
            rest_start = self._find_rest_start(
                lines,
                last_header_end,
                first_code_line
            )
            rest_lines = lines[rest_start:]
            rest = "\n".join(rest_lines)

            return f"{header}\n\n\n{rest}"

        return f"{header}\n"


    def _identify_header_sections(self, tree: ast.Module) -> list:
        body = tree.body

        if not body:
            return []

        docstring_ranges = []
        version_ranges = []
        all_ranges = []
        import_ranges = []

        for i, node in enumerate(body):
            if (
                i == 0
                and isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                docstring_ranges.append((node.lineno - 1, node.end_lineno))
            elif self._is_version_assignment(node):
                version_ranges.append((node.lineno - 1, node.end_lineno))
            elif self._is_all_assignment(node):
                all_ranges.append((node.lineno - 1, node.end_lineno))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                import_ranges.append((node.lineno - 1, node.end_lineno))
            else:
                break

        sections = []

        if docstring_ranges:
            sections.append(docstring_ranges)

        if version_ranges:
            sections.append(version_ranges)

        if all_ranges:
            sections.append(all_ranges)

        if import_ranges:
            sections.append(import_ranges)

        return sections


    def _find_first_code_line(
        self,
        tree: ast.Module,
        last_header_end: int
    ) -> int | None:
        """Find the first line of module code after the header.

        Returns 0-indexed line number, or None if no code follows.
        """
        for node in tree.body:
            line = node.lineno - 1

            if hasattr(node, "decorator_list") and node.decorator_list:
                line = node.decorator_list[0].lineno - 1

            if line >= last_header_end:
                return line

        return None


    def _find_rest_start(
        self,
        lines: list,
        last_header_end: int,
        first_code_line: int
    ) -> int:
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
        if not isinstance(node, ast.Assign):
            return False

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__all__":
                return True

        return False


    def _is_version_assignment(self, node) -> bool:
        if not isinstance(node, ast.Assign):
            return False

        for target in node.targets:
            if (
                isinstance(target, ast.Name)
                and target.id == "__version__"
            ):
                return True

        return False
