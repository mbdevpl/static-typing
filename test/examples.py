"""Examples to be used in tests."""

import ast
import contextlib
import inspect
import itertools
import sys
import typing as t

import numpy as np
import static_typing as st
import typed_ast.ast3

AST_MODULES = (ast, typed_ast.ast3)


def function_a1():
    """function with built-in types"""
    a = 0
    b = 0.0 # type: float
    c = 'spam'
    c = 'ham' # type: str
    d = 0 # type: int
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


def function_a2():
    """function with external types"""
    a = [0, 1] # type: t.List[int]
    b = [0, 1] # type: t.List[int]
    c = None # type: st.ndarray[2, float]
    d = None # type: st.ndarray[2, float]
    e = 0.0 # type: np.double


def function_3():
    """function with complex type annotations"""
    spam, ham, eggs = '', 0, 0.0 # type: str , int , float
    spam, ham, eggs = '', 0, 0.0 # type: ( str , int , float )
    spam, ham, eggs = '', 0, 0.0 # type: ( ( str , int , float ) )
    spam, (ham, eggs) = '', (0, 0.0) # type: str , ( int , float )
    spam, (ham, eggs) = '', (0, 0.0) # type: str , ( int , float )
    (spam, ham), eggs = ('', 0), 0.0 # type: ( str , int ) , float


def function_a4():
    """function with very complex type annotations, ver. 1"""
    spam, ((ham, bacon), eggs), sausage, beans = \
        '', ((0, 0.0), True), None, b'' # type: str, ((int, float), bool), object, bytes


def function_b4():
    """function with very complex type annotations, ver. 2"""
    spam, (ham, (bacon, eggs)), sausage, beans = \
        '', (0, (0.0, True)), None, b'' # type: str, (int, (float, bool)), object, bytes


def function_c4():
    """function with very complex type annotations, ver. 3"""
    spam, (ham, (bacon, eggs), sausage), beans = \
        '', (0, (0.0, True), None), b'' # type: str, (int, (float, bool), object), bytes


def function_a5():
    """function with very complex type annotations, ver. 4"""
    spam, (ham, eggs), (sausage, bacon) = \
        '', (0, 0.0), (True, None) # type: str, (int, float), (bool, object)


def function_b5():
    """function with very complex type annotations, ver. 5"""
    (spam, ham), eggs, (sausage, bacon) = \
        ('', 0), 0.0, (True, None) # type: (str, int), float, (bool, object)


def function_a6(eggs: bool = True):
    """function with conflicting types in branches"""
    spam = eggs # type: bool
    if spam:
        ham = '' # type: str
    else:
        ham = 0 # type: int


def function_7():
    """function with type-annotated value swap"""
    spam, ham = ham, spam = None, None # type: int, str


def function_a8(spam: int = 0, ham: str = '', eggs: float = 0.0):
    """function with args with type annotations"""
    spam, ham, eggs = None, None, None


def function_b8(spam=0, # type: int
                ham='', # type: str
                eggs=0.0): # type: float
    """function with args with type comments"""
    spam, ham, eggs = None, None, None


def function_9():
    """function with context manager"""
    with contextlib.redirect_stdout(sys.stderr):
        pass
    with contextlib.redirect_stdout(sys.stderr) as spam:  # type: object
        pass

FUNCTIONS = (function_a1, function_a2, function_3, function_a4, function_b4, function_c4,
             function_a5, function_b5, function_a6, function_7, function_a8, function_b8,
             function_9)

if sys.version_info[:2] >= (3, 6):
    from .examples_py36 import function_b1, function_b2, function_b6
    FUNCTIONS += (function_b1, function_b2, function_b6)

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
        't__': (int,),
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
        'e': (np.double,)},
    3: {
        'spam': (str,),
        'ham': (int,),
        'eggs': (float,)},
    4: {
        'spam': (str,),
        'ham': (int,),
        'bacon': (float,),
        'eggs': (bool,),
        'sausage': (object,),
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
        'ham': (str, int)},
    8: {
        'spam': (),
        'ham': (),
        'eggs': ()},
    9: {
        'spam': (object,)}}

FUNCTIONS_LOCAL_VARS = {function.__doc__: _FUNCTIONS_LOCAL_VARS[int(function.__name__[-1])]
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


class class_a2:
    """class with instance fields"""
    def __init__(self):
        self.x = {'spam': 'spam spam spam'} # type: dict
        self.y = 0.1 # type: float
        self.z, self.t = 0.1, 0 # type: float, int
        self.x['lovely'] = 'spam' # type: str


class class_a3:
    """class with instance fields using external types"""
    def __init__(self):
        self.x = 0 # type: np.float16
        self.y = 0.1 # type: np.float32
        self.z, self.t = 0.1, 0 # type: float, int


class class_a4:
    """class with class fields"""
    spam = {}
    ham = 1 # type: int
    eggs = True # type: bool
    spam['lovely'] = 'spam' # type: str
    spam['not lovely'] = 'ham' # type: str


CLASSES = (class_1, class_a2, class_a3, class_a4)

if sys.version_info[:2] >= (3, 6):
    from .examples_py36 import class_b2, class_b3, class_b4
    CLASSES += (class_b2, class_b3, class_b4)

CLASSES_SOURCE_CODES = {cls.__doc__: inspect.getsource(cls) for cls in CLASSES}

_CLASSES_MEMBERS = {
    1: (['x'], [], {'__init__', 'do_nothing', 'do_something', 'make_noise'}),
    2: ([], ['x', 'y', 'z', 't'], {'__init__'}),
    3: ([], ['x', 'y', 'z', 't'], {'__init__'}),
    4: (['spam', 'ham', 'eggs'], [], set())}

CLASSES_MEMBERS = {cls.__doc__: _CLASSES_MEMBERS[int(cls.__name__[-1])] for cls in CLASSES}

MODULES_SOURCE_CODES = {
    'simple module': 'import contextlib\n\n{}\n\nTEST = 1\n\n{}'.format(
        inspect.getsource(function_9), inspect.getsource(class_a4)),
    'simple module with external types': '{}\n\n{}'.format(
        '\n'.join(['import numpy as np', 'import static_typing as st', 'import typing as t']),
        inspect.getsource(function_a2))}

SOURCE_CODES = {k: v for k, v in itertools.chain(
    FUNCTIONS_SOURCE_CODES.items(), CLASSES_SOURCE_CODES.items(), MODULES_SOURCE_CODES.items())}

TYPE_HINTS = {ast_module: {
    'int': ('int', ast_module.Name('int', ast_module.Load()), int),
    'str': ('str', ast_module.Name('str', ast_module.Load()), str),
    'dict as AST': (ast_module.Name('dict', ast_module.Load()), ast_module.Name('dict', ast_module.Load()), dict),
    'hint with external type': ('np.float', ast_module.Attribute(
        ast_module.Name('np', ast_module.Load()), 'float', ast_module.Load()), np.float),
    'unresolvable hint': (int, int, int),
    'unresolvable hint with external type': (np.int, np.int, np.int)}
              for ast_module in AST_MODULES}

GLOBALS_NONE = None

GLOBALS_CLEAR = {'__builtins__': globals()['__builtins__']}

GLOBALS_EXTERNAL = {'__builtins__': globals()['__builtins__'], 'np': np, 'st': st, 't': t}

GLOBALS_EXAMPLES = (GLOBALS_NONE, GLOBALS_CLEAR, GLOBALS_EXTERNAL)

LOCALS_NONE = None

LOCALS_CLEAR = {}

LOCALS_EXTERNAL = {'np': np, 'st': st, 't': t}

LOCALS_EXAMPLES = (LOCALS_NONE, LOCALS_CLEAR, LOCALS_EXTERNAL)
