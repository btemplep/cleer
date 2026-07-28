
import ast

from cleer.validators.validator import Validator


class PythonSyntaxValidator(Validator):
    """Python syntax validator.
    """


    def validate(self, document:str) -> str | None:
        try:
            ast.parse(document)
        except SyntaxError as exc:
            return f"Python document has invalid syntax: {exc}"

        return None