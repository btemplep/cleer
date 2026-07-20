"""Cleer types module."""

__all__ = [
    "CleerStage",
    "CleerGroup",
    "CleerConfig",
    "TokenResult",
    "Violation",
    "FileInspectionResult"
]


import pathlib
from typing import List, TypedDict

from cleer.formatters.formatter import Formatter
from cleer.tokenizers.tokenizer import Tokenizer


class CleerStage(TypedDict):
    """Configuration for a cleer formatting stage.

    Attributes
    ----------
    tokenizer : cleer.tokenizer.Tokenizer
        Tokenizer subclass instance for this formatting stage.
    formatters : List[Formatter]
        List of formatters to run for each token in this formatting stage.
        Formatters are run sequentially in the order provided.
    """
    tokenizer: Tokenizer
    formatters: List[Formatter]


class CleerGroup(TypedDict):
    """A group in the cleer config filters files by a set of glob patterns, and runs a list of stages on them.

    Attributes
    ----------
    includes : List[str]
        Unix glob patterns used to include files for this Group.
    excludes : List[str]
        Unix glob patterns used to exclude files from this Group.
    stages : List[CleerStage]
        List of formatting stages to use for this group of files.
    """
    includes: List[str]
    excludes: List[str]
    stages: List[CleerStage]


class CleerConfig(TypedDict):
    """Formatting configuration for an instance of a cleer class.

    Attributes
    ----------
    groups : List[CleerGroup]
        List of groups that will be evaluated for glob matches.
    """
    groups: List[CleerGroup]


class TokenResult(TypedDict):
    """Token and location from a tokenizer.

    Attributes
    ----------
    token : str
        Token from a tokenizer.
    index : int
        Index where the token starts in the source document string, inclusive.
    length : int
        Character length of the token.
    """
    token: str
    index: int
    length: int


class Violation(TypedDict):
    """Formatting violation data.

    Attributes
    ----------
    start_index : str
        Start index of the token in violation.
    length : str
        Length of token in violation
    message : str
        Message describing the violation.
    """
    start_index: str
    length: str
    message: str


class FileInspectionResult(TypedDict):
    """Violations for a file.

    Attributes
    ----------
    path : pathlib.Path
        Path to the file.
    violations : List[Violation]
        List of violations for the file.
    """
    path: pathlib.Path
    violations: List[Violation]
