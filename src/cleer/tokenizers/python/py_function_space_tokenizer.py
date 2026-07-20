"""Function space tokenizer module."""

__all__ = ["PyFunctionSpaceTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyFunctionSpaceTokenizer(Tokenizer):
    """Tokenizes the whitespace between Python function definitions.

    Only captures the newlines between functions (after one function ends
    and before the next function or decorator starts). Does not include
    function content.

    Emits token type: `function_space`

    Examples
    --------

    ```python
    from cleer import PyFunctionSpaceTokenizer

    tokenizer = PyFunctionSpaceTokenizer()
    tokens = tokenizer.tokenize("def a():\\n    pass\\n\\n\\ndef b():\\n    pass\\n")
    ```
    """
    emits_token_type = "function_space"


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

        return i


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
        """Tokenize whitespace between function definitions.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyFunctionSpaceTokenizer()
        tokens = tokenizer.tokenize("def a():\\n    pass\\n\\ndef b():\\n    pass\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per whitespace gap between functions.

            ```python
            [
                {"token": "\\n\\n", "index": 18, "length": 2}
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

        def_pattern = re.compile(r"^([ \t]*)(async\s+)?def\s+")
        func_ranges = []

        covered_lines = set()
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
                func_ranges.append(
                    (
                        decorator_start,
                        func_end - 1,
                        base_indent
                    )
                )

                for j in range(decorator_start, func_end):
                    covered_lines.add(j)

        for idx in range(len(func_ranges) - 1):
            _, end_of_current, indent_current = func_ranges[idx]
            start_of_next, _, indent_next = func_ranges[idx + 1]

            if indent_current != indent_next:
                continue

            space_start_line = end_of_current + 1
            space_end_line = start_of_next

            start_index = line_starts[end_of_current] + len(lines[end_of_current])
            end_index = line_starts[start_of_next]

            token_text = document[start_index:end_index]

            has_non_whitespace = any(
                lines[line_idx].strip() != ""
                for line_idx in range(space_start_line, space_end_line)
                if line_idx < len(lines)
            )

            if has_non_whitespace:
                continue

            if token_text:
                tokens.append(
                    {
                        "token": token_text,
                        "index": start_index,
                        "length": len(token_text)
                    }
                )

        for start, end, indent in func_ranges:
            next_line = end + 1
            while next_line < len(lines) and lines[next_line].strip() == "":
                next_line += 1

            if next_line >= len(lines):
                continue

            is_next_func = (
                (
                    start,
                    end,
                    indent
                ) != func_ranges[-1]
                and any(s == next_line for s, _, _ in func_ranges)
            )
            if is_next_func:
                continue

            next_is_class = bool(re.match(r"^([ \t]*)class\s+", lines[next_line]))
            if next_is_class:
                continue

            start_index = line_starts[end] + len(lines[end])
            end_index = line_starts[next_line]

            token_text = document[start_index:end_index]

            if token_text and token_text != "\n\n\n":
                tokens.append(
                    {
                        "token": token_text,
                        "index": start_index,
                        "length": len(token_text)
                    }
                )

        import_pattern = re.compile(r"^([ \t]*)(import |from .+ import )")

        for start, end, indent in func_ranges:
            prev_line = start - 1
            while prev_line >= 0 and lines[prev_line].strip() == "":
                prev_line -= 1

            if prev_line < 0:
                continue

            is_prev_in_func = any(
                s <= prev_line <= e for s, e, _ in func_ranges
            )
            if is_prev_in_func:
                continue

            prev_is_class = bool(re.match(r"^([ \t]*)class\s+", lines[prev_line]))
            if prev_is_class:
                continue

            prev_is_import = bool(import_pattern.match(lines[prev_line]))
            if prev_is_import:
                continue

            start_index = line_starts[prev_line] + len(lines[prev_line])
            end_index = line_starts[start]

            token_text = document[start_index:end_index]

            if token_text and token_text != "\n\n\n":
                tokens.append(
                    {
                        "token": token_text,
                        "index": start_index,
                        "length": len(token_text)
                    }
                )

        tokens.sort(key=lambda t: t['index'])

        return tokens
