__all__ = ["cleer_default"]


from typing import List

from loguru import logger

from cleer.cleer import Cleer
from cleer.formatters import * 
from cleer.tokenizers import * 
from cleer.types import * 


def cleer_default(
    current_packages: List[str] | None=None,
    internal_packages: List[str] | None=None
) -> Cleer:
    """Generate a new instance of cleer with the default configs.

    Parameters
    ----------
    current_packages : List[str] | None, optional
        List of package names for this project/repo/dir.
        Used to classify imports as "current package" and to determine
        which directories should enforce ``__all__``. A separate group
        is created that only targets files under ``src/`` or directories
        matching the package names.
    internal_packages : List[str] | None, optional
        Identity the list of internal packages for import formatting.
        Internal packages are those that are hosted on private
        repositories, not including current packages.

    Returns
    -------
    Cleer
        Instance with default configs.
    """
    package_includes = ["src/**/*.py"]
    if current_packages is not None:
        package_includes += current_packages

    logger.debug(f"Package includes: {package_includes}")

    return Cleer(
        config={
            "groups": [
                {
                    "includes": package_includes,
                    "excludes": [
                        "**/.venv*/**",
                        "**/venv*/**"
                    ],
                    "stages": [
                        {
                            "tokenizer": FileTokenizer(),
                            "formatters": [PyAllModuleFormatter()]
                        }
                    ]
                },
                {
                    "includes": ["**/*.py"],
                    "excludes": [
                        "**/.venv*/**",
                        "**/venv*/**"
                    ],
                    "stages": [
                        {
                            "tokenizer": FileStartWhitespaceTokenizer(),
                            "formatters": [FileStartWhitespaceFormatter()]
                        },
                        {
                            "tokenizer": FileTokenizer(),
                            "formatters": [PyAllSpacingFormatter()]
                        },
                        {
                            "tokenizer": LineTokenizer(),
                            "formatters": [TrailingWhitespaceFormatter()]
                        },
                        {
                            "tokenizer": LineTokenizer(),
                            "formatters": [MaxSpaceFormatter()]
                        },
                        {
                            "tokenizer": NonAsciiWhitespaceTokenizer(),
                            "formatters": [ReplaceNonAsciiWhitespaceFormatter()]
                        },
                        {
                            "tokenizer": PyImportSectionTokenizer(),
                            "formatters": [
                                PyImportSeparatorFormatter(
                                    internal_packages=internal_packages,
                                    current_packages=current_packages
                                )
                            ]
                        },
                        {
                            "tokenizer": PyImportBlockTokenizer(),
                            "formatters": [PyImportSortFormatter()]
                        },
                        {
                            "tokenizer": PyImportStatementTokenizer(),
                            "formatters": [
                                PyImportEntrySortFormatter(),
                                PyImportParenthesisFormatter()
                            ]
                        },
                        {
                            "tokenizer": PyImportSectionSpaceTokenizer(),
                            "formatters": [PyImportSectionSpaceFormatter()]
                        },
                        {
                            "tokenizer": PyFunctionSignatureTokenizer(),
                            "formatters": [PySignatureNewLineFormatter()]
                        },
                        {
                            "tokenizer": PyDecoratorTokenizer(),
                            "formatters": [PyDecoratorArgsNewLineFormatter()]
                        },
                        {
                            "tokenizer": PyDecoratorSpaceTokenizer(),
                            "formatters": [PyDecoratorSpaceFormatter()]
                        },
                        {
                            "tokenizer": PyDocstringSpaceTokenizer(),
                            "formatters": [PyDocstringSpaceFormatter()]
                        },
                        {
                            "tokenizer": PyFunctionSpaceTokenizer(),
                            "formatters": [PyFunctionSpaceFormatter()]
                        },
                        {
                            "tokenizer": PyClassWhitespaceTokenizer(),
                            "formatters": [PyClassWhitespaceFormatter()]
                        },
                        {
                            "tokenizer": PyClassVarWhitespaceTokenizer(),
                            "formatters": [PyClassVarWhitespaceFormatter()]
                        },
                        {
                            "tokenizer": FileTokenizer(),
                            "formatters": [PyLogicBlockFormatter()]
                        },
                        {
                            "tokenizer": PyFunctionTokenizer(),
                            "formatters": [
                                PyFunctionInternalNewLinesFormatter(),
                                PyReturnYieldNewLineFormatter(),
                                PyCodeBlockNewLinesFormatter()
                            ]
                        },
                        {
                            "tokenizer": FileTokenizer(),
                            "formatters": [PyCodeBlockNewLinesFormatter()]
                        },
                        {
                            "tokenizer": PyTypeHintSpacingTokenizer(),
                            "formatters": [PyTypeHintSpacingFormatter()]
                        },
                        {
                            "tokenizer": BinaryOperatorTokenizer(),
                            "formatters": [BinaryOperatorSpaceFormatter()]
                        },
                        {
                            "tokenizer": UnaryOperatorTokenizer(),
                            "formatters": [UnaryOperatorSpaceFormatter()]
                        },
                        {
                            "tokenizer": PyFunctionCallKwargsEqualsTokenizer(),
                            "formatters": [NoSpaceEqualsFormatter()]
                        },
                        {
                            "tokenizer": PyFunctionSignatureKwargsEqualsTokenizer(),
                            "formatters": [NoSpaceEqualsFormatter()]
                        },
                        {
                            "tokenizer": CommaTokenizer(),
                            "formatters": [CommaSpaceFormatter()]
                        },
                        {
                            "tokenizer": CommaPlusTokenizer(),
                            "formatters": [TrailingCommaFormatter()]
                        },
                        {
                            "tokenizer": QuotationTokenizer(),
                            "formatters": [QuoteStyleFormatter()]
                        },
                        {
                            "tokenizer": PyDictKeyNotationTokenizer(),
                            "formatters": [QuoteStyleFormatter(style="'")]
                        },
                        {
                            "tokenizer": PairedPunctuationTokenizer(),
                            "formatters": [MultiLineNestedFormatter()]
                        },
                        {
                            "tokenizer": MaxNewlinesTokenizer(),
                            "formatters": [MaxNewlinesFormatter()]
                        },
                        {
                            "tokenizer": FileEndWhitespaceTokenizer(),
                            "formatters": [FileEndWhitespaceFormatter()]
                        }
                    ]
                }
            ]
        }
    )
