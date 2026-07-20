"""Decorator space formatter module."""

__all__ = ["PyDecoratorSpaceFormatter"]


from cleer.formatters.formatter import Formatter


class PyDecoratorSpaceFormatter(Formatter):
    """Removes all extra newlines between decorators.

    Decorators should be stacked with only a single newline between them
    (no blank lines).

    Accepts token types: `decorator_space`

    Examples
    --------

    ```python
    from cleer import PyDecoratorSpaceFormatter

    formatter = PyDecoratorSpaceFormatter()
    result = formatter.format("\\n\\n")
    ```
    """
    accepts_token_types = ["decorator_space"]


    def inspect(self, token: str) -> str | None:
        """Inspect whitespace between decorators.

        Parameters
        ----------
        token : str
            String token to inspect (whitespace between decorators).

        Examples
        --------

        ```python
        formatter = PyDecoratorSpaceFormatter()
        message = formatter.inspect("\\n\\n")
        ```

        Returns
        -------
        str | None
            Error message if extra newlines found, `None` otherwise.
        """
        if token != "\n":
            return "Decorators should not have blank lines between them."

        return None


    def format(self, token: str) -> str:
        """Remove extra newlines between decorators.

        Parameters
        ----------
        token : str
            Token to format (whitespace between decorators).

        Examples
        --------

        ```python
        formatter = PyDecoratorSpaceFormatter()
        result = formatter.format("\\n\\n")
        ```

        Returns
        -------
        str
            A single newline character.
        """
        return "\n"
