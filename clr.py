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
                            BlankLineFormatter(
                                num_blank_lines=0,
                                message="No blank lines between function definition and first line of body."
                            )
                        ]
                    }
                ]
            }
        ]
    }
)