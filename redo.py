


""""""

___all__ = ["hello"]


import os
from typing import Dict, List, Literal

from cleer import (
    Cleer,
    CleerConfig,
    CleerError,
    CleerGroup
)


# bad stuff 
tup = (2, )   
thing = {
    "hello": "there" ,
    "hi": "now" ,
}
find =  [0, 1, 3,4,5,"hello ther lov", "how is all of that",]

thing =[  
    {
        "hello":  [1,2, "hello", "there", "how"],
        "there":  [
            2, 
            7,
            - 1
        ], 
        "now": {
            "there": 103
        }
    }
]

@decor("ldkfjd  ", "sdflkjsdfk   ", "ksdjfdk", "alskdjfaslkdfj")

def say_hello(hello: str = None, hello_there: int = 10, fine_great: str = "1234232"):
    my_dict = {"thing": 'here'}
    print(my_dict["thing"])


def say_hello2(hello: str = None,  hello_there: int = 10,  fine_great: str=   "1234232"):
  pass
say_hello("dkfj", 1000, "asdflkjasdfkj", "alsdkflksdfj", "asldkfjalskdjflsdf")
Literal["alsdkfsdfl", "alskfjslkfdj", "aslkdfjsdfjk", - 1]
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
my_type = Dict[
    str, 
    List[
        Dict[str, Dict[str, str]]
    ]
]

@medcor

async def hello():
    print("hello")
    def inner():
        thing=- 1
        return thing
    print("after")
    

    print("one more")
    return 0


class MyClass:
    async def hello(self):
        print("hello")
        def inner():
          pass
        print("after")


        print("one more")
        return 0