"""My badly formatted python file!"""
import os
from cleer import (
    Cleer,
    CleerConfig,
    CleerError,
    CleerGroup
)
__version__ = "0.1.0"
from typing import Dict, List, Literal
from my_package import here, there, everywhere, now_here, now_there, and_everywhere
import requests
from some_lib.is_a_really_long.long_long.lots_of_lengthy_words_are_here import (
    a_really_long_here_toooooo)


# bad stuff
tup = (2, )
thing = {
    "hello"  :"there" ,
    "hi": "now" ,
}
find =  [0, 1, 3,4,5,"hello ther lov", "how is all of that",]

thing =[
    {
        "hello":  [1,2, "hello", "there", "how"],
        "there":  [
            2  ,
            7,
            - 1
        ],
        "now": {
            "there": 103
        }
    }
]

if thing == "this" or hello_there == "that" or fine_great != thing:

    print(0)
elif hello == "that" or True != False and fine_great == "1234":

    thing = "that"
    print(10)
else:

    print(8)

@decor("ldkfjd  ", "sdflkjsdfk   ", "ksdjfdk", "alskdjfaslkdfj")


def say_hello(hello: str=None, hello_there: int=10, fine_great: str="1234232"):
    my_dict = {"thing": "here"}
    print(my_dict['thing'])
    if thing == "this" or hello_there == "that" or fine_great != thing:

        return 0

    elif hello == "that" or True != False and fine_great == "1234":

        thing = "that"
        return 10
    elif True:

        my_thing = "another"

    else:

        return 8
def say_hello2(hello : str = None,  hello_there: int = 10,  fine_great: str=   "1234232"):

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

  pass
say_hello("dkfj" , 1000, "asdflkjasdfkj", "alsdkflksdfj", "asldkfjalskdjflsdf")
Literal["alsdkfsdfl" , "alskfjslkfdj", "aslkdfjsdfjk", - 1, "evenmore hwerskjfsl"]
my_type = Dict[
    str,
    Dict[
        Literal["asdf", "alsdkflsdkfj", "alskdjflskdfj"],
        Dict[
            str,
            List[Dict[str, int]]
        ]
    ]
]
my_type2 = Dict[
    str,
    List[Dict[str, Dict[str, str]]]
]

@medcor

async def hello(
    thing,
    over="here"
):
    print("hello")
    def inner():

        thing=- 1
        return thing
    print("after")


    print("one more")
    return 0


@some_class_decor(first_val="this_thing", second_value="other_thing")
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
        List[Dict[str, Dict[str, str]]]
    ]
    class InternalThing:
        """_summary_
        """

        var: str
class MyNewType:
    thing: Dict[
        str,
        List[Dict[str, Dict[str, str]]]
    ]
    val: Literal["alsdkfsdfl" , "alskfjslkfdj", "aslkdfjsdfjk", - 1, "evenmore hwerskjfsl"]
    def format(
            self, token: str) -> str:

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
inspection['excluded'].append( {"group": gi,"pattern": exclude_pattern})
def _keep_result(self,result: Inspection | Formatting | FormattingDocument,
    keep_only_excluded: bool,
    keep_not_included: bool
) -> bool:
    if (
        len(result['included']) > 0 or(
            len(result['excluded']) > 0 and keep_only_excluded is True
        ) or keep_not_included is True
    ):
        print(("this is my string literal"
                "this is my string literal 2"
            )
        )
        return True

    return False

def _format_one(
    self,file_path: str | pathlib.Path, document: str | None
) -> FormattingDocument:
    formatting: FormattingDocument = {"path": file_path,
        "included": [

        ],
        "excluded": [],
        "invalidations": [],
        "document": document
    }
def _keep_result(self,result: Inspection | Formatting | FormattingDocument,
    keep_only_excluded: bool,
    keep_not_included: bool
) -> bool:
    inspection['excluded'].append( {"group": gi,"pattern": exclude_pattern})
    if (
        len(result['included']) > 0 or(
            len(result['excluded']) > 0 and keep_only_excluded is True
        ) or keep_not_included is True
    ):
        print(("this is my string literal"
                "this is my string literal 2"
            )
        )
        return True
    elif (
        len(result['included']) > 0 or
        ( len(result['excluded']) > 0 and keep_only_excluded is True ) or
        keep_not_included is True or
        my_function_call(here, there="now", over="here") or my_other_call({"hello": "there"}) or
        last_call("here", 2, 3) or thing not in [0, 1, 2, 3] or ((1==2 or True)and(this=="that" or that =="this"))
    ):
        return True

    return False


my_func_call_herethere(thing="here", that="this", there="now").no_args_call().another_one("hello").last_one([1,2,3])
my_func_call_herethere(thing="here", that="this").no_args_call().another_one("hello").last_one([1,2,3, {"hello": "there"}])
my_func_call_herethere(thing="here", that="this").no_args_call()
my_func_call_herethere(thing="here", that="this").no_args_call().another_one("h")


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
                                num_blank_lines=0, message="No blank lines between start of code blocks and first line of body."
                            ),
                            thing(hello="there", here="now", you="good")
                        ]
                    }
                ]
            }
        ]
    }

logger.debug(
    f"Python Packages: {python_packages}\n"
    f"Internal Python Packages: {python_internal_packages}\n"
    f" Excludes: {json.dumps(excludes, indent=4)}"
)
logger.debug(f"Python Packages: {python_packages}\n"f"Internal Python Packages: {python_internal_packages}\n"
    f" Excludes: {json.dumps(excludes, indent=4)}"
)

thing = (
        f"Python Packages: {python_packages}\n"
    f"Internal Python Packages: {python_internal_packages}\n"
    f" Excludes: {json.dumps(excludes, indent=4)}"
)
other = here((f"Python Packages: {python_packages}\n"f"Internal Python Packages: {python_internal_packages}\n"f" Excludes: {json.dumps(excludes, indent=4)}"
), 1234)


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
            "**/tests/unit/fixtures/format_*.py",
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
                if innermost_class is None or (range_end - range_start) < (innermost_class[1] - innermost_class[0]):
                    innermost_func = (range_start, range_end)

        innermost_class = None

        for range_start, range_end in self._class_ranges:
            if start >= range_start and end <= range_end:
                if (
                    innermost_class is None
                    or (range_end - range_start) < (
                        innermost_class[1] - innermost_class[0]
                    )
                ):
                    innermost_class = (range_start, range_end)

        if innermost_func and innermost_class:
            func_size = innermost_func[1] - innermost_func[0]
            class_size = innermost_class[1] - innermost_class[0]

            return func_size < class_size

        is_docstring = i == 0 or isinstance(body[i - 1], (ast.Assign, ast.AnnAssign))
        is_docstring = (
            i == 0
            or isinstance(body[i - 1], (ast.Assign, ast.AnnAssign))
        )
        default_idx = i - (len(args.posonlyargs) + len(args.args) - num_defaults)
        default_idx = i - (
                len(args.posonlyargs) + len(args.args) - num_defaults
            )
        if thing:
            return [{
                "token": token,
                "index": prev_end,
                "length": len(token)
            }]

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


content_len = len(
    region['open_char']
) + len(", ".join(items)) + len(region['close_char'])
content_len = len(region['open_char']) + len(", ".join(items)) + len(region['close_char'])
quote = content[i:i + 3] if content[i:i + 3] in ('"""', "'''") else ch
quote = content[i:i + 3] if content[i:i + 3] in (
    '"""',
    "'''"
) else ch


def return_logic():
    if this:
        return (
            isinstance(first_node, ast.Expr) and isinstance(first_node.value, ast.Constant) and isinstance(first_node.value.value, str)
        )
    child_depth = depth if isinstance(
        node,
        ast.Module
    ) else depth + 1

    return (
            isinstance(first_node, ast.Expr)
            and isinstance(first_node.value, ast.Constant)
            and isinstance(first_node.value.value, str)
        )


actual_indent = len(leading.replace("\t", " " * self._tab_size))
actual_indent = len(
    leading.replace("\t", " " * self._tab_size)
)

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





    
