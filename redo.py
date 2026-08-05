"""TODO: Add module docstring."""

from this.is_a_really_long.long_long.lots_of_lengthy_words_are_here import a_really_long_here_toooooo


def _keep_result(
    self,
    result: Inspection | Formatting | FormattingDocument,
    keep_only_excluded: bool,
    keep_not_included: bool
) -> bool:
    inspection['excluded'].append(
        {
            "group": gi,
            "pattern": exclude_pattern
        }
    )
    if (
        len(result['included']) > 0
        or (
            len(result['excluded']) > 0
            and keep_only_excluded is True
        )
        or keep_not_included is True
    ):
        print(
            (
                "this is my string literal"
                "this is my string literal 2"
            )
        )

        return True

    elif (
        len(result['included']) > 0
        or (
            len(result['excluded']) > 0
            and keep_only_excluded is True
        )
        or keep_not_included is True
        or my_function_call(
            here,
            there="now",
            over="here"
        )
        or my_other_call(
            {
                "hello": "there"
            }
        )
        or last_call("here", 2, 3)
        or thing not in [0, 1, 2, 3]
        or (
            (
                1 == 2
                or True
            )
            and (
                this == "that"
                or that == "this"
            )
        )
    ):
        return True

    return False


def config_default():
    return {
        "groups": [
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
                        "tokenizer": PythonBlockStartTokenizer(),
                        "formatters": [
                            BlankLineFormatter(num_blank_lines=0, message="No blank lines between start of code blocks and first line of body."),
                            thing(
                                hello="there",
                                here="now",
                                you="good"
                            )
                        ]
                    }
                ]
            }
        ]
    }
logger.debug(
    f"Python Packages: {python_packages}\n"
    f"Internal Python Packages: {python_internal_packages}\n"
    f" Excludes: {json.dumps(excludes, indent=4)}"
)