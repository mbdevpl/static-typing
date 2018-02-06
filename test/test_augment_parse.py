"""Unit tests for augment() and parse() functions."""

import itertools
import logging
import sys
import unittest

from static_typing.augment import augment
from static_typing.parse import parse
from .examples import \
    AST_MODULES, FUNCTIONS_SOURCE_CODES, CLASSES_SOURCE_CODES, SOURCE_CODES, GLOBALS_EXTERNAL, \
    GLOBALS_EXAMPLES, LOCALS_EXTERNAL, LOCALS_EXAMPLES

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    maxDiff = None

    def _should_fail(self, description, globals_, locals_):
        return 'external types' in description and globals_ is not GLOBALS_EXTERNAL \
            and locals_ is not LOCALS_EXTERNAL

    @unittest.skipIf(sys.version_info[:2] < (3, 6), 'requires Python >= 3.6')
    def test_augment_functions(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, GLOBALS_EXAMPLES, LOCALS_EXAMPLES):
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    if self._should_fail(description, globals_, locals_):
                        with self.assertRaises(NameError):
                            augment(tree, True, globals_, locals_, ast_module)
                        continue
                    tree = augment(tree, True, globals_, locals_, ast_module)
                    # TODO: validate tree

    @unittest.skipIf(sys.version_info[:2] < (3, 6), 'requires Python >= 3.6')
    def test_augment_classes(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, GLOBALS_EXAMPLES, LOCALS_EXAMPLES):
            for description, example in CLASSES_SOURCE_CODES.items():
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    tree = ast_module.parse(example)
                    if self._should_fail(description, globals_, locals_):
                        with self.assertRaises(NameError):
                            augment(tree, True, globals_, locals_, ast_module)
                        continue
                    tree = augment(tree, True, globals_, locals_, ast_module)
                    # TODO: validate tree

    @unittest.skipIf(sys.version_info[:2] < (3, 6), 'requires Python >= 3.6')
    def test_parse_functions(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, GLOBALS_EXAMPLES, LOCALS_EXAMPLES):
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    if self._should_fail(description, globals_, locals_):
                        with self.assertRaises(NameError):
                            parse(example, True, globals_, locals_, ast_module)
                        continue
                    tree = parse(example, True, globals_, locals_, ast_module)
                    # TODO: validate tree

    @unittest.skipIf(sys.version_info[:2] < (3, 6), 'requires Python >= 3.6')
    def test_parse_classes(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, GLOBALS_EXAMPLES, LOCALS_EXAMPLES):
            for description, example in CLASSES_SOURCE_CODES.items():
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    if self._should_fail(description, globals_, locals_):
                        with self.assertRaises(NameError):
                            parse(example, True, globals_, locals_, ast_module)
                        continue
                    tree = parse(example, True, globals_, locals_, ast_module)
                    # TODO: validate tree

    def test_without_eval(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, GLOBALS_EXAMPLES, LOCALS_EXAMPLES):
            for description, example in SOURCE_CODES.items():
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    raw_tree = ast_module.parse(example)
                    try:
                        tree1 = parse(example, False, globals_, locals_, ast_module)
                        tree2 = augment(raw_tree, False, globals_, locals_, ast_module)
                    except TypeError:
                        continue
                    # TODO: validate tree1
                    # TODO: validate tree2

    def test_parse_in_caller_context(self):
        example = 'my_object = MyClass() # type: MyClass'
        with self.assertRaises(NameError):
            parse(example)
        class MyClass:
            pass
        tree = parse(example)
        assign = tree.body[0]
        self.assertDictEqual({k.id: v for k, v in assign._vars.items()}, {'my_object': MyClass})
