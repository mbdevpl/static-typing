"""Unit tests for nodes module."""

import ast
import collections
import itertools
import logging
import sys
import unittest

import ordered_set
import typed_ast.ast3
import typed_astunparse

from static_typing.ast_manipulation.type_hint_resolver import TypeHintResolver
from static_typing.nodes.statically_typed import StaticallyTyped
from static_typing.nodes.module import StaticallyTypedModule
from static_typing.nodes.function_def import StaticallyTypedFunctionDef
from static_typing.nodes.class_def import StaticallyTypedClassDef
from static_typing.nodes.declaration import StaticallyTypedAssign, StaticallyTypedAnnAssign
from static_typing.nodes.context import StaticallyTypedFor, StaticallyTypedWith
from static_typing.static_typer import StaticTyper
from .examples import \
    AST_MODULES, FUNCTIONS_SOURCE_CODES, FUNCTIONS_LOCAL_VARS, CLASSES_SOURCE_CODES, \
    CLASSES_MEMBERS, MODULES_SOURCE_CODES, SOURCE_CODES, GLOBALS_EXTERNAL

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    maxDiff = None

    def test_statically_typed(self):
        for ast_module in AST_MODULES:
            with self.assertRaises(NotImplementedError):
                StaticallyTyped[ast_module]()

    def test_from_other(self):
        for ast_module in AST_MODULES:
            function_def = ast_module.FunctionDef(
                name='my_function', args=ast_module.arguments(
                    args=[], vararg=None, kwonlyargs=[], kwarg=None, defaults=[], kw_defaults=[]),
                body=[ast_module.Pass()], decorator_list=[], returns=ast_module.NameConstant(None))
            function_def.resolved_returns = None
            static_function_def = StaticallyTypedFunctionDef[ast_module].from_other(function_def)
            self.assertTrue(hasattr(static_function_def, 'resolved_returns'))

    @unittest.skipIf(sys.version_info[:2] < (3, 6), 'requires Python >= 3.6')
    def test_empty(self):
        for ast_module, class_family in itertools.product(AST_MODULES, [
                StaticallyTypedModule, StaticallyTypedFunctionDef, StaticallyTypedClassDef,
                StaticallyTypedAssign, StaticallyTypedAnnAssign, StaticallyTypedFor,
                StaticallyTypedWith]):
            node = class_family[ast_module]()
            self.assertIsInstance(repr(node), str)
            self.assertIsInstance(str(node), str)

    def test_module(self):
        for ast_module in AST_MODULES:
            resolver = TypeHintResolver[ast_module, ast](globals_=GLOBALS_EXTERNAL)
            typer = StaticTyper[ast_module]()
            for description, example in itertools.chain(FUNCTIONS_SOURCE_CODES.items(),
                                                        CLASSES_SOURCE_CODES.items()):
                if description in FUNCTIONS_SOURCE_CODES:
                    classes_count, functions_count = 0, 1
                if description in CLASSES_SOURCE_CODES:
                    classes_count, functions_count = 1, 0
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    module = resolver.visit(tree)
                    module = typer.visit(tree)
                    self.assertIsInstance(module, StaticallyTypedModule[ast_module])
                    self.assertEqual(len(module._classes), classes_count)
                    self.assertEqual(len(module._functions), functions_count)
                    _LOG.info('%s', module)

            for description, example in MODULES_SOURCE_CODES.items():
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    module = resolver.visit(tree)
                    module = typer.visit(tree)
                    self.assertIsInstance(module, StaticallyTypedModule[ast_module])

    def test_function_def(self):
        for ast_module in AST_MODULES:
            resolver = TypeHintResolver[ast_module, ast](globals_=GLOBALS_EXTERNAL)
            typer = StaticTyper[ast_module]()
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                function_local_vars = FUNCTIONS_LOCAL_VARS[description]
                function_local_vars = {k: ordered_set.OrderedSet(v)
                                       for k, v in function_local_vars.items()}
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    function = tree.body[0]
                    function = resolver.visit(function)
                    function = typer.visit(function)
                    self.assertIsInstance(function, StaticallyTypedFunctionDef[ast_module])
                    if ast_module is ast:
                        self.assertEqual(len(function._local_vars), len(function_local_vars))
                    else:
                        self.assertDictEqual(function_local_vars, function._local_vars)
                    _LOG.info('%s', function)

    def test_class_def(self):
        for ast_module in AST_MODULES:
            resolver = TypeHintResolver[ast_module, ast](globals_=GLOBALS_EXTERNAL)
            typer = StaticTyper[ast_module]()
            for description, example in CLASSES_SOURCE_CODES.items():
                class_fields, instance_fields, methods = CLASSES_MEMBERS[description]
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    cls = tree.body[0]
                    cls = resolver.visit(cls)
                    cls = typer.visit(cls)
                    self.assertIsInstance(cls, StaticallyTypedClassDef[ast_module])
                    #if ast_module is ast:
                    #self.assertEqual(len(class_fields), len(cls._class_fields))
                    #self.assertEqual(len(instance_fields), len(cls._instance_fields))
                    #self.assertEqual(len(methods), len(cls._methods))
                    #else:
                    self.assertSetEqual(set(class_fields), set(cls._class_fields))
                    self.assertSetEqual(set(instance_fields), set(cls._instance_fields))
                    self.assertSetEqual(methods, set(cls._methods))
                    _LOG.info('%s', cls)
                    # TODO: validate types of class fields
                    # TODO: validate other details

    def test_assign(self):
        for ast_module in AST_MODULES:
            resolver = TypeHintResolver[ast_module, ast](globals_=GLOBALS_EXTERNAL)
            typer = StaticTyper[ast_module]()
            for example, assigned_vars in {
                    'a = 0\n': {'a': None},
                    'a = 0  # type: int\n': {'a': int},
                    # 'value: float = "oh my"\n': {'value': float}
                    }.items():
                tree = ast_module.parse(example, mode='single')
                node = tree.body[0]
                node = resolver.visit(node)
                with self.subTest(ast_module=ast_module, example=example,
                                  assigned_vars=assigned_vars, node=ast_module.dump(node)):
                    ann_assign = typer.visit(node)
                    self.assertIsInstance(ann_assign, StaticallyTypedAssign[ast_module])
                    self.assertIsInstance(ann_assign._vars, dict)
                    self.assertEqual(len(ann_assign._vars), len(assigned_vars))
                    ann_assign_vars = {typed_astunparse.unparse(name).rstrip(): type_
                                       for name, type_ in ann_assign._vars.items()}
                    if ast_module is ast:
                        self.assertSetEqual(set(ann_assign_vars.keys()), set(assigned_vars.keys()))
                    else:
                        self.assertDictEqual(ann_assign_vars, assigned_vars)
                    _LOG.info('%s', ann_assign)

    def test_assign_in_functions(self):
        for ast_module in AST_MODULES:
            resolver = TypeHintResolver[ast_module, ast](globals_=GLOBALS_EXTERNAL)
            typer = StaticTyper[ast_module]()
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                tree = ast_module.parse(example)
                for node in ast_module.walk(tree):
                    if not isinstance(node, ast_module.Assign):
                        continue
                    node = resolver.visit(node)
                    with self.subTest(ast_module=ast_module, msg=description, example=example,
                                      node=ast_module.dump(node)):
                        assign = typer.visit(node)
                        self.assertIsInstance(assign, StaticallyTypedAssign[ast_module])
                        self.assertGreaterEqual(len(assign._vars), 1)
                        _LOG.info('%s', assign)
                        # TODO: validate types of declared variables

    def test_bad_assign(self):
        example = 'x, y = 1, 2 # type: int'
        resolver = TypeHintResolver[typed_ast.ast3, ast](globals_=GLOBALS_EXTERNAL)
        typer = StaticTyper[typed_ast.ast3]()
        tree = typed_ast.ast3.parse(example)
        tree = resolver.visit(tree)
        with self.assertRaises(TypeError):
            typer.visit(tree)

    @unittest.skipIf(sys.version_info[:2] < (3, 6), 'requires Python >= 3.6')
    def test_ann_assign(self):
        for ast_module in AST_MODULES:
            resolver = TypeHintResolver[ast_module, ast](globals_=GLOBALS_EXTERNAL)
            typer = StaticTyper[ast_module]()
            for example, assigned_vars in {
                    'a: int\n': {'a': int},
                    'a: int = 0\n': {'a': int},
                    'value: float = "oh my"\n': {'value': float}}.items():
                tree = ast_module.parse(example, mode='single')
                node = tree.body[0]
                node = resolver.visit(node)
                with self.subTest(ast_module=ast_module, example=example,
                                  assigned_vars=assigned_vars, node=ast_module.dump(node)):
                    ann_assign = typer.visit(node)
                    self.assertIsInstance(ann_assign, StaticallyTypedAnnAssign[ast_module])
                    self.assertIsInstance(ann_assign._vars, dict)
                    self.assertEqual(len(ann_assign._vars), len(assigned_vars))
                    ann_assign_vars = {typed_astunparse.unparse(name).rstrip(): type_
                                       for name, type_ in ann_assign._vars.items()}
                    self.assertDictEqual(ann_assign_vars, assigned_vars)
                    _LOG.info('%s', ann_assign)

    @unittest.skipIf(sys.version_info[:2] < (3, 6), 'requires Python >= 3.6')
    def test_ann_assign_in_functions(self):
        for ast_module in AST_MODULES:
            resolver = TypeHintResolver[ast_module, ast](globals_=GLOBALS_EXTERNAL)
            typer = StaticTyper[ast_module]()
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                tree = ast_module.parse(example)
                for node in ast_module.walk(tree):
                    if not isinstance(node, ast_module.AnnAssign):
                        continue
                    node = resolver.visit(node)
                    with self.subTest(ast_module=ast_module, msg=description, example=example,
                                      node=ast_module.dump(node)):
                        ann_assign = typer.visit(node)
                        self.assertIsInstance(ann_assign, StaticallyTypedAnnAssign[ast_module])
                        self.assertEqual(len(ann_assign._vars), 1)
                        _LOG.info('%s', ann_assign)
                        # TODO: validate types of declared variables

    def test_use_unresolved_hints(self):
        for ast_module in AST_MODULES:
            if ast_module is ast:
                continue
            resolver = TypeHintResolver[ast_module, ast_module](False)
            typer = StaticTyper[ast_module]()
            raised = False
            for description, example in SOURCE_CODES.items():
                tree = ast_module.parse(example)
                tree = resolver.visit(tree)
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    #with self.assertRaises(TypeError):
                    # TODO: type error should be always raised
                    try:
                        typer.visit(tree)
                    except TypeError:
                        raised = True
            self.assertTrue(raised)
