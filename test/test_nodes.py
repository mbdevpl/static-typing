"""Unit tests for nodes module."""

import ast
import itertools
import logging
import unittest

import ordered_set

from static_typing.ast_manipulation.type_hint_resolver import TypeHintResolver
from static_typing.nodes.module import StaticallyTypedModule
from static_typing.nodes.function_def import StaticallyTypedFunctionDef
from static_typing.nodes.class_def import StaticallyTypedClassDef
from static_typing.nodes.declaration import StaticallyTypedAssign, StaticallyTypedAnnAssign
from static_typing.static_typer import StaticTyper
from .examples import \
    AST_MODULES, FUNCTIONS_SOURCE_CODES, FUNCTIONS_LOCAL_VARS, CLASSES_SOURCE_CODES, \
    CLASSES_MEMBERS, GLOBALS_EXTERNAL

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    maxDiff = None

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
                    self.assertListEqual(class_fields, list(cls._class_fields))
                    self.assertListEqual(instance_fields, list(cls._instance_fields))
                    self.assertSetEqual(methods, set(cls._methods))
                    _LOG.info('%s', cls)
                    # TODO: validate types of class fields
                    # TODO: validate other details

    def test_assign(self):
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

    def test_ann_assign(self):
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
