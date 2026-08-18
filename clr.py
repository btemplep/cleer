"""clr conf"""

from cleer import Cleer, cleer_default_config


clr = Cleer(
    config=cleer_default_config(
        python_packages=["cleer"],
        python_internal_packages=[],
        add_excludes=[
            "**/tests/unit/fixtures/format_*.py"
        ]
    )
)
