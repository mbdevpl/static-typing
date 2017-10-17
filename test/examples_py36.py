
import sys
import typing as t

import numpy as np
import static_typing as st


def function_b1():
    """function with built-in types"""
    a = 0
    b: float
    b = 0.0
    c = 'spam'
    c: str = 'ham'
    d: int
    e = 0.0 # type: float
    f = 0
    f = 0 # type: int
    g, h = 4, 2.0
    i, j = 4, 2.0 # type: int, float
    k, l = 4, 2.0 # type: (int, float)
    m, (n, o) = 4, (2.0, 'eggs')
    p, (r, s) = 4, (2.0, 'eggs') # type: int, (float, str)
    t__, (u, v) = 4, (2.0, 'eggs') # type: (int, (float, str))
    w = w1 = w2 = 'bacon'
    x = x1 = x2 = 'bacon' # type: str
    for y in [0, 1, 2]: # type: int
        z = object() # type: object


def function_b2():
    """function with external types"""
    a: t.List[int] = [0, 1]
    b = [0, 1] # type: t.List[int]
    c: st.ndarray[2, float] = None
    d = None # type: st.ndarray[2, float]
    e: np.double


def function_b6(eggs: bool = True):
    """function with conflicting types in branches"""
    spam = eggs # type: bool
    if spam:
        ham: str = ''
    else:
        ham: int = 0


class class_b2:
    """class with instance fields"""
    def __init__(self):
        self.x = {'spam': 'spam spam spam'} # type: dict
        self.y: float = 0.1
        self.z, self.t = 0.1, 0 # type: float, int
        self.x['lovely'] = 'spam' # type: str


class class_b3:
    """class with instance fields using external types"""
    def __init__(self):
        self.x = 0 # type: np.float16
        self.y: np.float32 = 0.1
        self.z, self.t = 0.1, 0 # type: float, int


class class_b4:
    """class with class fields"""
    spam = {}
    ham = 1 # type: int
    eggs: bool = True
    spam['lovely'] = 'spam' # type: str
    spam['not lovely']: str = 'ham'

