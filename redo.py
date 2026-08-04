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

    return False