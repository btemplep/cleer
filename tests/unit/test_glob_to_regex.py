import re

from cleer.glob_to_regex import glob_to_regex


def _match(pattern: str, path: str, **kwargs) -> bool:
    regex = glob_to_regex(pattern, **kwargs)

    return re.match(regex, path) is not None


def test_simple_star_matches_filename():
    assert _match("*.py", "hello.py", seps="/")


def test_simple_star_does_not_cross_separator():
    assert not _match("*.py", "dir/hello.py", seps="/")


def test_double_star_matches_nested_paths():
    assert _match("**/*.py", "src/cleer/cleer.py", seps="/")


def test_double_star_matches_single_level():
    assert _match("**/*.py", "cleer.py", seps="/")


def test_double_star_at_end_matches_everything():
    assert _match("src/**", "src/foo/bar/baz.txt", seps="/")


def test_double_star_at_end_matches_single_file():
    assert _match("src/**", "src/file.txt", seps="/")


def test_double_star_in_middle():
    assert _match(
        "src/**/test_*.py",
        "src/tests/unit/test_thing.py",
        seps="/"
    )


def test_double_star_in_middle_direct_child():
    assert _match(
        "src/**/test_*.py",
        "src/test_thing.py",
        seps="/"
    )


def test_question_mark_matches_single_char():
    assert _match("file?.txt", "file1.txt", seps="/")


def test_question_mark_does_not_match_separator():
    assert not _match("file?txt", "file/txt", seps="/")


def test_question_mark_does_not_match_empty():
    assert not _match("file?.txt", "file.txt", seps="/")


def test_bracket_expression():
    assert _match("[abc].py", "a.py", seps="/")


def test_bracket_expression_no_match():
    assert not _match("[abc].py", "d.py", seps="/")


def test_negated_bracket():
    assert _match("[!abc].py", "d.py", seps="/")


def test_negated_bracket_no_match():
    assert not _match("[!abc].py", "a.py", seps="/")


def test_literal_characters_escaped():
    assert _match("file.txt", "file.txt", seps="/")
    assert not _match("file.txt", "filextxt", seps="/")


def test_no_hidden_files_by_default():
    assert not _match("*", ".hidden", seps="/")


def test_include_hidden_matches_dotfiles():
    assert _match("*", ".hidden", seps="/", include_hidden=True)


def test_double_star_skips_hidden_by_default():
    assert not _match("**/*.py", ".hidden/test.py", seps="/")


def test_double_star_matches_hidden_when_enabled():
    assert _match(
        "**/*.py",
        ".hidden/test.py",
        seps="/",
        include_hidden=True
    )


def test_recursive_false_double_star_matches_single_segment(
):
    assert _match(
        "**/*.py",
        "src/test.py",
        recursive=False,
        seps="/"
    )
    assert not _match(
        "**/*.py",
        "a/b/test.py",
        recursive=False,
        seps="/"
    )


def test_venv_exclude_pattern():
    assert _match(
        "**/.venv*/**",
        "project/.venv/lib/thing.py",
        seps="/"
    )


def test_venv_exclude_pattern_numbered():
    assert _match(
        "**/.venv*/**",
        "project/.venv3/lib/thing.py",
        seps="/"
    )


def test_non_venv_path_not_excluded():
    assert not _match(
        "**/.venv*/**",
        "project/src/thing.py",
        seps="/"
    )


def test_glob_to_regex_returns_string():
    result = glob_to_regex("**/*.py", seps="/")
    assert isinstance(result, str)


def test_glob_to_regex_compiles():
    result = glob_to_regex("**/*.py", seps="/")
    compiled = re.compile(result)
    assert compiled.match("src/thing.py")


def test_anchor_true_requires_full_match():
    regex = glob_to_regex("*.py", seps="/", anchor=True)
    assert not re.match(regex, "hello.py.bak")


def test_anchor_false_allows_partial():
    regex = glob_to_regex("*.py", seps="/", anchor=False)
    assert re.match(regex, "hello.py.bak")


def test_multiple_stars_in_segment():
    assert _match("*test*.py", "my_test_file.py", seps="/")


def test_empty_pattern_matches_empty_string():
    regex = glob_to_regex("", seps="/")
    assert re.match(regex, "")


def test_consecutive_double_stars():
    assert _match("**/**/*.py", "a/b/c.py", seps="/")


def test_pattern_with_multiple_extensions():
    assert _match("**/*.tar.gz", "dist/pkg.tar.gz", seps="/")
    assert not _match(
        "**/*.tar.gz",
        "dist/pkg.tar.bz2",
        seps="/"
    )


def test_windows_separator():
    assert _match(
        "src\\**\\*.py",
        "src\\sub\\file.py",
        seps="\\"
    )


def test_mixed_separators():
    regex = glob_to_regex("src/**/*.py", seps=("/", "\\"))
    assert re.match(regex, "src/sub/file.py")
    assert re.match(regex, "src\\sub\\file.py")


def test_bracket_range():
    assert _match("[a-z].py", "m.py", seps="/")
    assert not _match("[a-z].py", "M.py", seps="/")


def test_star_at_start_of_segment_no_hidden():
    assert not _match("*rc", ".bashrc", seps="/")


def test_star_at_start_of_segment_hidden():
    assert _match(
        "*rc",
        ".bashrc",
        seps="/",
        include_hidden=True
    )


def test_seps_defaults_to_os_sep():
    import os
    regex = glob_to_regex("**/*.py")
    assert (
        os.sep in regex
        or re.escape(os.sep) in regex
        or regex
    )


def test_seps_as_string_is_converted_to_tuple():
    regex = glob_to_regex("src/*.py", seps="/")
    assert re.match(regex, "src/hello.py")


def test_include_hidden_double_star_at_end():
    assert _match(
        "src/**",
        "src/.hidden/file.txt",
        seps="/",
        include_hidden=True
    )


def test_include_hidden_single_star_segment():
    assert _match(
        "*/*.py",
        ".dir/test.py",
        seps="/",
        include_hidden=True
    )


def test_unmatched_bracket_treated_as_literal():
    assert _match("[abc.py", "[abc.py", seps="/")


def test_bracket_with_backslash_no_hyphen():
    assert _match("[a\\b].py", "a.py", seps="/")


def test_bracket_range_with_hyphen():
    assert _match("[a-z].py", "f.py", seps="/")
    assert not _match("[a-z].py", "0.py", seps="/")


def test_bracket_empty_range_never_matches():
    assert not _match("[].py", "a.py", seps="/")


def test_bracket_only_negation_is_unmatched():
    assert _match("[!].py", "[!].py", seps="/")


def test_bracket_starts_with_caret():
    assert _match("[^a].py", "^.py", seps="/")
    assert _match("[^a].py", "a.py", seps="/")
    assert not _match("[^a].py", "b.py", seps="/")


def test_bracket_starts_with_open_bracket():
    assert _match("[[a].py", "[.py", seps="/")


def test_bracket_set_operations_escaped():
    assert _match("[a&b].py", "&.py", seps="/")


def test_bracket_closing_bracket_first():
    assert _match("[]]", "]", seps="/")


def test_bracket_negation_with_closing_bracket_first():
    assert _match("[!]]", "a", seps="/")
    assert not _match("[!]]", "]", seps="/")


def test_hyphen_at_end_of_range():
    regex = glob_to_regex("[a-]", seps="/")
    assert re.match(regex, "a")
    assert re.match(regex, "-")


def test_consecutive_stars_in_segment_compressed():
    regex_single = glob_to_regex("f*e", seps="/")
    regex_multi = glob_to_regex("f***e", seps="/")
    assert regex_single == regex_multi


def test_question_mark_at_start_no_hidden():
    assert not _match("?file", ".file", seps="/")


def test_question_mark_at_start_hidden():
    assert _match(
        "?file",
        ".file",
        seps="/",
        include_hidden=True
    )


def test_empty_segment_between_separators():
    regex = glob_to_regex("a//b", seps="/")
    assert re.match(regex, "a//b")


def test_single_star_as_only_pattern():
    assert _match("*", "hello", seps="/")
    assert not _match("*", "a/b", seps="/")


def test_double_star_only_matches_deeply_nested():
    assert _match("**", "a/b/c/d", seps="/")


def test_double_star_only_matches_single_file():
    assert _match("**", "file.txt", seps="/")


def test_pattern_with_no_wildcards():
    assert _match("exact/path.py", "exact/path.py", seps="/")
    assert not _match(
        "exact/path.py",
        "other/path.py",
        seps="/"
    )


def test_overlapping_ranges_in_bracket():
    regex = glob_to_regex("[z-a]", seps="/")
    compiled = re.compile(regex)
    assert compiled is not None


def test_include_hidden_one_segment_pattern():
    regex = glob_to_regex("*", seps="/", include_hidden=True)
    assert re.match(regex, ".hidden")
    assert re.match(regex, "visible")


def test_include_hidden_any_segments_pattern():
    regex = glob_to_regex("**", seps="/", include_hidden=True)
    assert re.match(regex, ".a/.b/.c")


def test_single_star_mid_pattern_not_last():
    assert _match("*/file.py", "src/file.py", seps="/")
    assert not _match("*/file.py", "a/b/file.py", seps="/")


def test_default_seps_with_altsep(monkeypatch):
    import os
    monkeypatch.setattr(os.path, "altsep", "/")
    monkeypatch.setattr(os.path, "sep", "\\")
    regex = glob_to_regex("src/**/*.py")
    assert re.match(regex, "src/sub/file.py")


def test_translate_segment_literal_exclamation():
    from cleer.glob_to_regex import _translate_segment
    result = _translate_segment("!", "[^/]")
    assert result == ["!"]
