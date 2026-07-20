"""Class init docstring formatter module."""

__all__ = ["PyClassInitDocstringFormatter"]


import re

from cleer.formatters.formatter import Formatter


class PyClassInitDocstringFormatter(Formatter):
    """Ensures __init__ methods do not have docstrings.

    Class `__init__` methods should not have docstrings; documentation
    should be at the class level docstring instead.

    Accepts token types: `class`

    Examples
    --------

    ```python
    from cleer import PyClassInitDocstringFormatter

    formatter = PyClassInitDocstringFormatter()
    message = formatter.inspect(
        'class Foo:\\n    def __init__(self):\\n        \"\"\"Init.\"\"\"\\n        pass\\n'
    )
    ```
    """
    accepts_token_types = ["class"]

    INIT_DOCSTRING_PATTERN = re.compile(
        r"([ \t]*def __init__\([^)]*\)[^:]*:\s*\n)"
        r"([ \t]*(?:\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\')[ \t]*\n?)",
        re.MULTILINE
    )


    def inspect(self, token: str) -> str | None:
        """Inspect a class token for __init__ docstrings.

        Parameters
        ----------
        token : str
            String token to inspect (whole class).

        Examples
        --------

        ```python
        formatter = PyClassInitDocstringFormatter()
        message = formatter.inspect(
            'class Foo:\\n    def __init__(self):\\n        \"\"\"Init.\"\"\"\\n        pass\\n'
        )
        ```

        Returns
        -------
        str | None
            Error message if __init__ has a docstring, `None` otherwise.
        """
        if self.INIT_DOCSTRING_PATTERN.search(token):
            return "__init__ should not have a docstring. Docstrings should be at the class level."

        return None


    def format(self, token: str) -> str:
        """Remove docstrings from __init__ methods.

        Parameters
        ----------
        token : str
            Token to format (whole class).

        Examples
        --------

        ```python
        formatter = PyClassInitDocstringFormatter()
        result = formatter.format(
            'class Foo:\\n    def __init__(self):\\n        \"\"\"Init.\"\"\"\\n        pass\\n'
        )
        ```

        Returns
        -------
        str
            Token with __init__ docstrings removed.
        """
        return self.INIT_DOCSTRING_PATTERN.sub(r"\1", token)
