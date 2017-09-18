"""Unit tests for nodes module."""

import logging
import unittest

from static_typing.nodes.module import StaticallyTypedModule
from static_typing.nodes.function_def import StaticallyTypedFunctionDef
from static_typing.nodes.class_def import StaticallyTypedClassDef
from .examples import \
    AST_MODULES, FUNCTIONS_SOURCE_CODES, FUNCTIONS_LOCAL_VARS, CLASSES_SOURCE_CODES, CLASSES_MEMBERS

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
        pass

    def test_ann_assign(self):
        pass

    def test_for(self):
        pass
