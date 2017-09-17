"""Unit tests for nodes module."""

import logging
import unittest

from static_typing.nodes.module import StaticallyTypedModule
from .examples import AST_MODULES, FUNCTIONS_SOURCE_CODES, CLASSES_SOURCE_CODES

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    maxDiff = None

    def test_module(self):
        for ast_module in AST_MODULES:
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    module = StaticallyTypedModule[ast_module].from_other(tree)
                    self.assertEqual(len(module._functions), 1)
            for description, example in CLASSES_SOURCE_CODES.items():
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    module = StaticallyTypedModule[ast_module].from_other(tree)
                    self.assertEqual(len(module._classes), 1)

    def test_function_def(self):
        pass

    def test_class_def(self):
        pass

    def test_assign(self):
        pass

    def test_ann_assign(self):
        pass

    def test_for(self):
        pass
