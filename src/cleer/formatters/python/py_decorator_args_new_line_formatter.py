"""Decorator args new line formatter module."""

__all__ = ["PyDecoratorArgsNewLineFormatter"]


import re

from cleer.formatters.formatter import Formatter


class PyDecoratorArgsNewLineFormatter(Formatter):
    """Formats decorator arguments with more than 2 to one per line.

    Decorators that have more than 2 arguments should have one argument
    per newline.

    Accepts token types: `decorator`

    Examples
    --------

    ```python
    from cleer import PyDecoratorArgsNewLineFormatter

    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@my_decorator(arg1, arg2, arg3)")
    ```
    """
    accepts_token_types = ["decorator"]


    def _find_matching_paren(
        self,
        text: str,
        start: int
    ) -> int:
        """Find matching closing parenthesis."""
        depth = 1
        i = start + 1
        in_single = False
        in_double = False

        while i < len(text):
            if text[i] == "\\" and (in_single or in_double):
                i += 2
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

        for char in text:
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
        """Inspect a decorator for argument formatting.

        Parameters
        ----------
        token : str
            String token to inspect (decorator statement).

        Examples
        --------

        ```python
        formatter = PyDecoratorArgsNewLineFormatter()
        message = formatter.inspect("@my_decorator(arg1, arg2, arg3)")
        ```

        Returns
        -------
        str | None
            Error message if decorator needs reformatting, `None` otherwise.
        """
        formatted = self.format(token)
        if formatted != token:
            return "Decorators with more than 2 arguments should have one argument per line."

        return None


    def format(self, token: str) -> str:
        """Format decorators with more than 2 args to one per line.

        Parameters
        ----------
        token : str
            Token to format (decorator statement).

        Examples
        --------

        ```python
        formatter = PyDecoratorArgsNewLineFormatter()
        result = formatter.format("@my_decorator(arg1, arg2, arg3)")
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

        single_line = f"{indent}{prefix}({', '.join(a.strip() for a in args)}){suffix}"
        content_line = f"{prefix}({', '.join(a.strip() for a in args)}){suffix}"
        exceeds_total = len(single_line) > 100
        exceeds_content = len(content_line) > 60

        if not exceeds_total and not exceeds_content:
            return single_line

        arg_indent = indent + "    "
        lines = [f"{indent}{prefix}("]
        for i, arg in enumerate(args):
            comma = "," if i < len(args) - 1 else ""
            lines.append(f"{arg_indent}{arg}{comma}")

        lines.append(f"{indent}){suffix}")

        return "\n".join(lines)
