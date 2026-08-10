"""Glob to regex"""

__all__ = [
    "glob_to_regex"
]

from functools import lru_cache
import os
import re


_re_escape = lru_cache(maxsize=512)(re.escape)
_re_setops_sub = re.compile(r"([&~|])").sub


@lru_cache(maxsize=512)
def glob_to_regex(
    pattern: str,
    recursive: bool=True,
    include_hidden: bool=False,
    seps: str | tuple | None=None,
    anchor: bool=True
) -> str:
    """Translate a glob pattern to a regular expression string.

    Supports standard glob wildcards including `**` for recursive directory
    matching.

    Wildcard semantics:
    - `*` matches any characters within a single path segment (no separators).
    - `**` matches zero or more path segments (only when `recursive=True`).
    - `?` matches exactly one non-separator character.
    - `[seq]` matches one character in the bracket expression.
    - `[!seq]` matches one character not in the bracket expression.

    Arguments
    ---------
    pattern : str
        The glob pattern to translate.
    recursive : bool, default=True
        When True, `**` matches any number of path segments including none.
    include_hidden : bool, default=False
        When True, wildcards can match path segments starting with a dot.
    seps : str | tuple | None, default=None
        Path separator characters. Defaults to `os.sep` (and `os.altsep` if
        available).
    anchor : bool, default=True
        When True, the regex is anchored to match the full string. When False,
        returns an unanchored pattern suitable for embedding.

    Examples
    --------

    ```python
    import re

    from cleer.glob_to_regex import glob_to_regex

    regex = glob_to_regex("**/*.py")
    assert re.match(regex, "src/cleer/cleer.py")

    regex = glob_to_regex("src/**")
    assert re.match(regex, "src/foo/bar/baz.txt")

    regex = glob_to_regex("*.txt", recursive=False)
    assert re.match(regex, "notes.txt")
    assert not re.match(regex, "dir/notes.txt")
    ```

    Returns
    -------
    str
        A regular expression string that matches paths conforming to the glob
        pattern.
    """
    if not seps:
        if os.path.altsep:
            seps = (os.path.sep, os.path.altsep)
        else:
            seps = (os.path.sep,)

    elif isinstance(seps, str):
        seps = (seps,)

    escaped_seps = "".join(map(re.escape, seps))
    any_sep = f"[{escaped_seps}]" if len(seps) > 1 else escaped_seps
    not_sep = f"[^{escaped_seps}]"

    if include_hidden:
        one_last_segment = f"{not_sep}+"
        one_segment = f"{one_last_segment}{any_sep}"
        any_segments = f"(?:.+{any_sep})?"
        any_last_segments = ".*"
    else:
        one_last_segment = f"[^{escaped_seps}.]{not_sep}*"
        one_segment = f"{one_last_segment}{any_sep}"
        any_segments = f"(?:{one_segment})*"
        any_last_segments = f"{any_segments}(?:{one_last_segment})?"

    results = []
    parts = re.split(f"[{escaped_seps}]", pattern)
    last_part_idx = len(parts) - 1

    for idx, part in enumerate(parts):
        if part == "*":
            results.append(one_segment if idx < last_part_idx else one_last_segment)
        elif recursive and part == "**":
            if idx < last_part_idx:
                if parts[idx + 1] != "**":
                    results.append(any_segments)

            else:
                results.append(any_last_segments)

        else:
            if part:
                if not include_hidden and part[0] in "*?":
                    results.append(r"(?!\.)")

                results.extend(_translate_segment(part, not_sep))

            if idx < last_part_idx:
                results.append(any_sep)

    res = "".join(results)

    if anchor:
        return f"(?s:{res})\\Z"

    return res


def _translate_segment(pat: str, not_sep: str) -> list:
    res = []
    i, n = 0, len(pat)

    while i < n:
        c = pat[i]
        i += 1

        if c == "*":
            res.append(f"{not_sep}*")
            while i < n and pat[i] == "*":
                i += 1

        elif c == "?":
            res.append(not_sep)
        elif c == "[":
            j = i
            if j < n and pat[j] == "!":
                j += 1

            if j < n and pat[j] == "]":
                j += 1

            while j < n and pat[j] != "]":
                j += 1

            if j >= n:
                res.append("\\[")
            else:
                stuff = pat[i:j]
                if "-" not in stuff:
                    stuff = stuff.replace("\\", r"\\")
                else:
                    chunks = []
                    k = i + 2 if pat[i] == "!" else i + 1

                    while True:
                        k = pat.find("-", k, j)
                        if k < 0:
                            break

                        chunks.append(pat[i:k])
                        i = k + 1
                        k = k + 3

                    chunk = pat[i:j]
                    if chunk:
                        chunks.append(chunk)
                    else:
                        chunks[-1] += "-"

                    for k in range(len(chunks) - 1, 0, -1):
                        if chunks[k - 1][-1] > chunks[k][0]:
                            chunks[k - 1] = chunks[k - 1][:-1] + chunks[k][1:]
                            del chunks[k]

                    stuff = "-".join(s.replace("\\", r"\\").replace("-", r"\-") for s in chunks)

                i = j + 1

                if not stuff:
                    res.append("(?!)")
                else:
                    stuff = _re_setops_sub(r"\\\1", stuff)
                    if stuff[0] == "!":
                        stuff = "^" + stuff[1:]
                    elif stuff[0] in ("^", "["):
                        stuff = "\\" + stuff

                    res.append(f"[{stuff}]")

        else:
            res.append(_re_escape(c))

    return res
