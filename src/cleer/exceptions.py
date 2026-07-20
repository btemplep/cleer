"""Cleer Exceptions module."""

__all__ = [
    "CleerError",
    "BadPathError",
    "NotImplementedError"
]


class CleerError(Exception):
    """Base exception for cleer."""
    pass


class NotImplementedError(CleerError):
   """Internal error when a tokenizer or formatter has not implemented a necessary part of the interface."""
   pass


class BadPathError(CleerError):
    """Error when the given path does not match the expected value."""
    pass
