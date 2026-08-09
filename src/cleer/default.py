"""TODO: Add module docstring."""

__all__ = [
    "cleer_default_config"
]

import json

from loguru import logger

from cleer.formatters import *
from cleer.tokenizers import *
from cleer.types import *
from cleer.validators import *


def cleer_default_config(
    python_packages: list[str] | None=None,
    python_internal_packages: list[str] | None=None,
    excludes: list[str] | None=None
) -> CleerConfig:
    """Generate a new instance of cleer with the default configs.

    Parameters
    ----------
    python_packages : list[str] | None, optional
        List of package names for this project/repo/dir.
        Used to classify imports as "current package" and to determine
        which directories should enforce `__all__`. File globs are
        derived from names (e.g. `"my_pkg"` becomes
        `"my_pkg/**/*.py"`). `src/**/*.py` is always included.
    python_internal_packages : list[str] | None, optional
        List of internal package names for import formatting.
        Internal packages are those that are hosted on private
        repositories, not including current packages.
    excludes : list[str] | None, default=["**/venv*/**", "**/.venv*/**"]
        File patterns to exclude from formatting files.

    Returns
    -------
    CleerConfig
        Config dict for the `Cleer` class.
    """
    if python_packages is None:
        python_packages = []

    package_includes = [f"{pkg}/**/*.py" for pkg in python_packages]
    package_includes.append("src/**/*.py")

    if python_internal_packages is None:
        python_internal_packages = []

    if excludes is None:
        excludes = []

    excludes += [
        "**/.venv*/**",
        "**/venv*/**"
    ]
    logger.debug(
        (
            f"Python Packages: {python_packages}\n"
            f"Internal Python Packages: {python_internal_packages}\n"
            f" Excludes: {json.dumps(excludes, indent=4)}"
        )
    )

    return {
        "groups": [
            {
                "includes": [
                    "**/*.json"
                ],
                "excludes": excludes,
                "validators": [
                    JSONValidator()
                ],
                "stages": [
                    {
                        "tokenizer": FileTokenizer(),
                        "formatters": [
                            JSONFormatter()
                        ]
                    }
                ]
            },
            {
                "includes": [
                    "**/*.py"
                ],
                "excludes": excludes,
                "validators": [],
                "stages": [
                    {
                        "tokenizer": NonAsciiWhitespaceTokenizer(),
                        "formatters": [
                            NonAsciiWhitespaceFormatter()
                        ]
                    }
                ]
            },
            {
                "includes": package_includes,
                "excludes": excludes,
                "validators": [
                    PythonSyntaxValidator()
                ],
                "stages": [
                    {
                        "tokenizer": FileTokenizer(),
                        "formatters": [
                            PythonAllPresenceFormatter()
                        ]
                    }
                ]
            },
            {
                "includes": [
                    "**/*.py"
                ],
                "excludes": excludes,
                "validators": [
                    PythonSyntaxValidator()
                ],
                "stages": [
                    {
                        "tokenizer": PythonIndentTokenizer(),
                        "formatters": [
                            PythonIndentFormatter()
                        ]
                    },
                    {
                        "tokenizer": FileTokenizer(),
                        "formatters": [
                            PythonPairedPunctuationFormatter(),
                            PythonModuleDocstringPresenceFormatter(),
                            PythonModuleHeaderFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonAllTokenizer(),
                        "formatters": [
                            PythonAllFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonImportTokenizer(),
                        "formatters": [
                            PythonImportFormatter(
                                internal_packages=python_internal_packages,
                                current_packages=python_packages
                            )
                        ]
                    },
                    {
                        "tokenizer": PythonFunctionBoundaryTokenizer(),
                        "formatters": [
                            BlankLineFormatter(
                                num_blank_lines=2,
                                message="Expected 2 blank lines before/after definition."
                            )
                        ]
                    },
                    {
                        "tokenizer": PythonClassBoundaryTokenizer(),
                        "formatters": [
                            PythonClassBoundaryFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonBlockStartTokenizer(),
                        "formatters": [
                            BlankLineFormatter(
                                num_blank_lines=0,
                                message="No blank lines between start of code blocks and first line of body."
                            )
                        ]
                    },
                    {
                        "tokenizer": PythonDecoratorBoundaryTokenizer(),
                        "formatters": [
                            BlankLineFormatter(
                                num_blank_lines=0,
                                message="No blank lines between decorators and definitions."
                            )
                        ]
                    },
                    {
                        "tokenizer": PythonNestedFunctionBoundaryTokenizer(),
                        "formatters": [
                            BlankLineFormatter(
                                num_blank_lines=1,
                                message="Expected 1 blank line before/after nested definition."
                            )
                        ]
                    },
                    {
                        "tokenizer": PythonReturnYieldTokenizer(),
                        "formatters": [
                            PythonReturnYieldFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonCompoundChainTokenizer(),
                        "formatters": [
                            PythonCompoundChainFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonCompoundEndTokenizer(),
                        "formatters": [
                            BlankLineFormatter(
                                num_blank_lines=1,
                                message="Expected at least 1 blank line after compound statement."
                            )
                        ]
                    },
                    {
                        "tokenizer": PythonInnerMaxBlankLinesTokenizer(),
                        "formatters": [
                            BlankLineFormatter(
                                num_blank_lines=1,
                                message="No more than 1 consecutive blank line inside function bodies."
                            )
                        ]
                    },
                    {
                        "tokenizer": PythonStringQuoteTokenizer(),
                        "formatters": [
                            PythonStringQuoteFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonDictKeyQuoteTokenizer(),
                        "formatters": [
                            PythonDictKeyQuoteFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonMaxOneSpaceTokenizer(),
                        "formatters": [
                            PythonMaxOneSpaceFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonBinaryOperatorSpaceTokenizer(),
                        "formatters": [
                            PythonBinaryOperatorSpaceFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonKwargsSpaceTokenizer(),
                        "formatters": [
                            PythonKwargsSpaceFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonUnaryOperatorSpaceTokenizer(),
                        "formatters": [
                            PythonUnaryOperatorSpaceFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonColonSpaceTokenizer(),
                        "formatters": [
                            PythonColonSpaceFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonCommaSpaceTokenizer(),
                        "formatters": [
                            PythonCommaSpaceFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonTrailingCommaTokenizer(),
                        "formatters": [
                            PythonTrailingCommaFormatter()
                        ]
                    },
                    {
                        "tokenizer": TrailingWhitespaceTokenizer(),
                        "formatters": [
                            TrailingWhitespaceFormatter()
                        ]
                    },
                    {
                        "tokenizer": FileStartWhitespaceTokenizer(),
                        "formatters": [
                            FileStartWhitespaceFormatter()
                        ]
                    },
                    {
                        "tokenizer": WhitespaceTokenizer(),
                        "formatters": [
                            MaxBlankLinesFormatter()
                        ]
                    },
                    {
                        "tokenizer": FileEndWhitespaceTokenizer(),
                        "formatters": [
                            FileEndWhitespaceFormatter()
                        ]
                    }
                ]
            }
        ]
    }
