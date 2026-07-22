from cleer import cleer_default


clr = cleer_default(
    current_packages=["cleer"],
    internal_packages=["my_pkg"],
    python_excludes=["**/tests/unit/fixtures/format_*.py"]
)
