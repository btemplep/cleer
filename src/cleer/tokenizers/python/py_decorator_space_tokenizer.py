"""Decorator space tokenizer module."""

__all__ = ["PyDecoratorSpaceTokenizer"]


import re
from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class PyDecoratorSpaceTokenizer(Tokenizer):
    """Tokenizes whitespace between consecutive decorators.

    Captures all space after a decorator when the next non-whitespace
    content is another decorator. The token includes only the whitespace
    between them.

    Emits token type: `decorator_space`

    Examples
    --------

    ```python
    from cleer import PyDecoratorSpaceTokenizer

    tokenizer = PyDecoratorSpaceTokenizer()
    tokens = tokenizer.tokenize("@first\\n\\n@second\\ndef func():\\n    pass\\n")
    ```
    """
    emits_token_type = "decorator_space"


    def _find_decorator_end(
        self,
        document: str,
        start: int
    ) -> int:
        """Find the end of a decorator including multi-line with parens."""
        paren_pos = document.find("(", start)
        newline_pos = document.find("\n", start)

        if (
            paren_pos != -1
            and (
                newline_pos == -1
                or paren_pos < newline_pos
            )
        ):
            depth = 1
            i = paren_pos + 1
            while i < len(document) and depth > 0:
                if document[i] == "(":
                    depth += 1
                elif document[i] == ")":
                    depth -= 1

                i += 1

            return i
        elif newline_pos != -1:
            return newline_pos

        return len(document)


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize whitespace between consecutive decorators.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = PyDecoratorSpaceTokenizer()
        tokens = tokenizer.tokenize("@first\\n\\n@second\\ndef func():\\n    pass\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results for whitespace between decorators.

            ```python
            [
                {"token": "\\n\\n", "index": 6, "length": 2}
            ]
            ```
        """
        tokens: List[dict] = []
        decorator_pattern = re.compile(r"^([ \t]*)@", re.MULTILINE)
        def_pattern = re.compile(
            r"^([ \t]*)(async\s+)?def\s+|^([ \t]*)class\s+",
            re.MULTILINE
        )
        matches = list(decorator_pattern.finditer(document))

        for i in range(len(matches) - 1):
            current_match = matches[i]
            next_match = matches[i + 1]

            decorator_end = self._find_decorator_end(
                document,
                current_match.start()
            )

            space_start = decorator_end
            space_end = next_match.start()

            token_text = document[space_start:space_end]

            if token_text.strip() == "":
                tokens.append(
                    {
                        "token": token_text,
                        "index": space_start,
                        "length": len(token_text)
                    }
                )

        for match in matches:
            decorator_end = self._find_decorator_end(
                document,
                match.start()
            )
            remaining = document[decorator_end:]
            def_match = def_pattern.match(remaining.lstrip("\n "))

            if def_match:
                def_start = document.find(
                    def_match.group(0).rstrip(),
                    decorator_end
                )

                token_text = document[decorator_end:def_start]

                if "\n" in token_text and token_text != "\n":
                    tokens.append(
                        {
                            "token": token_text,
                            "index": decorator_end,
                            "length": len(token_text)
                        }
                    )

        tokens.sort(key=lambda t: t['index'])

        return tokens
