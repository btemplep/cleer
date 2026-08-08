"""TODO: Add module docstring."""

__all__ = [
    "Cleer"
]

import pathlib
import re

from loguru import logger

from cleer import exceptions
from cleer.glob_to_regex import glob_to_regex
from cleer.types import *


class Cleer:
    """Cleer class used for inspecting and formatting files.

    The `config` dict is where all of the formatting configuration originates.
    It contains a hierarchy structure as so:
    - groups - Groups are used to hold lists of formatting settings know as stages.
        - includes - List of glob strings used to include files that this group will accept. Any single match is accepted.
        - excludes - List of glob strings used to exclude files from this group. Any single match excludes the file.
        - stages - A list of steps taken to format files.
            - tokenizer - Takes a file and produces a list of tokens that are passed to the formatters in sequential order
            - formatters - list of formatters that will be used in this stage on each token.


    Arguments
    ---------
    config : CleerConfig
        Configuration for formatting files.

    Examples
    --------
    ``ython
    import pathlib

    from cleer import Cleer, LineTokenizer, TrailingWhitespaceFormatter


    clr = Cleer(
        config={
            "groups": [
                {
                    "includes": [
                        "**/*.py"
                    ],
                    "excludes": [
                        "**/.venv*/**",
                        "**/venv*/**"
                    ],
                    "stages": [
                        {
                            "tokenizer": LineTokenizer(),
                            "formatters": [
                                TrailingWhitespaceFormatter()
                            ]
                        }
                    ]
                }
            ]
        }
    )
    file_path = pathlib.Path("thing.py")
    doc = "thing = 5   "
    # view people friendly list of formatting violations
    violations = clr.inspect_str(doc, file_path) # the file path doesn't actually matter here except for matching the formatting groups
    formatted_doc = clr.format_str(doc, file_path)

    # can also inspect or format file pointers, files, and directories
    with open("thing.py", "r+") as fp:
        clr.format_fp(fp, file_path) # file path only matters for group matching here as well

    clr.format_file(file_path) # file path used for group matching and will read and update file with formatted code.
    clr.format_dir(pathlib.Path("./")) # dir path used with glob matching to list off all matching files for each group
    ```
    """


    def __init__(self, config: CleerConfig):
        self._config = config


    def _get_file_pattern_match(
        self,
        file_path: pathlib.Path,
        patterns: list[str]
    ) -> str | None:
        for pattern in patterns:
            regex = glob_to_regex(
                pattern=pattern,
                recursive=True,
                include_hidden=True
            )
            if re.match(regex, str(file_path)) is not None:
                return pattern

        return None


    def _validate_str_group(
        self,
        document: str,
        group: Group
    ) -> Invalidation | None:
        for vi, validator in enumerate(group['validators']):
            message = validator.validate(document)
            if message is not None:
                return {
                    "group": 0,
                    "validator": vi,
                    "message": message
                }

        return None


    def _inspect_one(
        self,
        file_path: str | pathlib.Path,
        document: str | None
    ) -> Inspection:
        inspection: Inspection = {
            "path": file_path,
            "included": [],
            "excluded": [],
            "invalidations": [],
            "violations": []
        }
        for gi, group in enumerate(self._config['groups']):
            logger.debug(f"Evaluating config groups[{gi}] for '{file_path}'.")
            include_pattern = self._get_file_pattern_match(file_path, group['includes'])
            if include_pattern is not None:
                exclude_pattern = self._get_file_pattern_match(file_path, group['excludes'])
                if exclude_pattern is not None:
                    logger.debug(f"Excluding '{file_path}' from groups[{gi}] for matching the '{exclude_pattern}' exclude pattern.")
                    inspection['excluded'].append(
                        {
                            "group": gi,
                            "pattern": exclude_pattern
                        }
                    )
                    continue

                logger.info(f"Including '{file_path}' in groups[{gi}] for matching the '{include_pattern}' include pattern.")
                inspection['included'].append(
                    {
                        "group": gi,
                        "pattern": include_pattern
                    }
                )
                if document is None:
                    with open(file_path, "r") as fp:
                        document = fp.read()

                inval = self._validate_str_group(document, group)
                if inval is not None:
                    logger.error(f"File '{file_path}' did not pass validation in groups[{gi}] from validators[{inval['validator']}]: {inval['message']}")
                    inspection['invalidations'].append(
                        {
                            "group": gi,
                            "validator": inval['validator'],
                            "message": inval['message']
                        }
                    )
                    continue

                for si, stage in enumerate(group['stages']):
                    tokens = stage['tokenizer'].tokenize(document)
                    for tr in tokens:
                        for fi, formatter in enumerate(stage['formatters']):
                            message = formatter.inspect(tr['token'])
                            if message is not None:
                                inspection['violations'].append(
                                    {
                                        "start_index": tr['index'],
                                        "length": tr['length'],
                                        "group": gi,
                                        "stage": si,
                                        "formatter": fi,
                                        "message": message
                                    }
                                )

        return inspection


    def inspects(self, path: str | pathlib.Path, document: str) -> Inspection:
        """Inspect a document string for violations.

        Parameters
        ----------
        path : str | pathlib.Path
            File path that is only used for glob matching.
            The file is not opened or checked for existence.
        document : str | None, default=None
            String document to inspect.

        Returns
        -------
        Inspection
            Inspection result.
        """
        file_path = pathlib.Path(file_path)

        return self._inspect_one(file_path=path, document=document)


    def _keep_result(
        self,
        result: Inspection | Formatting | FormattingDocument,
        keep_excluded: bool,
        keep_no_match: bool
    ) -> bool:
        if (
            len(result['included']) > 0
            or (
                len(result['excluded']) > 0
                and keep_excluded is True
            )
            or keep_no_match is True
        ):
            return True

        return False


    def inspect(
        self,
        path: str | pathlib.Path,
        keep_excluded: bool=False,
        keep_no_match=False
    ) -> list[Inspection]:
        """Inspect a file or directory for violations.

        Parameters
        ----------
        path : str | pathlib.Path
            File or dir path.
        keep_excluded : bool, default=False
            Keep results for files that matched at least one group, but were excluded from all matches.
            By default, these are not included in the results.
        keep_no_match : bool, default=False
            Keep results for files that did not match any groups.
            By default, these are not included in the results.

        Returns
        -------
        list[Inspection]
            List of inspections for the file or directory.
            By default, it does not include results that did not match any groups, or were excluded from all groups.

        Raises
        ------
        cleer.exceptions.BadPathError
            If the given path is not a file or directory.
        """
        path = pathlib.Path(path).resolve()
        if path.is_file() is True:
            inspection = self._inspect_one(file_path=path, document=None)
            if self._keep_result(
                result=inspection,
                keep_excluded=keep_excluded,
                keep_no_match=keep_no_match
            ) is False:
                return []

            return [inspection]

        elif path.is_dir() is True:
            inspections = []
            for p in path.rglob("*"):
                if p.is_file() is True:
                    inspection = self._inspect_one(file_path=p, document=None)
                    if self._keep_result(
                        result=inspection,
                        keep_excluded=keep_excluded,
                        keep_no_match=keep_no_match
                    ) is True:
                        inspections.append(inspection)

            return inspections

        else:
            raise exceptions.BadPathError(f"Path '{path}' must be a file or directory.")


    def _format_one(
        self,
        file_path: str | pathlib.Path,
        document: str | None
    ) -> FormattingDocument:
        formatting: FormattingDocument = {
            "path": file_path,
            "included": [],
            "excluded": [],
            "invalidations": [],
            "document": document
        }
        for gi, group in enumerate(self._config['groups']):
            logger.debug(f"Evaluating config groups[{gi}] for '{file_path}'.")
            include_pattern = self._get_file_pattern_match(file_path, group['includes'])
            if include_pattern is not None:
                exclude_pattern = self._get_file_pattern_match(file_path, group['excludes'])
                if exclude_pattern is not None:
                    logger.debug(f"Excluding '{file_path}' from groups[{gi}] for matching the '{exclude_pattern}' exclude pattern.")
                    formatting['excluded'].append(
                        {
                            "group": gi,
                            "pattern": exclude_pattern
                        }
                    )
                    continue

                logger.info(f"Including '{file_path}' in groups[{gi}] for matching the '{include_pattern}' include pattern.")
                formatting['included'].append(
                    {
                        "group": gi,
                        "pattern": include_pattern
                    }
                )
                if document is None:
                    with open(file_path, "r") as fp:
                        document = fp.read()

                inval = self._validate_str_group(document, group)
                if inval is not None:
                    logger.error(f"File '{file_path}' did not pass validation is groups[{gi}] from validators[{inval['validator']}]: {inval['message']}")
                    formatting['invalidations'].append(
                        {
                            "group": gi,
                            "validator": inval['validator'],
                            "message": inval['message']
                        }
                    )
                    continue

                for stage in group['stages']:
                    start_difference = 0
                    tokens = stage['tokenizer'].tokenize(document)
                    for tr in tokens:
                        token = tr['token']
                        for formatter in stage['formatters']:
                            token = formatter.format(token)

                        index = tr['index'] + start_difference
                        document = document[:index] + token + document[index + tr['length']:]
                        start_difference += len(token) - tr['length']

                if formatting['document'] is None:
                    with open(file_path, "w") as fp:
                        fp.write(document)

                else:
                    formatting['document'] = document

        return formatting


    def formats(
        self,
        path: str | pathlib.Path,
        document: str
    ) -> FormattingDocument:
        """Format a document string.

        Parameters
        ----------
        path : str | pathlib.Path
            File path that is only used for glob matching.
            The file is not opened or checked for existence.
        document : str | None, default=None
            String document to format.

        Returns
        -------
        FormattingDocument
            Formatting results with formatted document.
        """
        file_path = pathlib.Path(file_path)

        return self._format_one(file_path=path, document=document)


    def format(
        self,
        path: str | pathlib.Path,
        keep_excluded: bool=False,
        keep_no_match: bool=False
    ) -> list[Formatting]:
        """Format a file or directory of files.

        Parameters
        ----------
        path : str | pathlib.Path
            File or dir path.
        keep_excluded : bool, default=False
            Keep results for files that matched at least one group, but were excluded from all matches.
            By default these are not included in the result.
        keep_no_match : bool, default=False
            Keep results for files that did not match any groups.
            By default, these are not included in the results.

        Returns
        -------
        list[Formatting]
            List of formatting results for the file or directory.
            By default, it does not include results that did not match any groups, or were excluded from all groups.

        Raises
        ------
        cleer.exceptions.BadPathError
            If the given path is not a file or directory.
        """
        path = pathlib.Path(path).resolve()
        if path.is_file() is True:
            formatting = self._format_one(file_path=path, document=None)
            if self._keep_result(
                result=formatting,
                keep_excluded=keep_excluded,
                keep_no_match=keep_no_match
            ) is False:
                return []

            formatting.pop("document")

            return [formatting]

        elif path.is_dir() is True:
            formattings = []
            for p in path.rglob("*"):
                if p.is_file() is True:
                    formatting = self._format_one(file_path=p, document=None)
                    if self._keep_result(
                        result=formatting,
                        keep_excluded=keep_excluded,
                        keep_no_match=keep_no_match
                    ) is True:
                        formatting.pop("document")
                        formattings.append(formatting)

            return formattings

        else:
            raise exceptions.BadPathError(f"Path '{path}' must be a file or directory.")
