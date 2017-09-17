"""Unit tests for nodes module."""

import ast
import itertools
import logging
import typing as t
import unittest

import numpy as np
import typed_ast.ast3

import static_typing as st
from static_typing.nodes.module import StaticallyTypedModule
from .examples import EXAMPLES, CODE_EXAMPLES

_LOG = logging.getLogger(__name__)

AST_MODULES = (ast, typed_ast.ast3)


class Tests(unittest.TestCase):

    maxDiff = None

    def test_module(self):
        for ast_module in AST_MODULES:
            for description, example in CODE_EXAMPLES.items():
                example_data = EXAMPLES[description]
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    module = StaticallyTypedModule[ast_module].from_other(tree)
                    self.assertEqual(len(module._functions), 1 if 'function' in example_data else 0)
                    self.assertEqual(len(module._classes), 1 if 'class' in example_data else 0)

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
