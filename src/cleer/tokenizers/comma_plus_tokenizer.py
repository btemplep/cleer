"""Comma plus tokenizer module."""

__all__ = ["CommaPlusTokenizer"]


from typing import List

from cleer.tokenizers.tokenizer import Tokenizer


class CommaPlusTokenizer(Tokenizer):
    """Tokenizes commas with following whitespace and the first non-whitespace character.

    Each comma is returned as a token that includes the comma, all following
    whitespace, and the first non-whitespace character after the whitespace.

    Emits token type: `comma_plus`

    Examples
    --------

    ```python
    from cleer import CommaPlusTokenizer

    tokenizer = CommaPlusTokenizer()
    tokens = tokenizer.tokenize("[1, 2,\\n]\\n")
    ```
    """
    emits_token_type = "comma_plus"


    def _is_single_item_set(self, document: str, comma_pos: int) -> bool:
        """Check if comma at comma_pos is the sole comma in a single-item set."""
        depth = 0
        has_colon = False
        has_other_comma = False
        i = comma_pos - 1
        in_single = False
        in_double = False

        while i >= 0:
            char = document[i]

            if in_single:
                if char == "'" and (i == 0 or document[i - 1] != "\\"):
                    in_single = False

                i -= 1
                continue

            if in_double:
                if char == '"' and (i == 0 or document[i - 1] != "\\"):
                    in_double = False

                i -= 1
                continue

            if char == "'" and not in_double:
                in_single = True
                i -= 1
                continue

            if char == '"' and not in_single:
                in_double = True
                i -= 1
                continue

            if char in ")]}":
                depth += 1
            elif char in "([{":
                if depth == 0:
                    if char == "{":
                        return not has_colon and not has_other_comma

                    return False

                depth -= 1
            elif char == ":" and depth == 0:
                has_colon = True
            elif char == "," and depth == 0:
                has_other_comma = True

            i -= 1

        return False


    def _is_single_item_tuple(self, document: str, comma_pos: int) -> bool:
        """Check if comma at comma_pos is the sole comma in a single-item tuple (not a function call)."""
        depth = 0
        has_other_comma = False
        i = comma_pos - 1
        in_single = False
        in_double = False

        while i >= 0:
            char = document[i]
            if in_single:
                if char == "'" and (i == 0 or document[i - 1] != "\\"):
                    in_single = False

                i -= 1
                continue

            if in_double:
                if char == '"' and (i == 0 or document[i - 1] != "\\"):
                    in_double = False

                i -= 1
                continue

            if char == "'" and not in_double:
                in_single = True
                i -= 1
                continue

            if char == '"' and not in_single:
                in_double = True
                i -= 1
                continue

            if char in ")]}":
                depth += 1
            elif char in "([{":
                if depth == 0:
                    if char == "(":
                        if has_other_comma:
                            return False

                        before = i - 1
                        while before >= 0 and document[before] in " \t":
                            before -= 1

                        if before >= 0 and (document[before].isalnum() or document[before] in "_)"):
                            return False

                        return True

                    return False

                depth -= 1
            elif char == "," and depth == 0:
                has_other_comma = True

            i -= 1

        return False


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize commas with following whitespace and next character.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Examples
        --------

        ```python
        tokenizer = CommaPlusTokenizer()
        tokens = tokenizer.tokenize("[1, 2]\\n")
        ```

        Returns
        -------
        List[TokenResult]
            List of token results, one per comma with context.

            ```python
            [
                {"token": ", 2", "index": 2, "length": 3}
            ]
            ```
        """
        tokens: List[dict] = []
        i = 0
        in_single = False
        in_double = False
        in_triple_single = False
        in_triple_double = False

        while i < len(document):
            remaining = document[i:]
            if in_triple_single:
                if remaining.startswith("'''"):
                    in_triple_single = False
                    i += 3
                    continue

                i += 1
                continue

            if in_triple_double:
                if remaining.startswith('"""'):
                    in_triple_double = False
                    i += 3
                    continue

                i += 1
                continue

            if in_single:
                if document[i] == "\\" and i + 1 < len(document):
                    i += 2
                    continue

                if document[i] == "'":
                    in_single = False

                i += 1
                continue

            if in_double:
                if document[i] == "\\" and i + 1 < len(document):
                    i += 2
                    continue

                if document[i] == '"':
                    in_double = False

                i += 1
                continue

            if remaining.startswith("'''"):
                in_triple_single = True
                i += 3
                continue

            if remaining.startswith('"""'):
                in_triple_double = True
                i += 3
                continue

            if document[i] == "'" and not in_double:
                in_single = True
                i += 1
                continue

            if document[i] == '"' and not in_single:
                in_double = True
                i += 1
                continue

            if document[i] == "#":
                newline = document.find("\n", i)
                if newline == -1:
                    break

                i = newline + 1
                continue

            if document[i] == ",":
                start = i
                j = i + 1

                while j < len(document) and document[j] in " \t\n":
                    j += 1

                if j < len(document):
                    if document[j] == "}":
                        if self._is_single_item_set(document, start):
                            i = j + 1
                            continue

                    if document[j] == ")":
                        if self._is_single_item_tuple(document, start):
                            i = j + 1
                            continue

                    end = j + 1
                    token_text = document[start:end]
                    tokens.append(
                        {
                            "token": token_text,
                            "index": start,
                            "length": len(token_text)
                        }
                    )
                    i = end
                    continue

                i = j
                continue

            i += 1

        return tokens
