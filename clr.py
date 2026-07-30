from cleer import Cleer, cleer_default_config



clr = Cleer(
    config=cleer_default_config(
        python_packages=["cleer"],
        python_internal_packages=None,
        python_excludes=["**/tests/unit/fixtures/format_*.py"]
    )
)

from cleer import *

clr = Cleer(
    config={
        "groups": [
            {
                "includes": [
                    "**/*.py"
                ],
                "excludes": [
                    # "thing.py"
                    "**/venv*/**",
                    ".nox/**"
                ],
                "validators": [
                    PythonSyntaxValidator()
                ],
                "stages": [
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
                    }
                ]
            }
        ]
    }
)