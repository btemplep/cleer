"""Unit tests for the Cleer class."""

import io
import pathlib

from cleer import Cleer, LineTokenizer, TrailingWhitespaceFormatter


def _make_config(includes=None, excludes=None):
    return {
        "groups": [
            {
                "includes": includes or ["**/*.py"],
                "excludes": excludes or [],
                "stages": [
                    {
                        "tokenizer": LineTokenizer(),
                        "formatters": [TrailingWhitespaceFormatter()]
                    }
                ]
            }
        ]
    }


def test_init_stores_config():
    config = _make_config()
    cleer = Cleer(config=config)

    assert cleer._config == config


def test_init_multiple_groups():
    config = {
        "groups": [
            {
                "includes": ["**/*.py"],
                "excludes": [],
                "stages": [
                    {
                        "tokenizer": LineTokenizer(),
                        "formatters": [TrailingWhitespaceFormatter()]
                    }
                ]
            },
            {
                "includes": ["**/*.txt"],
                "excludes": [],
                "stages": [
                    {
                        "tokenizer": LineTokenizer(),
                        "formatters": [TrailingWhitespaceFormatter()]
                    }
                ]
            }
        ]
    }
    cleer = Cleer(config=config)

    assert len(cleer._config['groups']) == 2


def test_inspect_str_with_violations():
    config = _make_config()
    cleer = Cleer(config=config)
    violations = cleer.inspect_str(
        "hello   \nworld\n",
        pathlib.Path("test.py")
    )

    assert len(violations) == 1
    assert violations[0]['start_index'] == 0
    assert violations[0]['length'] == 8
    assert "trail" in violations[0]['message'].lower()


def test_inspect_str_no_matching_glob():
    config = _make_config(includes=["**/*.txt"])
    cleer = Cleer(config=config)
    violations = cleer.inspect_str(
        "hello   \nworld\n",
        pathlib.Path("test.py")
    )

    assert violations == []


def test_inspect_str_no_violations():
    config = _make_config()
    cleer = Cleer(config=config)
    violations = cleer.inspect_str(
        "hello\nworld\n",
        pathlib.Path("test.py")
    )

    assert violations == []


def test_inspect_fp():
    config = _make_config()
    cleer = Cleer(config=config)
    fp = io.StringIO("hello   \nworld\n")
    violations = cleer.inspect_fp(fp, pathlib.Path("test.py"))

    assert len(violations) == 1
    assert violations[0]['start_index'] == 0


def test_inspect_file(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \nworld\n")
    violations = cleer.inspect_file(file_path)

    assert len(violations) == 1


def test_inspect_file_no_matching_glob(tmp_path):
    config = _make_config(includes=["**/*.txt"])
    cleer = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \nworld\n")
    violations = cleer.inspect_file(file_path)

    assert violations == []


def test_inspect_dir_finds_matching_files(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    (tmp_path / "test.py").write_text("hello   \n")
    results = cleer.inspect_dir(tmp_path)

    assert len(results) == 1
    assert results[0]['path'] == (tmp_path / "test.py").resolve()
    assert len(results[0]['violations']) == 1


def test_inspect_dir_with_subdirectories(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "deep.py").write_text("trailing   \n")
    results = cleer.inspect_dir(tmp_path)

    assert len(results) == 1
    assert len(results[0]['violations']) == 1


def test_inspect_dir_deduplicates_same_file_across_globs(
    tmp_path
):
    config = {
        "groups": [
            {
                "includes": ["**/*.py", "*.py"],
                "excludes": [],
                "stages": [
                    {
                        "tokenizer": LineTokenizer(),
                        "formatters": [TrailingWhitespaceFormatter()]
                    }
                ]
            }
        ]
    }
    cleer = Cleer(config=config)
    (tmp_path / "test.py").write_text("hello   \n")
    results = cleer.inspect_dir(tmp_path)

    assert len(results) == 1


def test_format_str_with_matching_glob():
    config = _make_config()
    cleer = Cleer(config=config)
    result = cleer.format_str(
        "hello   \nworld   \n",
        pathlib.Path("test.py")
    )

    assert result == "hello\nworld\n"


def test_format_str_with_no_matching_glob():
    config = _make_config(includes=["**/*.txt"])
    cleer = Cleer(config=config)
    result = cleer.format_str(
        "hello   \nworld   \n",
        pathlib.Path("test.py")
    )

    assert result == "hello   \nworld   \n"


def test_format_fp(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hello\nworld\n")
    with open(file_path, "r+") as fp:
        cleer.format_fp(fp, pathlib.Path("test.py"))

    assert file_path.read_text() == "hello\nworld\n"


def test_format_fp_writes_formatted_content(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hi   \n")
    with open(file_path, "r+") as fp:
        cleer.format_fp(fp, pathlib.Path("test.py"))

    assert file_path.read_text() == "hi\n"


def test_format_file(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \nworld   \n")
    cleer.format_file(file_path)

    assert file_path.read_text() == "hello\nworld\n"


def test_format_file_no_matching_glob(tmp_path):
    config = _make_config(includes=["**/*.txt"])
    cleer = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \nworld   \n")
    cleer.format_file(file_path)

    assert file_path.read_text() == "hello   \nworld   \n"


def test_format_dir_formats_matching_files(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    (tmp_path / "test.py").write_text("hello   \n")
    cleer.format_dir(tmp_path)

    assert (tmp_path / "test.py").read_text() == "hello\n"


def test_format_dir_skips_non_matching_files(tmp_path):
    config = _make_config(includes=["**/*.py"])
    cleer = Cleer(config=config)
    (tmp_path / "test.txt").write_text("hello   \n")
    cleer.format_dir(tmp_path)

    assert (tmp_path / "test.txt").read_text() == "hello   \n"


def test_format_dir_handles_subdirectories(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "deep.py").write_text("trailing   \n")
    cleer.format_dir(tmp_path)

    assert (sub / "deep.py").read_text() == "trailing\n"


def test_format_dir_deduplicates_same_file_across_globs(
    tmp_path
):
    config = {
        "groups": [
            {
                "includes": ["**/*.py", "*.py"],
                "excludes": [],
                "stages": [
                    {
                        "tokenizer": LineTokenizer(),
                        "formatters": [TrailingWhitespaceFormatter()]
                    }
                ]
            }
        ]
    }
    cleer = Cleer(config=config)
    (tmp_path / "test.py").write_text("hello   \n")
    cleer.format_dir(tmp_path)

    assert (tmp_path / "test.py").read_text() == "hello\n"


def test_multiple_groups_with_different_globs(tmp_path):
    config = {
        "groups": [
            {
                "includes": ["**/*.py"],
                "excludes": [],
                "stages": [
                    {
                        "tokenizer": LineTokenizer(),
                        "formatters": [TrailingWhitespaceFormatter()]
                    }
                ]
            },
            {
                "includes": ["**/*.txt"],
                "excludes": [],
                "stages": [
                    {
                        "tokenizer": LineTokenizer(),
                        "formatters": [TrailingWhitespaceFormatter()]
                    }
                ]
            }
        ]
    }
    cleer = Cleer(config=config)
    (tmp_path / "test.py").write_text("hello   \n")
    (tmp_path / "test.txt").write_text("world   \n")
    cleer.format_dir(tmp_path)

    assert (tmp_path / "test.py").read_text() == "hello\n"
    assert (tmp_path / "test.txt").read_text() == "world\n"


def test_format_str_with_string_path():
    config = _make_config()
    cleer = Cleer(config=config)
    result = cleer.format_str("hello   \nworld   \n", "test.py")

    assert result == "hello\nworld\n"


def test_format_fp_with_string_path(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hi   \n")
    with open(file_path, "r+") as fp:
        cleer.format_fp(fp, "test.py")

    assert file_path.read_text() == "hi\n"


def test_format_file_with_string_path(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \nworld   \n")
    cleer.format_file(str(file_path))

    assert file_path.read_text() == "hello\nworld\n"


def test_format_dir_with_string_path(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    (tmp_path / "test.py").write_text("hello   \n")
    cleer.format_dir(str(tmp_path))

    assert (tmp_path / "test.py").read_text() == "hello\n"


def test_inspect_str_with_string_path():
    config = _make_config()
    cleer = Cleer(config=config)
    violations = cleer.inspect_str(
        "hello   \nworld\n",
        "test.py"
    )

    assert len(violations) == 1


def test_inspect_fp_with_string_path():
    config = _make_config()
    cleer = Cleer(config=config)
    fp = io.StringIO("hello   \nworld\n")
    violations = cleer.inspect_fp(fp, "test.py")

    assert len(violations) == 1


def test_inspect_file_with_string_path(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \nworld\n")
    violations = cleer.inspect_file(str(file_path))

    assert len(violations) == 1


def test_inspect_dir_with_string_path(tmp_path):
    config = _make_config()
    cleer = Cleer(config=config)
    (tmp_path / "test.py").write_text("hello   \n")
    results = cleer.inspect_dir(str(tmp_path))

    assert len(results) == 1
    assert len(results[0]['violations']) == 1


def test_format_str_excluded_by_pattern():
    config = _make_config(excludes=["**/venv*/**"])
    cleer = Cleer(config=config)
    result = cleer.format_str("hello   \n", "venv/test.py")

    assert result == "hello   \n"


def test_format_str_not_excluded():
    config = _make_config(excludes=["**/venv*/**"])
    cleer = Cleer(config=config)
    result = cleer.format_str("hello   \n", "src/test.py")

    assert result == "hello\n"


def test_inspect_str_excluded_by_pattern():
    config = _make_config(excludes=["**/.venv*/**"])
    cleer = Cleer(config=config)
    violations = cleer.inspect_str(
        "hello   \n",
        ".venv/test.py"
    )

    assert violations == []


def test_format_dir_excludes_venv(tmp_path):
    config = _make_config(excludes=["**/venv*/**"])
    cleer = Cleer(config=config)
    venv = tmp_path / "venv"
    venv.mkdir()
    (venv / "test.py").write_text("hello   \n")
    (tmp_path / "main.py").write_text("hello   \n")
    cleer.format_dir(tmp_path)

    assert (venv / "test.py").read_text() == "hello   \n"
    assert (tmp_path / "main.py").read_text() == "hello\n"


def test_inspect_dir_excludes_venv(tmp_path):
    config = _make_config(excludes=["**/venv*/**"])
    cleer = Cleer(config=config)
    venv = tmp_path / "venv"
    venv.mkdir()
    (venv / "test.py").write_text("hello   \n")
    (tmp_path / "main.py").write_text("hello   \n")
    results = cleer.inspect_dir(tmp_path)

    assert len(results) == 1
    assert "main.py" in str(results[0]['path'])


def test_excludes_dot_venv_pattern():
    config = _make_config(excludes=["**/.venv*/**"])
    cleer = Cleer(config=config)
    result = cleer.format_str(
        "hello   \n",
        ".venv311/lib/test.py"
    )

    assert result == "hello   \n"
