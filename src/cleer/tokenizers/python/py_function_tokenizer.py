"""Function tokenizer module."""

__all__ = ["PyFunctionTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyFunctionTokenizer(Tokenizer):
    """Tokenizes whole Python functions including decorators and indent.

    Each function definition is returned as a single token including any
    decorators above it and its full body. Does not include extra newlines
    before or after the function.

    Tokens cannot overlap, so nested functions are included within their
    parent function token but not returned as separate tokens.

    Emits token type: `function`

    Examples
    --------

    ```python
    from cleer import PyFunctionTokenizer

    tokenizer = PyFunctionTokenizer()
    tokens = tokenizer.tokenize("@decorator\\ndef my_func():\\n    pass\\n")
    ```
    """
    emits_token_type = "function"


    def _find_signature_end(
        self,
        lines: List[str],
        def_line_idx: int
    ) -> int:
        """Find the line index where the function signature ends (the line with colon)."""
        line = lines[def_line_idx]
        if "(" not in line:
            return def_line_idx

        paren_depth = 0
        i = def_line_idx

        while i < len(lines):
            for char in lines[i]:
                if char == "(":
                    paren_depth += 1
                elif char == ")":
                    paren_depth -= 1

            if paren_depth == 0:
                if lines[i].rstrip().endswith(":"):
                    return i

                if i + 1 < len(lines) and lines[i + 1].strip().startswith("->"):
                    j = i + 1
                    while j < len(lines):
                        if lines[j].rstrip().endswith(":"):
                            return j

                        j += 1

                return i

            i += 1

        return def_line_idx


    def _find_function_end(
        self,
        lines: List[str],
        def_line_idx: int,
        base_indent: int
    ) -> int:
        """Find the last line of a function body."""
        sig_end = self._find_signature_end(lines, def_line_idx)
        i = sig_end + 1

        while i < len(lines):
            line = lines[i]

            if line.strip() == "":
                i += 1
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent:
                break

            i += 1

        while i > sig_end + 1 and lines[i - 1].strip() == "":
            i -= 1

        return i - 1


    def _find_decorators_start(
        self,
        lines: List[str],
        def_line_idx: int
    ) -> int:
        """Find the first decorator line above the def."""
        def_indent = len(lines[def_line_idx]) - len(lines[def_line_idx].lstrip())
        i = def_line_idx - 1
        result = def_line_idx

        while i >= 0:
            line = lines[i]
            stripped = line.strip()

            if stripped == "":
                i -= 1
                continue

            current_indent = len(line) - len(line.lstrip())

            if current_indent < def_indent:
                break

            if current_indent == def_indent and stripped.startswith("@"):
                result = i
                i -= 1
                continue

            if current_indent > def_indent:
                i -= 1
                continue

            if current_indent == def_indent and not stripped.startswith("@"):
                paren_depth = 0
                scan = i
                found_decorator = False
                while scan >= 0:
                    scan_line = lines[scan]
                    scan_stripped = scan_line.strip()
                    if scan_stripped == "":
                        scan -= 1
                        continue

                    scan_indent = len(scan_line) - len(scan_line.lstrip())
                    if scan_indent < def_indent:
                        break

                    for char in reversed(scan_line):
                        if char == ")":
                            paren_depth += 1
                        elif char == "(":
                            paren_depth -= 1

                    if (
                        paren_depth <= 0
                        and scan_indent == def_indent
                        and scan_stripped.startswith("@")
                    ):
                        found_decorator = True
                        result = scan
                        i = scan - 1
                        break

                    if (
                        paren_depth <= 0
                        and scan_indent == def_indent
                        and not scan_stripped.startswith("@")
                    ):
                        break

                    scan -= 1

                if not found_decorator:
                    break

                continue

        return result


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize whole function definitions in a document.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyFunctionTokenizer()
        tokens = tokenizer.tokenize("def func_a():\\n    pass\\n\\ndef func_b():\\n    return 1\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per function definition.

            ```python
            [
                {"token": "def func_a():\\n    pass", "index": 0, "length": 18},
                {"token": "def func_b():\\n    return 1", "index": 20, "length": 22}
            ]
            ```
        """
        tokens: List[dict] = []
        lines = document.split("\n")
        line_starts = []
        current_pos = 0

        for line in lines:
            line_starts.append(current_pos)
            current_pos += len(line) + 1

        covered_lines = set()
        def_pattern = re.compile(r"^([ \t]*)(async\s+)?def\s+")

        for i, line in enumerate(lines):
            if i in covered_lines:
                continue

            match = def_pattern.match(line)
            if match:
                base_indent = len(match.group(1))

                decorator_start = self._find_decorators_start(lines, i)

                func_end = self._find_function_end(
                    lines,
                    i,
                    base_indent
                )

                start_index = line_starts[decorator_start]
                end_index = line_starts[func_end] + len(lines[func_end])
                token_text = document[start_index:end_index]

                tokens.append(
                    {
                        "token": token_text,
                        "index": start_index,
                        "length": len(token_text)
                    }
                )

                for j in range(decorator_start, func_end + 1):
                    covered_lines.add(j)

        return tokens
