"""Signature new line formatter module."""

__all__ = ["PySignatureNewLineFormatter"]


import re

from cleer.formatters.formatter import Formatter


class PySignatureNewLineFormatter(Formatter):
    """Formats function signatures with more than 2 arguments to one per line.

    Function signatures and calls that have more than 2 arguments should
    have one argument per newline. Additionally, if the total line length
    of the signature exceeds `max_line_length`, arguments are split to
    new lines even with fewer arguments.

    Accepts token types: `function_signature`

    Parameters
    ----------
    max_line_length : int, default=100
        Maximum line length before forcing arguments onto new lines.

    Examples
    --------

    ```python
    from cleer import PySignatureNewLineFormatter

    formatter = PySignatureNewLineFormatter()
    result = formatter.format("def my_func(a, b, c):")
    ```
    """
    accepts_token_types = ["function_signature"]


    def __init__(self, max_line_length: int=100) -> None:
        self.max_line_length = max_line_length


    def _find_matching_paren(self, text: str, start: int) -> int:
        """Find matching closing parenthesis."""
        depth = 1
        i = start + 1
        in_single = False
        in_double = False

        while i < len(text):
            if text[i] == "\\" and (in_single or in_double):
                i += 2
                continue

            if text[i:i + 3] in (
                "'''",
                '"""'
            ):
                quote = text[i:i + 3]
                end = text.find(quote, i + 3)
                if end != -1:
                    i = end + 3
                    continue

            if text[i] == "'" and not in_double:
                in_single = not in_single
                i += 1
                continue

            if text[i] == '"' and not in_single:
                in_double = not in_double
                i += 1
                continue

            if not in_single and not in_double:
                if text[i] == "(":
                    depth += 1
                elif text[i] == ")":
                    depth -= 1
                    if depth == 0:
                        return i

            i += 1

        return -1


    def _split_args(self, text: str) -> list[str]:
        """Split arguments by commas at the top level."""
        args = []
        depth = 0
        current = ""
        in_single = False
        in_double = False

        for i, char in enumerate(text):
            if char == "\\" and (in_single or in_double):
                current += char
                continue

            if char == "'" and not in_double:
                in_single = not in_single
            elif char == '"' and not in_single:
                in_double = not in_double

            if not in_single and not in_double:
                if char in "([{":
                    depth += 1
                elif char in ")]}":
                    depth -= 1
                elif char == "," and depth == 0:
                    args.append(current.strip())
                    current = ""
                    continue

            current += char

        if current.strip():
            args.append(current.strip())

        return args


    def _get_indent(self, token: str) -> str:
        """Get the base indent of the token."""
        match = re.match(r"^(\s*)", token)

        return match.group(1) if match else ""


    def inspect(self, token: str) -> str | None:
        """Inspect a function signature for argument formatting.

        Parameters
        ----------
        token : str
            String token to inspect (function signature).

        Examples
        --------

        ```python
        formatter = PySignatureNewLineFormatter()
        message = formatter.inspect("def my_func(a, b, c):")
        ```

        Returns
        -------
        str | None
            Error message if signature needs reformatting, `None` otherwise.
        """
        formatted = self.format(token)
        if formatted != token:
            return "Function signature with more than 2 arguments should have one argument per line."

        return None


    def format(self, token: str) -> str:
        """Format function signatures with more than 2 args to one per line.

        Parameters
        ----------
        token : str
            Token to format (function signature).

        Examples
        --------

        ```python
        formatter = PySignatureNewLineFormatter()
        result = formatter.format("def my_func(a, b, c):")
        ```

        Returns
        -------
        str
            Token with arguments on separate lines if more than 2.
        """
        indent = self._get_indent(token)
        stripped = token.strip()

        paren_start = stripped.find("(")
        if paren_start == -1:
            return token

        paren_end = self._find_matching_paren(stripped, paren_start)
        if paren_end == -1:
            return token

        prefix = stripped[:paren_start]
        inner = stripped[paren_start + 1:paren_end]
        suffix = stripped[paren_end + 1:]

        args = self._split_args(inner)

        countable_args = [a for a in args if a.strip() not in ("self", "cls")]

        single_line = f"{indent}{prefix}({', '.join(a.strip() for a in args)}){suffix}"
        exceeds_length = len(single_line) > self.max_line_length

        if len(countable_args) <= 2 and not exceeds_length:
            return token

        arg_indent = indent + "    "
        lines = [f"{indent}{prefix}("]
        for i, arg in enumerate(args):
            comma = "," if i < len(args) - 1 else ""
            lines.append(f"{arg_indent}{arg}{comma}")

        lines.append(f"{indent}){suffix}")

        return "\n".join(lines)
