import pathlib

from cleer import cleer_default


FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"
FILE_PATH = "src/test.py"


def test_format_bad_to_good():
    clr = cleer_default(internal_packages=["my_pkg"], current_packages=["cleer"])
    bad = (FIXTURES_DIR / "format_bad.py").read_text()
    good = (FIXTURES_DIR / "format_good.py").read_text()
    formatted = clr.format_str(bad, FILE_PATH)

    assert formatted == good


def test_format_bad2_to_good2():
    clr = cleer_default(internal_packages=["my_pkg"], current_packages=["cleer"])
    bad = (FIXTURES_DIR / "format_bad2.py").read_text()
    good = (FIXTURES_DIR / "format_good2.py").read_text()
    formatted = clr.format_str(bad, FILE_PATH)

    assert formatted == good


def test_format_bad3_to_good3():
    clr = cleer_default(internal_packages=["my_pkg"], current_packages=["cleer"])
    bad = (FIXTURES_DIR / "format_bad3.py").read_text()
    good = (FIXTURES_DIR / "format_good3.py").read_text()
    formatted = clr.format_str(bad, FILE_PATH)

    assert formatted == good


def test_format_good_is_idempotent():
    clr = cleer_default(internal_packages=["my_pkg"], current_packages=["cleer"])
    good = (FIXTURES_DIR / "format_good.py").read_text()
    formatted = clr.format_str(good, FILE_PATH)

    assert formatted == good


def test_format_good2_is_idempotent():
    clr = cleer_default(internal_packages=["my_pkg"], current_packages=["cleer"])
    good = (FIXTURES_DIR / "format_good2.py").read_text()
    formatted = clr.format_str(good, FILE_PATH)

    assert formatted == good


def test_format_good3_is_idempotent():
    clr = cleer_default(internal_packages=["my_pkg"], current_packages=["cleer"])
    good = (FIXTURES_DIR / "format_good3.py").read_text()
    formatted = clr.format_str(good, FILE_PATH)

    assert formatted == good


def test_format_good_no_violations():
    clr = cleer_default(internal_packages=["my_pkg"], current_packages=["cleer"])
    good = (FIXTURES_DIR / "format_good.py").read_text()
    violations = clr.inspect_str(good, FILE_PATH)

    assert violations == []


def test_format_good2_no_violations():
    clr = cleer_default(internal_packages=["my_pkg"], current_packages=["cleer"])
    good = (FIXTURES_DIR / "format_good2.py").read_text()
    violations = clr.inspect_str(good, FILE_PATH)

    assert violations == []


def test_format_good3_no_violations():
    clr = cleer_default(internal_packages=["my_pkg"], current_packages=["cleer"])
    good = (FIXTURES_DIR / "format_good3.py").read_text()
    violations = clr.inspect_str(good, FILE_PATH)

    assert violations == []
