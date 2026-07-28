__all__ = [
    "cleer_default_config"
]


from typing import List

from loguru import logger

from cleer.cleer import Cleer
from cleer.formatters import * 
from cleer.tokenizers import * 
from cleer.validators import *
from cleer.types import * 


def cleer_default_config(
    python_packages: List[str] | None=None,
    python_internal_packages: List[str] | None=None,
    python_excludes: List[str] | None=None
) -> CleerConfig:
    """Generate a new instance of cleer with the default configs.

    Parameters
    ----------
    python_packages : List[str] | None, default=["src/**/*.py"]
        List of package names for this project/repo/dir.
        Used to classify imports as "current package" and to determine
        which directories should enforce ``__all__``. A separate group
        is created that only targets files under ``src/`` or directories
        matching the package names.
    python_internal_packages : List[str] | None, optional
        Identity the list of internal packages for import formatting.
        Internal packages are those that are hosted on private
        repositories, not including current packages.
    python_excludes : List[str] | None, default=["**/venv*/**", "**/.venv*/**"]
        File patterns to exclude from formatting python files.

    Returns
    -------
    Cleer
        Instance with default configs.
    """
    if python_packages is None:
        python_packages = []

    python_packages.append("src/**/*.py")

    if python_internal_packages is None:
        python_internal_packages = []

    if python_excludes is None:
        python_excludes = []

    python_excludes += ["**/.venv*/**", "**/venv*/**"]
    logger.debug(
        f"Python Packages: {python_packages}\n"
        f"Internal Python Packages: {python_internal_packages}\n"
        f"Python Excludes: {python_excludes}"
    )

    
    return {
        "groups": [
            # {
            #     "includes": package_includes,
            #     "excludes": python_excludes,
            #     "stages": [
            #         {
            #             "tokenizer": FileTokenizer(),
            #             "formatters": [PyAllModuleFormatter()]
            #         }
            #     ]
            # },
            {
                "includes": ["**/*.py"],
                "excludes": python_excludes,
                "validators": [
                    PythonSyntaxValidator()
                ],
                "stages": [
                    {
                        "tokenizer": NonAsciiWhitespaceTokenizer(),
                        "formatters": [
                            NonAsciiWhitespaceFormatter()
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
                    },
                    {
                        "tokenizer": PythonFunctionBoundaryTokenizer(),
                        "formatters": [
                            PythonFunctionBoundaryFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonDecoratorBoundaryTokenizer(),
                        "formatters": [
                            PythonDecoratorBoundaryFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonNestedFunctionBoundaryTokenizer(),
                        "formatters": [
                            PythonNestedFunctionBoundaryFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonInnerMaxBlankLinesTokenizer(),
                        "formatters": [
                            PythonInnerMaxBlankLinesFormatter()
                        ]
                    }
                ]
            }
        ]
    }
