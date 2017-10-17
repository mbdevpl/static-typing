"""Unit tests for augment() and parse() functions."""

import itertools
import logging
import unittest

from static_typing.augment import augment
from static_typing.parse import parse
from .examples import \
    AST_MODULES, FUNCTIONS_SOURCE_CODES, CLASSES_SOURCE_CODES, GLOBALS_EXTERNAL, \
    GLOBALS_EXAMPLES

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    maxDiff = None

    def test_augment_functions(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, GLOBALS_EXAMPLES, (None,)):
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                with self.subTest(msg=description, example=example):
                    tree = ast_module.parse(example)
                    if 'external types' in description and globals_ is not GLOBALS_EXTERNAL:
                        with self.assertRaises(NameError):
                            augment(tree, globals_, locals_, ast_module)
                        continue
                    tree = augment(tree, globals_, locals_, ast_module)
                    # TODO: validate tree

    def test_augment_classes(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, GLOBALS_EXAMPLES, (None,)):
            for description, example in CLASSES_SOURCE_CODES.items():
                with self.subTest(msg=description, example=example):
                    tree = ast_module.parse(example)
                    if 'external types' in description and globals_ is not GLOBALS_EXTERNAL:
                        with self.assertRaises(NameError):
                            augment(tree, globals_, locals_, ast_module)
                        continue
                    tree = augment(tree, globals_, locals_, ast_module)
                    # TODO: validate tree

    def test_parse_functions(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, GLOBALS_EXAMPLES, (None,)):
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                with self.subTest(msg=description, example=example):
                    if 'external types' in description and globals_ is not GLOBALS_EXTERNAL:
                        with self.assertRaises(NameError):
                            parse(example, globals_, locals_, ast_module)
                        continue
                    tree = parse(example, globals_, locals_, ast_module)
                    # TODO: validate tree

    def test_parse_classes(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, GLOBALS_EXAMPLES, (None,)):
            for description, example in CLASSES_SOURCE_CODES.items():
                with self.subTest(msg=description, example=example):
                    if 'external types' in description and globals_ is not GLOBALS_EXTERNAL:
                        with self.assertRaises(NameError):
                            parse(example, globals_, locals_, ast_module)
                        continue
                    tree = parse(example, globals_, locals_, ast_module)
                    # TODO: validate tree
