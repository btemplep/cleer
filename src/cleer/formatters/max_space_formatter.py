"""Max space formatter module."""

__all__ = ["MaxSpaceFormatter"]


import re

from cleer.formatters.formatter import Formatter


class MaxSpaceFormatter(Formatter):
    """Collapses multiple consecutive spaces to a single space.

    Preserves leading indentation and spaces inside string literals
    (single, double, triple-quoted, and f-strings).

    Accepts token types: `line`

    Examples
    --------

    ```python
    from cleer import MaxSpaceFormatter

    formatter = MaxSpaceFormatter()
    result = formatter.format("x  =  1")
    ```
    """
    accepts_token_types = ["line"]


    def _collapse_spaces(self, text: str) -> str:
        """Collapse multiple spaces to one, skipping string literals."""
        result = []
        i = 0

        while i < len(text):
            if (
                i < len(text)
                and text[i] in ("f", "r", "b", "F", "R", "B")
            ):
                if (
                    i + 1 < len(text)
                    and text[i + 1] in ("'", '"')
                ):
                    result.append(text[i])
                    i += 1
                    continue

                if (
                    i + 2 < len(text)
                    and text[i + 1] in ("f", "r", "b", "F", "R", "B")
                    and text[i + 2] in ("'", '"')
                ):
                    result.append(text[i])
                    i += 1
                    continue

            if text[i] in ("'", '"'):
                quote_char = text[i]
                if text[i:i + 3] in ('"""', "'''"):
                    triple = text[i:i + 3]
                    end = text.find(triple, i + 3)
                    if end != -1:
                        result.append(text[i:end + 3])
                        i = end + 3
                        continue
                    else:
                        result.append(text[i:])
                        break

                else:
                    j = i + 1
                    while j < len(text):
                        if text[j] == "\\":
                            j += 2
                            continue

                        if text[j] == quote_char:
                            break

                        j += 1

                    result.append(text[i:j + 1])
                    i = j + 1
                    continue

            if text[i] == " ":
                result.append(" ")
                i += 1
                while i < len(text) and text[i] == " ":
                    i += 1

                continue

            result.append(text[i])
            i += 1

        return "".join(result)


    def inspect(self, token: str) -> str | None:
        """Inspect a token for multiple consecutive spaces.

        Parameters
        ----------
        token : str
            String token to inspect.

        Examples
        --------

        ```python
        formatter = MaxSpaceFormatter()
        message = formatter.inspect("x  =  1")
        ```

        Returns
        -------
        str | None
            Error message if multiple consecutive spaces found outside
            of strings and indentation, `None` otherwise.
        """
        if self.format(token) != token:
            return "Lines should not have more than 1 consecutive space outside of strings and indentation."

        return None


    def format(self, token: str) -> str:
        """Collapse multiple spaces to one outside strings and indentation.

        Parameters
        ----------
        token : str
            Token to format.

        Examples
        --------

        ```python
        formatter = MaxSpaceFormatter()
        result = formatter.format("x  =  1")
        ```

        Returns
        -------
        str
            Token with multiple spaces collapsed to one.
        """
        leading_match = re.match(r"^( *)", token)
        leading = leading_match.group(1) if leading_match else ""
        rest = token[len(leading):]

        if not rest:
            return token

        collapsed = self._collapse_spaces(rest)

        return leading + collapsed
