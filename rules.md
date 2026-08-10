# cleer Default Rules


## General

- [x] End of file whitespace
    - Files should end with a configurable number of blank lines
    - Default: 1
- [x] Start of file whitespace
    - Files should start with a configurable number of blank lines
    - Default: 0
- [x] Max consecutive blank lines
    - No more than the configured max blank lines in a row
    - Default: 2
- [x] Non-ASCII whitespace
    - Non-ASCII whitespace characters should not exist
- [x] Trailing whitespace
    - Lines should not have any trailing whitespace


## Python

### Spacing

- [x] Single space maximum
    - Only one consecutive space allowed outside of indentation and string literals
- [x] Binary operators
    - One space on each side
    - Exception: function default kwargs and function call kwargs should have no space around `=`
- [x] Unary operators
    - No space between unary negative (-) and its operand
- [x] Indentation
    - Spaces only, 4 spaces per level
- [x] Colons
    - No space before, one space after
    - Applies to type hints, dictionaries, slices
- [x] Commas
    - No space before, one space after (or newline)
    - No trailing comma, except for single-value tuples
    - For loop variables never have trailing comma

### Strings

- [x] Quote style
    - String literals use `"`
    - Dict key bracket notation uses `'`
    - Multiline strings use `"""`

### Functions and methods

- [x] Blank lines
    - 2 blank lines before and after top-level functions
    - 1 blank line before and after nested functions or classes
    - Max 1 blank line inside function bodies
    - No blank line between `def` and docstring or first line of code

### Returns and yields

- [x] Returns
    - Blank line before, unless it is the only statement in the block
    - At least one blank line after
- [x] Yields
    - Blank line before, unless it is the only statement in the block
    - At least one blank line after

### Classes

- [x] Class body spacing
    - No blank lines between class declaration, docstring, class vars, or pass
    - 2 blank lines before anything else (methods, etc.)
    - 2 blank lines before and after root-indent classes

### Compound statements

- [x] if/elif/else, try/except/finally, with, etc.
    - No blank lines between chain parts (if→elif, try→except)
        - Exception: after return, yield, or exit()
    - At least one blank line after the end of a chain
    - No blank lines between block opener and first line of inner code

### `__all__`

- [x] Presence and formatting
    - Should exist in all modules belonging to configured packages
    - One blank line before and after
    - One item per line if more than 0 items
    - Sorted alphabetically
    - Only formats the first `__all__` assignment in a module

### Imports

- [x] Import section formatting
    - 4 blocks separated by a blank line, in order:
        1. Standard library
        2. Third party (PyPI)
        3. Internal libraries (private repos)
        4. Current package
    - Each block sorted alphabetically (not including `import`/`from` keyword)
    - Items within a multi-import statement sorted alphabetically
    - Flatten each import; if over 80 chars, expand to one per line
    - 1 blank line before, 2 blank lines after an import section

### Module header

- [x] Header ordering
    - Items in this order, with 1 blank line between each (if they exist):
        1. Module docstring
        2. `__version__`
        3. `__all__`
        4. Imports
    - 2 blank lines after the header before module code

### Module docstring

- [x] Presence
    - All modules should have a docstring at the top

### Type hints

- [x] Handled by paired punctuation formatter
    - Colon spacing follows the colons rule (no space before, one space after)
    - Flatten first, then expand if:
        - Over annotation_max_len (40) chars, not including indent
        - Over annotation_max_line_len (80) chars including indent
        - Nesting exceeds annotation_max_depth (2) bracket levels
    - Handles all annotation contexts: function params, return types, variable annotations, type aliases

### Paired punctuation

- [x] Core behavior
    - Flatten first, then expand based on thresholds
    - Any paired punctuation containing a comment is not formatted
    - No space between openers/closers and inner values on the same line
    - Excludes: `__all__`, for loop variables

- [x] Configurable thresholds (PythonPairedPunctuationFormatter parameters):
    - def_max_len: 80 — func def flat length, no indent
    - def_max_line_len: 100 — func def with indent
    - def_max_args: 4 — func def params before expansion
    - def_max_args_kw: 2 — func def params when defaults present
    - call_max_len: 60 — call flat length, no indent (also boolops, chain segments)
    - call_max_line_len: 80 — call with indent (also boolops)
    - call_max_args: 4 — call args before expansion (also chain segments)
    - call_max_args_kw: 2 — call args when kwargs present (also chain segments)
    - chain_call_max_len: 80 — total flat chain, no indent
    - chain_call_max_line_len: 100 — total chain with indent
    - lst_max_len: 30 — container literal length
    - lst_max_line_len: 80 — container with indent
    - lst_max_num: 3 — max container items before inline expansion in call args
    - annotation_max_len: 40 — type annotation flat length
    - annotation_max_line_len: 80 — type annotation with indent
    - annotation_max_depth: 2 — max bracket nesting before expansion

- [x] Dictionaries
    - Always expanded if more than 0 items

- [x] Lists, sets, tuples
    - Flatten first
    - Expand if literal length > lst_max_len (30) or with indent > lst_max_line_len (80)
    - Nested containers (inside another list, dict, set, tuple) always expand if non-empty
    - If any nested containers expand, all siblings expand too (unless empty)

- [x] Function definitions
    - Flatten first
    - Expand if:
        - Flat length > def_max_len (80)
        - With indent > def_max_line_len (100)
        - More than def_max_args (4) params
        - More than def_max_args_kw (2) params when any have defaults
        - Any inner paired punctuation is expanded
    - Never split empty parens to a new line
    - If any args expand, all expand (unless empty)

- [x] Function calls
    - Flatten first
    - Expand if:
        - Flat length > call_max_len (60)
        - With indent > call_max_line_len (80)
        - More than call_max_args (4) args
        - More than call_max_args_kw (2) args when any are kwargs
        - Any inner paired punctuation is expanded
    - Never split empty parens to a new line
    - Never split single non-kwarg string arg (useful for logging, exceptions)
        - Does not include chained calls or string concats
    - If any args expand, all expand (unless empty)

- [x] Chained function calls
    - Flatten first
    - Individual segments use call_max_len, call_max_args, call_max_args_kw
    - Expand all (except 0-arg calls) if:
        - Any segment meets call expansion criteria
        - Total flat length > chain_call_max_len (80)
        - Total with indent > chain_call_max_line_len (100)

- [x] Decorators
    - Treated as function calls — same rules and thresholds (call_max_*)

- [x] Logic blocks (boolean expressions)
    - Operators `or` and `and` separate statements
    - Flatten first
    - Expand if:
        - More than 2 statements
        - Flat length > call_max_len (60)
        - With indent > call_max_line_len (80)
        - Any inner paired punctuation or other logic block is expanded
    - Expanded operators precede the following operand on each line
    - Add parenthesis to clarify order of operations

- [x] Native string concatenation
    - Flatten first
    - Always multiline, surrounded by parenthesis
    - Fully expand containing context
    - Applies to return statements, assignments, and call args

- [x] Dictionary key notation
    - Always flatten, never expand

- [x] Inline generators
    - Always flatten, never expand
