"""See [](#cleer.formatters.json_formatter.JSONFormatter)"""

__all__ = [
    "JSONFormatter"
]

import json

from cleer.formatters.formatter import Formatter, FormatterViolation


class JSONFormatter(Formatter):
    accepts_token_types: list[str] = ["file"]


    def __init__(self, indent: int=4):
        self._indent = indent


    def inspect(self, token: str) -> list[FormatterViolation]:
        if (
            token
            != json.dumps(json.loads(token), indent=self._indent)
        ):
            return [
                {
                    "start_index": 0,
                    "length": len(token),
                    "message": f"JSON should be formatted with {self._indent}-space indentation."
                }
            ]

        return []


    def format(self, token: str) -> str:
        return json.dumps(json.loads(token), indent=self._indent)
