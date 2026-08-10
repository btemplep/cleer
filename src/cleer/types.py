"""Cleer types module."""

__all__ = [
    "CleerConfig",
    "Formatting",
    "FormattingDocument",
    "Group",
    "GroupMatch",
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

    Examples
    --------

    ```python
    {
        "tokenizer": LineTokenizer(),
        "formatters": [
            TrailingWhitespaceFormatter()
        ]
    }
    ```

    Attributes
    ----------
    tokenizer : Tokenizer
        Tokenizer subclass instance for this formatting stage.
    formatters : list[Formatter]
        List of formatters to run for each token in this formatting stage.
        Formatters are run sequentially in the order provided.
    """
    tokenizer: Tokenizer
    formatters: list[Formatter]


class Group(TypedDict):
    """A group filters files by glob patterns and runs a list of stages on them.

    Examples
    --------

    ```python
    {
        "includes": [
            "**/*.py"
        ],
        "excludes": [
            "**/.venv*/**"
        ],
        "validators": [
            PythonSyntaxValidator()
        ],
        "stages": [
            {
                "tokenizer": LineTokenizer(),
                "formatters": [
                    TrailingWhitespaceFormatter()
                ]
            }
        ]
    }
    ```

    Attributes
    ----------
    includes : list[str]
        Unix glob patterns used to include files for this Group.
    excludes : list[str]
        Unix glob patterns used to exclude files from this Group.
    validators : list[Validator]
        List of validators to run for each document.
        Documents that fail validation will not be inspected or formatted.
    stages : list[Stage]
        List of formatting stages to use for this group of files.
    """
    includes: list[str]
    excludes: list[str]
    validators: list[Validator]
    stages: list[Stage]


class CleerConfig(TypedDict):
    """Formatting configuration for an instance of the Cleer class.

    Examples
    --------

    ```python
    {
        "groups": [
            {
                "includes": [
                    "**/*.py"
                ],
                "excludes": [
                    "**/.venv*/**"
                ],
                "validators": [
                    PythonSyntaxValidator()
                ],
                "stages": [
                    {
                        "tokenizer": LineTokenizer(),
                        "formatters": [
                            TrailingWhitespaceFormatter()
                        ]
                    }
                ]
            }
        ]
    }
    ```

    Attributes
    ----------
    groups : list[Group]
        List of groups that will be evaluated for glob matches.
    """
    groups: list[Group]


class Invalidation(TypedDict):
    """Result when a document fails a validator check.

    Examples
    --------

    ```python
    {
        "validator": 0,
        "message": "File is not valid Python."
    }
    ```

    Attributes
    ----------
    validator : int
        Config validator index within the group.
    message : str
        Message describing why the document is invalid.
    """
    validator: int
    message: str


class GroupMatch(TypedDict):
    """Result for a file matching a group glob pattern.

    Examples
    --------

    ```python
    {
        "group": 0,
        "pattern": "**/*.py"
    }
    ```

    Attributes
    ----------
    group : int
        Config group index that was matched.
    pattern : str
        The glob pattern that was matched in the config group.
    """
    group: int
    pattern: str


class Violation(TypedDict):
    """Formatting violation with full context for locating it in the config and document.

    Examples
    --------

    ```python
    {
        "start_index": 49,
        "length": 3,
        "group": 0,
        "stage": 0,
        "formatter": 0,
        "message": "Lines should not have any trailing whitespace."
    }
    ```

    Attributes
    ----------
    start_index : int
        Start index of the violation in the document.
    length : int
        Length of the violating span in the document.
    group : int
        Config group index.
    stage : int
        Config stage index.
    formatter : int
        Config formatter index.
    message : str
        Message describing the violation.
    """
    start_index: int
    length: int
    group: int
    stage: int
    formatter: int
    message: str


class Inspection(TypedDict):
    """Inspection result for a file.

    Examples
    --------

    ```python
    {
        "path": pathlib.Path("/full/path/to/file.py"),
        "included": [
            {
            "group": 0,
            "pattern": "**/*.py"
            }
        ],
        "excluded": [
            {
            "group": 0,
            "pattern": "**/*.py"
            }
        ],
        "invalidations": [
            {
                "validator": 0,
                "message": "File is not valid."
            }
        ],
        "violations": [
            {
                "start_index": 49,
                "length": 3,
                "group": 0,
                "stage": 0,
                "formatter": 0,
                "message": "Lines should not have any trailing whitespace."
            }
        ]
    }
    ```

    Attributes
    ----------
    path : pathlib.Path
        Path to the file.
    included : list[GroupMatch]
        Config groups the file was included in.
    excluded : list[GroupMatch]
        Config groups the file was explicitly excluded from.
    invalidations : list[Invalidation]
        Any times the file was found to be invalid for a group.
    violations : list[Violation]
        List of violations for the file.
    """
    path: pathlib.Path
    included: list[GroupMatch]
    excluded: list[GroupMatch]
    invalidations: list[Invalidation]
    violations: list[Violation]


class Formatting(TypedDict):
    """Formatting result for a file formatted in place.

    Examples
    --------

    ```python
    {
        "path": pathlib.Path("/full/path/to/file.py"),
        "included": [
            {
            "group": 0,
            "pattern": "**/*.py"
            }
        ],
        "excluded": [
            {
            "group": 0,
            "pattern": "**/*.py"
            }
        ],
        "invalidations": [
            {
                "validator": 0,
                "message": "File is not valid."
            }
        ]
    }
    ```

    Attributes
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
    included: list[GroupMatch]
    excluded: list[GroupMatch]
    invalidations: list[Invalidation]


class FormattingDocument(Formatting):
    """Result of formatting a document string, including the formatted output.

    Examples
    --------

    ```python
    {
        {
        "path": pathlib.Path("/full/path/to/file.py"),
        "included": [
            {
            "group": 0,
            "pattern": "**/*.py"
            }
        ],
        "excluded": [
            {
            "group": 0,
            "pattern": "**/*.py"
            }
        ],
        "invalidations": [
            {
                "validator": 0,
                "message": "File is not valid."
            }
        ]
        "document": "x = 1\n"
    }
    ```

    Attributes
    ----------
    path : pathlib.Path
        Path to the file.
    included : list[GroupMatch]
        Config groups the file was included in.
    excluded : list[GroupMatch]
        Config groups the file was explicitly excluded from.
    invalidations : list[Invalidation]
        Any times the file was found to be invalid for a group.
    document : str | None
        Formatted document string. None if the file was not included in any group.
    """
    document: str | None
