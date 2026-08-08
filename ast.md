Here's the audit:
  
  Methods That Should Use AST (Currently Don't)
  
  High-impact — these are doing what AST already does natively:
  
  ┌──────────────────────────┬────────────────────────────────────────┬─────────────────────────────────────────────────────────┐
  │ Method                   │ Manual Approach                            │ AST Alternative                                       │
  ├──────────────────────────┼────────────────────────────────────────────┼───────────────────────────────────────────────────────┤
  │ _split_logic_statements  │ String-aware splitting by or/and           │ ast.BoolOp gives .op (And/Or) and .values list        │
  │                          │                                            │ directly                                              │
  ├──────────────────────────┼─────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ _split_by_operator       │ Char walk with bracket/string tracking      │ Unnecessary if BoolOp.values is used                 │
  ├───────────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ _has_logic_operator       │ Regex after stripping string contents       │ isinstance(node, ast.BoolOp)                        │
  ├───────────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ _has_logic_operator_word  │ Same regex approach                         │ Same — ast.BoolOp                                   │
  ├───────────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ _is_logic_subgroup        │ Paren check + string-stripped keyword       │ ast.BoolOp nested inside paren                      │
  │                           │ search                                      │                                                     │
  ├───────────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ _is_ternary               │ String-stripped if/else search + bracket    │ ast.IfExp                                           │
  │                           │ depth                                       │                                                     │
  ├───────────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ _is_comprehension_content │ Char walk looking for for ... in            │ ast.ListComp / ast.GeneratorExp / etc.              │
  ├───────────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ _is_chained_call          │ Char walk + regex for ).method(             │ Nested ast.Call(func=ast.Attribute(...))            │
  ├───────────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ _detect_context           │ String prefix checks + regex                │ AST node type (FunctionDef, Call, BoolOp, IfExp,    │
  │                           │                                             │ etc.)                                               │
  ├───────────────────────────┼─────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ _region_context           │ Preceding-char heuristics + keyword lists   │ ast.Dict, ast.List, ast.Subscript, ast.Call, etc.   │
  └───────────────────────────┴─────────────────────────────────────────────┴─────────────────────────────────────────────────────┘
  
  Partially replaceable (if token fragments can be parsed):
  
  ┌───────────────────────────┬─────────────────────────────────────────────────────────────────────┐
  │ Method                    │ What it does                                                        │
  ├───────────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ _split_items              │ Split by top-level commas → AST gives node.args, dict .keys/.values │
  ├───────────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ _item_has_container       │ Check for nested brackets → AST identifies nested List/Dict/Call    │
  ├───────────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ _is_string_concat_content │ Detect implicit string concat → AST: sequence of ast.Constant       │
  ├───────────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ _extract_string_literals  │ Get individual strings → AST node positions                         │
  └───────────────────────────┴─────────────────────────────────────────────────────────────────────┘
  
  Methods That Can't Use AST (Text Normalization)
  
  These operate below AST's abstraction — AST discards whitespace, comments, and exact bracket positions:
  
  - _flatten_string — collapses whitespace while preserving strings/comments
  - _collapse_paren_spaces — removes spaces after ( and before )
  - _collapse_empty_pairs — ( ) → ()
  - _find_matching_close — character-level bracket matching
  - _find_top_regions — bracket position discovery
  - _is_closing_quote — backslash counting
  - _brackets_balanced — bracket depth validation
  
  Already Using AST
  
  - PythonCompoundChainTokenizer — fully AST
  - PythonCompoundChainFormatter — fully AST
  - PythonCompoundEndTokenizer — fully AST
  - PythonBinaryOperatorSpaceTokenizer — fully AST
  - PythonClassBoundaryFormatter — fully AST
  
  Bottom Line
  
  The paired punctuation formatter has ~10 methods doing semantic classification (is this a ternary? is this a logic expression? what
  kind of bracket is this?) that AST already answers definitively. The practical path: try-parse the token fragment with
  ast.parse(fragment, mode='eval') and use the resulting node type for classification and splitting decisions, falling back to the
  manual approach only if parsing fails.
  
  Want me to start refactoring the logic splitting (_split_logic_statements and related) to use AST?
