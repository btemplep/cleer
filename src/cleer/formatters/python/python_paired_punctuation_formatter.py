"""Python paired punctuation formatter module."""

__all__ = ["PythonPairedPunctuationFormatter"]


import re
from typing import List, Tuple

from cleer.formatters.formatter import Formatter


class PythonPairedPunctuationFormatter(Formatter):
    """Formats paired punctuation by flattening and conditionally expanding.

    Handles function definitions, function calls, decorators, dict/list/set/
    tuple literals, and logic blocks (if/elif/while with and/or).

    Rules:
    - Flatten first, then expand based on context-specific thresholds
    - Dicts with >0 items always expand
    - Lists/sets/tuples: flatten if not nested; expand if >30 chars
    - Nested containers expand if >0 items; if any sibling expands, all expand
    - Function defs: expand if >80 chars (no indent), >100 (with indent),
      >4 args, any kwarg with >1 arg, or inner expanded
    - Function calls: expand if >60 chars (no indent), >80 (with indent),
      >4 args, any kwarg with >1 arg, or inner expanded
    - Decorators: same as function calls
    - Logic blocks: expand if >2 statements, >60 (no indent), >80 (with
      indent), or inner expanded; add parentheses when expanded

    Examples
    --------

    ```python
    from cleer import PythonPairedPunctuationFormatter

    formatter = PythonPairedPunctuationFormatter()
    result = formatter.format("my_func(a, b, c, d, e)")
    ```
    """
    accepts_token_types = ["python_paired_punctuation"]

    _OPEN_BRACKETS = "([{"
    _CLOSE_BRACKETS = ")]}"
    _BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}"}
    _CLOSE_TO_OPEN = {")": "(", "]": "[", "}": "{"}


    def inspect(self, token: str) -> str | None:
        """Inspect a token for paired punctuation violations.

        Parameters
        ----------
        token : str
            Token string to inspect.

        Returns
        -------
        str | None
            Error message if the token has a paired punctuation
            violation. Returns ``None`` if there is no violation.
        """
        formatted = self.format(token)

        if formatted != token:
            return "Paired punctuation formatting violation."

        return None


    def format(self, token: str) -> str:
        """Format paired punctuation in the token.

        Parameters
        ----------
        token : str
            Token string to format.

        Returns
        -------
        str
            Formatted token.
        """
        indent = self._get_indent(token)
        context = self._detect_context(token)

        if context == "logic":
            return self._format_logic(token, indent)

        return self._format_punctuation(token, indent, context)


    def _get_indent(self, token: str) -> str:
        """Get the leading whitespace of the token."""
        for i, ch in enumerate(token):
            if ch != " " and ch != "\t":
                return token[:i]

        return ""


    def _is_string_parens(self, token: str) -> bool:
        """Check if the token is parentheses containing concatenated string literals.

        Matches implicit string concatenation in parens like:
        ``x = ("part one" "part two")`` or multiline variants. These
        should not be flattened or expanded. A single string in parens
        is NOT string concatenation and is handled normally.

        Only matches when the outermost paired punctuation after the
        assignment is ``(``.
        """
        stripped = token.strip()

        eq_pos = stripped.find("=")
        if eq_pos == -1:
            return False

        after_eq = stripped[eq_pos + 1:].lstrip()

        if not after_eq.startswith("("):
            return False

        depth = 0
        i = 0
        paren_end = -1
        while i < len(after_eq):
            if after_eq[i] == "(":
                depth += 1
            elif after_eq[i] == ")":
                depth -= 1
                if depth == 0:
                    paren_end = i
                    break
            i += 1

        if paren_end == -1:
            return False

        content = after_eq[1:paren_end].strip()

        if not content:
            return False

        return self._is_string_concat_content(content)


    def _format_string_concat(self, token: str, indent: str) -> str:
        """Format parenthesized string concatenation.

        Flattens the content, extracts individual string literals, and
        expands with one string per line.
        """
        stripped = token.strip()
        paren_start = stripped.find("(")
        paren_end = stripped.rfind(")")
        before = stripped[:paren_start + 1]
        content = stripped[paren_start + 1:paren_end]
        inner_indent = indent + "    "

        strings = self._extract_string_literals(content)

        if not strings:
            return token

        lines = [f"{indent}{before}"]
        for s in strings:
            lines.append(f"{inner_indent}{s}")
        lines.append(f"{indent})")

        return "\n".join(lines)


    def _is_string_concat_content(self, content: str) -> bool:
        """Check if content contains only concatenated string literals.

        Returns True only when there are 2+ adjacent string literals
        with no other content (commas, expressions, etc).
        """
        s = content.strip()

        if not s:
            return False

        i = 0
        string_count = 0

        while i < len(s):
            ch = s[i]

            if ch in (" ", "\t", "\n", "\r"):
                i += 1
                continue

            if s[i:i + 3] in ('"""', "'''"):
                string_count += 1
                quote = s[i:i + 3]
                i += 3
                while i < len(s) - 2:
                    if s[i:i + 3] == quote:
                        i += 3
                        break
                    i += 1
                else:
                    i = len(s)
                continue

            if ch in ('"', "'"):
                string_count += 1
                quote = ch
                i += 1
                while i < len(s):
                    if s[i] == quote and s[i - 1] != "\\":
                        i += 1
                        break
                    i += 1
                continue

            return False

        return string_count > 1


    def _extract_string_literals(self, content: str) -> list:
        """Extract individual string literals from concatenated content."""
        strings = []
        i = 0
        s = content.strip()

        while i < len(s):
            ch = s[i]

            if ch in (" ", "\t", "\n", "\r"):
                i += 1
                continue

            if s[i:i + 3] in ('"""', "'''"):
                quote = s[i:i + 3]
                start = i
                i += 3
                while i < len(s) - 2:
                    if s[i:i + 3] == quote:
                        i += 3
                        break
                    i += 1
                else:
                    i = len(s)
                strings.append(s[start:i])
                continue

            if ch in ('"', "'"):
                quote = ch
                start = i
                i += 1
                while i < len(s):
                    if s[i] == quote and s[i - 1] != "\\":
                        i += 1
                        break
                    i += 1
                strings.append(s[start:i])
                continue

            break

        return strings


    def _detect_context(self, token: str) -> str:
        """Detect what kind of paired punctuation context this is."""
        stripped = token.strip()

        if stripped.startswith("@"):
            return "decorator"

        if stripped.startswith(("def ", "async def ")):
            return "funcdef"

        if (
            stripped.startswith(("if ", "elif ", "while "))
            and stripped.endswith(":")
            and self._has_logic_operator(stripped)
        ):
            return "logic"

        if "=" in stripped and not stripped.startswith("return"):
            eq_idx = stripped.find("=")
            if eq_idx > 0 and stripped[eq_idx - 1] not in "!<>":
                after_eq = stripped[eq_idx + 1:].lstrip()
                if after_eq.startswith(("{", "[", "(")):
                    return "assignment"

        return "call"


    def _has_logic_operator(self, s: str) -> bool:
        """Check if a string contains a top-level 'or' or 'and' operator.

        Recognizes operators with or without surrounding spaces,
        including adjacent to parentheses (e.g., ``or(``, ``)and``).
        """
        import re
        return bool(re.search(r"(?<=[ )\n])or(?=[ (\n])|(?<=[ )\n])and(?=[ (\n])", s))


    def _format_logic(self, token: str, indent: str) -> str:
        """Format a logic condition (if/elif/while with and/or)."""
        stripped = token.strip()

        keyword_match = re.match(r"^(if|elif|while)\s+", stripped)
        if not keyword_match:
            return token

        keyword = keyword_match.group(0)
        rest = stripped[len(keyword):]

        if rest.endswith(":"):
            rest = rest[:-1].rstrip()

        condition = self._flatten_string(rest)

        if condition.startswith("(") and condition.endswith(")"):
            inner = condition[1:-1]
            if self._brackets_balanced(inner):
                condition = inner.strip()

        statements = self._split_logic_statements(condition)
        inner_indent = indent + "    "

        formatted_parts = self._format_logic_parts(statements, inner_indent)

        needs_expand = self._logic_needs_expand(
            keyword, formatted_parts, indent, inner_indent
        )

        if not needs_expand:
            flat_condition = self._join_logic_flat(formatted_parts)
            return f"{indent}{keyword}{flat_condition}:"

        return self._expand_logic(keyword, formatted_parts, indent, inner_indent)


    def _format_logic_parts(self, statements: list, indent: str) -> list:
        """Extract logic parts with their operators.

        Returns a list of dicts with:
        - operator: "or", "and", or "" (first item)
        - content: the raw expression (not yet formatted for inner punctuation)
        """
        parts = []

        for i, item in enumerate(statements):
            if item in ("or", "and"):
                continue

            operator = ""
            if i > 0:
                prev_idx = i - 1
                if prev_idx >= 0 and statements[prev_idx] in ("or", "and"):
                    operator = statements[prev_idx]

            parts.append(
                {
                    "operator": operator,
                    "content": item
                }
            )

        return parts


    def _format_logic_item(self, item: str, indent: str) -> str:
        """Format inner paired punctuation within a logic item.

        Applies normal expansion rules to any paired punctuation
        found in the item. The indent parameter is the indent level
        where the item will be placed in the final output.

        Also handles logic sub-groups: paren-wrapped and/or expressions
        are expanded as nested logic blocks.
        """
        if self._is_logic_subgroup(item):
            return self._expand_logic_subgroup(item, indent)

        regions = self._find_top_regions(item)

        if not regions:
            return item

        result = item
        offset = 0

        for region in regions:
            rc = self._region_context(region, item)

            if rc == "subscript":
                continue

            inner_items = self._split_items(region["content"])

            if not inner_items:
                continue

            if region["open_char"] == "(" and self._is_string_concat_content(region["content"]):
                strings = self._extract_string_literals(region["content"])
                exp_indent = indent + "    "
                parts = [f"{region['open_char']}"]
                for s in strings:
                    parts.append(f"\n{exp_indent}{s}")
                parts.append(f"\n{indent}{region['close_char']}")
                expanded = "".join(parts)
                start = region["start"] + offset
                end = region["end"] + offset + 1
                result = result[:start] + expanded + result[end:]
                offset += len(expanded) - (region["end"] - region["start"] + 1)
                continue

            before = item[:region["start"]]
            after = item[region["end"] + 1:]
            full_line_len = len(before) + 1 + len(", ".join(inner_items)) + 1 + len(after)

            should_exp = self._should_expand(
                inner_items, region, rc, indent, full_line_len=full_line_len
            )

            if should_exp:
                expanded = self._expand_inner(inner_items, region, indent, rc)
                start = region["start"] + offset
                end = region["end"] + offset + 1
                result = result[:start] + expanded + result[end:]
                offset += len(expanded) - (region["end"] - region["start"] + 1)

        return result


    def _is_logic_subgroup(self, item: str) -> bool:
        """Check if an item is a paren-wrapped logic sub-expression."""
        stripped = item.strip()
        if not (stripped.startswith("(") and stripped.endswith(")")):
            return False

        inner = stripped[1:-1]
        if not self._brackets_balanced(inner):
            return False

        return " and " in inner or " or " in inner


    def _expand_logic_subgroup(self, item: str, indent: str) -> str:
        """Expand a paren-wrapped logic sub-group."""
        stripped = item.strip()
        inner = stripped[1:-1].strip()
        inner_indent = indent + "    "

        statements = self._split_logic_statements(inner)
        parts = self._format_logic_parts(statements, inner_indent)

        lines = ["("]
        for part in parts:
            raw_content = part["content"]
            operator = part["operator"]

            formatted = self._format_logic_item(raw_content, inner_indent)

            if "\n" in formatted:
                content_lines = formatted.split("\n")
                first_line = content_lines[0]
                if operator:
                    lines.append(f"{inner_indent}{operator} {first_line}")
                else:
                    lines.append(f"{inner_indent}{first_line}")
                for cl in content_lines[1:]:
                    lines.append(cl)
            else:
                if operator:
                    lines.append(f"{inner_indent}{operator} {formatted}")
                else:
                    lines.append(f"{inner_indent}{formatted}")

        lines.append(f"{indent})")
        return "\n".join(lines)


    def _logic_needs_expand(
        self,
        keyword: str,
        parts: list,
        indent: str,
        inner_indent: str
    ) -> bool:
        """Determine if logic should be expanded."""
        condition_count = len(parts)
        indent_len = len(indent)

        if condition_count > 2:
            return True

        any_inner_expands = any(
            self._logic_item_has_expansion(p["content"], inner_indent)
            for p in parts
        )
        if any_inner_expands:
            return True

        flat_condition = self._join_logic_flat(parts)
        flat_len = len(keyword) + len(flat_condition) + 1

        if flat_len > 60:
            return True
        if flat_len + indent_len > 80:
            return True

        return False


    def _logic_item_has_expansion(self, item: str, indent: str) -> bool:
        """Check if a logic item has inner paired punctuation that would expand."""
        regions = self._find_top_regions(item)

        for region in regions:
            rc = self._region_context(region, item)
            if rc == "subscript":
                continue

            if region["open_char"] == "(" and self._is_string_concat_content(region["content"]):
                return True

            inner_items = self._split_items(region["content"])
            if not inner_items:
                continue

            before = item[:region["start"]]
            after = item[region["end"] + 1:]
            full_line_len = len(before) + 1 + len(", ".join(inner_items)) + 1 + len(after)

            if self._should_expand(inner_items, region, rc, indent, full_line_len=full_line_len):
                return True

        return False


    def _join_logic_flat(self, parts: list) -> str:
        """Join logic parts into a single flat condition string."""
        pieces = []
        for p in parts:
            if p["operator"]:
                pieces.append(f" {p['operator']} {p['content']}")
            else:
                pieces.append(p["content"])
        return "".join(pieces)


    def _expand_logic(
        self,
        keyword: str,
        parts: list,
        indent: str,
        inner_indent: str
    ) -> str:
        """Expand a logic condition across multiple lines with parens."""
        lines = [f"{indent}{keyword}("]

        for part in parts:
            raw_content = part["content"]
            operator = part["operator"]

            formatted = self._format_logic_item(raw_content, inner_indent)

            if "\n" in formatted:
                content_lines = formatted.split("\n")
                first_line = content_lines[0]
                if operator:
                    lines.append(f"{inner_indent}{operator} {first_line}")
                else:
                    lines.append(f"{inner_indent}{first_line}")

                for cl in content_lines[1:]:
                    lines.append(cl)
            else:
                if operator:
                    lines.append(f"{inner_indent}{operator} {formatted}")
                else:
                    lines.append(f"{inner_indent}{formatted}")

        lines.append(f"{indent}):")

        return "\n".join(lines)


    def _split_logic_statements(self, condition: str) -> List[str]:
        """Split a logic condition by top-level operators.

        Splits by 'or' first. If there are no 'or' operators, splits by 'and'.
        Groups 'and' expressions together when mixed with 'or', adding
        parentheses to clarify precedence.
        """
        or_parts = self._split_by_operator(condition, " or ")

        if len(or_parts) > 1:
            result = []
            for i, part in enumerate(or_parts):
                if self._has_logic_operator_word(part, "and"):
                    if not (part.startswith("(") and part.endswith(")") and self._brackets_balanced(part[1:-1])):
                        part = f"({part})"
                result.append(part)
                if i < len(or_parts) - 1:
                    result.append("or")
            return result

        and_parts = self._split_by_operator(condition, " and ")
        if len(and_parts) > 1:
            result = []
            for i, part in enumerate(and_parts):
                result.append(part)
                if i < len(and_parts) - 1:
                    result.append("and")
            return result

        return [condition]


    def _has_logic_operator_word(self, s: str, keyword: str) -> bool:
        """Check if string contains the given operator keyword at top level."""
        import re
        pattern = rf"(?<=[ )\n]){keyword}(?=[ (\n])"
        return bool(re.search(pattern, s))


    def _split_by_operator(self, s: str, operator: str) -> List[str]:
        """Split string by an operator at depth 0, respecting strings and brackets.

        Handles operators adjacent to parentheses (e.g., ``or(``, ``)and(``).
        The operator keyword is extracted from the padded operator string.
        """
        parts = []
        current = ""
        depth = 0
        in_string = False
        string_char = ""
        triple_quote = False
        i = 0
        keyword = operator.strip()
        kw_len = len(keyword)

        while i < len(s):
            ch = s[i]

            if not in_string:
                if s[i:i + 3] in ('"""', "'''"):
                    in_string = True
                    string_char = s[i:i + 3]
                    triple_quote = True
                    current += s[i:i + 3]
                    i += 3
                    continue
                elif ch in ('"', "'"):
                    in_string = True
                    string_char = ch
                    triple_quote = False
                    current += ch
                    i += 1
                    continue

                if ch in self._OPEN_BRACKETS:
                    depth += 1
                    current += ch
                    i += 1
                elif ch in self._CLOSE_BRACKETS:
                    depth -= 1
                    current += ch
                    i += 1
                elif depth == 0 and s[i:i + kw_len] == keyword:
                    before_ok = (
                        i == 0
                        or s[i - 1] in (" ", "\t", ")")
                    )
                    after_ok = (
                        i + kw_len >= len(s)
                        or s[i + kw_len] in (" ", "\t", "(")
                    )
                    if before_ok and after_ok:
                        parts.append(current.strip())
                        current = ""
                        i += kw_len
                        if i < len(s) and s[i] == " ":
                            i += 1
                    else:
                        current += ch
                        i += 1
                else:
                    current += ch
                    i += 1
            else:
                if triple_quote and s[i:i + 3] == string_char:
                    in_string = False
                    current += s[i:i + 3]
                    i += 3
                    continue
                elif not triple_quote and ch == string_char and (i == 0 or s[i - 1] != "\\"):
                    in_string = False
                    current += ch
                    i += 1
                else:
                    current += ch
                    i += 1

        if current.strip():
            parts.append(current.strip())

        return parts


    def _format_punctuation(self, token: str, indent: str, context: str) -> str:
        """Format paired punctuation (non-logic contexts)."""
        if context == "assignment" and self._is_string_parens(token):
            return self._format_string_concat(token, indent)

        flat = self._flatten_token(token, indent, context)

        parsed = self._parse_regions(flat, indent, context)

        if parsed is None:
            return flat

        result = self._rebuild(parsed, indent, context)

        return result


    def _flatten_token(self, token: str, indent: str, context: str) -> str:
        """Flatten a multiline token into a single line."""
        stripped = token.strip()
        flat = self._flatten_string(stripped)

        if context == "funcdef":
            flat = re.sub(r"\s*:\s*", ": ", flat)
            flat = re.sub(r"\s*=\s*", "=", flat)
            flat = re.sub(r":\s*=", ":=", flat)
            flat = re.sub(r":\s+", ": ", flat)

        return indent + flat


    def _flatten_string(self, s: str) -> str:
        """Collapse internal whitespace/newlines into single spaces."""
        result = []
        i = 0
        in_string = False
        string_char = ""
        triple_quote = False

        while i < len(s):
            if not in_string:
                if s[i:i + 3] in ('"""', "'''"):
                    in_string = True
                    string_char = s[i:i + 3]
                    triple_quote = True
                    result.append(s[i:i + 3])
                    i += 3
                elif s[i] in ('"', "'"):
                    in_string = True
                    string_char = s[i]
                    triple_quote = False
                    result.append(s[i])
                    i += 1
                elif s[i] in (" ", "\t", "\n", "\r"):
                    if result and result[-1] != " ":
                        result.append(" ")
                    i += 1
                else:
                    result.append(s[i])
                    i += 1
            else:
                if triple_quote and s[i:i + 3] == string_char:
                    in_string = False
                    result.append(s[i:i + 3])
                    i += 3
                elif not triple_quote and s[i] == string_char and (i == 0 or s[i - 1] != "\\"):
                    in_string = False
                    result.append(s[i])
                    i += 1
                else:
                    result.append(s[i])
                    i += 1

        return "".join(result)


    def _parse_regions(self, flat: str, indent: str, context: str):
        """Parse a flattened token into a tree of regions.

        Returns a dict with:
        - type: 'root'
        - content: the full flat string
        - regions: list of nested region dicts
        - context: the detected context

        Each region dict has:
        - open_char, close_char
        - start, end: indices in the flat string
        - items: list of item strings (split by commas at depth 0)
        - sub_regions: nested regions within items
        - region_context: what this specific region represents
        """
        stripped = flat.strip()
        regions = self._find_top_regions(stripped)

        if not regions:
            return None

        return {
            "type": "root",
            "content": flat,
            "stripped": stripped,
            "indent": indent,
            "context": context,
            "regions": regions
        }


    def _find_top_regions(self, s: str) -> list:
        """Find all top-level paired punctuation regions in a string."""
        regions = []
        i = 0
        in_string = False
        string_char = ""
        triple_quote = False

        while i < len(s):
            if not in_string:
                if s[i:i + 3] in ('"""', "'''"):
                    in_string = True
                    string_char = s[i:i + 3]
                    triple_quote = True
                    i += 3
                elif s[i] in ('"', "'"):
                    in_string = True
                    string_char = s[i]
                    triple_quote = False
                    i += 1
                elif s[i] in self._OPEN_BRACKETS:
                    end = self._find_matching_close(s, i)
                    if end is not None:
                        regions.append(
                            {
                                "open_char": s[i],
                                "close_char": s[end],
                                "start": i,
                                "end": end,
                                "content": s[i + 1:end]
                            }
                        )
                        i = end + 1
                    else:
                        i += 1
                else:
                    i += 1
            else:
                if triple_quote and s[i:i + 3] == string_char:
                    in_string = False
                    i += 3
                elif not triple_quote and s[i] == string_char and (i == 0 or s[i - 1] != "\\"):
                    in_string = False
                    i += 1
                else:
                    i += 1

        return regions


    def _find_matching_close(self, s: str, start: int) -> int | None:
        """Find matching closing bracket."""
        open_ch = s[start]
        close_ch = self._BRACKET_PAIRS[open_ch]
        depth = 0
        i = start
        in_string = False
        string_char = ""
        triple_quote = False

        while i < len(s):
            if not in_string:
                if s[i:i + 3] in ('"""', "'''"):
                    in_string = True
                    string_char = s[i:i + 3]
                    triple_quote = True
                    i += 3
                    continue
                elif s[i] in ('"', "'") and i != start:
                    in_string = True
                    string_char = s[i]
                    triple_quote = False
                    i += 1
                    continue

                if s[i] == open_ch:
                    depth += 1
                elif s[i] == close_ch:
                    depth -= 1
                    if depth == 0:
                        return i
            else:
                if triple_quote and s[i:i + 3] == string_char:
                    in_string = False
                    i += 3
                    continue
                elif not triple_quote and s[i] == string_char and (i == 0 or s[i - 1] != "\\"):
                    in_string = False

            i += 1

        return None


    def _split_items(self, content: str) -> List[str]:
        """Split content by top-level commas."""
        items = []
        current = ""
        depth = 0
        in_string = False
        string_char = ""
        triple_quote = False
        i = 0

        while i < len(content):
            ch = content[i]

            if not in_string:
                if content[i:i + 3] in ('"""', "'''"):
                    in_string = True
                    string_char = content[i:i + 3]
                    triple_quote = True
                    current += content[i:i + 3]
                    i += 3
                    continue
                elif ch in ('"', "'"):
                    in_string = True
                    string_char = ch
                    triple_quote = False
                    current += ch
                    i += 1
                    continue

                if ch in self._OPEN_BRACKETS:
                    depth += 1
                    current += ch
                elif ch in self._CLOSE_BRACKETS:
                    depth -= 1
                    current += ch
                elif ch == "," and depth == 0:
                    items.append(current.strip())
                    current = ""
                else:
                    current += ch
            else:
                if triple_quote and content[i:i + 3] == string_char:
                    in_string = False
                    current += content[i:i + 3]
                    i += 3
                    continue
                elif not triple_quote and ch == string_char and (i == 0 or content[i - 1] != "\\"):
                    in_string = False
                    current += ch
                else:
                    current += ch

            i += 1

        if current.strip():
            items.append(current.strip())

        return items


    def _brackets_balanced(self, s: str) -> bool:
        """Check if brackets are balanced in a string (ignoring strings)."""
        depth = 0
        in_string = False
        string_char = ""
        triple_quote = False
        i = 0

        while i < len(s):
            if not in_string:
                if s[i:i + 3] in ('"""', "'''"):
                    in_string = True
                    string_char = s[i:i + 3]
                    triple_quote = True
                    i += 3
                    continue
                elif s[i] in ('"', "'"):
                    in_string = True
                    string_char = s[i]
                    triple_quote = False
                    i += 1
                    continue

                if s[i] in self._OPEN_BRACKETS:
                    depth += 1
                elif s[i] in self._CLOSE_BRACKETS:
                    depth -= 1
                    if depth < 0:
                        return False
            else:
                if triple_quote and s[i:i + 3] == string_char:
                    in_string = False
                    i += 3
                    continue
                elif not triple_quote and s[i] == string_char and (i == 0 or s[i - 1] != "\\"):
                    in_string = False

            i += 1

        return depth == 0


    def _has_expanded_inner(self, content: str, indent: str) -> bool:
        """Check if any inner region would need to be expanded."""
        regions = self._find_top_regions(content)

        for region in regions:
            items = self._split_items(region["content"])
            rc = self._region_context(region, content)

            if self._should_expand(items, region, rc, indent + "    "):
                return True

        return False


    def _region_context(self, region: dict, full_str: str) -> str:
        """Determine the context of a specific region."""
        start = region["start"]
        before = full_str[:start].rstrip()

        if region["open_char"] == "{":
            items = self._split_items(region["content"])
            if items and ":" in items[0]:
                return "dict"
            return "set"

        if region["open_char"] == "[":
            if before and (before[-1].isalnum() or before[-1] in ("_", "'", '"', ")")):
                return "subscript"
            return "list"

        if region["open_char"] == "(":
            if before.endswith("@") or re.search(r"@[\w.]+$", before):
                return "decorator"

            if re.search(r"(def|async\s+def)\s+\w+$", before):
                return "funcdef"

            if before and (before[-1].isalnum() or before[-1] in ("_", ".", ")")):
                return "call"

            return "tuple"

        return "unknown"


    def _should_expand(
        self,
        items: List[str],
        region: dict,
        region_context: str,
        indent: str,
        is_nested: bool = False,
        full_line_len: int = 0
    ) -> bool:
        """Determine if a region should be expanded."""
        if not items:
            return False

        if region_context == "subscript":
            return False

        indent_len = len(indent)
        content_len = len(region["open_char"]) + len(", ".join(items)) + len(region["close_char"])

        if region_context == "dict":
            return len(items) > 0

        if region_context in ("list", "set", "tuple"):
            if is_nested:
                return len(items) > 0

            has_nested = any(
                self._item_has_container(item) for item in items
            )
            if has_nested:
                return len(items) > 0
            return content_len > 30

        has_kwarg = any("=" in item and not self._eq_in_string(item) for item in items)
        more_than_two = len(items) > 2

        if full_line_len == 0:
            full_line_len = content_len

        if region_context == "funcdef":
            if full_line_len > 80:
                return True
            if full_line_len + indent_len > 100:
                return True
            if len(items) > 4:
                return True
            if has_kwarg and more_than_two:
                return True
            if self._any_inner_expanded(items, indent + "    "):
                return True
            return False

        if region_context in ("call", "decorator"):
            if full_line_len > 60:
                return True
            if full_line_len + indent_len > 80:
                return True
            if len(items) > 4:
                return True
            if has_kwarg and more_than_two:
                return True
            if self._any_inner_expanded(items, indent + "    "):
                return True
            return False

        return False


    def _item_has_container(self, item: str) -> bool:
        """Check if an item contains a nested container."""
        in_string = False
        string_char = ""
        triple_quote = False
        i = 0

        while i < len(item):
            if not in_string:
                if item[i:i + 3] in ('"""', "'''"):
                    in_string = True
                    string_char = item[i:i + 3]
                    triple_quote = True
                    i += 3
                    continue
                elif item[i] in ('"', "'"):
                    in_string = True
                    string_char = item[i]
                    triple_quote = False
                    i += 1
                    continue

                if item[i] in self._OPEN_BRACKETS:
                    return True
            else:
                if triple_quote and item[i:i + 3] == string_char:
                    in_string = False
                    i += 3
                    continue
                elif not triple_quote and item[i] == string_char and (i == 0 or item[i - 1] != "\\"):
                    in_string = False

            i += 1

        return False


    def _eq_in_string(self, item: str) -> bool:
        """Check if the '=' in an item is inside a string (not a kwarg)."""
        in_string = False
        string_char = ""
        triple_quote = False
        depth = 0
        i = 0

        while i < len(item):
            if not in_string:
                if item[i:i + 3] in ('"""', "'''"):
                    in_string = True
                    string_char = item[i:i + 3]
                    triple_quote = True
                    i += 3
                    continue
                elif item[i] in ('"', "'"):
                    in_string = True
                    string_char = item[i]
                    triple_quote = False
                    i += 1
                    continue

                if item[i] in self._OPEN_BRACKETS:
                    depth += 1
                elif item[i] in self._CLOSE_BRACKETS:
                    depth -= 1
                elif item[i] == "=" and depth == 0:
                    if i > 0 and item[i - 1] not in "!<>":
                        if i + 1 < len(item) and item[i + 1] != "=":
                            return False
            else:
                if triple_quote and item[i:i + 3] == string_char:
                    in_string = False
                    i += 3
                    continue
                elif not triple_quote and item[i] == string_char and (i == 0 or item[i - 1] != "\\"):
                    in_string = False

            i += 1

        return True


    def _any_inner_expanded(self, items: List[str], indent: str) -> bool:
        """Check if any item contains an inner region that would expand."""
        for item in items:
            regions = self._find_top_regions(item)
            for region in regions:
                if (
                    region["open_char"] == "("
                    and self._is_string_concat_content(region["content"])
                ):
                    return True

                if region["open_char"] == "(" and self._is_logic_subgroup(
                    item[region["start"]:region["end"] + 1]
                ):
                    return True

                inner_items = self._split_items(region["content"])
                rc = self._region_context(region, item)
                if self._should_expand(
                    inner_items, region, rc, indent, is_nested=False
                ):
                    return True

        return False


    def _rebuild(self, parsed: dict, indent: str, context: str) -> str:
        """Rebuild the token with proper expansion/flattening."""
        stripped = parsed["stripped"]
        regions = parsed["regions"]

        if not regions:
            return parsed["content"]

        if context == "funcdef":
            return self._rebuild_funcdef(stripped, regions, indent)
        elif context == "decorator":
            return self._rebuild_decorator(stripped, regions, indent)
        elif context == "call":
            return self._rebuild_call(stripped, regions, indent)
        elif context == "assignment":
            return self._rebuild_assignment(stripped, regions, indent)

        return indent + stripped


    def _rebuild_funcdef(self, stripped: str, regions: list, indent: str) -> str:
        """Rebuild a function definition."""
        if not regions:
            return indent + stripped

        region = regions[0]
        items = self._split_items(region["content"])
        rc = "funcdef"

        if not items:
            return indent + stripped

        before = stripped[:region["start"]]
        after = stripped[region["end"] + 1:]
        full_line_len = len(before) + 1 + len(", ".join(items)) + 1 + len(after)

        if not self._should_expand(items, region, rc, indent, full_line_len=full_line_len):
            flat = self._format_items_flat(items, region, stripped)
            return indent + flat

        return self._expand_region_in_context(
            stripped, region, items, indent, rc
        )


    def _rebuild_decorator(self, stripped: str, regions: list, indent: str) -> str:
        """Rebuild a decorator."""
        if not regions:
            return indent + stripped

        region = regions[0]
        items = self._split_items(region["content"])
        rc = "decorator"

        if not items:
            return indent + stripped

        before = stripped[:region["start"]]
        after = stripped[region["end"] + 1:]
        full_line_len = len(before) + 1 + len(", ".join(items)) + 1 + len(after)

        if not self._should_expand(items, region, rc, indent, full_line_len=full_line_len):
            flat = self._format_items_flat(items, region, stripped)
            return indent + flat

        return self._expand_region_in_context(
            stripped, region, items, indent, rc
        )


    def _rebuild_call(self, stripped: str, regions: list, indent: str) -> str:
        """Rebuild a function call."""
        if not regions:
            return indent + stripped

        last_call_region = None
        for region in regions:
            rc = self._region_context(region, stripped)
            if rc != "subscript":
                last_call_region = region
                break

        if last_call_region is None:
            region = regions[0]
            items = self._split_items(region["content"])
            formatted_items = []
            for item in items:
                formatted_items.append(self._format_item(item, indent, "subscript"))
            flat = self._format_items_flat(formatted_items, region, stripped)
            return indent + flat

        region = last_call_region
        items = self._split_items(region["content"])
        rc = self._region_context(region, stripped)

        if not items:
            return indent + stripped

        before = stripped[:region["start"]]
        after = stripped[region["end"] + 1:]
        full_line_len = len(before) + 1 + len(", ".join(items)) + 1 + len(after)

        if not self._should_expand(items, region, rc, indent, full_line_len=full_line_len):
            flat = self._format_items_flat(items, region, stripped)
            return indent + flat

        return self._expand_region_in_context(
            stripped, region, items, indent, rc
        )


    def _rebuild_assignment(self, stripped: str, regions: list, indent: str) -> str:
        """Rebuild an assignment with paired punctuation value."""
        if not regions:
            return indent + stripped

        region = regions[0]
        items = self._split_items(region["content"])
        rc = self._region_context(region, stripped)

        if not items:
            return indent + stripped

        if not self._should_expand(items, region, rc, indent):
            flat = self._format_items_flat(items, region, stripped)
            return indent + flat

        return self._expand_region_in_context(
            stripped, region, items, indent, rc
        )


    def _format_items_flat(self, items: List[str], region: dict, stripped: str) -> str:
        """Format items as a flat single line."""
        before = stripped[:region["start"]]
        after = stripped[region["end"] + 1:]
        inner = ", ".join(items)

        if (
            region["open_char"] == "("
            and len(items) == 1
            and self._region_context(region, stripped) == "tuple"
        ):
            inner += ","

        return f"{before}{region['open_char']}{inner}{region['close_char']}{after}"


    def _expand_region_in_context(
        self,
        stripped: str,
        region: dict,
        items: List[str],
        indent: str,
        region_context: str
    ) -> str:
        """Expand a region with proper indentation."""
        before = stripped[:region["start"]]
        after = stripped[region["end"] + 1:]
        inner_indent = indent + "    "

        lines = [f"{indent}{before}{region['open_char']}"]

        for i, item in enumerate(items):
            formatted_item = self._format_item(item, inner_indent, region_context)
            trailing = "," if i < len(items) - 1 else ""
            lines.append(f"{inner_indent}{formatted_item}{trailing}")

        lines.append(f"{indent}{region['close_char']}{after}")

        return "\n".join(lines)


    def _format_item(self, item: str, indent: str, parent_context: str) -> str:
        """Format a single item, potentially expanding its inner regions."""
        regions = self._find_top_regions(item)

        if not regions:
            return item

        result = item
        offset = 0

        any_expanded = False
        expansion_decisions = []
        is_nested = parent_context in ("dict", "list", "set", "tuple")

        for region in regions:
            if region["open_char"] == "(" and self._is_string_concat_content(region["content"]):
                expansion_decisions.append("string_concat")
                any_expanded = True
                continue

            if region["open_char"] == "(" and self._is_logic_subgroup(
                item[region["start"]:region["end"] + 1]
            ):
                expansion_decisions.append("logic_subgroup")
                any_expanded = True
                continue

            inner_items = self._split_items(region["content"])
            rc = self._region_context(region, item)
            should_exp = self._should_expand(
                inner_items, region, rc, indent, is_nested=is_nested
            )
            expansion_decisions.append(should_exp)
            if should_exp:
                any_expanded = True

        if any_expanded:
            for i, region in enumerate(regions):
                if expansion_decisions[i] == "string_concat":
                    strings = self._extract_string_literals(region["content"])
                    inner_indent = indent + "    "
                    parts = [f"{region['open_char']}"]
                    for s in strings:
                        parts.append(f"\n{inner_indent}{s}")
                    parts.append(f"\n{indent}{region['close_char']}")
                    expanded = "".join(parts)
                    start = region["start"] + offset
                    end = region["end"] + offset + 1
                    result = result[:start] + expanded + result[end:]
                    offset += len(expanded) - (region["end"] - region["start"] + 1)
                    continue

                if expansion_decisions[i] == "logic_subgroup":
                    subgroup_text = item[region["start"]:region["end"] + 1]
                    expanded = self._expand_logic_subgroup(subgroup_text, indent)
                    start = region["start"] + offset
                    end = region["end"] + offset + 1
                    result = result[:start] + expanded + result[end:]
                    offset += len(expanded) - (region["end"] - region["start"] + 1)
                    continue

                inner_items = self._split_items(region["content"])
                rc = self._region_context(region, item)

                if not inner_items:
                    continue

                if expansion_decisions[i] or (any_expanded and inner_items and rc != "subscript"):
                    expanded = self._expand_inner(
                        inner_items, region, indent, rc
                    )
                    start = region["start"] + offset
                    end = region["end"] + offset + 1
                    result = result[:start] + expanded + result[end:]
                    offset += len(expanded) - (region["end"] - region["start"] + 1)

        return result


    def _expand_inner(
        self,
        items: List[str],
        region: dict,
        indent: str,
        region_context: str
    ) -> str:
        """Expand an inner region."""
        inner_indent = indent + "    "
        lines = [region["open_char"]]

        for i, item in enumerate(items):
            formatted = self._format_item(item, inner_indent, region_context)
            trailing = "," if i < len(items) - 1 else ""
            lines.append(f"{inner_indent}{formatted}{trailing}")

        lines.append(f"{indent}{region['close_char']}")

        return "\n".join(lines)
