



import pytest

from cleer import there, Cleer, here, everywhere
import my_pkg
from . import utils
import sys
import os

@pytest.thing("thing", 4, 
    "here")


def my_func(a, b, c = "hello", d=4):
    x=my_dict["key"]
    y = other.get('value')
    data = [1, 2, 3]
    nested = my_func([{"my_key": [1,2], 'other_key': [0],}])
    bad_nested = {
[
    {
    "bad_nesting": True
    }
]
    }
    worse_nesting = {
[
    {
    "bad_nesting": True,
    "worse_nesting": True
    }
]
    }

    return x + y


here=True==[]    
def short():
    return 1
def another(a,  b):
    thing = "hello"
    result = thing + " world"

    yield result
    result = "none"
    return result
another(a="thing",
        b = "hello")

class Thing:     
    def __init__(self, thing, another):
        """_summary_

        Parameters
        ----------
        thing : _type_
            _description_
        another : _type_
            _description_
        """
        pass
        
    def do_it(self):
        """Do the thing

        Returns
        -------
        _type_
            _description_
        
        Examples
        -------
        ```python 
        tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
        tokens = tokenizer.tokenize("def func(x, y = 5):\\n    pass\\n")
        ```
        """
        to = 4
        return 4
    
    
    def another(self):
        if True:
            hello="goodbye"
        for _ in range(5):

            print("hello")
        if True:
            if True:
        
                return 8 
        hello = "hello"

    def another1(self):

        return 9
def new_thing(a,b,c
):

    return -1
async def athing(a, b, c):

    return -1

class MyType:


    my_var: int=5

class MyOtherType:
    """Thing
    """

    my_other_var: str = "hello"

    def _find_close_in_text(
        self,
        text: str,
        open_pos: int,
        open_char: str,
        close_char: str
    ) -> int:
        """Find the matching closing character in text."""
        depth = 1
        i = open_pos + 1
        in_single = False
        in_double = False

        while i < len(text):
            if text[i] == "\\" and (in_single or in_double):
                i += 2
                continue

            if text[i] == "'" and not in_double:
                in_single = not in_single

            elif text[i] == '"' and not in_single:
                in_double = not in_double

            elif not in_single and not in_double:
                if text[i] == open_char:
                    depth += 1

                elif text[i] == close_char:
                    depth -= 1
                    if depth == 0:
                        return i

            i += 1

        return -1

for i in range(
    5 - 1,
    - 1,
    - 1
):
    print(i)

def translate(pat, *, recursive=False, include_hidden=False, seps=None):
    return 4