import pytest

from cleer import NoSpaceEqualsFormatter


def test_removes_spaces():
    formatter = NoSpaceEqualsFormatter()
    result = formatter.format(" = ")

    assert result == "="


def test_already_correct_unchanged():
    formatter = NoSpaceEqualsFormatter()
    result = formatter.format("=")

    assert result == "="


def test_inspect_detects_spaces():
    formatter = NoSpaceEqualsFormatter()
    result = formatter.inspect(" = ")

    assert result is not None
    assert "space" in result.lower()


def test_inspect_passes_correct():
    formatter = NoSpaceEqualsFormatter()
    result = formatter.inspect("=")

    assert result is None
