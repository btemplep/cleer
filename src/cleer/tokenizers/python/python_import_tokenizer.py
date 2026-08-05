"""Python import section tokenizer module."""

__all__ = ["PythonImportTokenizer"]


import ast


from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonImportTokenizer(Tokenizer):
    """Tokenizes import sections in a Python module.

    An import section is a sequence of consecutive import and import-from
    statements, possibly separated by blank lines, that are not
    interrupted by non-import code.

    Emits one token per import section, spanning from the end of the
    previous code through the start of the next code (including
    surrounding whitespace for boundary enforcement).

    Examples
    --------

    ```python
    from cleer import PythonImportTokenizer

    tokenizer = PythonImportTokenizer()
    tokens = tokenizer.tokenize("import os\\nimport sys\\n")
    ```
    """
    emits_token_type = "python_import"


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize import sections with surrounding context.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results, one per import section found.
        """
        tree = ast.parse(document)
        line_offsets = self._build_line_offsets(document)
        sections = self._find_import_sections(tree)

        if not sections:
            return []

        results = []

        for section in sections:
            prev_end, next_start = self._find_boundaries(
                tree,
                section,
                document,
                line_offsets
            )
            token = document[prev_end:next_start]
            results.append(
                {
                    "token": token,
                    "index": prev_end,
                    "length": len(token)
                }
            )

        return results


    def _find_import_sections(self, tree: ast.Module) -> list[list[ast.stmt]]:
        """Find contiguous groups of import statements in the module body.

        Returns a list of sections, where each section is a list of
        consecutive import/import-from nodes.
        """
        sections = []
        current_section = []

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                current_section.append(node)
            else:
                if current_section:
                    sections.append(current_section)
                    current_section = []

        if current_section:
            sections.append(current_section)

        return sections


    def _find_boundaries(
        self,
        tree: ast.Module,
        section: list[ast.stmt],
        document: str,
        line_offsets: list[int]
    ):
        """Find start and end boundaries including surrounding whitespace."""
        first_node = section[0]
        last_node = section[-1]

        prev_node = None
        next_node = None
        found_first = False
        found_last = False

        for node in tree.body:
            if node is first_node:
                found_first = True

                if node is last_node:
                    found_last = True

                continue

            if node is last_node:
                found_last = True
                continue

            if not found_first:
                prev_node = node
            elif found_last:
                next_node = node
                break

        if prev_node is not None:
            prev_end_line = prev_node.end_lineno
            prev_end = line_offsets[prev_end_line]
        else:
            prev_end = 0

        if next_node is not None:
            last_import_end = last_node.end_lineno
            next_start = line_offsets[last_import_end]

            for line_idx in range(last_import_end, len(line_offsets) - 1):
                line_start = line_offsets[line_idx]
                line_end = line_offsets[line_idx + 1] if line_idx + 1 < len(line_offsets) else len(document)
                line_text = document[line_start:line_end]

                if line_text.strip() == "":
                    next_start = line_offsets[line_idx + 1] if line_idx + 1 < len(line_offsets) else len(document)
                else:
                    break
        else:
            next_start = len(document)

        return prev_end, next_start


    def _build_line_offsets(self, document: str) -> list[int]:
        """Build a list mapping line numbers (0-indexed) to character offsets."""
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
