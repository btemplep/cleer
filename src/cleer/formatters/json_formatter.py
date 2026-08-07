""""""

__all__ = [
    "JSONFormatter"
]

import json

from cleer.formatters.formatter import Formatter


class JSONFormatter(Formatter):
    accepts_token_types: list[str] = ["file"]


    def __init__(self, indent: int=4):
        self._indent = indent


    def inspect(self, token: str) -> str | None:
        if token != json.dumps(json.loads(token), indent=self._indent):
            return "JSON must be properly formatted."

        return None


    def format(self, token: str) -> str:
        return json.dumps(json.loads(token), indent=self._indent)
