__all__ = ["Cleer"]


import io
import pathlib
import re
from typing import Dict, List, Literal, Tuple

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
    ```python
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
        patterns: List[str]
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
    ) -> Inspection | None:
        """Inspect a file or document string for violations.

        Parameters
        ----------
        file_path : str | pathlib.Path
            File path.
            If document is not `None` then this is only used for glob matching
        document : str | None
            String document to inspect.

        Returns
        -------
        Inspection
            Inspection details of `None` if the file didn't match any groups. 
        """
        inspection: Inspection = {
            "path": file_path,
            "included": [],
            "excluded": [],
            "invalidations": [],
            "violations": []
        }
        for gi, group in enumerate(self._config['groups']):
            logger.info(f"Evaluating config groups[{gi}].")
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

                logger.info(f"Including '{file_path.resolve()}' in groups[{gi}] for matching the '{include_pattern}' include pattern.")
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
                    logger.error(f"File '{file_path}' did not pass validation is groups[{gi}] from validators[{inval['validator']}]: {inval['message']}")
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

        if len(inspection['included']) == 0:
            return None

        return inspection


    def inspect(
        self,
        path: str | pathlib.Path,
        document: str | None = None
    ) -> List[Inspection]:
        """Inspect a file, dir, or document string for violations.

        Parameters
        ----------
        path : str | pathlib.Path
            File or dir path.
            If `document` is provided, then this is only used for glob matching. 
            The file is not opened.
        document : str | None, default=None
            String document to inspect.
            If provided, then `path` is only used for glob matching.
            The file is not opened.

        Returns
        -------
        List[Inspection]
            List of inspections for files that match at least one group in the config. 
            Includes files that would be included, but were explicitly excluded.
            The excluded files are not inspected. 
        
        Raises
        ------
        cleer.exceptions.BadPathError
            If the given path is not a file or directory.    
        """
        path = pathlib.Path(path)
        if document is not None or path.is_file() is True:
            inspection = self._inspect_one(
                file_path=path,
                document=document
            )
            if inspection is None:
                return []

            return [inspection]

        if path.is_dir() is True:
            inspections = []
            for p in path.rglob("*"):
                if p.is_file() is True:
                    inspection = self._inspect_one(
                        file_path=p,
                        document=document
                    )
                    if inspection is not None:
                        inspections.append(inspection)
                        print(inspection)

            return inspections

        raise exceptions.BadPathError(f"Path '{path}' must be a file or directory.")


    def _format_one(
        self,
        file_path: str | pathlib.Path,
        document: str | None
    ) -> FormattingDocument:
        """Format a file or document string.

        Parameters
        ----------
        file_path : str | pathlib.Path
            File path.
            If document is not `None` then this is only used for glob matching
        document : str | None
            String document to format.

        Returns
        -------
        Inspection
            Inspection details for the file. 
        """
        formatting: FormattingDocument = {
            "path": file_path,
            "included": [],
            "excluded": [],
            "invalidations": [],
            "document": document
        }
        for gi, group in enumerate(self._config['groups']):
            logger.info(f"Evaluating config groups[{gi}].")
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

                logger.info(f"Including '{file_path.resolve()}' in groups[{gi}] for matching the '{include_pattern}' include pattern.")
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


    def _format_str_group(
        self,
        document: str,
        group: Group
    ) -> str:
        for stage in group['stages']:
            start_difference = 0
            for tr in stage['tokenizer'].tokenize(document):
                token = tr['token']
                for formatter in stage['formatters']:
                    token = formatter.format(token)

                index = tr['index'] + start_difference
                document = document[:index] + token + document[index + tr['length']:]
                start_difference += len(token) - tr['length']

        return document


    def format_str(
        self,
        document: str,
        file_path: str | pathlib.Path
    ) -> FormatStringResult:
        """Format a document string.

        Parameters
        ----------
        document : str
            Document to format.
        file_path : str | pathlib.Path
            File path that is only used for glob matching of formatting groups.

        Returns
        -------
        FormatStringResult
            Formatted document and info.
        """
        file_path = pathlib.Path(file_path)
        for gi, group in enumerate(self._config['groups']):
            logger.info(f"Evaluating config groups[{gi}].")
            if self._include_group(file_path, group) is True:
                document = self._format_str_group(document, group)

        return document


    def format_fp(
        self,
        fp: io.TextIOBase,
        file_path: str | pathlib.Path
    ) -> FormatResult:
        """Format a document file pointer.

        **Does not close the file pointer upon return.**

        **Requires a file pointer that in read and write mode: `r+`.**

        Parameters
        ----------
        fp : io.TextIOBase
            File pointer of document.
        file_path : str | pathlib.Path
            File path that is only used for glob matching of formatting groups.

        Returns
        -------
        FormatResult
            Info about the formatted files.
        """
        file_path = pathlib.Path(file_path)
        document = self.format_str(fp.read(), file_path)
        fp.seek(0)
        fp.write(document)
        fp.truncate()


    def format_file(
        self,
        file_path: str | pathlib.Path
    ) -> FormatResult:
        """Format a document at the given path.

        Parameters
        ----------
        file_path : str | pathlib.Path
            Path to document.

        Returns
        -------
        FormatResult
            Info about the formatted files.
        """
        file_path = pathlib.Path(file_path)
        document = file_path.read_text()
        document = self.format_str(document, file_path)
        file_path.write_text(document)


    def format_dir(self, dir_path: str | pathlib.Path) -> FormatResult:
        """Format files under a directory.

        Files will be filtered for each stage by the glob for that stage.

        Parameters
        ----------
        dir_path : str | pathlib.Path
            Path to directory that the stage glob pattern will be run on.

        Returns
        -------
        FormatResult
            Info about the formatted files.
        """
        dir_path = pathlib.Path(dir_path)
        for gi, group in enumerate(self._config['groups']):
            logger.info(f"Evaluating config groups[{gi}].")
            # keeps track of if a path was already run for this group
            group_included_paths = set()
            group_excluded_paths = set()
            for pattern in group['includes']:
                for file_path in dir_path.glob(pattern):
                    if file_path in group_excluded_paths:
                        continue

                    if self._matches_exclude(file_path, group) is True:
                        group_excluded_paths.add(file_path)
                        continue

                    if file_path.is_file() is True:
                        file_path = file_path.resolve()
                        if file_path not in group_included_paths:
                            logger.info(f"Including '{file_path}' file for matching the '{pattern}' include pattern.")
                            document = file_path.read_text()
                            document = self._format_str_group(
                                file_path.read_text(),
                                group
                            )
                            file_path.write_text(document)


    def format_path(self, path: str | pathlib.Path) -> FormatResult:
        """Format a file or directory.

        Parameters
        ----------
        path : str | pathlib.Path
            Path to file or directory.

        Returns
        -------
        FormatResult
            Info about the formatted files.ne

        Raises
        ------
        cleer.exceptions.BadPathError
            If the given path is not a file or directory.
        """
        path = pathlib.Path(path)
        if path.is_file() is True:
            self.format_file(path)
        elif path.is_dir() is True:
            self.format_dir(path)
        else:
            raise exceptions.BadPathError(f"Path '{path}' must be a file or directory.")
