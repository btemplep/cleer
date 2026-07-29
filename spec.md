# cleer

This project is cleer.  A file formatter that primarily uses tokenizers, whose tokens are passed to formatters, then the Cleer class collects these all.  The Cleer class is the primary API for cleer. 

I need to start filling out the tokenizers and formatters. 


## New General Guides

- Should use as granular of a tokenizer as possible in order to more easily identity tokens for violations
- validators will check for valid files

d
- nest invalidations into included? 
    - need to finish this in cleer and types docstrings

- formatter result, always include document as str|None??



inspect verbose, condensed 
- inspections are included files
- inspections are validated files
```json
{
    "inspections": [
        {
            "path": "/path/to/here.py",
            "included": [
                {
                    "group": 0,
                    "pattern": "**/*.py"
                }
            ],
            "excluded": [
                {
                    "group": 0,
                    "pattern": "**/*.py"
                }
            ],
            "violations": [
                {
                    "start_index": 1,
                    "length": 1,
                    "group": 0,
                    "stage": 0,
                    "formatter": 10,
                    "message": "Must do this or else."
                }
            ],
            "invalidations": [
                {
                    "group": 0,
                    "validator": 0,
                    "message": "The file has a syntax error: Bad syntax."
                }
            ]
        }
    ]
}
```

```json
{
    "inspections": [
        {
            "path": "/path/to/here.py",
            "included": [
                {
                    "group": 0,
                    "pattern": "**/*.py",
                    "invalidation": { // or null
                        "validator": 0,
                        "message": "bad syntax"
                    }
                }
            ],
            "excluded": [
                {
                    "group": 0,
                    "pattern": "**/*.py"
                }
            ],
            "violations": [
                {
                    "start_index": 1,
                    "length": 1,
                    "group": 0,
                    "stage": 0,
                    "formatter": 10,
                    "message": "Must do this or else."
                }
            ],
            "invalidations": [
                {
                    "group": 0,
                    "validator": 0,
                    "message": "The file has a syntax error: Bad syntax."
                }
            ]
        }
    ]
}
```


Format most verbose:
```json
{
    "formatted": [
        {
            "path": "/path/to/here.py",
            "included": [
                {
                    "group": 0,
                    "pattern": "**/*.py"
                }
            ],
            "invalidations": [
                {
                    "group": 0,
                    "validator": "PythonSyntaxValidator",
                    "message": "The file has a syntax error: Bad syntax."
                }
            ]
        }
    ],
    "excluded": [
        {
            "path": "/path/to/here.py",
            "groups": [
                {
                    "group": 0,
                    "pattern": "**/*.py"
                }
            ]
        }
    ]
}
```


## Formatting Rules

### General Rules

- End of file space formatter
    - set number of spaces
    - default 1
- start of file space formatter
    - set number of spaces
    - default 0
- max blank lines in a row
    - set max number of blank lines in a row
    - default 2
- non-ascii whitespace should not exist
- no trailing whitespace on lines



### Python Specific Rules

- one space in a row max, outside of indent and string literals.
- Binary operators should have one space around them on each side
- specific unary operators should not have space between them and the variable
    - "negative" (-)
- indent with spaces, tab size is 4 spaces
- default string quote style
    - set to " or ' separately for
        - string literals
        - dict key lookup
    - multiline """ or '''
- comma separated values
    - no space before
    - one space after, or newline
    - set to have a trailing comma, or remove it
        - except for one value items like python tuples
        - for loop vars never have trailing comma
- functions/methods
    - inside of functions and methods should be a max of 1 blank line in a row
    - 2 blank lines before and after functions, except nested functions
    - 1 blank line before and after nested functions
- no space between = for python default kwargs defs, and python function calls with kwargs
- docstring 
    - should exist at top of all modules with one blank line following
    - No blank lines between docstring and preceding definition (class, func, var, etc)
    - no blank lines between docstrings and following function code
    - no blank line between class docstring and class vars
    - 2 blank lines between class docstring and methods
    - 1 indent level in for classes and functions
    - same level for variables and modules
- __all__ should be in all modules that belong to a packages
    - one blank line before and after
    - one item per line if there is more than 0 items
    - sort alphabetically
    - only capture the first instance of all that is a list of strings.
- imports section
    - Should be separated into 4 blocks, that are separated by a space, in this order
        - std lib
        - 3rd party (pypi)
        - Internal Libraries (private repo)
        - The current package
    - Each block should be sorted alphabetically
    - If more than 3 import or import from items in a line, then it should be multi-line with one per line
    - 1 blank line before, 2 blank lines after an imports section
    - items in a multi import or import from statement are sorted alphabetically
    - condense imports??
- paired punctuation
    - excludes __all__ and type hints
    - first step of all paired punctuation is to flatten it. 
    - no space between paired punctuation and inner values if they are on the same line
    - dicts that have more than 0 items, are always expanded
    - dict colons have no space before, and one space after
    - Lists, sets, or tuples that are not nested, 
        - should be flattened
        - if the list, set, or tuple itself is over 30 chars, then expand.
    - nested lists, sets, or tuples (inside of another list, dict, set, tuple) are expanded if more than 0 items
        - if any are expanded then they all are expanded, unless empty
    - for loop vars are never expanded
    - function definitions
        - first flatten
        - expand if any of the following
            - over 80 characters not including indent
            - over 100 chars including indent
            - over 4 args
            - any inner paired punct is expanded
        - if any sub items are expanded
        - never split empty args
        - if any are expanded then they all are expanded, unless empty
    - function calls
        - first flatten
        - expand if any of the following
            - over 60 characters not including indent
            - over 80 chars including indent
            - over 4 args
            - any inner paired punct is expanded
        - never split empty args
        - if any are expanded then they all are expanded, unless empty
    - decorators
        - flatten first
        - expand if any of the following
            - Over 4 args,
            - more than 60 chars not including indent
            - over 80 chars including indent
            - any inner paired punct is expanded
        - no blank lines between decorator and following code (class, func, etc)
        - never split empty args
        - if any are expanded then they all are expanded, unless empty
    - logic blocks
        - statements are separated by `or` and `and`
        - First flatten
        - expand if any of the following
            - more than 2 statements
            - length is over 60 without indent
            - length is over 80 with indent
            - any inner paired punct is expanded
        - if expanded should add parenthesis around them
            - Add parenthesis to clarify order of operations
- end of if/elif/else and try/except/finally blocks always have a blank line following them
    - If multiple end it should only be one blank line total
- no blank lines between indent block (class, func, if, for etc) and inner code
- classes
    - no blank lines between class declaration, docstring, class vars, or pass
    - 2 blank lines before and after class
- returns
    - returns have a blank line before them unless they are the only statement in that code block
- yields
    - have a blank like before unless they are the only statement in that code block
    - blank line after if there is another statement in the same code block
Type hints
    - no space before colon, one space after
    - First flatten
    - Don't expand unless one of the following happen, in this order:
        - A Single non-nested statement is over 40 chars, not including indent just type and brackets
        - Any non expanded section is over 2 types/brackets deep, expand that started at the most external, non-expanded section


## Rule Tokenizers and Formatters


### General Rules
- [x] End of file space formatter
    - set number of spaces
    - default 1
- [x] start of file space formatter
    - set number of spaces
    - default 0
- [x] max blank lines in a row
    - set max number of blank lines in a row
    - default 2
- [x] non-ascii whitespace should not exist
- [x] no trailing whitespace on lines


### Python Specific Rules

- [ ] one space in a row max, outside of indent and string literals.
- [ ] Binary operators should have one space around them on each side
- [ ] specific unary operators should not have space between them and the variable
    - "negative" (-)
- [ ] indent with spaces, tab size is 4 spaces
- [ ] default string quote style
    - set to " or ' separately for
        - string literals
        - dict key lookup
    - multiline """ or '''
- [ ] comma separated values
    - no space before
    - one space after, or newline
    - set to have a trailing comma, or remove it
        - except for one value items like python tuples
        - for loop vars never have trailing comma
- [ ] functions/methods
    - [ ] inside of functions and methods should be a max of 1 blank line in a row
    - [x] 2 blank lines before and after functions, except nested functions
    - [ ] 1 blank line before and after nested functions
- [ ] no space between = for python default kwargs defs, and python function calls with kwargs
- [ ] docstring 
    - should exist at top of all modules with one blank line following
    - No blank lines between docstring and preceding definition (class, func, var, etc)
    - no blank lines between docstrings and following function code
    - no blank line between class docstring and class vars
    - 2 blank lines between class docstring and methods
    - 1 indent level in for classes and functions
    - same level for variables and modules
- [ ] __all__ should be in all modules that belong to a packages
    - one blank line before and after
    - one item per line if there is more than 0 items
    - sort alphabetically
    - only capture the first instance of all that is a list of strings.
- [ ] imports section
    - Should be separated into 4 blocks, that are separated by a space, in this order
        - std lib
        - 3rd party (pypi)
        - Internal Libraries (private repo)
        - The current package
    - Each block should be sorted alphabetically
    - If more than 3 import or import from items in a line, then it should be multi-line with one per line
    - 1 blank line before, 2 blank lines after an imports section
    - items in a multi import or import from statement are sorted alphabetically
    - condense imports??
- [ ] paired punctuation
    - excludes __all__ and type hints
    - first step of all paired punctuation is to flatten it. 
    - no space between paired punctuation and inner values if they are on the same line
    - dicts that have more than 0 items, are always expanded
    - dict colons have no space before, and one space after
    - Lists, sets, or tuples that are not nested, 
        - should be flattened
        - if the list, set, or tuple itself is over 30 chars, then expand.
    - nested lists, sets, or tuples (inside of another list, dict, set, tuple) are expanded if more than 0 items
        - if any are expanded then they all are expanded, unless empty
    - for loop vars are never expanded
    - function definitions
        - first flatten
        - expand if any of the following
            - over 80 characters not including indent
            - over 100 chars including indent
            - over 4 args
            - any inner paired punct is expanded
        - if any sub items are expanded
        - never split empty args
        - if any are expanded then they all are expanded, unless empty
    - function calls
        - first flatten
        - expand if any of the following
            - over 60 characters not including indent
            - over 80 chars including indent
            - over 4 args
            - any inner paired punct is expanded
        - never split empty args
        - if any are expanded then they all are expanded, unless empty
    - decorators
        - flatten first
        - expand if any of the following
            - Over 4 args,
            - more than 60 chars not including indent
            - over 80 chars including indent
            - any inner paired punct is expanded
        - [x] no blank lines between decorator and following code (class, func, etc)
        - never split empty args
        - if any are expanded then they all are expanded, unless empty
    - logic blocks
        - statements are separated by `or` and `and`
        - First flatten
        - expand if any of the following
            - more than 2 statements
            - length is over 60 without indent
            - length is over 80 with indent
            - any inner paired punct is expanded
        - if expanded should add parenthesis around them
            - Add parenthesis to clarify order of operations
    - Type hints
        - no space before colon, one space after
        - First flatten
        - Don't expand unless one of the following happen, in this order:
            - A Single non-nested statement is over 40 chars, not including indent just type and brackets
            - Any non expanded section is over 2 types/brackets deep, expand that started at the most external, non-expanded section
- [ ] end of if/elif/else and try/except/finally blocks always have a blank line following them
    - If multiple end it should only be one blank line total
- [ ] no blank lines between indent block (class, func, if, for etc) and inner code
- [ ] classes
    - no blank lines between class declaration, docstring, class vars, or pass
    - 2 blank lines before and after class
- [ ] returns
    - returns have a blank line before them unless they are the only statement in that code block
- [ ] yields
    - have a blank like before unless they are the only statement in that code block
    - blank line after if there is another statement in the same code block



