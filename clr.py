from cleer import Cleer, cleer_default_config


clr = Cleer(
    config=cleer_default_config(
        python_packages=["cleer"],
        python_internal_packages=["my_package"],
        python_excludes=["**/tests/unit/fixtures/format_*.py"]
    )
)

from cleer import *

# clr = Cleer(
#     config={
#         "groups": [
            
#             {
#                 "includes": [
#                     "**/*.py"
#                 ],
#                 "excludes": [],
#                 "validators": [
#                     PythonSyntaxValidator()
#                 ],
#                 "stages": [
#                     {
#                         "tokenizer": PythonChainBoundaryTokenizer(),
#                         "formatters": [
#                             BlankLineFormatter(
#                                 num_blank_lines=0,
#                                 message="No blank lines between chain connectors."
#                             )
#                         ]
#                     },
#                     {
#                         "tokenizer": PythonChainBoundaryTokenizer(after_return=True),
#                         "formatters": [
#                             BlankLineFormatter(
#                                 num_blank_lines=1,
#                                 message="Expected 1 blank line after return/yield before chain connector."
#                             )
#                         ]
#                     },
#                     {
#                         "tokenizer": PythonCompoundEndTokenizer(),
#                         "formatters": [
#                             BlankLineFormatter(
#                                 num_blank_lines=1,
#                                 message="Expected at least 1 blank line after compound statement."
#                             )
#                         ]
#                     },
#                     {
#                         "tokenizer": PythonBlockStartTokenizer(),
#                         "formatters": [
#                             BlankLineFormatter(
#                                 num_blank_lines=0,
#                                 message="No blank lines between function definition and first line of body."
#                             )
#                         ]
#                     }
#                 ]
#             }
#         ]
#     }
# )