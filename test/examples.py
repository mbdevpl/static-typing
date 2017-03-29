'''
Created on Mar 27, 2017

@author: mb
'''

import typing as t

import static_typing as st

def function1():
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

function1_reference = {
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
    'z': (object,)}

def function2():
    a: t.List[int] = [0, 1]
    b = [0, 1] # type: t.List[int]
    c: st.ndarray[2, float] = None
    d = None # type: st.ndarray[2, float]

function2_reference = {
    'a': (t.List[int],),
    'b': (t.List[int],),
    'c': (st.ndarray[2, float],),
    'd': (st.ndarray[2, float],)}

def function3():
    spam, ham, eggs = '', 0, 0.0 # type: str , int , float
    spam, ham, eggs = '', 0, 0.0 # type: ( str , int , float )
    spam, ham, eggs = '', 0, 0.0 # type: ( ( str , int , float ) )
    spam, (ham, eggs) = '', 0, 0.0 # type: str , ( int , float )
    spam, (ham, eggs) = '', 0, 0.0 # type: str , ( int , float )
    (spam, ham), eggs = '', 0, 0.0 # type: ( str , int ) , float

function3_reference = {
    'spam': (str,),
    'ham': (int,),
    'eggs': (float,)}

def function4a():
    spam , ( ( ham , bacon ) , eggs ) , sausage , beans = '', 0, 0.0, True, None, b'' # type: str, ((int, float), bool), object, bytes

def function4b():
    spam , ( ham , ( bacon , eggs ) ) , sausage , beans = '', 0, 0.0, True, None, b'' # type: str, (int, (float, bool)), object, bytes

def function4c():
    spam , ( ham , ( bacon , eggs ) , sausage ) , beans = '', 0, 0.0, True, None, b'' # type: str, (int, (float, bool), object), bytes

function4_reference = {
    'spam': (str,),
    'ham': (int,),
    'eggs': (float,),
    'sausage': (bool,),
    'bacon': (object,),
    'beans': (bytes,)}

def function5a():
    spam , (ham, eggs), (sausage, bacon) = '', 0, 0.0, True, None # type: str, (int, float), bool, object

def function5b():
    (spam, ham), eggs, (sausage, bacon) = '', 0, 0.0, True, None # type: (str, int), float, (bool, object)

function5_reference = {
    'spam': (str,),
    'ham': (int,),
    'eggs': (float,),
    'sausage': (bool,),
    'bacon': (object,)}

def function6():
    spam: bool = True
    if spam:
        ham: str = ''
    else:
        ham: int = 0

function6_reference = {
    'spam': (bool,),
    'ham': (str, int)}

def function7():
    spam, ham = ham, spam = None, None # type: int, str

function7_reference = {
    'spam': (int, str),
    'ham': (str, int)}

class class1:
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

class1_reference = {
    '__init__',
    'do_nothing',
    'do_something',
    'make_noise'}

EXAMPLES = {
    'function with built-in types': {
        'function': function1, 'reference': function1_reference},
    'function with external types': {
        'function': function2, 'reference': function2_reference},
    'function with complex type annotations': {
        'function': function3, 'reference': function3_reference},
    'function with very complex type annotations': {
        'function': function4a, 'reference': function4_reference},
    'function with very complex type annotations': {
        'function': function4b, 'reference': function4_reference},
    'function with very complex type annotations': {
        'function': function4c, 'reference': function4_reference},
    'function with very complex type annotations': {
        'function': function5a, 'reference': function5_reference},
    'function with very complex type annotations': {
        'function': function5b, 'reference': function5_reference},
    'function with conflicting types in branches': {
        'function': function6, 'reference': function6_reference},
    'function with type-annotated value swap': {
        'function': function7, 'reference': function7_reference},
    'very simple class': {
        'class': class1, 'reference': class1_reference}}
