""""""

__all__ = [
    "JSONFormatter"
]

from cleer.formatters.formatter import Formatter


class JSONFormatter(Formatter):
    accepts_token_types: list[str] = []


    def inspect(self, token: str) -> str | None:
        """Inspect a token for a violation.

        Formatters must implement this method.

        Parameters
        ----------
        token : str
            String token to inspect.

        Returns
        -------
        str | None
            Error message. `None` if there is no violation.
        """
        raise NotImplementedError("Formatter classes must implement the inspect method!")


    def format(self, token: str) -> str:
        """Format the given token.

        Formatters must implement this method.

        Parameters
        ----------
        token : str
            Token to format.

        Returns
        -------
        str
            Formatted token.
        """
        raise NotImplementedError("Formatter classes must implement the format method!")

