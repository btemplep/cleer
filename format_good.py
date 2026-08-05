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
