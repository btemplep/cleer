"""Import separator formatter module."""

__all__ = ["PyImportSeparatorFormatter"]


import re

from cleer.formatters.formatter import Formatter


STDLIB_MODULES = {
    "abc",
    "aifc",
    "argparse",
    "array",
    "ast",
    "asynchat",
    "asyncio",
    "asyncore",
    "atexit",
    "audioop",
    "base64",
    "bdb",
    "binascii",
    "binhex",
    "bisect",
    "builtins",
    "bz2",
    "calendar",
    "cgi",
    "cgitb",
    "chunk",
    "cmath",
    "cmd",
    "code",
    "codecs",
    "codeop",
    "collections",
    "colorsys",
    "compileall",
    "concurrent",
    "configparser",
    "contextlib",
    "contextvars",
    "copy",
    "copyreg",
    "cProfile",
    "crypt",
    "csv",
    "ctypes",
    "curses",
    "dataclasses",
    "datetime",
    "dbm",
    "decimal",
    "difflib",
    "dis",
    "distutils",
    "doctest",
    "email",
    "encodings",
    "enum",
    "errno",
    "faulthandler",
    "fcntl",
    "filecmp",
    "fileinput",
    "fnmatch",
    "fractions",
    "ftplib",
    "functools",
    "gc",
    "getopt",
    "getpass",
    "gettext",
    "glob",
    "grp",
    "gzip",
    "hashlib",
    "heapq",
    "hmac",
    "html",
    "http",
    "idlelib",
    "imaplib",
    "imghdr",
    "imp",
    "importlib",
    "inspect",
    "io",
    "ipaddress",
    "itertools",
    "json",
    "keyword",
    "lib2to3",
    "linecache",
    "locale",
    "logging",
    "lzma",
    "mailbox",
    "mailcap",
    "marshal",
    "math",
    "mimetypes",
    "mmap",
    "modulefinder",
    "multiprocessing",
    "netrc",
    "nis",
    "nntplib",
    "numbers",
    "operator",
    "optparse",
    "os",
    "ossaudiodev",
    "pathlib",
    "pdb",
    "pickle",
    "pickletools",
    "pipes",
    "pkgutil",
    "platform",
    "plistlib",
    "poplib",
    "posix",
    "posixpath",
    "pprint",
    "profile",
    "pstats",
    "pty",
    "pwd",
    "py_compile",
    "pyclbr",
    "pydoc",
    "queue",
    "quopri",
    "random",
    "re",
    "readline",
    "reprlib",
    "resource",
    "rlcompleter",
    "runpy",
    "sched",
    "secrets",
    "select",
    "selectors",
    "shelve",
    "shlex",
    "shutil",
    "signal",
    "site",
    "smtpd",
    "smtplib",
    "sndhdr",
    "socket",
    "socketserver",
    "spwd",
    "sqlite3",
    "sre_compile",
    "sre_constants",
    "sre_parse",
    "ssl",
    "stat",
    "statistics",
    "string",
    "stringprep",
    "struct",
    "subprocess",
    "sunau",
    "symtable",
    "sys",
    "sysconfig",
    "syslog",
    "tabnanny",
    "tarfile",
    "telnetlib",
    "tempfile",
    "termios",
    "test",
    "textwrap",
    "threading",
    "time",
    "timeit",
    "tkinter",
    "token",
    "tokenize",
    "tomllib",
    "trace",
    "traceback",
    "tracemalloc",
    "tty",
    "turtle",
    "turtledemo",
    "types",
    "typing",
    "unicodedata",
    "unittest",
    "urllib",
    "uu",
    "uuid",
    "venv",
    "warnings",
    "wave",
    "weakref",
    "webbrowser",
    "winreg",
    "winsound",
    "wsgiref",
    "xdrlib",
    "xml",
    "xmlrpc",
    "zipapp",
    "zipfile",
    "zipimport",
    "zlib",
    "zoneinfo",
    "_thread",
    "__future__",
    "typing_extensions"
}


class PyImportSeparatorFormatter(Formatter):
    """Separates imports into up to 4 blocks with newlines between them.

    Import blocks:
    1. Standard library imports
    2. Third-party imports
    3. Internal package imports (configurable)
    4. Current package imports (relative imports or same package)

    Ensures 2 newlines after the end of the entire import section.

    Accepts token types: `import_section`

    Parameters
    ----------
    internal_packages : list[str] | None, default=[]
        List of internal package names for the third block.
    current_packages : list[str] | None, default=[]
        List of current package names for the fourth block. Imports matching
        these packages are grouped with relative imports.

    Examples
    --------

    ```python
    from cleer import PyImportSeparatorFormatter

    formatter = PyImportSeparatorFormatter(
        internal_packages=["my_internal_lib"],
        current_packages=["my_project"]
    )
    result = formatter.format("import os\\nimport requests\\n")
    ```
    """
    accepts_token_types = ["import_section"]


    def __init__(
        self,
        internal_packages: list[str] | None=None,
        current_packages: list[str] | None=None
    ) -> None:
        self._internal_packages: set[str] = set(internal_packages or [])
        self._current_packages: set[str] = set(current_packages or [])


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


    def _is_relative_import(self, import_line: str) -> bool:
        """Check if an import is a relative import."""
        stripped = import_line.strip()

        return stripped.startswith("from .")


    def _get_full_import_statement(
        self,
        lines: list[str],
        start_idx: int
    ) -> tuple[str, int]:
        """Get a full import statement that may span multiple lines."""
        statement_lines = [lines[start_idx]]
        i = start_idx

        if "(" in lines[start_idx] and ")" not in lines[start_idx]:
            i += 1
            while i < len(lines):
                statement_lines.append(lines[i])
                if ")" in lines[i]:
                    break

                i += 1

        elif lines[start_idx].rstrip().endswith("\\"):
            i += 1
            while i < len(lines):
                statement_lines.append(lines[i])
                if not lines[i].rstrip().endswith("\\"):
                    break

                i += 1

        return "\n".join(statement_lines), i


    def _classify_import(self, import_line: str) -> int:
        """Classify an import into one of the 4 blocks."""
        if self._is_relative_import(import_line):
            return 3

        module_name = self._get_module_name(import_line)

        if module_name in STDLIB_MODULES:
            return 0

        if module_name in self._internal_packages:
            return 2

        if module_name in self._current_packages:
            return 3

        return 1


    def _parse_import_statements(self, token: str) -> list[str]:
        """Parse import statements from the token."""
        lines = token.split("\n")
        statements = []
        i = 0

        while i < len(lines):
            stripped = lines[i].strip()
            if (
                stripped.startswith("import ")
                or stripped.startswith("from ")
            ):
                statement, end_idx = self._get_full_import_statement(
                    lines,
                    i
                )
                statements.append(statement)
                i = end_idx + 1
            else:
                i += 1

        return statements


    def inspect(self, token: str) -> str | None:
        """Inspect a token for import separation issues.

        Parameters
        ----------
        token : str
            String token to inspect (import section).

        Examples
        --------

        ```python
        formatter = PyImportSeparatorFormatter()
        message = formatter.inspect("import os\\nimport requests\\n")
        ```

        Returns
        -------
        str | None
            Error message if imports are not properly separated, `None` otherwise.
        """
        formatted = self.format(token)
        if formatted != token:
            return "Imports should be separated into 4 blocks in this order: Standard Libraries, 3rd party libraries, internal libraries, and the current package."

        return None


    def format(self, token: str) -> str:
        """Separate imports into blocks.

        Parameters
        ----------
        token : str
            Token to format (import section).

        Examples
        --------

        ```python
        formatter = PyImportSeparatorFormatter()
        result = formatter.format("import os\\nimport requests\\nfrom . import thing\\n")
        ```

        Returns
        -------
        str
            Token with imports separated into proper blocks with newlines between.
        """
        statements = self._parse_import_statements(token)

        if not statements:
            return token

        blocks: list[list[str]] = [[], [], [], []]

        for statement in statements:
            first_line = statement.split("\n")[0]
            block_idx = self._classify_import(first_line)
            blocks[block_idx].append(statement)

        result_parts = []
        for block in blocks:
            if block:
                result_parts.append("\n".join(block))

        result = "\n\n".join(result_parts)
        if not result.endswith("\n"):
            result += "\n"

        return result
