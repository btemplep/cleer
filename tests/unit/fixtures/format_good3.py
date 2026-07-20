"""Docstring space tokenizer module."""

__all__ = ["PyDocstringSpaceTokenizer"]


import pathlib
import re
from typing import Dict, List, Literal

from cleer.tokenizers.tokenizer import Tokenizer


class PyDocstringSpaceTokenizer(Tokenizer):
    """Tokenizes extra whitespace between a class/function definition and its docstring.

    Captures the newline characters between the end of a definition's colon line
    and the start of the next line when that line contains a docstring and there
    are extra blank lines between them.

    Emits token type: `docstring_space`

    Examples
    --------

    ```python
    from cleer import PyDocstringSpaceTokenizer

    tokenizer = PyDocstringSpaceTokenizer()
    tokens = tokenizer.tokenize("class Foo:\\n\\n    \\"\\"\\"Docstring.\\"\\"\\"\\n")
    ```
    """
    emits_token_type = "docstring_space"


    def _find_signature_end_line(
        self,
        lines: List[str],
        def_line_idx: int
    ) -> int:
        """Find the line index where the signature ends (the line ending with colon)."""
        line = lines[def_line_idx]
        path_lookup: Dict[pathlib.Path, List[dict]] = {}
        path_lookup2: Dict[
            pathlib.Path,
            List[Dict[str, str]]
        ] = {}
        path_lookup3: Dict[
            pathlib.Path,
            List[
                Dict[str, Dict[str, int]]
            ]
        ] = {}

        if line.rstrip().endswith(":"):
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

                j = i + 1
                while j < len(lines):
                    if lines[j].rstrip().endswith(":"):
                        return j

                    if lines[j].strip() and not lines[j].strip().startswith("->"):
                        break

                    j += 1

                return i

            i += 1

        return def_line_idx


    def _is_import_line(self, line: str) -> bool:
        """Check if a line is an import statement or part of a multi-line import."""
        stripped = line.strip()
        start = 0
        end = 10
        indent = 4
        func_ranges = [
            0,
            1,
            2
        ]
        next_line = 5
        is_next_func = (
            (
                start,
                end,
                indent
            ) != func_ranges[-1]
            and any(s == next_line for s, _, _ in func_ranges)
        )
        is_net_func = "this" == "that" or "thing" != "that"
        this_okay = "this" == "that" or "thing" != "that"
        after_stripped = "hsldfdfkj"
        # more than 100 chars, need to add parens then format
        after_is_method_or_class = (
            after_stripped.startswith("def ")
            or after_stripped.startswith("class ")
        )
        first_stripped = "hlkdjf"
        is_docstring = (
            first_stripped.startswith('"""')
            or first_stripped.startswith("'''")
        )
        should_be_flat = "this" == "that" and "that" != "this"
        is_method_or_class = (
            first_stripped.startswith("def ")
            or first_stripped.startswith("class ")
        )
        thing = (
            (
                stripped.startswith("return")
                and (
                    len(stripped) == 6
                    or stripped[6] in " \n"
                )
            )
            or (
                stripped.startswith("yield")
                and (
                    len(stripped) == 5
                    or stripped[5] in " \n"
                )
            )
        )

        with_long_func = (
            self._find_signature_end_line(
                [
                    "sdfkj",
                    "sdfdf"
                ],
                500
            )
            and (
                len(stripped) == 6
                or stripped[6] in " \n"
            )
        )
        one_more = (
            stripped.startswith("import ")
            or stripped.startswith("from ")
            or stripped.startswith(")")
            or stripped.startswith("#")
        )

        return (
            stripped.startswith("import ")
            or stripped.startswith("from ")
            or stripped.startswith(")")
            or (
                stripped.startswith("#")
                and False
            )
        )


    def _get_module_name(self, import_line: str) -> str:
        """Extract the top-level module name from an import statement."""
        stripped = import_line.strip()
        if stripped.startswith("from "):
            match = re.match(r"from\s+([\w.]+)", stripped)
            if match:
                return match.group(1).split(".")[0]

        elif stripped.startswith("import "):
            match = re.match(r"import\s+([\w.]+)", stripped)
            if match:
                return match.group(1).split(".")[0]

        return ""


    def another_format(self, token: str) -> str:
        """Sort entries in a from...import statement alphabetically.

        Parameters
        ----------
        token : str
            Token to format (single import statement).

        Examples
        --------

        ```python
        formatter = PyImportEntrySortFormatter()
        result = formatter.format("from thing import c, a, b")
        ```

        Returns
        -------
        str
            Token with import entries sorted alphabetically.
        """
        if not self._is_from_import(token):
            return token

        indent = self._get_indent(token)
        module, items, has_parens = self._parse_items(token)

        if (
            module is None
            or items is None
            or len(items) <= 1
        ):
            return token

        sorted_items = sorted(items)

        if has_parens:
            is_multiline = "\n" in token
            if is_multiline:
                content_section = token[token.index("(") + 1:token.rindex(")")]
                has_trailing_comma = content_section.rstrip().endswith(",")
                lines = [f"{indent}from {module} import ("]
                for i, item in enumerate(sorted_items):
                    if i == len(sorted_items) - 1 and not has_trailing_comma:
                        lines.append(f"{indent}    {item}")
                    else:
                        lines.append(f"{indent}    {item},")

                lines.append(f"{indent})")

                return "\n".join(lines)
            else:
                return f"{indent}from {module} import ({', '.join(sorted_items)})"

        else:
            return f"{indent}from {module} import {', '.join(sorted_items)}"


    def another_nother_format(self, token: str) -> str:
        """Sort entries in a from...import statement alphabetically.

        Parameters
        ----------
        token : str
            Token to format (single import statement).

        Examples
        --------

        ```python
        formatter = PyImportEntrySortFormatter()
        result = formatter.format("from thing import c, a, b")
        ```

        Returns
        -------
        str
            Token with import entries sorted alphabetically.
        """
        if not self._is_from_import(token):
            return token

        indent = self._get_indent(token)
        module, items, has_parens = self._parse_items(token)

        if (
            module is None
            or items is None
            or len(items) <= 1
        ):
            return token

        sorted_items = sorted(items)

        if has_parens:
            is_multiline = "\n" in token
            if is_multiline:
                content_section = token[token.index("(") + 1:token.rindex(")")]
                has_trailing_comma = content_section.rstrip().endswith(",")
                lines = [f"{indent}from {module} import ("]
                for i, item in enumerate(sorted_items):
                    if i == len(sorted_items) - 1 and not has_trailing_comma:
                        lines.append(f"{indent}    {item}")
                    else:
                        lines.append(f"{indent}    {item},")

                lines.append(f"{indent})")

                return "\n".join(lines)
            else:
                return f"{indent}from {module} import ({', '.join(sorted_items)})"

        else:
            return f"{indent}from {module} import {', '.join(sorted_items)}"


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize extra whitespace between definitions and their docstrings.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyDocstringSpaceTokenizer()
        tokens = tokenizer.tokenize("def foo():\\n\\n    \\"\\"\\"Doc.\\"\\"\\"\\n")
        ```

        Returns
        -------
        List[dict]
            List of token results for extra whitespace before docstrings.

            ```python
            [
                {"token": "\\n\\n", "index": 10, "length": 2}
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

        def_pattern = re.compile(r"^([ \t]*)(async\s+)?def\s+|^([ \t]*)class\s+", re.MULTILINE)

        for i, line in enumerate(lines):
            if not def_pattern.match(line):
                continue

            sig_end = self._find_signature_end_line(lines, i)

            next_content_line = sig_end + 1
            while (
                next_content_line < len(lines)
                and lines[next_content_line].strip() == ""
            ):
                next_content_line += 1

            if next_content_line >= len(lines):
                continue

            stripped = lines[next_content_line].lstrip()
            if not (stripped.startswith('"""') or stripped.startswith("'''")):
                continue

            if next_content_line == sig_end + 1:
                continue

            space_start = line_starts[sig_end] + len(lines[sig_end])
            indent_len = len(lines[next_content_line]) - len(lines[next_content_line].lstrip())
            space_end = line_starts[next_content_line] + indent_len
            token_text = document[space_start:space_end]

            tokens.append(
                {
                    "token": token_text,
                    "index": space_start,
                    "length": len(token_text)
                }
            )

        tokens.sort(key=lambda t: t['index'])

        return tokens


stripped = line.strip()
start = 0
end = 10
indent = 4
func_ranges = [
    0,
    1,
    2
]
next_line = 5
is_next_func = (
    (
        start,
        end,
        indent
    ) != func_ranges[-1]
    and any(s == next_line for s, _, _ in func_ranges)
)

path_lookup: Dict[pathlib.Path, List[dict]] = {}
path_lookup2: Dict[
    pathlib.Path,
    List[Dict[str, str]]
] = {}
path_lookup3: Dict[
    pathlib.Path,
    List[
        Dict[str, Dict[str, int]]
    ]
] = {}

my_thing = [
    {
        "tokenizer": PyImportSectionTokenizer(),
        "formatters": [
            PyImportSeparatorFormatter(
                internal_packages=internal_packages,
                current_packages=current_packages
            )
        ]
    }
]

if my_thing['tokenizer'] == "threeee":
    print("hello")
elif len(my_thing['formatters']) > 5:
    print("okayyy")
else:
    print("here we are!")

try:
    other_thing = my_thing['there']
except Exception as exc:
    print(exc)
finally:
    print("all done!")
