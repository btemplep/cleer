from this.is_a_really_long.long_long.lots_of_lengthy_words_are_here import a_really_long_here_toooooo
def _keep_result(self,result: Inspection | Formatting | FormattingDocument,
    keep_only_excluded: bool,
    keep_not_included: bool
) -> bool:
    inspection['excluded'].append( {"group": gi,"pattern": exclude_pattern})
    if (
        len(result['included']) > 0 or(
            len(result['excluded']) > 0 and keep_only_excluded is True
        ) or keep_not_included is True
    ):
        print(("this is my string literal"
                "this is my string literal 2"
            )
        )
        return True
    elif (
        len(result['included']) > 0 or
        ( len(result['excluded']) > 0 and keep_only_excluded is True ) or
        keep_not_included is True or
        my_function_call(here, there="now", over="here") or my_other_call({"hello": "there"}) or
        last_call("here", 2, 3) or thing not in [0, 1, 2, 3] or ((1==2 or True)and(this=="that" or that =="this"))
    ):
        return True

    return False


def _format_one(
    self,
    file_path: str | pathlib.Path,
    document: str | None
) -> FormattingDocument:
    formatting: FormattingDocument = {"path": file_path,
        "included": [

        ],
        "excluded": [],
        "invalidations": [],
        "document": document
    }
