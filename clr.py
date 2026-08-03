from cleer import Cleer, cleer_default_config


clr = Cleer(
    config=cleer_default_config(
        python_packages=["cleer"],
        python_internal_packages=["my_package"],
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
                        "tokenizer": FileTokenizer(),
                        "formatters": [
                            PythonModuleDocstringPresenceFormatter(),
                            PythonAllPresenceFormatter()
                        ]
                    },
                    {
                        "tokenizer": PythonImportTokenizer(),
                        "formatters": [
                            PythonImportFormatter(
                                internal_packages=[],
                                current_packages=["cleer"]
                            )
                        ]
                    },
                    {
                        "tokenizer": FileTokenizer(),
                        "formatters": [
                            PythonModuleHeaderFormatter()
                        ]
                    },
                ]
            }
        ]
    }
)