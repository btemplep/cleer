"""My well formatted python file!"""

__version__ = "0.1.0"

import os
from typing import Dict, List, Literal

from my_package import (
    and_everywhere,
    everywhere,
    here,
    now_here,
    now_there,
    there
)
import requests
from some_lib.is_a_really_long.long_long.lots_of_lengthy_words_are_here import a_really_long_here_toooooo

from cleer import Cleer, CleerConfig, CleerError, CleerGroup


# bad stuff
tup = (2,)
thing = {
    "hello": "there",
    "hi": "now"
}
find = [
    0,
    1,
    3,
    4,
    5,
    "hello ther lov",
    "how is all of that"
]

thing = [
    {
        "hello": [
            1,
            2,
            "hello",
            "there",
            "how"
        ],
        "there": [
            2,
            7,
            -1
        ],
        "now": {
            "there": 103
        }
    }
]

if (
    thing == "this"
    or hello_there == "that"
    or fine_great != thing
):
    print(0)
elif (
    hello == "that"
    or (
        True != False
        and fine_great == "1234"
    )
):
    thing = "that"
    print(10)
else:
    print(8)


@decor(
    "ldkfjd  ",
    "sdflkjsdfk   ",
    "ksdjfdk",
    "alskdjfaslkdfj"
)
def say_hello(
    hello: str=None,
    hello_there: int=10,
    fine_great: str="1234232"
):
    my_dict = {
        "thing": "here"
    }
    print(my_dict['thing'])
    if (
        thing == "this"
        or hello_there == "that"
        or fine_great != thing
    ):
        return 0

    elif (
        hello == "that"
        or (
            True != False
            and fine_great == "1234"
        )
    ):
        thing = "that"

        return 10

    elif True:
        my_thing = "another"
    else:
        return 8


def say_hello2(
    hello: str=None,
    hello_there: int=10,
    fine_great: str="1234232"
):
    """_summary_

    Parameters
    ----------
    hello : str, optional
        _description_, by default None
    hello_there : int, optional
        _description_, by default 10
    fine_great : str, optional
        _description_, by default "1234232"
    """
    string_to_keep_formatting = """Thing here
  and here
     and here
and here
"""
    bad_var = [
        "alsdkfsdfl",
        "alskfjslkfdj",
        "aslkdfjsdfjk",
        -1,
        "evenmore hwerskjfsl"
    ]

    pass


say_hello(
    "dkfj",
    1000,
    "asdflkjasdfkj",
    "alsdkflksdfj",
    "asldkfjalskdjflsdf"
)
Literal[
    "alsdkfsdfl",
    "alskfjslkfdj",
    "aslkdfjsdfjk",
    -1,
    "evenmore hwerskjfsl"
]
my_type = Dict[
    str,
    Dict[
        Literal[
            "asdf",
            "alsdkflsdkfj",
            "alskdjflskdfj"
        ],
        Dict[
            str,
            List[Dict[str, int]]
        ]
    ]
]
my_type2 = Dict[
    str,
    List[
        Dict[str, Dict[str, str]]
    ]
]


@medcor
async def hello(thing, over="here"):
    print("hello")

    def inner():
        thing = -1

        return thing

    print("after")

    print("one more")

    return 0


@some_class_decor(
    first_val="this_thing",
    second_value="other_thing"
)
class MyClass:
    """_summary_
    """
    my_int: int


    async def hello(self):
        print("hello")

        def inner():
            pass

        print("after")

        print("one more")

        return 0


async def my_agen():
    print("hello")

    yield 1

    print("almost")

    return None


def type_creator():
    my_type2 = Dict[
        str,
        List[
            Dict[str, Dict[str, str]]
        ]
    ]

    class InternalThing:
        """_summary_
        """
        var: str


class MyNewType:
    thing: Dict[
        str,
        List[
            Dict[str, Dict[str, str]]
        ]
    ]
    val: Literal[
        "alsdkfsdfl",
        "alskfjslkfdj",
        "aslkdfjsdfjk",
        -1,
        "evenmore hwerskjfsl"
    ]


    def format(self, token: str) -> str:
        """Replace the token with the configured number of blank lines.

        Parameters
        ----------
        token : str
            Whitespace token to format.

        Returns
        -------
        str
            The configured number of newline characters.
        """
        return self._replacement


for thing in ["hello", "there", "how", "are"]:
    print(thing)


if hello in ("thing", "there", "how"):
    print(hello)

inspection['excluded'].append(
    {
        "group": gi,
        "pattern": exclude_pattern
    }
)


def _keep_result(
    self,
    result: Inspection | Formatting | FormattingDocument,
    keep_only_excluded: bool,
    keep_not_included: bool
) -> bool:
    if (
        len(result['included']) > 0
        or (
            len(result['excluded']) > 0
            and keep_only_excluded is True
        )
        or keep_not_included is True
    ):
        print(
            (
                "this is my string literal"
                "this is my string literal 2"
            )
        )

        return True

    return False


def _format_one(
    self,
    file_path: str | pathlib.Path,
    document: str | None
) -> FormattingDocument:
    formatting: FormattingDocument = {
        "path": file_path,
        "included": [],
        "excluded": [],
        "invalidations": [],
        "document": document
    }


def _keep_result(
    self,
    result: Inspection | Formatting | FormattingDocument,
    keep_only_excluded: bool,
    keep_not_included: bool
) -> bool:
    inspection['excluded'].append(
        {
            "group": gi,
            "pattern": exclude_pattern
        }
    )
    if (
        len(result['included']) > 0
        or (
            len(result['excluded']) > 0
            and keep_only_excluded is True
        )
        or keep_not_included is True
    ):
        print(
            (
                "this is my string literal"
                "this is my string literal 2"
            )
        )

        return True

    elif (
        len(result['included']) > 0
        or (
            len(result['excluded']) > 0
            and keep_only_excluded is True
        )
        or keep_not_included is True
        or my_function_call(
            here,
            there="now",
            over="here"
        )
        or my_other_call(
            {
                "hello": "there"
            }
        )
        or last_call("here", 2, 3)
        or thing not in [0, 1, 2, 3]
        or (
            (
                1 == 2
                or True
            )
            and (
                this == "that"
                or that == "this"
            )
        )
    ):
        return True

    return False


my_func_call_herethere(
    thing="here",
    that="this",
    there="now"
).no_args_call().another_one(
    "hello"
).last_one(
    [1, 2, 3]
)
my_func_call_herethere(
    thing="here",
    that="this"
).no_args_call().another_one(
    "hello"
).last_one(
    [
        1,
        2,
        3,
        {
            "hello": "there"
        }
    ]
)
my_func_call_herethere(thing="here", that="this").no_args_call()
my_func_call_herethere(
    thing="here",
    that="this"
).no_args_call().another_one(
    "h"
)


def config_default():
    return {
        "groups": [
            {
                "includes": [
                    "**/*.py"
                ],
                "excludes": excludes,
                "validators": [
                    PythonSyntaxValidator()
                ],
                "stages": [
                    {
                        "tokenizer": PythonBlockStartTokenizer(),
                        "formatters": [
                            BlankLineFormatter(
                                num_blank_lines=0,
                                message="No blank lines between start of code blocks and first line of body."
                            ),
                            thing(
                                hello="there",
                                here="now",
                                you="good"
                            )
                        ]
                    }
                ]
            }
        ]
    }


logger.debug(
    (
        f"Python Packages: {python_packages}\n"
        f"Internal Python Packages: {python_internal_packages}\n"
        f" Excludes: {json.dumps(excludes, indent=4)}"
    )
)
logger.debug(
    (
        f"Python Packages: {python_packages}\n"
        f"Internal Python Packages: {python_internal_packages}\n"
        f" Excludes: {json.dumps(excludes, indent=4)}"
    )
)

thing = (
    f"Python Packages: {python_packages}\n"
    f"Internal Python Packages: {python_internal_packages}\n"
    f" Excludes: {json.dumps(excludes, indent=4)}"
)
other = here(
    (
        f"Python Packages: {python_packages}\n"
        f"Internal Python Packages: {python_internal_packages}\n"
        f" Excludes: {json.dumps(excludes, indent=4)}"
    ),
    1234
)


def new_func():
    if args.command == "inspect":
        logger.info("Running inspect command...")
        try:
            print(
                json.dumps(
                    clr.inspect(args.path),
                    indent=4,
                    default=str
                ),
                flush=True
            )
            logger.info("Inspect command complete!")
        except Exception as exc:
            logger.opt(
                exception=True if args.log_level == "DEBUG" else False
            ).critical(
                f"Inspect Failed! [{type(exc).__name__}]: {exc}"
            )
            exit(1)

    elif args.command == "format":
        logger.info("Running format command...")
        try:
            print(
                json.dumps(
                    clr.format(args.path),
                    indent=4,
                    default=str
                ),
                flush=True
            )
            logger.info("Format command complete!")
        except Exception as exc:
            logger.opt(
                exception=True if args.log_level == "DEBUG" else False
            ).critical(
                f"Format Failed! [{type(exc).__name__}]: {exc}"
            )
            exit(1)

    if not seps:
        if os.path.altsep:
            seps = (os.path.sep, os.path.altsep)
        else:
            seps = (os.path.sep,)

    elif isinstance(seps, str):
        seps = (seps,)

    results = []
    parts = re.split(f"[{escaped_seps}]", pattern)
    last_part_idx = len(parts) - 1

    for idx, part in enumerate(parts):
        if part == "*":
            results.append(one_segment if idx < last_part_idx else one_last_segment)
        elif recursive and part == "**":
            if idx < last_part_idx:
                if parts[idx + 1] != "**":
                    results.append(any_segments)

            else:
                results.append(any_last_segments)

        else:
            if part:
                if not include_hidden and part[0] in "*?":
                    results.append(r"(?!\.)")

                results.extend(_translate_segment(part, not_sep))

            if idx < last_part_idx:
                results.append(any_sep)

    res = "".join(results)
    while i < n:
        c = pat[i]
        i += 1

        if c == "*":
            res.append(f"{not_sep}*")
            while i < n and pat[i] == "*":
                i += 1

        elif c == "?":
            res.append(not_sep)

    stuff = "-".join(s.replace("\\", r"\\").replace("-", r"\-") for s in chunks)
    thing(thing(thing(s for s in my_list)))
    for idx, part in enumerate(parts):
        if part == "*":
            results.append(one_segment if idx < last_part_idx else one_last_segment)
        elif recursive and part == "**":
            if idx < last_part_idx:
                if parts[idx + 1] != "**":
                    results.append(any_segments)

                print("my thing")
            else:
                results.append(any_last_segments)


clr = Cleer(
    config=cleer_default_config(
        python_packages=["cleer"],
        python_internal_packages=[],
        excludes=[
            "**/.nox/**",
            "**/tests/unit/fixtures/format_*.py"
            # "**format_bad.py"
            # "**/format_good.py"
        ]
    )
)


class AnotherClass:


    def _is_inside_function(
        self,
        start: int,
        end: int,
        function_ranges: list[tuple[int, int]]
    ) -> bool:
        """Check if a span falls inside a function body but not directly in a class body.

        A span inside a method (which is inside a class) is still
        considered inside a function. Only spans that are in a class body
        but not in any function body are excluded.
        """
        inside_function = False

        for range_start, range_end in function_ranges:
            if start >= range_start and end <= range_end:
                inside_function = True
                break

        if not inside_function:
            return False

        inside_class = False

        for range_start, range_end in self._class_ranges:
            if start >= range_start and end <= range_end:
                inside_class = True
                break

        if not inside_class:
            return True

        innermost_func = None

        for range_start, range_end in function_ranges:
            if start >= range_start and end <= range_end:
                if (
                    innermost_class is None
                    or (range_end - range_start) < (innermost_class[1] - innermost_class[0])
                ):
                    innermost_func = (range_start, range_end)

        innermost_class = None

        for range_start, range_end in self._class_ranges:
            if start >= range_start and end <= range_end:
                if (
                    innermost_class is None
                    or (range_end - range_start) < (innermost_class[1] - innermost_class[0])
                ):
                    innermost_class = (range_start, range_end)

        if innermost_func and innermost_class:
            func_size = innermost_func[1] - innermost_func[0]
            class_size = innermost_class[1] - innermost_class[0]

            return func_size < class_size

        is_docstring = (
            i == 0
            or isinstance(body[i - 1], (ast.Assign, ast.AnnAssign))
        )
        is_docstring = (
            i == 0
            or isinstance(body[i - 1], (ast.Assign, ast.AnnAssign))
        )
        default_idx = i - (len(args.posonlyargs) + len(args.args) - num_defaults)
        default_idx = i - (len(args.posonlyargs) + len(args.args) - num_defaults)
        if thing:
            return [
                {
                    "token": token,
                    "index": prev_end,
                    "length": len(token)
                }
            ]

        return [
            {
                "token": token,
                "index": prev_end,
                "length": len(token)
            }
        ]


flat = flat.replace("[ ]", "[]")
flat = flat.replace("( )", "()")
flat = flat.replace("{ }", "{}")


content_len = (
    len(region['open_char'])
    + len(", ".join(items))
    + len(region['close_char'])
)
content_len = (
    len(region['open_char'])
    + len(", ".join(items))
    + len(region['close_char'])
)
quote = content[i:i + 3] if content[i:i + 3] in ('"""', "'''") else ch
quote = content[i:i + 3] if content[i:i + 3] in ('"""', "'''") else ch


def return_logic():
    if this:
        return (
            isinstance(first_node, ast.Expr)
            and isinstance(first_node.value, ast.Constant)
            and isinstance(first_node.value.value, str)
        )

    child_depth = depth if isinstance(node, ast.Module) else depth + 1

    return (
        isinstance(first_node, ast.Expr)
        and isinstance(first_node.value, ast.Constant)
        and isinstance(first_node.value.value, str)
    )


actual_indent = len(leading.replace("\t", " " * self._tab_size))
actual_indent = len(leading.replace("\t", " " * self._tab_size))

if " or " in safe_inner or " and " in safe_inner:
    print("return_logic")
elif (
    not triple_quote
    and s[i] == string_char
    and (
        i == 0
        or s[i - 1] != "\\"
    )
):
    print("here")


if isinstance(
    node,
    (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.With,
        ast.AsyncWith,
        ast.Try
    )
):
    print(True)


def another_one():
    return ["\n".join(import_lines)]


class AnotherOne:


    def _parse_at(self, text: str, pos: int) -> tuple[list, int]:
        """Parse segments starting at position.

        Returns
        -------
        tuple[list, int]
            Parsed segments and the position after parsing.
        """
        segments = []
        current = ""

        while pos < len(text):
            char = text[pos]

            if char == "[":
                name = current
                current = ""
                pos += 1
                children, pos = self._parse_children(text, pos)
                segments.append([name, children])
                if node.orelse:
                    else_line = self._find_keyword_line(
                        document,
                        line_offsets,
                        node.handlers[-1].end_lineno if node.handlers else node.body[-1].end_lineno,
                        node.orelse[0].lineno
                    )

                if not isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                        ast.ClassDef
                    )
                ):
                    print("hello")

                target_types = (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef
                )


class JSONValidator:


    def validate(self, document: str) -> str | None:
        try:
            json.loads(document)
        except Exception as exc:
            return f"Failed to parse JSON. [{type(exc).__name__}]: {exc}"

        logger.debug(f"Excluding '{file_path}' from groups[{gi}] for matching the '{exclude_pattern}' exclude pattern.")
        old_indent = len(
            self._get_leading_whitespace(line).replace("\t", " " * self._tab_size)
        )
        unchanged = {
            "this": [
                {
                    # it does this
                    "that": "thing"},
                {
                    "that": "there"
                }
            ]
        }
        content_len = (
            len(region['open_char'])
            + len(", ".join(items))
            + len(region['close_charsherer'])
        )
        if (
            before != before.rstrip(" \t")
            or (
                after != " "
                and not after.startswith("\n")
            )
        ):
            return "thing"

        if formatted != token:
            return (
                "Class body spacing should have no blank lines between class declaration, docstring, class vars, or pass. "
                "There should be two blank lines between those and the first method."
            )

        if not (
            isinstance(child, ast.Constant)
            and isinstance(child.value, str)
            and child.end_lineno > child.lineno
        ):
            return None

        should_expand = (
            content_len > self._call_max_len
            or content_len + indent_len > self._call_max_line_len
            or len(all_args) > self._call_max_args
            or (
                any(self._is_kwarg_str(a) for a in all_args)
                and len(all_args) > self._call_max_args_kw
            )
            or self._any_arg_is_expanded(node)
        )
        # OUTPUT:
        # {
        #     "is_authorized": true,
        #     "grant": {
        #         "effect": "allow",
        #         "actions": [
        #             "Balloon:Read",
        #             "pop"
        #         ],
        #         "query": "contains(request.identities.User[0].role, 'admin')",
        #         "equality": true,
        #         "data": {}
        #     },
        #     "message": "An allow grant is applicable to the request, and there are no deny grants that are applicable to the request. Therefore, the request is authorized.",
        #     "error": null
        # }
        # ✅ Access granted!

        if (
            not emitted
            and isinstance(
                child,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                    ast.If,
                    ast.For,
                    ast.AsyncFor,
                    ast.While,
                    ast.Try,
                    ast.With,
                    ast.AsyncWith
                )
            )
        ):
            self._walk(
                child,
                lines,
                line_offsets,
                document,
                tokens,
                seen_ranges
            )

        result['errors']['locality_incompatibility'] = [
            {
                "is_critical": False,
                "message": f"The '{self._storage.locality}' storage locality is not compatible with the '{self._compute.locality}' compute locality."
            }
        ]
        result['errors'][thing(here, "there")] = [
            {
                "is_critical": False,
                "message": f"The '{self._storage.locality}' storage locality is not compatible with the '{self._compute.locality}' compute locality."
            }
        ]
        identity_def_tasks = [create_task(self._storage.get_identity_def(it, config['get_identity_def'])) for it in request['identities']]

        return None


batch_request_schema = {
    "properties": {
        "identities": _request_identities_schema | {
            "description": _request_identities_schema['description'] + _request_level_description
        },
        "batch": {
            "type": "array",
            "description": "Batch of resources and contexts to process with shared identities, action, resource type, and context type.",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [], # hello there
                "properties": {
                    "identities": _request_identities_schema | {
                        "type": [
                            "object",
                            "null"
                        ],
                        "description": _request_identities_schema['description'] + _batch_item_level_description
                    },
                    "resource_type": _resource_type_schema | {
                        "type": [
                            "string",
                            "null"
                        ],
                        "description": _resource_type_schema['description'] + _batch_item_level_description
                    }
                }
            }
        }
    }
}
self._storage_dict['context_defs_lut'][context_def['context_type']] = context_def
if (
    jsonschema_rs.validator_for(
        resource_def['schema']
    ).is_valid(
        request['resource']
    )
    is False
):
    print("here")


class New:


    @functions.signature(
        {
            "types": [
                "array"
            ]
        },
        {
            "types": [
                "array"
            ]
        },
        {
            "types": [
                "string"
            ]
        }
    )
    def my_thing():
        print("hello")


print(json.dumps(result, indent=4))
if result['is_authorized'] is True:
    print("✅ Access granted!")
else:
    print("❌ Access denied!")

# OUTPUT:
# {
#     "is_authorized": true,
#     "grant": {
#         "effect": "allow",
#         "actions": [
#             "Balloon:Read",
#             "pop"
#         ],
#         "query": "contains(request.identities.User[0].role, 'admin')",
#         "equality": true,
#         "data": {}
#     },
#     "message": "An allow grant is applicable to the request, and there are no deny grants that are applicable to the request. Therefore, the request is authorized.",
#     "error": null
# }
# ✅ Access granted!

thing = (
    len("alskdfjksdjf")
    + len("slkdfjsldkfj")
    + len("slkdfjslkdfjskdkdfjdk")
)
thing = (
    my_func_call(
        this="2dlkfjsdf",
        that={
            "hello": "there"
        }
    )
    + len("slkdfjdlkf")
)
thing = (
    jsonschema_rs.validator_for(
        resource_def['schema']
    ).is_valid(
        request['resource']
    )
    + len("slkdfjdlkf")
)
thing = len("alskdfjksdjf") + len("slkdfjsld") + len("")
thing = len("") + len("kfj") + len("jdf") + len("fj")
thing = (
    len("")
    + len("")
    + len("")
    + len("")
    + len("")
)
if (
    len("alskdfjksdjf")
    + len("slkdfjsldkfj")
    + len("slkdfjslkdfjskdkdfjdk")
    == 100
):
    print("long!")

thing = 5 == 4
thing = (
    my_long_call(
        thing="that",
        this="slkdfjsldfk",
        there=4
    )
    + my_other_long_call(
        thing="slkdfjlsdfj",
        that=23434,
        there="aalskjdfsdlfkj"
    )
    == 100
)
if (
    my_long_call(
        thing="that",
        this="slkdfjsldfk",
        there=4
    )
    == my_other_long_call(
        thing="slkdfjlsdfj",
        that=23434,
        there="aalskjdfsdlfkj"
    )
):
    print("I got here")


class CustomFunctions(jmespath.functions.Functions):
    """
    result = formatter.format("   ")
    """


    @jmespath.functions.signature(
        {
            "types": [
                "number"
            ]
        },
        {
            "types": [
                "number"
            ]
        }
    )
    def _func_my_add(self, x, y):
        return x + y


my_set = {1}
my_set2 = {1, 2}
long_set = {
    "hello_there",
    "how_are_you",
    "doing_today"
}
nested_set = [
    {
        "alpha",
        "beta"
    },
    {
        "gamma",
        "delta"
    }
]
frozen = frozenset(
    {
        "thing_one",
        "thing_two",
        "thing_three"
    }
)


while (
    condition_a is True
    or condition_b is True
    or condition_c is True
):
    print("looping")

while x < 10 and y < 20:
    x += 1

while (
    some_long_variable_name is True
    and another_long_variable_name is True
    and yet_another_variable is True
):
    break

while (
    counter
    + offset
    + padding
    + margin
    > maximum_allowed_value
):
    counter -= 1


should_run = x > 0 and y > 0
should_stop = (
    error_count > max_errors
    or timeout_reached is True
    or user_cancelled is True
)
is_valid = (
    has_name is True
    and has_email is True
    and (is_admin is True or has_permission is True)
)


config['settings'] = "value"
config['settings']['nested'] = "deep"
result['errors']['locality_check'] = some_function(arg1, arg2)
my_dict[compute_key(param1, param2, param3)] = "computed"


@decorator_one
@decorator_two
@decorator_three(
    param="value",
    other="thing",
    more="stuff"
)
def multi_decorated():
    pass


@app.route("/api/v1/endpoint")
@requires_auth
@rate_limit(max_calls=100, period=60)
class DecoratedClass:
    """Decorated class."""
    pass


my_lambda = lambda x: x + 1
sorter = lambda item: item.get("priority", 0)
transform = lambda x, y, z: x * y + z
items.sort(key=lambda x: x.name)
filtered = filter(lambda x: x > 0 and x < 100, numbers)


first, *rest = my_list
a, b, *remaining = get_values(
    source="database",
    timeout=30,
    retries=3
)
merged = {
    **defaults,
    **overrides,
    "extra": "value"
}
result = my_func(*args, **kwargs)
combined = [
    *list_one,
    *list_two,
    "extra"
]


try:
    result = do_something()
except ValueError as exc:
    handle_error(exc)
except (TypeError, KeyError):
    handle_other()
finally:
    cleanup()

try:
    data = fetch_data(
        url="https://example.com",
        timeout=30,
        headers={
            "Authorization": "Bearer token"
        }
    )
except requests.Timeout:
    retry()
except requests.HTTPError as exc:
    log_error(message=str(exc), code=exc.response.status_code)
else:
    process(data)
finally:
    close_connection()


with open("file.txt") as f:
    content = f.read()

with open("file.txt", "r") as f, open("out.txt", "w") as out:
    out.write(f.read())

with database.transaction(
    isolation="serializable",
    timeout=30,
    retries=3
) as txn:
    txn.execute("SELECT 1")


match command:
    case "quit":
        quit_game()
    case "go" | "move":
        do_move()
    case _:
        print("unknown")

match point:
    case (0, 0):
        print("origin")
    case (x, 0):
        print(f"x={x}")
    case (0, y):
        print(f"y={y}")
    case (x, y):
        print(f"x={x}, y={y}")


squares = [x ** 2 for x in range(10)]
evens = [x for x in numbers if x % 2 == 0]
mapping = {k: v for k, v in items.items() if v is not None}
unique = {item.name for item in collection if item.active}
total = sum(x.value for x in items if x.category == "primary")
nested_comp = [item for sublist in matrix for item in sublist if item > 0]
long_comp = [transform_function(item) for item in get_all_items_from_source() if item.is_valid()]


def positional_only(
    x: int,
    y: int,
    /,
    z: int=0
) -> int:
    return x + y + z


def keyword_only(
    *,
    name: str,
    value: int,
    default: bool=False
) -> dict:
    return {
        "name": name,
        "value": value
    }


def mixed_params(
    pos_only: int,
    /,
    normal: str,
    *args,
    kw_only: bool=True,
    **kwargs
) -> None:
    pass


def short_star(
    x,
    /,
    y,
    *,
    z
):
    return x + y + z


class SimpleChild(BaseClass):
    pass


class MultiInherit(BaseOne, BaseTwo, BaseThree):
    pass


class WithMetaclass(BaseClass, metaclass=ABCMeta):
    pass


class LongInheritance(VeryLongBaseClassName, AnotherLongBaseClassName, ThirdBaseClassName, metaclass=CustomMetaclass):
    """Class with many bases."""
    pass


assert x > 0
assert result is not None, "Result should not be None"
assert len(items) > 0, "Items list must not be empty after processing the input data from source"
assert isinstance(value, str), f"Expected str, got {type(value).__name__}"


counter += 1
total += item.value
message += "short"
long_accumulator += first_long_value + second_long_value + third_long_value
result -= overhead_cost + maintenance_fee + depreciation_amount
buffer += chunk_one + chunk_two


simple_f = f"Hello {name}"
complex_f = f"Result: {obj.method(arg1, arg2)}"
nested_f = f"Value: {data['key']}"
multipart_f = f"{prefix}{separator}{suffix}"
conditional_f = f"Status: {'active' if is_active else 'inactive'}"
formatted_f = f"Price: ${amount:.2f}"
long_fstring = f"The {item_type} with id={item_id} has status={status} and was last updated at {timestamp}"


in_range = 0 < x < 100
valid = 0 <= index < len(items)
bounded = lower <= value <= upper
if 0 < x < 10 and 0 < y < 10:
    print("in bounds")


value = "yes" if condition else "no"
result = compute_a() if flag else compute_b()
default = config.get("key") if config else None
items = get_cached_items() if cache_valid else fetch_fresh_items()


def simple_gen():
    yield 1


def multi_gen():
    for item in source:
        processed = transform(item)

        yield processed

    return None


def yield_from_gen():
    items = range(10)

    yield from items

    yield from other_generator(param1="value", param2="other")

    return "done"


def outer():
    counter = 0

    def inner():
        nonlocal counter
        counter += 1

        return counter

    return inner


offset = (
    calculate_base(x=start_pos, y=end_pos)
    + calculate_adjustment(factor=scale, offset=margin)
)
is_match = normalize(input_text) == normalize(expected_text)


short_call(a, b)
medium_call(a, b, c, d)
kwargs_call(key="val")
mixed_short(a, key="val")
mixed_expand(
    first_arg,
    second_arg,
    keyword_one="value_one",
    keyword_two="value_two"
)
all_kwargs_expand(
    alpha="first",
    beta="second",
    gamma="third"
)


empty_structures = ([], {}, set(), ())
single_items = ([1], {"k": "v"}, {1}, (1,))

nested_in_if = (
    isinstance(node, ast.Call)
    and len(node.args) > 0
    and any(isinstance(a, ast.Starred) for a in node.args)
)

long_method_chain = queryset.filter(
    active=True
).exclude(
    deleted=True
).order_by(
    "-created"
).select_related(
    "author"
)

dict_with_calls = {
    "computed": compute_value(input_data, transform="normalize"),
    "static": "hello",
    "nested": {
        "inner": get_inner(key="test")
    }
}

multiline_return_dict = {
    "status": "success",
    "data": process_response(
        raw_data,
        format="json",
        validate=True
    ),
    "metadata": {
        "timestamp": now(),
        "version": "1.0"
    }
}


result = (
    my_func(
        arg1,
        arg2,
        kwarg1="value1",
        kwarg2="value2"
    )
    + other_func(
        x,
        y,
        z,
        key="thing"
    )
    == expected_val
)

if (
    (
        some_condition is True
        or other_condition is True
    )
    and validate(
        input_data,
        schema={
            "type": "object",
            "required": [
                "name",
                "age"
            ]
        }
    ) is True
):
    print("valid")

config = {
    "handlers": [
        create_handler(
            name="stdout",
            level="DEBUG",
            formatter=build_formatter(style="json", indent=4)
        )
    ],
    "loggers": {
        "root": {
            "level": "INFO",
            "handlers": [
                "stdout"
            ]
        }
    }
}

response = client.post(
    "/api/v1/users",
    json={
        "name": "test",
        "email": "test@example.com",
        "roles": [
            "admin",
            "user"
        ]
    },
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
)

pipeline = data.filter(
    lambda x: x > 0
).map(
    lambda x: x * 2
).reduce(
    lambda acc, x: acc + x,
    0
)

nested_comp_result = {key: [transform(item, config={"mode": "fast"}) for item in values] for key, values in grouped_data.items() if len(values) > threshold}


def process_batch(
    items: list[dict[str, str | int | None]],
    config: dict[str, dict[str, list[str]]] | None=None,
    callback: Callable[[dict], bool] | None=None
) -> dict[str, list[dict[str, Any]]]:
    pass


class EventHandler(BaseHandler, LoggingMixin, metaclass=ABCMeta):
    """Handler."""
    pass


result = (func_a(
    x=1,
    y=2,
    z=3
) if condition_alpha and condition_beta else func_b(
    a="hello",
    b="world",
    c="test"
))

while (
    not queue.empty()
    and (
        time.time() - start_time < timeout
        or force_continue is True
    )
):
    item = queue.get()

try:
    result = await asyncio.gather(
        *[process_item(item, config={"timeout": 30, "retries": 3}) for item in batch]
    )
except (
    asyncio.TimeoutError,
    ConnectionError
) as exc:
    log_error(
        message=f"Batch failed: {exc}",
        context={
            "batch_size": len(batch),
            "elapsed": time.time() - start
        }
    )
    raise


def complex_function():
    validated = schema.validate(
        data={
            "users": [{"name": n, "age": a} for n, a in zip(names, ages)],
            "config": {
                "strict": True,
                "mode": "batch"
            }
        },
        options={
            "raise_on_error": True,
            "collect_errors": False
        }
    )

    if (
        (
            isinstance(node, ast.FunctionDef)
            or isinstance(node, ast.AsyncFunctionDef)
        )
        and hasattr(node, "returns")
        and node.returns is not None
    ):
        print("has return type")

    mapping = {k: process(v, transform_fn=lambda x: x.strip().lower(), fallback=get_default(k, config={"env": "production"})) for k, v in raw.items() if v is not None and len(v) > 0}

    result.update(
        {
            "processed": True,
            "output": format_output(
                data=result['raw'],
                template=load_template(name="default", version=2),
                options={
                    "indent": 4,
                    "sort_keys": True
                }
            )
        }
    )

    return {
        "items": sorted(
            [{"id": item.id, "name": item.name, "score": calculate_score(item, weights={"relevance": 0.6, "freshness": 0.3, "popularity": 0.1})} for item in filtered_items],
            key=lambda x: x['score'],
            reverse=True
        ),
        "total": len(filtered_items)
    }


class ComplexProcessor(BaseProcessor, CacheMixin):
    """Processor."""
    default_config: dict = {
        "timeout": 30,
        "retries": 3
    }


    def process(
        self,
        items: list[dict[str, Any]],
        callback: Callable[[str, dict], tuple[bool, str | None]] | None=None
    ) -> dict[str, list[tuple[str, int]]]:
        results = [{"key": k, "values": [v for v in item[k] if v > self.threshold]} for item in items for k in item if isinstance(item[k], list)]

        if (
            any(len(r['values']) > self.max_items for r in results)
            or all(r['values'] == [] for r in results)
        ):
            raise ValueError(f"Invalid results: {len(results)} items, max_items={self.max_items}")

        return {
            "success": [r for r in results if r['values']],
            "empty": [r for r in results if not r['values']],
            "metadata": {
                "total": len(results),
                "config": self.default_config
            }
        }


_context_type_schema = (
    _type_schema
    | {
        "title": "Authzee Context Type",
        "description": "A unique name to identity this context type."
    }
)


def my_func(*args, **kwargs):
    pass


def another_func(
    a,
    b,
    *args,
    key="value",
    **kwargs
):
    pass


def typed_func(*args: str, **kwargs: int) -> None:
    pass


class MyClass:
    """Class."""


    def method(self, *args, **kwargs):
        pass


    def complex_method(
        self,
        first,
        second,
        *args,
        option=True,
        **kwargs
    ):
        pass


result = my_func(*unpacked_list, **unpacked_dict)

response = client.post(*path_parts, **headers, **extra_kwargs)

data = dict(
    **base_config,
    **overrides,
    extra="value"
)

merged = {
    **dict_a,
    **dict_b,
    "key": "value"
}


class Serializable(Protocol):
    """Protocol."""


    def serialize(self, format: str="json", **options) -> bytes: ...


    def deserialize(cls, data: bytes, **options) -> "Serializable": ...


@dataclass
class ServerConfig:
    """Config."""
    host: str = "localhost"
    port: int = 8080
    debug: bool = False
    allowed_origins: list[str] = field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:8080"
        ]
    )
    middleware: list[
        tuple[str, dict[str, str | int | bool]]
    ] = field(default_factory=list)
    ssl_config: dict[str, str | bool] | None = None


async def fetch_all(
    urls: list[str],
    session: aiohttp.ClientSession,
    max_concurrent: int=10,
    timeout: float=30.0,
    retry_config: dict[str, int]={"max_retries": 3, "backoff": 2}
) -> list[dict[str, str | int | None]]:
    """Fetch."""
    semaphore = asyncio.Semaphore(max_concurrent)
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_one(url, session, semaphore, timeout=timeout, retries=retry_config['max_retries'])) for url in urls]

    return [t.result() for t in tasks]


@app.route(
    "/api/v1/users",
    methods=["GET", "POST"]
)
@require_auth(
    roles=["admin", "manager"],
    permissions=["read:users", "write:users"]
)
@rate_limit(requests_per_minute=60, burst=10)
async def users_endpoint(
    request: Request,
    db: Database=Depends(get_db),
    cache: Redis=Depends(get_cache)
) -> Response:
    """Users."""
    if request.method == "GET":
        users = await db.query(
            "SELECT * FROM users WHERE active = :active AND role IN :roles",
            {
                "active": True,
                "roles": [
                    "admin",
                    "user"
                ]
            }
        )

        return Response(
            json={
                "users": [serialize_user(u, include_fields=["id", "name", "email", "role"]) for u in users],
                "total": len(users)
            }
        )


class DataStore(ABC):
    """Store."""
    __slots__ = (
        "_connection",
        "_pool",
        "_config"
    )


    @abstractmethod
    async def connect(self, host: str, port: int, **options) -> None: ...


    @abstractmethod
    async def disconnect(self) -> None: ...


    @cached_property
    def connection_string(self) -> str:
        return f"{self._config['host']}:{self._config['port']}/{self._config['database']}"


    @property
    def is_connected(self) -> bool:
        return (
            self._connection is not None
            and self._connection.is_open
        )


    @overload
    def get(self, key: str) -> str | None: ...


    @overload
    def get(self, key: str, default: str) -> str: ...


    @overload
    def get(self, key: str, default: int) -> str | int: ...


    def get(
        self,
        key: str,
        default=None
    ):
        """Get."""
        return self._connection.get(key, default)


@contextmanager
def managed_connection(
    host: str,
    port: int=5432,
    database: str="default",
    pool_size: int=10,
    timeout: float=30.0
):
    """Connection."""
    pool = create_pool(
        host=host,
        port=port,
        database=database,
        size=pool_size,
        timeout=timeout
    )
    try:
        conn = pool.acquire()

        yield conn

    finally:
        pool.release(conn)
        pool.close()


class Registry(Generic[T]):
    """Registry."""
    _instances: dict[str, T] = {}
    _factories: dict[str, Callable[..., T]] = {}


    def register(
        self,
        name: str,
        factory: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs
    ) -> None:
        self._factories[name] = lambda: factory(*args, **kwargs)


    def get_or_create(
        self,
        name: str,
        factory: Callable[..., T] | None=None,
        **defaults
    ) -> T:
        if (instance := self._instances.get(name)) is not None:
            return instance

        if factory is not None:
            self._instances[name] = factory(**defaults)
        elif name in self._factories:
            self._instances[name] = self._factories[name]()
        else:
            raise KeyError(f"No factory registered for {name!r}")

        return self._instances[name]


while chunk := file.read(8192):
    if (match := pattern.search(chunk)) is not None:
        results.append(
            {
                "offset": file.tell() - len(chunk) + match.start(),
                "value": match.group(0),
                "groups": match.groups()
            }
        )

first, *middle, last = sorted(
    itertools.chain.from_iterable(group.items() for group in groups if group.is_active),
    key=lambda x: (x.priority, -x.timestamp)
)


def build_query(
    table: str,
    conditions: list[str],
    order_by: str | None=None,
    limit: int | None=None
) -> str:
    """Query."""
    query = f"""
        SELECT *
        FROM {table}
        WHERE {' AND '.join(conditions)}
        {f"ORDER BY {order_by}" if order_by else ''}
        {f"LIMIT {limit}" if limit else ''}
    """

    return query.strip()


def format_config(
    host: str="0.0.0.0",
    port: int=8000,
    workers: int=4,
    db_url: str="sqlite:///db.sqlite3",
    pool_size: int=5
) -> str:
    """Format."""
    return config_template.format(
        host=host,
        port=port,
        workers=workers,
        db_url=db_url,
        pool_size=pool_size
    )


result = some_module.some_class(param1="value1", param2="value2").method_one(arg1, arg2, kwarg=True).method_two(transform=lambda x: x * 2, filter_fn=lambda x: x > 0).method_three().final_result
match command.split():
    case ["quit"]:
        sys.exit(0)
    case ["move", direction] if direction in (
        "up",
        "down",
        "left",
        "right"
    ):
        player.move(direction, speed=config.get("move_speed", 1.0))
    case ["attack", target, *modifiers] if target in active_enemies:
        damage = calculate_damage(
            player.stats,
            target.defense,
            modifiers=modifiers,
            critical=random.random() > 0.9
        )
        apply_damage(
            target,
            damage,
            source=player,
            effects=[parse_modifier(m) for m in modifiers]
        )
    case ["use", item_name, "on", target_name]:
        item = inventory.find(
            item_name,
            filters={
                "usable": True,
                "equipped": False
            }
        )
        target = world.find_entity(
            target_name,
            radius=player.interaction_range
        )
        if item and target:
            item.use(
                target,
                context={
                    "player": player,
                    "world": world
                }
            )
    case _:
        print(f"Unknown command: {command}")


class PluginMeta(type):
    """Meta."""
    _registry: dict[str, type] = {}


    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs
    ):
        cls = super().__new__(mcs, name, bases, namespace)
        if name != "PluginBase":
            mcs._registry[name.lower()] = cls

        return cls


    def __init_subclass__(
        cls,
        /,
        plugin_name: str | None=None,
        version: str="1.0.0",
        **kwargs
    ):
        super().__init_subclass__(**kwargs)
        cls._plugin_name = plugin_name or cls.__name__.lower()
        cls._version = version


class EventEmitter:
    """Emitter."""
    _listeners: dict[
        str,
        list[Callable[..., None]]
    ] = {}
    _once_listeners: dict[
        str,
        list[Callable[..., None]]
    ] = {}


    def on(
        self,
        event: str,
        callback: Callable[..., None],
        *,
        priority: int=0,
        once: bool=False
    ) -> "EventEmitter":
        target = self._once_listeners if once else self._listeners
        target.setdefault(event, []).append((priority, callback))
        target[event].sort(key=lambda x: x[0], reverse=True)

        return self


    def emit(self, event: str, *args, **kwargs) -> list[Any]:
        results = []
        for _, callback in self._listeners.get(event, []):
            results.append(callback(*args, **kwargs))

        for _, callback in self._once_listeners.pop(event, []):
            results.append(callback(*args, **kwargs))

        return results


class Validator:
    """Validator."""


    class ValidationError(Exception):
        """Error."""
        def __init__(
            self,
            field: str,
            message: str,
            code: str="invalid",
            params: dict[str, Any] | None=None
        ):
            self.field = field
            self.message = message
            self.code = code
            self.params = params or {}
            super().__init__(f"{field}: {message}")


    class ValidationResult:
        """Result."""
        def __init__(
            self,
            errors: list['Validator.ValidationError'] | None=None,
            warnings: list[str] | None=None
        ):
            self.errors = errors or []
            self.warnings = warnings or []
        @property
        def is_valid(self) -> bool:
            return len(self.errors) == 0


    def validate(
        self,
        data: dict[str, Any],
        schema: dict[str, dict[str, Any]],
        strict: bool=False
    ) -> "ValidationResult":
        """Validate."""
        errors = []
        warnings = []
        for field_name, rules in schema.items():
            value = data.get(field_name)
            if value is None and rules.get("required", False):
                errors.append(
                    self.ValidationError(
                        field_name,
                        "Field is required",
                        code="required"
                    )
                )
            elif value is not None and not isinstance(
                value,
                rules.get("type", object)
            ):
                errors.append(
                    self.ValidationError(
                        field_name,
                        f"Expected {rules['type'].__name__}, got {type(value).__name__}",
                        code="type_error",
                        params={
                            "expected": rules['type'],
                            "actual": type(value)
                        }
                    )
                )

        return self.ValidationResult(errors=errors, warnings=warnings)


CONNECTION_DEFAULTS: dict[str, str | int | bool | None] = {
    "host": "localhost",
    "port": 5432,
    "database": "app",
    "user": "admin",
    "password": None,
    "ssl": True,
    "timeout": 30,
    "pool_min": 1,
    "pool_max": 10
}

ERROR_MESSAGES: dict[int, str] = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable"
}

LONG_TUPLE = (
    "first_element",
    "second_element",
    "third_element",
    "fourth_element",
    "fifth_element",
    "sixth_element"
)

a = b = c = some_function(
    arg1,
    arg2,
    kwarg1="value",
    kwarg2="other"
)

x, y = get_coordinates(
    point,
    transform=Matrix4x4.identity(),
    normalize=True
)

(
    error_code,
    error_message,
    error_details
) = parse_error_response(
    response,
    include_traceback=debug_mode,
    max_depth=5
)


class HTTPClient(BaseClient, RetryMixin, LoggingMixin, CacheMixin, metaclass=ClientMeta):
    """Client."""
    DEFAULT_HEADERS: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Version": "2.0"
    }
    MAX_RETRIES: int = 3
    TIMEOUT: float = 30.0


    def __init__(
        self,
        base_url: str,
        api_key: str | None=None,
        headers: dict[str, str] | None=None,
        timeout: float | None=None,
        max_retries: int | None=None,
        session: aiohttp.ClientSession | None=None
    ):
        """Init."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            **self.DEFAULT_HEADERS,
            **(headers or {})
        }
        self.timeout = timeout or self.TIMEOUT
        self.max_retries = max_retries or self.MAX_RETRIES
        self._session = session


    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None=None,
        json: dict[str, Any] | None=None,
        headers: dict[str, str] | None=None,
        timeout: float | None=None
    ) -> dict[str, Any]:
        """Request."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        merged_headers = {
            **self.headers,
            **(headers or {}),
            **({} if not self.api_key else {
                "Authorization": f"Bearer {self.api_key}"
            })
        }

        async with self._session.request(
            method,
            url,
            params=params,
            json=json,
            headers=merged_headers,
            timeout=aiohttp.ClientTimeout(total=timeout or self.timeout)
        ) as response:
            if response.status >= 400:
                raise HTTPError(
                    status=response.status,
                    message=await response.text(),
                    url=url,
                    method=method
                )

            return await response.json()


@functools.lru_cache(maxsize=256)
def compute_hash(
    data: bytes,
    algorithm: str="sha256",
    encoding: str="hex"
) -> str:
    """Hash."""
    return hashlib.new(algorithm, data).hexdigest() if encoding == "hex" else hashlib.new(algorithm, data).digest()


process_batch = functools.partial(
    process_items,
    batch_size=100,
    timeout=30.0,
    retry_config={
        "max_retries": 3,
        "backoff_factor": 2.0
    },
    on_error=lambda e: logger.error(f"Batch failed: {e}")
)

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "standard",
                "filename": "app.log",
                "maxBytes": 10485760,
                "backupCount": 5
            }
        },
        "loggers": {
            "": {
                "level": "INFO",
                "handlers": [
                    "console",
                    "file"
                ],
                "propagate": True
            }
        }
    }
)

cleanup_tasks = [asyncio.create_task(resource.cleanup(), name=f"cleanup-{resource.name}") for resource in active_resources if resource.state != ResourceState.CLOSED and (resource.age > max_age or resource.error_count > max_errors)]
