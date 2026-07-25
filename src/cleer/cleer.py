__all__ = ["Cleer"]


import glob
import io
import pathlib
import re
from typing import Dict, List

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


    def _is_excluded(
        self,
        file_path: pathlib.Path,
        group: CleerGroup
    ) -> bool:
        for pattern in group['excludes']:
            exclude_regex = glob_to_regex(
                pattern,
                recursive=True,
                include_hidden=True
            )
            if re.match(exclude_regex, str(file_path)) is not None:
                logger.debug(f"Excluding '{file_path}' file for matching the '{pattern}' exclude pattern.")

                return True

        return False


    def _matches_group(
        self,
        file_path: pathlib.Path,
        group: CleerGroup
    ) -> bool:
        for pattern in group['includes']:
            include_regex = glob_to_regex(
                pattern,
                recursive=True,
                include_hidden=True
            )
            if re.match(include_regex, str(file_path)) is not None:
                if self._is_excluded(file_path, group):
                    return False

                logger.info(f"Including '{file_path.resolve()}' file for matching the '{pattern}' include pattern.")

                return True

        return False


    def _inspect_str_group(
        self,
        document: str,
        group: CleerGroup
    ) -> List[Violation]:
        violations: List[Violation] = []
        for stage in group['stages']:
            tokens = stage['tokenizer'].tokenize(document)
            for tr in tokens:
                for formatter in stage['formatters']:
                    message = formatter.inspect(tr['token'])
                    if message is not None:
                        violations.append(
                            {
                                "start_index": tr['index'],
                                "length": tr['length'],
                                "message": message
                            }
                        )

        return violations


    def inspect_str(
        self,
        document: str,
        file_path: str | pathlib.Path
    ) -> List[Violation]:
        """Inspect a document string for violations.

        Parameters
        ----------
        document : str
            Document to inspect for violations
        file_path : str | pathlib.Path
            File path that is only used for glob matching of formatting groups.

        Returns
        -------
        List[Violation]
            List of violations for the document.
        """
        file_path = pathlib.Path(file_path)
        violations: List[Violation] = []
        for gi, group in enumerate(self._config['groups']):
            logger.info(f"Evaluating config groups[{gi}].")
            if self._matches_group(file_path, group) is True:
                violations += self._inspect_str_group(document, group)

        return violations


    def inspect_fp(
        self,
        fp: io.TextIOBase,
        file_path: str | pathlib.Path
    ) -> List[Violation]:
        """Inspect a document file pointer for violations.

        **Does not close the file pointer upon return.**

        **Requires a file pointer in at least read mode: `r`.**

        Parameters
        ----------
        fp : io.TextIOBase
            File pointer of document.
        file_path : str | pathlib.Path
            File path that is only used for glob matching of formatting groups.

        Returns
        -------
        List[Violation]
            List of violations for the document.
        """
        file_path = pathlib.Path(file_path)

        return self.inspect_str(fp.read(), file_path)


    def inspect_file(
        self,
        file_path: str | pathlib.Path
    ) -> List[Violation]:
        """Inspect a document at the given path for violations.

        Parameters
        ----------
        file_path : str | pathlib.Path
            Path to document that will be read. Also used for glob matching of formatting groups.

        Returns
        -------
        List[Violation]
            List of violations for the document.
        """
        file_path = pathlib.Path(file_path)
        document = file_path.read_text()

        return self.inspect_str(document, file_path)


    def inspect_dir(
        self,
        dir_path: str | pathlib.Path
    ) -> List[FileInspectionResult]:
        """Inspect files under a directory.

        Files will be filtered for each stage by the glob for that stage.

        Parameters
        ----------
        dir_path : str | pathlib.Path
            Path to directory to run formatting on. Also used for glob matching of formatting groups.

        Returns
        -------
        List[FileInspectionResult]
            List of inspection results that include the file path and violations.
        """
        dir_path = pathlib.Path(dir_path)
        path_lookup: Dict[pathlib.Path, List[Violation]] = {}
        for gi, group in enumerate(self._config['groups']):
            logger.info(f"Evaluating config groups[{gi}].")
            # keeps track of if a path was already run for this group
            group_included_paths = set()
            group_excluded_paths = set()
            for pattern in group['includes']:
                for file_path in dir_path.glob(pattern):
                    if file_path in group_excluded_paths:
                        continue

                    if self._is_excluded(file_path, group) is True:
                        group_excluded_paths.add(file_path)
                        continue

                    if file_path.is_file() is True:
                        file_path = file_path.resolve()
                        if file_path not in group_included_paths:
                            logger.info(f"Including '{file_path}' file for matching the '{pattern}' include pattern.")
                            if file_path not in path_lookup:
                                path_lookup[file_path] = []

                            document = file_path.read_text()
                            path_lookup[file_path] += self._inspect_str_group(
                                document,
                                group
                            )

        results: List[FileInspectionResult] = []
        for path, violations in path_lookup.items():
            results.append(
                {
                    "path": path,
                    "violations": violations
                }
            )

        return results


    def inspect_path(
        self,
        path: str | pathlib.Path
    ) -> List[FileInspectionResult]:
        """Inspect a file or directory.

        Parameters
        ----------
        path : str | pathlib.Path
            Path to file or directory.

        Returns
        -------
        List[FileInspectionResult]
            List of inspection results that include the file path and violations.
            For a file this will only be one entry.

        Raises
        ------
        cleer.exceptions.BadPathError
            If the given path is not a file or directory.
        """
        path = pathlib.Path(path)
        if path.is_file() is True:
            return [
                {
                    "path": path.resolve(),
                    "violations": self.inspect_file(path)
                }
            ]
        elif path.is_dir() is True:
            return self.inspect_dir(path)
        else:
            raise exceptions.BadPathError(f"Path '{path}' must be a file or directory.")


    def _format_str_group(
        self,
        document: str,
        group: CleerGroup
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
    ) -> str:
        """Format a document string.

        Parameters
        ----------
        document : str
            Document to format.
        file_path : str | pathlib.Path
            File path that is only used for glob matching of formatting groups.

        Returns
        -------
        str
            Formatted document.
        """
        file_path = pathlib.Path(file_path)
        for gi, group in enumerate(self._config['groups']):
            logger.info(f"Evaluating config groups[{gi}].")
            if self._matches_group(file_path, group) is True:
                document = self._format_str_group(document, group)

        return document


    def format_fp(
        self,
        fp: io.TextIOBase,
        file_path: str | pathlib.Path
    ) -> None:
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
        None
        """
        file_path = pathlib.Path(file_path)
        document = self.format_str(fp.read(), file_path)
        fp.seek(0)
        fp.write(document)
        fp.truncate()


    def format_file(
        self,
        file_path: str | pathlib.Path
    ) -> None:
        """Format a document at the given path.

        Parameters
        ----------
        file_path : str | pathlib.Path
            Path to document.

        Returns
        -------
        None
        """
        file_path = pathlib.Path(file_path)
        document = file_path.read_text()
        document = self.format_str(document, file_path)
        file_path.write_text(document)


    def format_dir(self, dir_path: str | pathlib.Path) -> None:
        """Format files under a directory.

        Files will be filtered for each stage by the glob for that stage.

        Parameters
        ----------
        dir_path : str | pathlib.Path
            Path to directory that the stage glob pattern will be run on.

        Returns
        -------
        None
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

                    if self._is_excluded(file_path, group) is True:
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


    def format_path(self, path: str | pathlib.Path) -> None:
        """Format a file or directory.

        Parameters
        ----------
        path : str | pathlib.Path
            Path to file or directory.

        Returns
        -------
        None

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
