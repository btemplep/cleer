# cleer

The rules are cleer... or at least that was the idea.

cleer is a customizable and extensible file formatter. Primarily made for Python (in Python), but works with any language.

It has a set of defaults that I have chosen for a specifically readable style.  It does not try to make the smallest git diffs, but the most readable code.  Objectively speaking of course (I like the formatting).


## Installation

```console
pip install cleer
```


## CLI

The CLI is the primary interface. Use `--help` on the base or any command for all options.

```console
cleer --help
```

Two main commands:

- `inspect` — JSON output of formatting violations
- `format` — format files in place

Both work on a single file or all matching files in a directory.

```console
cleer inspect path/to/file.py
cleer inspect path/to/dir/
cleer format path/to/file.py
cleer format path/to/dir/
```

### Inspect output

```json
[
    {
        "path": "/full/path/to/file.py",
        "violations": [
            {
                "start_index": 49,
                "length": 22,
                "message": "Lines should not have any trailing whitespace."
            }
        ]
    }
]
```

### Format output

```json
[
    {
        "path": "/full/path/to/file.py"
    }
]
```


### Custom config

```console
cleer format --cleer python_path.to.my_file:my_cleer_instance path/to/file.py
```


### Options

```console
cleer format --log-level DEBUG --verbose --keep-excluded --keep-no-match path/to/dir/
```

- `--log-level` — Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: ERROR.
- `--verbose` — Include `included`, `excluded`, and `invalidations` in output.
- `--keep-excluded` — Include results for files that matched a group but were excluded.
- `--keep-no-match` — Include results for files that did not match any groups.


### Config resolution

1. Custom instance from `--cleer` argument.
2. Default path `clr:clr`. A `clr.py` file in the current directory with a `clr` variable.  The `clr` variable should be an instance of the `Cleer`.
3. Auto-generated default configuration. See [Default Rules](./rules.md).


## Configuration

Create a `clr.py` file in the root of your project. 
For the easiest start use the `cleer_default_config` generator to create a default config with some tweaks exposed. 

```python
"""clr.py"""

from cleer import cleer_default_config, Cleer


clr = Cleer(config=cleer_default_config(python_packages=["my_package"]))
```

For the most control, you can create you formatting config from scratch. 

```python
from cleer import *


clr = Cleer(
    config={
        "groups": [
            {
                "includes": [
                    "**/*.py"
                ],
                "excludes": [
                    "**/.venv*/**",
                    "**/venv*/**"
                ],
                "stages": [
                    {
                        "tokenizer": LineTokenizer(),
                        "formatters": [
                            TrailingWhitespaceFormatter()
                        ]
                    }
                ]
            }
        ]
    }
)
```


## VSCode Integration

Auto-format on save with the [Run On Save](https://marketplace.visualstudio.com/items?itemName=emeraldwalk.RunOnSave) extension.

`.vscode/settings.json`:

```json
{
    "emeraldwalk.runonsave": {
        "commands": [
            {
                "cmd": "./venv/bin/cleer format --log-level DEBUG ${file}"
            }
        ]
    }
}
```


## Programmatic API

The CLI is a thin wrapper around the `Cleer` class. You can use it directly:

```python
import pathlib

from cleer import Cleer, cleer_default_config


clr = Cleer(config=cleer_default_config(python_packages=["my_package"]))

# Inspect a string — path is only used for glob matching
result = clr.inspects("my_pkg/thing.py", "x = 1   \n")
# {
#     "path": "my_pkg/thing.py",
#     "included": [{"group": 0, "pattern": "**/*.py"}],
#     "excluded": [],
#     "invalidations": [],
#     "violations": [
#         {
#             "start_index": 0,
#             "length": 9,
#             "group": 0,
#             "stage": 0,
#             "formatter": 0,
#             "message": "Lines should not have any trailing whitespace."
#         }
#     ]
# }

# Inspect a file or directory
results = clr.inspect("my_pkg/")
# [{"path": ..., "violations": [...]}, ...]

# Format a string — returns result with formatted document
result = clr.formats("my_pkg/thing.py", "x = 1   \n")
# {
#     "path": "my_pkg/thing.py",
#     "included": [{"group": 0, "pattern": "**/*.py"}],
#     "excluded": [],
#     "invalidations": [],
#     "document": "x = 1\n"
# }

# Format a file or directory in place
results = clr.format("my_pkg/")
# [{"path": ..., "included": [...], "excluded": [], "invalidations": []}, ...]
```
