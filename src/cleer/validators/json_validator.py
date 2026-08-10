"""See :class:`JSONValidator`."""

__all__ = [
    "JSONValidator"
]

import json


class JSONValidator:


    def validate(self, document: str) -> str | None:
        try:
            json.loads(document)
        except Exception as exc:
            return f"Failed to parse JSON. [{type(exc).__name__}]: {exc}"

        return None
