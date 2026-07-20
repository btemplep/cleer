import sys

import nox


nox.options.sessions = ["unit-tests-versions"]


@nox.session(name="publish-package")
def publish(session: nox.Session):
    """Build a new src and wheel and publish to PYPI
    """
    dev_venv_setup(session=session)
    session.run(
        "rm",
        "-rf",
        "./build/",
        "./dist/",
        external=True
    )
    session.run(
        "python",
        "-m",
        "build",
        "--sdist",
        "--wheel"
    )
    session.run(
        "twine",
        "upload",
        "dist/*",
        "--repository",
        "cleer"
    )


@nox.session(
    name="unit-tests",
    python=False
)
def unit_tests(session: nox.Session):
    """Run tests with current python version and generate html coverage report.
    """
    session.run("coverage", "erase")
    session.run(
        "pytest",
        "-vvv",
        "--cov=src/cleer",
        "--cov-report",
        "html",
        "--cov-report",
        "term",
        "tests/unit"
    )


@nox.session(
    name="unit-tests-versions",
    python=[
        "3.11",
        "3.12",
        "3.13",
        "3.14"
    ]
)
def unit_tests_versions(session: nox.Session):
    """Run tests with all specified python version and generate missing coverage report in terminal.
    """
    dev_venv_setup(session=session)
    session.run("coverage", "erase")
    session.run(
        "pytest",
        "-vvv",
        "--cov=src/cleer",
        "--cov-report",
        "term-missing",
        "tests/unit"
    )


def dev_venv_setup(session: nox.Session):
    session.install(
        "-U",
        "pip",
        "build"
    )
    session.install("-e", ".[dev,all]")
