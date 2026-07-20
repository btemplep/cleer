"""Tests covering uncovered lines in py_type_hint_spacing_tokenizer, cleer.py, and cli.py."""

import pathlib
import subprocess

import pytest

from cleer import (
    Cleer,
    LineTokenizer,
    TrailingWhitespaceFormatter,
)
from cleer.exceptions import BadPathError
from cleer.tokenizers.python.py_type_hint_spacing_tokenizer import PyTypeHintSpacingTokenizer


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


def test_tokenizer_skips_keyword_colon():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "for x in items:\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_if_keyword_bad_spacing():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "if  :thing\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_colon_inside_comment():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = 5  # note:something\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_colon_inside_string_with_quotes_before():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = 'name:str'\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_block_end_colon_def():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "def foo(x):\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_block_end_colon_class():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "class Foo:\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_block_end_colon_if():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "if x:\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_block_end_colon_elif():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "elif x:\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_block_end_colon_for():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "for x in y:\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_block_end_colon_with_comment():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "if x:  # comment\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_block_end_colon_async_def():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "async def foo():\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_detects_bad_spacing_no_space_after():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "name:str = 'hello'\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1
    assert tokens[0]['token'] == ":"
    assert tokens[0]['index'] == 4


def test_tokenizer_detects_space_before_colon():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "name :str = 'hello'\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1
    assert tokens[0]['token'] == " :"


def test_tokenizer_correct_spacing_no_token():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "name: str = 'hello'\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_dict_literal_colon():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "d = {name:value}\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_slice_notation_colon():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = items[start:end]\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_skips_comment_line():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "# name:str\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_in_string_unterminated_triple_quote():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = '"""name:str\n'
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_in_string_triple_quote_contains_colon():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = '"""x:int"""\nname:str = "hello"\n'
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1
    assert tokens[0]['index'] == 16


def test_tokenizer_in_string_single_quote_contains_colon():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = 'name:str'\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_in_string_double_quote_contains_colon():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = 'x = "name:str"\n'
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_in_string_with_escape():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = 'na\\'me:str'\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_in_comment_with_string_before():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = 'hi' # name:str\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_in_comment_escape_in_string_context():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = 'h\\'i' # name:str\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_dict_with_escape_in_string():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "d = {'ke\\'y':val}\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_dict_with_double_quote_string():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = 'd = {"key":val}\n'
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_bracket_depth_tracking():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = items[{name:val}]\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_paren_depth_no_effect_on_result():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "func(name:str)\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1


def test_tokenizer_multiple_lines():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x: int = 5\ny:str = 'hello'\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1
    assert tokens[0]['token'] == ":"
    assert tokens[0]['index'] == 12


def test_will_expand_multiline_shallow():
    tokenizer = PyTypeHintSpacingTokenizer()
    line = "x: List[int] = []"
    result = tokenizer._will_expand_multiline(line, 1)

    assert result is False


def test_will_expand_multiline_two_levels():
    tokenizer = PyTypeHintSpacingTokenizer()
    line = "x: Dict[str, List[int]] = {}"
    result = tokenizer._will_expand_multiline(line, 1)

    assert result is False


def test_will_expand_multiline_three_levels():
    tokenizer = PyTypeHintSpacingTokenizer()
    line = "x: Dict[str, List[Dict[str, int]]] = {}"
    result = tokenizer._will_expand_multiline(line, 1)

    assert result is True


def test_will_expand_multiline_stops_at_equals():
    tokenizer = PyTypeHintSpacingTokenizer()
    line = "x: int = some[deep[nested[thing]]]"
    result = tokenizer._will_expand_multiline(line, 1)

    assert result is False


def test_will_expand_multiline_no_brackets():
    tokenizer = PyTypeHintSpacingTokenizer()
    line = "x: int = 5"
    result = tokenizer._will_expand_multiline(line, 1)

    assert result is False


def test_inspect_path_file(tmp_path):
    config = _make_config()
    clr = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \n")
    results = clr.inspect_path(file_path)

    assert len(results) == 1
    assert results[0]['path'] == file_path.resolve()
    assert len(results[0]['violations']) == 1


def test_inspect_path_dir(tmp_path):
    config = _make_config()
    clr = Cleer(config=config)
    (tmp_path / "test.py").write_text("hello   \n")
    results = clr.inspect_path(tmp_path)

    assert len(results) == 1
    assert len(results[0]['violations']) == 1


def test_inspect_path_bad_path():
    config = _make_config()
    clr = Cleer(config=config)
    with pytest.raises(BadPathError):
        clr.inspect_path("/nonexistent/path/to/thing")


def test_inspect_path_string_file(tmp_path):
    config = _make_config()
    clr = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \n")
    results = clr.inspect_path(str(file_path))

    assert len(results) == 1


def test_format_path_file(tmp_path):
    config = _make_config()
    clr = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \n")
    clr.format_path(file_path)

    assert file_path.read_text() == "hello\n"


def test_format_path_dir(tmp_path):
    config = _make_config()
    clr = Cleer(config=config)
    (tmp_path / "test.py").write_text("hello   \n")
    clr.format_path(tmp_path)

    assert (tmp_path / "test.py").read_text() == "hello\n"


def test_format_path_bad_path():
    config = _make_config()
    clr = Cleer(config=config)
    with pytest.raises(BadPathError):
        clr.format_path("/nonexistent/path/to/thing")


def test_format_path_string_file(tmp_path):
    config = _make_config()
    clr = Cleer(config=config)
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \n")
    clr.format_path(str(file_path))

    assert file_path.read_text() == "hello\n"


def test_format_path_string_dir(tmp_path):
    config = _make_config()
    clr = Cleer(config=config)
    (tmp_path / "test.py").write_text("hello   \n")
    clr.format_path(str(tmp_path))

    assert (tmp_path / "test.py").read_text() == "hello\n"


def test_cli_help():
    result = subprocess.run(
        ["cleer", "--help"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "cleer" in result.stdout.lower()


def test_cli_version():
    result = subprocess.run(
        ["cleer", "--version"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0


def test_cli_inspect_file(tmp_path):
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \n")
    result = subprocess.run(
        [
            "cleer",
            "inspect",
            str(file_path)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "violations" in result.stdout


def test_cli_format_file(tmp_path):
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \n")
    result = subprocess.run(
        [
            "cleer",
            "format",
            str(file_path)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert file_path.read_text() == "hello\n"


def test_cli_inspect_dir(tmp_path):
    (tmp_path / "test.py").write_text("hello   \n")
    result = subprocess.run(
        [
            "cleer",
            "inspect",
            str(tmp_path)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "violations" in result.stdout


def test_cli_format_dir(tmp_path):
    (tmp_path / "test.py").write_text("hello   \n")
    result = subprocess.run(
        [
            "cleer",
            "format",
            str(tmp_path)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert (tmp_path / "test.py").read_text() == "hello\n"


def test_cli_custom_cleer_bad_path():
    result = subprocess.run(
        [
            "cleer",
            "inspect",
            "--cleer",
            "nonexistent.module:clr",
            "."
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 1


def test_cli_log_level(tmp_path):
    file_path = tmp_path / "test.py"
    file_path.write_text("hello\n")
    result = subprocess.run(
        [
            "cleer",
            "inspect",
            "--log-level",
            "DEBUG",
            str(file_path)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0


def test_cli_no_args_shows_help():
    result = subprocess.run(
        ["cleer"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "usage" in result.stdout.lower() or "help" in result.stdout.lower()


def test_cli_main_function_direct_call(tmp_path, capsys):
    from cleer.cli import main

    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \n")
    with pytest.raises(SystemExit) as exc_info:
        main(["inspect", str(file_path)])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "violations" in captured.out


def test_cli_main_format_direct_call(tmp_path):
    from cleer.cli import main

    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \n")
    with pytest.raises(SystemExit) as exc_info:
        main(["format", str(file_path)])

    assert exc_info.value.code == 0
    assert file_path.read_text() == "hello\n"


def test_cli_main_default_cleer_fallback(tmp_path, capsys):
    from cleer.cli import main

    file_path = tmp_path / "test.py"
    file_path.write_text("hello\n")
    with pytest.raises(SystemExit) as exc_info:
        main(["inspect", str(file_path)])

    assert exc_info.value.code == 0


def test_tokenizer_in_string_newline_terminates_single_quote():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = 'unterminated\nname:str = 'hello'\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) >= 1


def test_tokenizer_colon_inside_triple_quote_string():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = '''name:str'''\ny:int = 5\n"
    tokens = tokenizer.tokenize(doc)

    found = [t for t in tokens if t['index'] >= 19]
    assert len(found) == 1


def test_tokenizer_dict_brace_close_tracking():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "d = {a:1}; name:str = ''\n"
    tokens = tokenizer.tokenize(doc)

    has_name_token = any(t['index'] >= 11 for t in tokens)
    assert has_name_token


def test_tokenizer_bracket_close_tracking():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = items[0:1]; name:str = ''\n"
    tokens = tokenizer.tokenize(doc)

    has_name_token = any(t['index'] >= 16 for t in tokens)
    assert has_name_token


def test_tokenizer_paren_open_close_tracking():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = (a); name:str = ''\n"
    tokens = tokenizer.tokenize(doc)

    has_name_token = any(t['index'] >= 9 for t in tokens)
    assert has_name_token


def test_tokenizer_match_case_block_end():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "match x:\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_case_block_end():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "    case pattern:\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_cli_main_bad_cleer_path_direct_call():
    from cleer.cli import main

    with pytest.raises(SystemExit) as exc_info:
        main([
            "inspect",
            "--cleer",
            "nonexistent.module:clr",
            "."
        ])

    assert exc_info.value.code == 1


def test_cli_main_custom_cleer_success(tmp_path):
    from cleer.cli import main

    clr_module = tmp_path / "my_clr.py"
    clr_module.write_text(
        "from cleer import cleer_default\nclr = cleer_default()\n"
    )
    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \n")

    import sys
    sys.path.insert(0, str(tmp_path))
    try:
        with pytest.raises(SystemExit) as exc_info:
            main([
                "inspect",
                "--cleer",
                "my_clr:clr",
                str(file_path)
            ])

        assert exc_info.value.code == 0
    finally:
        sys.path.remove(str(tmp_path))
        if "my_clr" in sys.modules:
            del sys.modules["my_clr"]


def test_tokenizer_is_in_comment_escape_in_single_quote():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "x = 'it\\'s' # note:thing\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_is_dict_or_slice_escape_in_string_key():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "d = {'it\\'s':val}\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_is_dict_or_slice_double_quote_string_key():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = 'd = {"key\\"s":val}\n'
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_inspect_dir_excluded_path_set(tmp_path):
    config = _make_config(excludes=["**/excluded/**"])
    clr = Cleer(config=config)
    excluded_dir = tmp_path / "excluded"
    excluded_dir.mkdir()
    (excluded_dir / "test.py").write_text("hello   \n")
    (tmp_path / "good.py").write_text("hello   \n")
    results = clr.inspect_dir(tmp_path)

    assert len(results) == 1
    assert "good.py" in str(results[0]['path'])


def test_format_dir_excluded_path_set(tmp_path):
    config = _make_config(excludes=["**/excluded/**"])
    clr = Cleer(config=config)
    excluded_dir = tmp_path / "excluded"
    excluded_dir.mkdir()
    (excluded_dir / "test.py").write_text("hello   \n")
    (tmp_path / "good.py").write_text("hello   \n")
    clr.format_dir(tmp_path)

    assert (excluded_dir / "test.py").read_text() == "hello   \n"
    assert (tmp_path / "good.py").read_text() == "hello\n"


def test_tokenizer_is_in_comment_hash_after_identifier():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "val = 1 # x:int here\n"
    tokens = tokenizer.tokenize(doc)

    assert tokens == []


def test_tokenizer_is_dict_or_slice_escape_before_colon_in_brace():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = "d = {'k\\'ey':val}; name:str = 'x'\n"
    tokens = tokenizer.tokenize(doc)

    name_tokens = [t for t in tokens if t['index'] >= 19]
    assert len(name_tokens) >= 1


def test_tokenizer_is_dict_or_slice_double_quote_toggle():
    tokenizer = PyTypeHintSpacingTokenizer()
    doc = 'd = {"key":val}; name:str = "x"\n'
    tokens = tokenizer.tokenize(doc)

    name_tokens = [t for t in tokens if t['index'] >= 17]
    assert len(name_tokens) >= 1


def test_cli_main_default_cleer_fallback_no_clr_file(tmp_path, capsys, monkeypatch):
    from cleer.cli import main
    import sys

    file_path = tmp_path / "test.py"
    file_path.write_text("hello\n")
    monkeypatch.chdir(tmp_path)
    if "clr" in sys.modules:
        monkeypatch.delitem(sys.modules, "clr")
    with pytest.raises(SystemExit) as exc_info:
        main(["inspect", str(file_path)])

    assert exc_info.value.code == 0


def test_cli_main_no_argv_shows_help(monkeypatch, capsys):
    from cleer.cli import main
    import sys

    monkeypatch.setattr(sys, "argv", ["cleer"])
    with pytest.raises(SystemExit) as exc_info:
        main(None)

    assert exc_info.value.code == 0


def test_comma_plus_tokenizer_is_single_item_set_returns_false_for_list_bracket():
    """Cover line 75 in comma_plus_tokenizer.py: return False when '[' found at depth 0."""
    from cleer.tokenizers.comma_plus_tokenizer import CommaPlusTokenizer

    tokenizer = CommaPlusTokenizer()
    result = tokenizer._is_single_item_set("[1,}", 2)

    assert result is False


def test_comma_plus_tokenizer_is_single_item_set_returns_false_for_paren():
    """Cover line 75 in comma_plus_tokenizer.py: return False when '(' found at depth 0."""
    from cleer.tokenizers.comma_plus_tokenizer import CommaPlusTokenizer

    tokenizer = CommaPlusTokenizer()
    result = tokenizer._is_single_item_set("(1,}", 2)

    assert result is False


def test_comma_plus_tokenizer_tokenize_comma_before_brace_in_list():
    """Cover line 75 via tokenize: comma followed by } inside a list."""
    from cleer.tokenizers.comma_plus_tokenizer import CommaPlusTokenizer

    tokenizer = CommaPlusTokenizer()
    tokens = tokenizer.tokenize("[1, }")

    assert len(tokens) == 1
    assert tokens[0]['token'] == ", }"


def test_cli_main_default_fallback_import_fails(tmp_path, capsys, monkeypatch):
    """Cover cli.py lines 109-112: default clr:clr import fails, fallback to cleer_default()."""
    import sys
    from cleer.cli import main

    file_path = tmp_path / "test.py"
    file_path.write_text("hello   \n")

    monkeypatch.chdir(tmp_path)

    if "clr" in sys.modules:
        monkeypatch.delitem(sys.modules, "clr")

    original_path = sys.path[:]
    clean_path = [
        p for p in sys.path
        if not (
            p == "" or
            p == "." or
            p.endswith("/cleer") or
            p.endswith("\\cleer")
        )
    ]
    clean_path.insert(0, str(tmp_path))
    monkeypatch.setattr(sys, "path", clean_path)

    with pytest.raises(SystemExit) as exc_info:
        main(["inspect", str(file_path)])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "violations" in captured.out


def test_inspect_dir_excluded_file_is_skipped(tmp_path):
    """Exercise cleer.py inspect_dir with excluded files to cover _is_excluded branch (line 232)."""
    config = _make_config(excludes=["**/skip_me.py"])
    clr = Cleer(config=config)
    (tmp_path / "skip_me.py").write_text("hello   \n")
    (tmp_path / "keep_me.py").write_text("hello   \n")
    results = clr.inspect_dir(tmp_path)

    paths = [str(r['path']) for r in results]
    assert any("keep_me.py" in p for p in paths)
    assert not any("skip_me.py" in p for p in paths)


def test_format_dir_excluded_file_is_skipped(tmp_path):
    """Exercise cleer.py format_dir with excluded files to cover _is_excluded branch (line 395)."""
    config = _make_config(excludes=["**/skip_me.py"])
    clr = Cleer(config=config)
    (tmp_path / "skip_me.py").write_text("hello   \n")
    (tmp_path / "keep_me.py").write_text("hello   \n")
    clr.format_dir(tmp_path)

    assert (tmp_path / "skip_me.py").read_text() == "hello   \n"
    assert (tmp_path / "keep_me.py").read_text() == "hello\n"


def test_inspect_dir_excluded_path_cache_hit(tmp_path):
    """Cover line 229: file excluded by first glob is skipped on second glob match."""
    config = {
        "groups": [
            {
                "includes": [
                    "**/*.py",
                    "**/*test*.py"
                ],
                "excludes": [
                    "**/excluded/**"
                ],
                "stages": [
                    {
                        "tokenizer": LineTokenizer(),
                        "formatters": [TrailingWhitespaceFormatter()]
                    }
                ]
            }
        ]
    }
    clr = Cleer(config=config)
    excluded_dir = tmp_path / "excluded"
    excluded_dir.mkdir()
    (excluded_dir / "test_thing.py").write_text("hello   \n")
    (tmp_path / "good.py").write_text("hello   \n")
    results = clr.inspect_dir(tmp_path)

    assert len(results) == 1
    assert "good.py" in str(results[0]['path'])


def test_format_dir_excluded_path_cache_hit(tmp_path):
    """Cover line 395: file excluded by first glob is skipped on second glob match."""
    config = {
        "groups": [
            {
                "includes": [
                    "**/*.py",
                    "**/*test*.py"
                ],
                "excludes": [
                    "**/excluded/**"
                ],
                "stages": [
                    {
                        "tokenizer": LineTokenizer(),
                        "formatters": [TrailingWhitespaceFormatter()]
                    }
                ]
            }
        ]
    }
    clr = Cleer(config=config)
    excluded_dir = tmp_path / "excluded"
    excluded_dir.mkdir()
    (excluded_dir / "test_thing.py").write_text("hello   \n")
    (tmp_path / "good.py").write_text("hello   \n")
    clr.format_dir(tmp_path)

    assert (excluded_dir / "test_thing.py").read_text() == "hello   \n"
    assert (tmp_path / "good.py").read_text() == "hello\n"
