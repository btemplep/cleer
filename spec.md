# cleer

This project is cleer.  A file formatter that primarily uses tokenizers, whose tokens are passed to formatters, then the Cleer class collects these all.  The Cleer class is the primary API for cleer. 

I need to start filling out the tokenizers and formatters. 


## New General Guides

- Should use as granular of a tokenizer as possible in order to more easily identity tokens for violations
- validators will check for valid files


## Formatting Rules

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

- [x] one space in a row max, outside of indent and string literals.
- [x] Binary operators should have one space around them on each side
    - not including function default kwargs, or function call kwargs. Should be a default of 0
- [x] specific unary operators should not have space between them and the variable
    - "negative" (-)
- [x] indent with spaces, tab size is 4 spaces
- [x] default string quote style
    - set to " or ' separately for
        - string literals
        - dict key lookup
    - multiline """ or '''
- [x] colons for type hints, dictionaries etc
    - no space before
    - one space after
- [x] comma separated values
    - no space before
    - one space after, or newline
    - set to have a trailing comma, or remove it
        - default, no trailing comma
        - except for one value items like python tuples
        - for loop vars never have trailing comma
- [x] functions/methods
    - inside of functions and methods should be a max of 1 blank line in a row
    - 2 blank lines before and after functions, except nested functions
    - 1 blank line before and after nested functions
- [x] __all__ 
    - should be in all modules that belong to a packages
        - Take a var for current_packages, by default None
    - one blank line before and after
    - one item per line if there is more than 0 items
    - sort alphabetically
    - only applies formatting to the first instance of __all__ in a module. Ignore other times it is assigned.
- [x] imports section
    - Should be separated into 4 blocks, that are separated by a space, in this order
        - std lib
        - 3rd party (pypi)
        - Internal Libraries (private repo)
        - The current package
    - an imports section is sequential lines of code that only have import statements or blank lines
    - Should take a list of internal package names and current package names, by default none
    - Each block should be sorted alphabetically
    - flatten each import, if more than 80 characters then it should be multi-line with one per line
    - 1 blank line before, 2 blank lines after an imports section
    - items in a multi import or import from statement are sorted alphabetically, as well.
- [ ] returns
    - returns have a blank line before them 
        - unless they are the only statement in that code block
    - returns have a at least one blank line after them.
- [ ] yields
    - have a blank like before unless they are the only statement in that code block
    - have at least one blank line after it
- [ ] Type hints
    - no space before colon, one space after, add this to the existing colon checks if it makes sense
    - First flatten
    - Don't expand unless one of the following happen, in this order:
        - A Single non-nested statement is over 40 chars, not including indent just type and brackets
        - Any non expanded section is over 2 types/brackets deep, expand that started at the most external, non-expanded section



- [ ] docstring 
    - should exist at top of all modules with one blank line following
    - No blank lines between docstring and preceding definition (class, func, var, etc)
    - 2 blank lines between class docstring and methods
    - 1 indent level in for classes and functions
    - docstrings should be at same indent level for variables and modules
- [ ] no blank lines between indent block (if, for, while, etc) and inner code, excluding functions and classes
- [ ] classes
    - no blank lines between class declaration, docstring, class vars, or pass
    - 2 blank lines if it is a method definition
    - 2 blank lines before and after class, if not internal

- [ ] paired punctuation
    - excludes:
        - __all__
        - type hints
        - for loop variables like `x` and `y` in `for x,y in thing:`
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
            - more than one arg with at least one given as a kwarg
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
            - 
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
- [ ] end of if/elif/else and try/except/finally blocks
    - always have a blank line following them
        - If multiple end it should only be one blank line total
    - no blank lines between the in-between statements
        - except after a return statement, should be default 1 blank line
        - Can configure this 

