"""Unit tests for the cleer_default function."""

import pathlib

from cleer import Cleer, cleer_default


def test_returns_cleer_instance():
    result = cleer_default()

    assert isinstance(result, Cleer)


def test_accepts_internal_packages_parameter():
    result = cleer_default(internal_packages="mypackage")

    assert isinstance(result, Cleer)


def test_can_format_simple_file(tmp_path):
    clr = cleer_default(current_packages=["my_pkg"])
    file_path = tmp_path / "test.py"
    file_path.write_text("x = 1   \n")
    clr.format_file(file_path)

    assert file_path.read_text() == "x = 1\n"
