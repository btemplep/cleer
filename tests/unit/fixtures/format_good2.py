"""Class init docstring formatter module."""

__all__ = ["PyClassInitDocstringFormatter"]


import re

from cleer.formatters.formatter import Formatter


thing = (2,)


class PyClassInitDocstringFormatter(Formatter):
    """Ensures __init__ methods do not have docstrings.

    Class `__init__` methods should not have docstrings; documentation
    should be at the class level docstring instead.

    Accepts token types: ``class``

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
    init_docstring_pattern = re.compile(
        (
            r"([ \t]*def __init__\([^)]*\)[^:]*:\s*\n)"
            r"([ \t]*(?:\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\')[ \t]*\n?)"
        ),
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
        if self.init_docstring_pattern.search(token):
            return "__init__ should not have a docstring; document at the class level instead."

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
        return self.init_docstring_pattern.sub(r"\1", token)
