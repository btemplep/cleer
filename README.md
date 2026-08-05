# cleer

cleer is a file formatter that is customizable and easy to extend. 

It was primarily made for python (in python), but can work with any language. 

It has a set of defaults that I have chosen for a specific and readable style.  It does not try to make the smallest git diffs, but he most readable code in general.  Objectively speaking of course (I like the formatting).


## Installation

``console
pip install cleer
```

## Tutorial

### Quickstart

Out of the box it comes with a CLI.

Use `--help`on the base or any commands for all options.

``onsole
cleer --help
```

It has 2 main commands:
- inspect - JSON output of the formatting violations
- format - format files in place

You can use them both on a single file or a all files/dirs in a directory. 

``onsole
cleer inspect path/to/file.py
```

``onsole
cleer inspect path/to/dir/
```

Output example for inspect:

``son
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

Format files in place:
``onsole
cleer format path/to/file.py
```

Inspect or format with specific config and log level
``onsole
cleer format --log-level DEBUG --cleer python_path.to.my_file:my_cleer_instance  path/to/file.py
```

Formatters for python packages are recommended to create a `clr.py` file in the root of the project. 

If the package can by imported as "my_package", and you just want the default formatting:

``ython
"""clr.py"""

from cleer import cleer_default


clr = cleer_default(current_packages=["my_package"])
```

This will ensure that imports are properly grouped and sorted.


### Configuration

The chain of configuration is as follows:
1. If a custom cleer instance is given with the `--cleer` argument.
2. The default python path of `clr:clr`.
3. A default configuration is generated.


Example of custom `Cleer` instance/config:

``ython
from cleer import *


# use the defaults with minimal input
clr = cleer_default(current_packages=["my_package"], internal_packages=["my_other_private_package"])
# create your own config from scratch
clr = Cleer(
    config={
        "groups": [ # Groups are collections of formatting stages
            {
                "includes": ["**/*.py"], # A group uses glob style include and exclude patterns to determine which files be collected
                "excludes": [
                    "**/.venv*/**",
                    "**/venv*/**"
                ],
                "stages": [ # stages are run in serial to format or inspect documents
                    {
                        "tokenizer": LineTokenizer(), # each stage has a tokenizer, that will tokenize and iterate through the tokens
                        "formatters": [ # formatters are all run in order on each token. 
                            TrailingWhitespaceFormatter(),
                        ]
                    }
                ]
            }
        ]
    }
)
```


### Logging

`cleer` uses standard python logging levels.  By default it is set to `CRITICAL`. You can change this with the `--log-level` argument.

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`


### Run with VSCode

You can automatically format on save in vscode by installing the (Run On Save)[https://marketplace.visualstudio.com/items?itemName=emeraldwalk.RunOnSave] extension and adding a config like this under `.vscode/settings.json`:

``son
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

Update the path to cleer to where ever you installed cleer at. 


## Programmatic API

The `cleer` CLI is a thin wrapper around the `Cleer` class. 

You can directly call different inspect and format options on the `Cleer` class instance.

``ython
import pathlib

from cleer import *


# get a default instance, set some configs
clr = cleer_default(current_packages=["my_package"], internal_packages=["my_internal_pkg"])
# Or create your own instance from scratch
clr = Cleer(
    config={
        "groups": [
            {
                "includes": ["**/*.py"],
                "excludes": [
                    "**/.venv*/**",
                    "**/venv*/**"
                ],
                "stages": [
                    {
                        "tokenizer": LineTokenizer(),
                        "formatters": [
                            TrailingWhitespaceFormatter(),
                        ]
                    }
                ]
            }
        ]
    }
)

# inspect a document string for violations
violations = clr.inspect_str("x = 1   \n", "my_pkg/thing.py") 
# note that even for strings you have to pass a "file name"
# this is so that the "file" can be picked up by the matching config groups. 
# [
#     {
#         "start_index": 29,
#         "length": 20,
#         "message": "Lines should not have any trailing whitespace."
#     }
# ]


# inspect a file pointer
with open("thing.py", "r") as fp:
    violations = clr.inspect_fp(fp, "my_pkg/thing.py")
# note that even for strings you have to pass a "file name"
# this is so that the "file" can be picked up by the matching config groups. 
# [
#     {
#         "start_index": 29,
#         "length": 20,
#         "message": "Lines should not have any trailing whitespace."
#     }
# ]

# inspect a file by path
violations = clr.inspect_file("my_pkg/thing.py")
# [
#     {
#         "start_index": 29,
#         "length": 20,
#         "message": "Lines should not have any trailing whitespace."
#     }
# ]

# inspect all matching files in a directory
results = clr.inspect_dir(pathlib.Path("./"))
# [
#     {
#         "path": "my_pkg/thing.py",
#         "violations": [
#             {
#                 "start_index": 29,
#                 "length": 20,
#                 "message": "Lines should not have any trailing whitespace."
#             }
#         ]
#     }
# ]

# inspect a path (file or directory, auto-detected)
# this is what is used by the CLI to take either
results = clr.inspect_path("my_pkg/")
# for files, one entry at most will be returned.
# [
#     {
#         "path": "my_pkg/thing.py",
#         "violations": [
#             {
#                 "start_index": 29,
#                 "length": 20,
#                 "message": "Lines should not have any trailing whitespace."
#             }
#         ]
#     }
# ]

# format a document string (returns the formatted string)
formatted = clr.format_str("x = 1   \n", "my_pkg/thing.py")

# format a file pointer in place
with open("thing.py", "r+") as fp:
    clr.format_fp(fp, "my_pkg/thing.py")

# format a file in place by path
clr.format_file("my_pkg/thing.py")

# format all matching files in a directory in place
clr.format_dir(pathlib.Path("./"))

# format a path (file or directory, auto-detected)
# this is what is used by the CLI to take either
clr.format_path("my_pkg/")
```
