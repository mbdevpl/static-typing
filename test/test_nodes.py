"""Unit tests for nodes module."""

import ast
import logging
import unittest

from static_typing.ast_manipulation.type_hint_resolver import TypeHintResolver
from static_typing.nodes.module import StaticallyTypedModule
from static_typing.nodes.function_def import StaticallyTypedFunctionDef
from static_typing.nodes.class_def import StaticallyTypedClassDef
from static_typing.nodes.declaration import StaticallyTypedAssign, StaticallyTypedAnnAssign
from .examples import \
    AST_MODULES, FUNCTIONS_SOURCE_CODES, FUNCTIONS_LOCAL_VARS, CLASSES_SOURCE_CODES, \
    CLASSES_MEMBERS, GLOBALS_EXTERNAL

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    maxDiff = None

    def test_module(self):
        for ast_module in AST_MODULES:
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    module = StaticallyTypedModule[ast_module].from_other(tree)
                    self.assertEqual(len(module._classes), 0)
                    self.assertEqual(len(module._functions), 1)
                    _LOG.info('%s', module)
            for description, example in CLASSES_SOURCE_CODES.items():
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    module = StaticallyTypedModule[ast_module].from_other(tree)
                    self.assertEqual(len(module._classes), 1)
                    self.assertEqual(len(module._functions), 0)
                    _LOG.info('%s', module)

    def test_function_def(self):
        for ast_module in AST_MODULES:
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                function_local_vars = FUNCTIONS_LOCAL_VARS[description]
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    function_tree = tree.body[0]
                    function = StaticallyTypedFunctionDef[ast_module].from_other(function_tree)
                    #self.assertEqual(len(function._local_vars), len(function_local_vars))
                    _LOG.info('%s', function)
                    # TODO: validate types of local vars

    def test_class_def(self):
        for ast_module in AST_MODULES:
            for description, example in CLASSES_SOURCE_CODES.items():
                class_members = CLASSES_MEMBERS[description]
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    cls_tree = tree.body[0]
                    cls = StaticallyTypedClassDef[ast_module].from_other(cls_tree)
                    #self.assertEqual(len(cls._methods), len(class_members))
                    _LOG.info('%s', cls)
                    # TODO: validate types of class fields

    def test_assign(self):
        for ast_module in AST_MODULES:
            resolver = TypeHintResolver[ast_module, ast](globals_=GLOBALS_EXTERNAL)
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                tree = ast_module.parse(example)
                for node in ast_module.walk(tree):
                    if isinstance(node, ast_module.Assign):
                        node = resolver.visit(node)
                        with self.subTest(ast_module=ast_module, msg=description, example=example,
                                          node=ast_module.dump(node)):
                            assign = StaticallyTypedAssign[ast_module].from_other(node)
                            self.assertGreaterEqual(len(assign._vars), 1)
                            _LOG.info('%s', assign)
                            # TODO: validate types of declared variables

    def test_ann_assign(self):
        for ast_module in AST_MODULES:
            resolver = TypeHintResolver[ast_module, ast](globals_=GLOBALS_EXTERNAL)
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                tree = ast_module.parse(example)
                for node in ast_module.walk(tree):
                    if isinstance(node, ast_module.AnnAssign):
                        node = resolver.visit(node)
                        with self.subTest(ast_module=ast_module, msg=description, example=example,
                                          node=ast_module.dump(node)):
                            ann_assign = StaticallyTypedAnnAssign[ast_module].from_other(node)
                            self.assertEqual(len(ann_assign._vars), 1)
                            _LOG.info('%s', ann_assign)
                            # TODO: validate types of declared variables
