"""Examples to be used in tests."""

import ast
import inspect
import typing as t

import numpy as np
import static_typing as st
import typed_ast.ast3

AST_MODULES = (ast, typed_ast.ast3)


def function_1():
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
    t, (u, v) = 4, (2.0, 'eggs') # type: (int, (float, str))
    w = w1 = w2 = 'bacon'
    x = x1 = x2 = 'bacon' # type: str
    for y in [0, 1, 2]: # type: int
        z = object() # type: object


def function_2():
    """function with external types"""
    a: t.List[int] = [0, 1]
    b = [0, 1] # type: t.List[int]
    c: st.ndarray[2, float] = None
    d = None # type: st.ndarray[2, float]
    e: np.double


def function_3():
    """function with complex type annotations"""
    spam, ham, eggs = '', 0, 0.0 # type: str , int , float
    spam, ham, eggs = '', 0, 0.0 # type: ( str , int , float )
    spam, ham, eggs = '', 0, 0.0 # type: ( ( str , int , float ) )
    spam, (ham, eggs) = '', 0, 0.0 # type: str , ( int , float )
    spam, (ham, eggs) = '', 0, 0.0 # type: str , ( int , float )
    (spam, ham), eggs = '', 0, 0.0 # type: ( str , int ) , float


def function_a4():
    """function with very complex type annotations, ver. 1"""
    spam , ( ( ham , bacon ) , eggs ) , sausage , beans = \
        '', 0, 0.0, True, None, b'' # type: str, ((int, float), bool), object, bytes


def function_b4():
    """function with very complex type annotations, ver. 2"""
    spam , ( ham , ( bacon , eggs ) ) , sausage , beans = \
        '', 0, 0.0, True, None, b'' # type: str, (int, (float, bool)), object, bytes


def function_c4():
    """function with very complex type annotations, ver. 3"""
    spam , ( ham , ( bacon , eggs ) , sausage ) , beans = \
        '', 0, 0.0, True, None, b'' # type: str, (int, (float, bool), object), bytes


def function_a5():
    """function with very complex type annotations, ver. 4"""
    spam , (ham, eggs), (sausage, bacon) = \
        '', 0, 0.0, True, None # type: str, (int, float), bool, object


def function_b5():
    """function with very complex type annotations, ver. 5"""
    (spam, ham), eggs, (sausage, bacon) = \
        '', 0, 0.0, True, None # type: (str, int), float, (bool, object)


def function_6():
    """function with conflicting types in branches"""
    spam: bool = True
    if spam:
        ham: str = ''
    else:
        ham: int = 0


def function_7():
    """function with type-annotated value swap"""
    spam, ham = ham, spam = None, None # type: int, str


FUNCTIONS = (function_1, function_2, function_3, function_a4, function_b4, function_c4,
            function_a5, function_b5, function_6, function_7)

FUNCTIONS_SOURCE_CODES = {function.__doc__: inspect.getsource(function) for function in FUNCTIONS}

_FUNCTIONS_LOCAL_VARS = {
    1: {
        'a': (),
        'b': (float,),
        'c': (str,),
        'd': (int,),
        'e': (float,),
        'f': (int,),
        'g': (),
        'h': (),
        'i': (int,),
        'j': (float,),
        'k': (int,),
        'l': (float,),
        'm': (),
        'n': (),
        'o': (),
        'p': (int,),
        'r': (float,),
        's': (str,),
        't': (int,),
        'u': (float,),
        'v': (str,),
        'w': (),
        'w1': (),
        'w2': (),
        'x': (str,),
        'x1': (str,),
        'x2': (str,),
        'y': (int,),
        'z': (object,)},
    2: {
        'a': (t.List[int],),
        'b': (t.List[int],),
        'c': (st.ndarray[2, float],),
        'd': (st.ndarray[2, float],),
        'd': (np.double,)},
    3: {
        'spam': (str,),
        'ham': (int,),
        'eggs': (float,)},
    4: {
        'spam': (str,),
        'ham': (int,),
        'eggs': (float,),
        'sausage': (bool,),
        'bacon': (object,),
        'beans': (bytes,)},
    5: {
        'spam': (str,),
        'ham': (int,),
        'eggs': (float,),
        'sausage': (bool,),
        'bacon': (object,)},
    6: {
        'spam': (bool,),
        'ham': (str, int)},
    7: {
        'spam': (int, str),
        'ham': (str, int)}}

FUNCTIONS_LOCAL_VARS = {
    function.__doc__: (inspect.getsource(function),
                       _FUNCTIONS_LOCAL_VARS[int(function.__name__[-1])])
    for function in FUNCTIONS}


class class_1:
    """very simple class"""
    x = 0
    def __init__(self):
        pass
    def do_nothing(self) -> None:
        pass
    @classmethod
    def do_something(cls) -> bool:
        return True
    @staticmethod
    def make_noise() -> str:
        return 'noise'


class class_2:
    """class with instance fields"""
    def __init__(self):
        self.x = 'spam' # type: str
        self.y: float = 0.1
        self.z, self.t = 0.1, 0 # type: float, int


class class_3:
    """class with instance fields using external types"""
    def __init__(self):
        self.x = 0 # type: np.float16
        self.y: np.float32 = 0.1
        self.z, self.t = 0.1, 0 # type: float, int


CLASSES = (class_1, class_2, class_3)

CLASSES_SOURCE_CODES = {cls.__doc__: inspect.getsource(cls) for cls in CLASSES}

_CLASSES_MEMBERS = {
    1: {
        '__init__',
        'do_nothing',
        'do_something',
        'make_noise'},
    2: {
        '__init__'},
    3: {
        '__init__'}}

CLASSES_MEMBERS = {
    cls.__doc__: (inspect.getsource(cls), _CLASSES_MEMBERS[int(cls.__name__[-1])])
    for cls in CLASSES}

SOURCE_CODES = {**FUNCTIONS_SOURCE_CODES, **CLASSES_SOURCE_CODES}
