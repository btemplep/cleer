"""Python max one space tokenizer module."""

__all__ = [
    "PythonMaxOneSpaceTokenizer"
]

import ast
import re

from cleer.tokenizers.tokenizer import TokenResult, Tokenizer


class PythonMaxOneSpaceTokenizer(Tokenizer):
    """Tokenizes runs of 2+ consecutive spaces outside indentation and strings.

    Uses the AST to identify string literal ranges and excludes them.
    Leading whitespace (indentation) on each line is also excluded.

    Examples
    --------

    ```python
    from cleer import PythonMaxOneSpaceTokenizer

    tokenizer = PythonMaxOneSpaceTokenizer()
    tokens = tokenizer.tokenize("x  =  1\\n")
    ```
    """
    emits_token_type = "python_max_one_space"
    _multi_space = re.compile(r" {2,}")


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize runs of 2+ spaces outside indentation and string literals.

        Parameters
        ----------
        document : str
            Python source document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results for each multi-space run.

            ```python
            [
                {"token": "  ", "index": 1, "length": 2}
            ]
            ```
        """
        tree = ast.parse(document)

        string_ranges = self._collect_string_ranges(tree, document)
        indent_ranges = self._collect_indent_ranges(document)
        excluded = indent_ranges + string_ranges
        excluded.sort()

        tokens = []

        for match in self._multi_space.finditer(document):
            start = match.start()
            end = match.end()

            if self._is_excluded(start, end, excluded):
                continue

            tokens.append(
                {
                    "token": match.group(),
                    "index": start,
                    "length": end - start
                }
            )

        return tokens


    def _is_excluded(
        self,
        start: int,
        end: int,
        excluded: list[tuple[int, int]]
    ) -> bool:
        """Check if a range overlaps with any excluded range."""
        for ex_start, ex_end in excluded:
            if start >= ex_start and end <= ex_end:
                return True

            if ex_start > end:
                break

        return False


    def _collect_indent_ranges(self, document: str) -> list[tuple[int, int]]:
        """Collect the byte ranges of leading whitespace on each line."""
        ranges = []
        pos = 0

        for line in document.split("\n"):
            if line and line[0] in " \t":
                stripped = line.lstrip()
                indent_len = len(line) - len(stripped)
                ranges.append((pos, pos + indent_len))

            pos += len(line) + 1

        return ranges


    def _collect_string_ranges(
        self,
        tree: ast.Module,
        document: str
    ) -> list[tuple[int, int]]:
        """Collect the byte ranges of all string literals in the source."""
        line_offsets = self._build_line_offsets(document)
        ranges = []

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
            ):
                start = line_offsets[node.lineno - 1] + node.col_offset
                end = line_offsets[node.end_lineno - 1] + node.end_col_offset
                ranges.append((start, end))
            elif isinstance(node, ast.JoinedStr):
                if (
                    node.end_lineno is not None
                    and node.end_col_offset is not None
                ):
                    start = line_offsets[node.lineno - 1] + node.col_offset
                    end = line_offsets[node.end_lineno - 1] + node.end_col_offset
                    ranges.append((start, end))

            elif (
                hasattr(ast, "TemplateStr")
                and isinstance(node, ast.TemplateStr)
                and node.end_lineno is not None
                    and node.end_col_offset is not None
            ):
                start = line_offsets[node.lineno - 1] + node.col_offset
                end = line_offsets[node.end_lineno - 1] + node.end_col_offset
                ranges.append((start, end))

        return ranges


    def _build_line_offsets(self, document: str) -> list[int]:
        """Build a list mapping line numbers (0-indexed) to character offsets."""
        offsets = [0]

        for i, char in enumerate(document):
            if char == "\n":
                offsets.append(i + 1)

        return offsets
