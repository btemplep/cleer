import pytest

from cleer import Formatter


def test_inspect_raises_not_implemented():
    with pytest.raises(NotImplementedError, match="inspect"):
        Formatter().inspect("test")


def test_format_raises_not_implemented():
    with pytest.raises(NotImplementedError, match="format"):
        Formatter().format("test")
