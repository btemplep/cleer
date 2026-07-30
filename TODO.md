# TODO


- [ ] slogan!  It's become cleer to me...
- [ ] update all docstring and README examples. 
- [ ] ClI should be default print less verbose json, flag for verbose
- [ ] cli flags for what values to keep in the results that match the API
- [ ] make sure tokenizers type hints for returns are correct
- [ ] logging should only be debug for formatters, validators, and tokenizers
- [x] config default generator instead of cleer class


## OLD

This project is cleer.  A file formatter that primarily uses tokenizers, whose tokens are passed to formatters, then the Cleer
instance updates the document accordingly. 


- [ ] Formatters
    - if no args in function call don't ever expand
    - special handler for string type of paired punctuation
    - ```("def func():\n" "    x = a or b or c\n")```
    - this should always be multi line if it is setup a string type paired punctuation
    - if lists are nested under other lists or dicts or tuple, always expand as well, unless empty
    - At this point I think you need to merge all the pair punctuation into one python specific formatter. just because all the different scenarios are so closely linked and the different formatters play with each other in weird ways. and it's not always clear how that is resold unless it is in just one formatter.  
        - the tokenizer can probably just take any any top level statement for paired punctuation, including indent. 
        - the formatter should first condense it all down to one properly formatted line
        - 
```python
result = subprocess.run([
            "cleer",
            "inspect",
            str(tmp_path)
        ], capture_output=True, text=True)
```

```python
if not (self._exclude_dict_keys and self._is_dict_key_context(document, i)):
```

```python
    pairs = [(
                "(",
                ")"
            ), (
                "[",
                "]"
            ), (
                "{",
                "}"
            )]
```

```python
for i, (
        s1,
        e1
    ) in enumerate(indices):
        for j, (
            s2,
            e2
        ) in enumerate(indices):
            if i != j:
                assert not (s1 < e2 and s2 < e1)
```

```python
def test_format_adds_newline_after_yield_with_following_statement(
):
```

- [ ] default cleer function should be for config, not class. That way they can easily update the config as needed.
- [ ] fix errors when formatting project
- [ ] 100% coverage


- [x] change function call formatting to be multi line if any of the follwoing
    - the length of the whole line without indent is over 60 characters
    - the length of the line with indent is over 100 characters
    - there is a multiline statement within the function call.
- [x] do the same for function definition formatting and non-nested paired punctuation
    - non-nested paired punctuation different rules for dicts.  if a dict has more than one entry always expand. Keep the rule that if a nested dict, always expand, unless empty. 
- [x] update so that python exclude patterns are taken with default_cleer
- [x] update to make glob.translate compatible with 3.11/12
- [x] update so that {} with at least one entry that are nested, should be expanded.
- [x] fix formatting with *, in good_format.py
- [x] before release
    - test coverage 100%
    - upload to github
- [x] vscode integration
    - vscode run on save extension to run it on save `cleer format ${file}`
    - Add to README
- [x] formatters
    - spacing formatters
        - outside of string literals/formatting, and excluding indent, there should be at max 1 space in a row
        - probably a tokenizer just for this, and a formatter
    - update formatter so that there is no extra space between these, only after that block
        - if, elif, else
        - try, except, finally
        
    - make sure that if a function call is nested under a punctuation pair and it is expanded to multiline, that the punctuation pair is also multi line formatted.
    - I updated tests/unit/fixtures/format_good3.py and bad3 with some cases for these
- [x] formatters
    - need to make sure that the paired punctuation and function definitions and calls split up args when over 100 characters including indent.
    - Type hints
        - no space between var and colon
        - on space between colon and type hint
        - should maintain the lowest level of multiline nesting, with the max nesting on a single line to be 2 levels
    - logic blocks like for if statements or variables with boolean logic values
        - making logic blocks multi line, involves added outer parenthesis if needed and splitting.
        - Should make multiline if there are more than 2 statements, or the length with indent is over 80
        - if any of the logic blocks are turned into multiline, make all statements in that logic block multiline
        - remove extra parenthesis if only one statement inside
        - Statements are separated by `and` and `or`
        - update the logic block character limit count from 80 to 100, if the indent is more than 2 levels
    - use the new files format_bad3.py and format_good3.py as what it should look like before and after.   Add those to the unit tests as well for regression testing. 
- [x] README
    - add examples for all methods in Cleer
- [x] check path formatting for cleer
    - should this always be full path, or just what was passed for files?
    - What about for dirs? 
- [x] update logging 
    - include group number when saying whether something is included or excluded
        - info level logs for inspect or formatting with group, file, glob pattern for include or exclude
    - DEBUG only inside tokes and fokes
- [x] formatters
    - formatting for list and dict comprehensions should be skipped by paired punctuation. 
- [x] formatters
    - formatting for list and dict comprehensions should be skipped by paired punctuation. 
- [x] formatters
    - new formatter to limit new lines.  Should only ever have at most 2 new lines between any item
    - when unindent happens, there should be at least one new line between that in the piece of code
        - function spacing takes care of this
        - needs to also work in for, while, if etc. 
        - multiple unindents do not need one per indent level
        - see difference between format_bad3.py and format_good3.py
    - test files within a project
        - Don't need __all__
        - need to be able to detect the package under test to properly format imports
        - or else we need a clr config that states what the current package is, along side the internal packages?
    - only modules within a package should enforce __all__
        - not needed for scripts or tests
- [x] violations exist win good format .py files
- [x] error when formatting all clr files it runs into a recursive loop or something
    - tokenizer `py_function_call_kwargs_equals_tokenizer.py`
    - running on format_bad3.py
- [x] User interface? 
    - CLI
    - just do a cleer.py for each one? 
        - CLI should pick up cleer.py by default or you can pass it
        - `cleer --config cleer.py:clr inspect <dir or file path>`
        - need a method to inspect and format a file in place just name it "inspect" and "format"
            - just combine inspect file and dir to inspect_path and it takes a file or dir
            - combine to clean up the api having both is redundant
            - what to name cleercfg.py
- [x] python logger without loguru
- [x] formatters
    - Class space between class declaration and first inner line should exclude `pass` and class vars.  There should be no newlines between class declaration and pass or class vars
    - update all code to have type hints
    - make sure binary operator formatter excludes chars when used as unary operators
        - `-1` negative 1 should stay formatted like that, and not like `- 1`
- [x] work through code and change to my style
- [x] update all inspection messages
- [x] Trailing comma formatter should not remove commas from python sets with a single item. 
- [x] add excludes patterns to config groups
    - change globs to includes
    - add field for excludes
    - update code so that andy match in excludes are not ran for that group
    - Add excludes to the default config for python to exclude venvs like `**/.venv*/` and `**/venv*/`
- [x] label tokenizer and formatters and Py if they are python only, and move to own folder
- [x] inline code blocks in docstrings should use single backticks for MyST format docstrings. 
- [x] I've also added the ability to pass strings to all cleer methods.  Add tests for each method to make sure strings work as well as Paths.
- [x] do tokenizers need to not overlap still??
    - I don't think they need that constraint unless set by the tokenizer. 
- [x] formatters
    - Tokenizer for space between func or class and docstring
        - Formatters
            - no new lines between class or functions and their docstrings
    - 2 new lines before and after class, except when end of file
        - Check class whitespace formatter - not working correctly
    - 2 new lines after end of import section
        - Already have the import section tokenizer
    - 2 new lines before and after all methods
        - Should be handled by FunctionSpaceFormatter - needs to always make sure there are 2 new lines before and after functions
        - may need to tokenize a different way to avoid overlap of tokens
    - 2 new lines after __all__
        - all_module formatter should take care of this
        - also needs to handle that __all__ is after a module docstring if it exists, and there is a space in between.
        - the after the __all__ is 2 new lines





- more formatters:
    - minimize use of whole file tokenizer for smaller tokenizer formatting violations
        - new tokenizers for whitespace at start and end of file
    - all formatters should indicate which tokenizers they can accept 
        - in the docstrings 
        - a class var called `accepts_token_types` and a list of strings
    - all tokenizers should indicate the token types they emit
        - in the docstrings
        - a class var called `emits_token_type`
    - the token types are not enforced in any way but purely to help identity compatibilty. 
    - more testing to reach 100% coverage. 
        - note that the Cleer class api was updated. 


This project is cleer.  A file formatter that primarily uses tokenizers, whose tokens are passed to formatters, then  the Cleer
instance updates the document accordingly.  I already have the Cleer class complete, and the base classes for Tokenizer and Formatter.
I need a new tokenizer and formatters. 

- how to structure class for groups
    - str ops just need a group
    - fp ops the same
    - file and dir ops need the whole list of groups for glob matching

- Can't run all ops on str and fp??!!?!?!?
    - should we have to pass the group every time? 
    - should we default to all
    - should we default to one
    - should we ask for the filename then glob pattern it? 

- how this would be used/configured with a CLI that could be:
    - configured with the tokenizers and formatters
    - Work on a whole dir
    - format on save. 

- Starting all over with the tokenizers and formatters.  Gonna go one by one here. with key points
    - make sure in docstrings for tokenizers to describe what whitespace is included with the tokens. 
    - try to show in the tokenize and class examples

- [x] need to filter single file and dir by glob pattern
    - glob does this automatically by using glob
        - need a way to just run a stage without checking the glob pattern
    - file will have to change glob pattern to regex(built in) then match it to the absolute path





- make sure that formatters format to the rule rather than trying to correct it in specific ways. 

- make sure to remove the class "Parameters" section from docstrings if no parameters. 
- mark formatters to say which types of tokens they can consume
- fill out tester.py cleer instance with all tokenizers and formatters


new tokenizer and formatter mappings:
- [x] line tokenizer  
    - all languages 
    - split by new lines, includes all whitespace besides newlines
    - formatters:
        - end of line whitespace removal

- [x] non-ascii whitespace
    - all languages
    - tokenizes non-ascii whitespace
    - formatters
        - replace with ascii whitespace

- [x] file tokenizer 
    - all languages for tokenizer
    - whole file 
    - formatters:
        - all modules should have an `__all__` variable declaration
        - file whitespace 
            - only leave one new line at the end of the file
            - leave no white space at start of file
        - code block new lines
            - for non-function or class code blocks including
                - for loop blocks
                - if/else statements. should not be new lines between if, ifel, or else blocks. 
                - try/except block
                - with blocks
                - while blocks
            - A single new line after all code blocks
            - nested ones should only have one new line total, unless the next section is in the same code block
            

- [x] import section tokenizer 
    - python specific
    - any contiguous section of only python imports including all whitespace around it
    - formatters: 
        - import separator
            - import should be in up to 4 blocks with a new line between each block
            - first block should be standard lib imports
                - keep list of all standard lib imports for python
            - second block is for third party imports
                - anything that isn't in the first, third, or 4th block goes here
            - third block is for internal package imports
                - should take a list of internal packages in the class
            - fourth block is for current package imports
                - determine what the package name is internally with this:
                    - `package_name = getattr(sys.modules[__name__]   , "__package__", None)`
                - or if the import uses . notation
            - 2 new lines after end of import block

- [x] import block tokenizer 
    - python specific
    - a block of imports separated be at least one new line, includes indent but no extra new lines
    - formatters: 
        - sort imports within a block of imports

- [x] import statement tokenizer
    - python
    - single import statement with indent
    - formatters
        - imports that have more than 3 items in an "import" or "from import" statement should be put into parenthesis, with new lines for each element.
            - For example. `from thing import other, one, here, there` should turn into:
                ```python
                from thing import (
                    other,
                    one,
                    here,
                    there
                )
        - multiple entries in a "from import" statement should be sorted
            - for example: `from thing import a, c, b` would turn into `from thing import a, b, c`

- [x] paired punctuation tokenizer 
    - python specific
    - any statement that has paired punctuation like (), {}, []
    - tokenizer needs to pull in the whole, highest level statement that has the paired punctuation with the indent, no external new lines
    - formatters:
        - multi-line nested paired punctuation
            - if more than 1 element
                - each element should be on a new line 
                - opening and closing brackets or braces also on a new line
            - if there is more than one element in any nested paired punctuation, each parent layer above that layer should be on a new line
                - Example   
                -  Incorrect:
                    ```python
                    my_func([{"my_key": [1,2], "other_key": [0]}])
                    ```
                - Correct:
                    ```python
                    my_func(
                        [
                            {
                                "my_key": [
                                    1,
                                    2
                                ], 
                                "other_key": [0]
                            }
                        ]
                    )
                    ```
            - spaces in nested pair punctuation
                - there should be no space between pared punctuation and the inner items, excludes new lines.  
        

- [x] function signature tokenizer 
    - python specific
    - function with indent and no newlines 
    - formatters:
        - signatures and calls that have more than 2 arguments should have one argument per newline

- [x] decorator tokenizer 
    - python specific
    - includes single decorator statement with indent, no extra newlines
    - formatters:
        - decorators that have more than 2 arguments should have one argument per newline

- [x] function tokenizer 
    - python specifc
    - whole function including decorators and indent.  Does not include extra newlines - python specific
    - formatters:
        - Return/yield statements
            - should have a new line between return or yield statements if there is a statement before it in the same block. 
            - Yields should have a space after them is there is another statement in the same indent/block
            - should have no new lines between return or yield statements if it is the only statement in a code block.
        - no code within a function should have 2 newlines in a row

- [x] function space tokenizer
    - python specific
    - only for new lines between functions
    - formatters:
        - should have 2 new lines before and after definition

- [x] decorator space tokenizer
    - python specific
    - includes all space after a decorator
    - formatters
        - decorator newlines
            - removes all newlines between decorators

- [x] quotation tokenizer
    - python only
    - returns outermost quotations with string
    - ability to exclude dictionary key notation like `my_dict['my_key']`
    - formatters:
        - enforce double of single quotes for all strings

- [x] dict key notation tokenizer
    - python only
    - returns string literals from within dict key notation like `my_dict['my_key']` would have a token for `'my_key'`
    - formatters
        - same formatter for quotations, to enforce double or single quotes for strings

- [x] binary operator tokenizer
    - python only
    - includes the binary operator, and the whitespace around it. 
    - ability to exclude function signature and function call equals signs
        - like when declaring a function with default kwargs
        - or when calling a function with kwargs
    - formatters:
        - binary operators should have a single space on both sides. 

- [x] function signature default kwargs equals sign tokenizer
    - python only
    - include the equals sign and any whitespace around it. 
    - formatters:
        - equals signs should not have space around them

- [x] function call with kwargs equals sign tokenizer
    - python only
    - include equals sign and any whitespace around it
    - formatters:
        - equals signs should not have space around them, same as from function signature

- [x] class tokenizer
    - python only
    - includes indent, does not include new lines on outside of class
    - formatters:
        - class __init__ methods should not have docstrings, message should say they should be on the class level

- [x] class whitespace tokenizer
    - python only
    - include whitespace before and after classes
    - formatters
        - 2 new lines before and after classes
    
- [x] comma tokenizer
    - general language tokenizer
    - commas that include all whitespace around them
    - formatters
        - commas should either be followed by a space or a newline

- [x] comma plus tokenizer
    - all languages
    - include the comma and all following whitespace, as well as the the first non-whitespace character
    - formatters:   
        - The last item in a multi-item structure does not have a comma
            - If the first non-whitespace character is a ), ], or } then remove the comma

- remember that tokenizers should not give overlapping tokens for outputs of a single doc
- python function tokenizer says it has overlapping functions because of the whitespace flag - don't do this
- in general tokenizers should include whitespace only when needed, and as little as needed.



- [x] how to handle file types that are picked up?
    - Do we need to enforce that certain formatters and tokenizers only work on specific languages? 
        - Maybe this is just done through human readable things? 
    - no config approach
        - cleer runs all files through all stages, the stages say what glob patterns (filter by file types this way)
        - up to the people to correctly configure the glob patterns for the different stages?
        - pros
            - No extra configs needed for new tokenizers or formatters
            - can possible reuse tokenizers and formatters for file types they don't support without additional changes? 
        - cons
            - up to people to read the docs and set glob patterns accordingly
            - lack or errors telling you if you are doing it wrong
    - config for languages with lookups to file extensions
        - pros
            - errors for using the tokenizers and formatters with the wrong file types
        - cons
            - have to provide a special lookup for new file types or extensions
            - have to provide special lookups when adding things like .bak files or other extensions to the same language? 
            - can still reuse other tokenizers and formatters, but would need to update the var to say that they accept the language
    - **solution** - just use globs, not validation on the non file type ones


- [x] Rework
    - 2 main pieces under cleer class
        - tokenizers - break up pieces of code into smaller pieces
        - formatters - can be used to:
            - inpsect
                - return human readable output for rules
            - format
                - format any rules that it enforces

    - cleer class:
        - takes list tokenizer instances to run, in specified order
        - for each tokenizer, a list of formatters is specified
        - 2 main functionalities:
            - inspect - list off human readable rule violations
            - format - format documents
        - These should be runnable on either a string, file pointer, file path, or directory path
            - inspect and format takes either str, fp, or pathlib path (file or directory) with sub functions that are also part of the api
                - inspect_str
                - inspect_fp
                - inspect_file
                - inspect_dir - should be a generator for files
                - format_str
                - format_fp
                - format_file
                - format_dir

    
    - tokenizer
        - must have var declaring the languages they support
        - main function is tokenize, which should be  a generator for tokens
            - takes the language as an arg
        - tokenizer whitespace should be case by case
            - If you need indent, then include it
            - if you can include extra whitespace around it, then include it or not
                - function would want indent, but not new lines. Would be better to have a module level tokenizer to 
        - tokenizers cannot have overlap in tokens
    
    - formatter 
        - must also declare languages it supports


- overall workflow
    - cleer class created
        - pass in config of list of tokenizer instances, with formatters to have for the tokenizer
        -   ```python
            {
                "stages": [
                    {
                        "tokenizer": Tokenzer1(),
                        "formatters": [
                            Formatter1()
                        ],
                        "file_types": [ # both tokenizers and formatter must support these lanuages
                            language.PYTHON, # auto filters by python files *.py
                            language.JSON # auto filters by json files
                        ],
                        "glob_patterns": [
                            "./my_dir/*.py" # or leave empty for no filters
                        ]
                    }
                ]
            }
            ```
    - cleer format is run
        - cleer class finds first file and pulls it into memory as a string
        - starts iterating through stages
            - first tokenizer - first document
            - tokenize with the first tokenizer, pass language
                - tokens have the
                    - token string
                    - start and end locations
            - Cleer goes through tokens and generates UUIDs for each
            - goes through the file
                - deletes token contents
                - marks all tokens with special UUID string
            - now iterates through formatters
                - for each formatter, iterate through tokens
                - formatter updates token string only, doesn't need to update columns or anything
            
            - when first stage is complete for first file, cleer reconstructs file relacing token strings with new contents
            - next stage has the updates string
        
        - when all stages are complete return results
    
    - cleer inspect is run
        - cleer class finds first file and pulls it into memory as a string    
        - starts iterating through stages
            - first tokenizer - first document
            - tokenize with the first tokenizer
                - tokens have the
                    - token string
                    - start and end locations
            - now iterates through formatters
                - formatters return any violations
        - return value for this should reflect stages, a g
    
        