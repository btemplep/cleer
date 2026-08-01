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
                "excludes": [],
                "validators": [
                    PythonSyntaxValidator()
                ],
                "stages": [
                    {
                        "tokenizer": PythonFunctionStartTokenizer(),
                        "formatters": [
                            PythonFunctionStartFormatter()
                        ]
                    },
                ]
            }
        ]
    }
)