"""Cleer types module."""

__all__ = [
    "CleerConfig",
    "Excluded",
    "Formatting",
    "FormattingDocument",
    "Group",
    "Included",
    "Inspection",
    "Invalidation",
    "Stage",
    "Violation"
]

import pathlib
from typing import TypedDict

from cleer.formatters.formatter import Formatter
from cleer.tokenizers.tokenizer import Tokenizer
from cleer.validators.validator import Validator


class Stage(TypedDict):
    """Configuration for a cleer formatting stage.

    Attributes
    ----------
    tokenizer : cleer.tokenizer.Tokenizer
        Tokenizer subclass instance for this formatting stage.
    formatters : list[Formatter]
        List of formatters to run for each token in this formatting stage.
        Formatters are run sequentially in the order provided.
    """
    tokenizer: Tokenizer
    formatters: list[Formatter]


class Group(TypedDict):
    """A group in the cleer config filters files by a set of glob patterns, and runs a list of stages on them.

    Attributes
    ----------
    includes : list[str]
        Unix glob patterns used to include files for this Group.
    excludes : list[str]
        Unix glob patterns used to exclude files from this Group.
    validators : list[Validator]
        List of validators to run for each document.
        Documents that fail validation, will not be inspected or formatted.
    stages : list[Stage]
        List of formatting stages to use for this group of files.
    """
    includes: list[str]
    excludes: list[str]
    validators: list[Validator]
    stages: list[Stage]


class CleerConfig(TypedDict):
    """Formatting configuration for an instance of a cleer class.

    Attributes
    ----------
    groups : list[Group]
        List of groups that will be evaluated for glob matches.
    """
    groups: list[Group]


class Invalidation(TypedDict):
    validator: int
    message: str


class Included(TypedDict):
    group: int
    pattern: str
    invalidation: Invalidation | None


class Excluded(TypedDict):
    """Response element for files matching group globs.

    Parameters
    ----------
    group : int
        Config group index that was matched.
    pattern : str
        The pattern that was matched in the config group.
    """
    group: int
    pattern: str


class Violation(TypedDict):
    """Formatting violation data.

    Attributes
    ----------
    start_index : str
        Start index of the token in violation.
    length : str
        Length of token in violation
    group : int
        Config group index.
    stage : int
        Config stage index.
    formatter : int
        Config formatter index.
    message : str
        Message describing the violation.
    """
    start_index: str
    length: str
    group: int
    stage: int
    formatter: int
    message: str


class Inspection(TypedDict):
    """Inspection for a file.

    Attributes
    ----------
    path : pathlib.Path
        Path to the file.
    included : list[Included]
        Config groups the file was included in.
    excluded : list[Excluded]
        Config groups the file was explicitly excluded from..
    invalidations : list[Invalidation]
        Any times the file was found to be invalid for a group.
    violations : list[Violation]
        List of violations for the file
    """
    path: pathlib.Path
    included: list[Included]
    excluded: list[Excluded]
    invalidations: list[Invalidation]
    violations: list[Violation]


class Formatting(TypedDict):
    """Formatting results for a file.

    Parameters
    ----------
    path : pathlib.Path
        Path to the file.
    included : list[GroupMatch]
        Config groups the file was included in.
    excluded : list[GroupMatch]
        Config groups the file was explicitly excluded from.
    invalidations : list[Invalidation]
        Any times the file was found to be invalid for a group.
    """
    path: pathlib.Path
    included: list[Included]
    excluded: list[Excluded]
    invalidations: list[Invalidation]


class FormattingDocument(Formatting):
    """Result of formatting a file string, with the formatted string.

    Parameters
    ----------
    path : pathlib.Path
        Path to the file.
    included : list[GroupMatch]
        Config groups the file was included in.
    excluded : list[GroupMatch]
        Config groups the file was explicitly excluded from.
    invalidations : list[Invalidation]
        Any times the file was found to be invalid for a group.
    document : str
        Formatted Document
    """
    document: str | None
