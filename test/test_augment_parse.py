"""Unit tests for augment() and parse() functions."""

import itertools
import logging
import typing as t
import unittest

import numpy as np

import static_typing as st
from static_typing.augment import augment
from static_typing.parse import parse
from .examples import AST_MODULES, FUNCTIONS_SOURCE_CODES, CLASSES_SOURCE_CODES

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    maxDiff = None

    def test_augment_functions(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, (None, globals()), (None,)):
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                with self.subTest(msg=description, example=example):
                    tree = ast_module.parse(example)
                    if globals_ is None and 'external types' in description:
                        with self.assertRaises(NameError):
                            augment(tree, globals_, locals_, ast_module)
                        continue
                    tree = augment(tree, globals_, locals_, ast_module)
                    # TODO: validate tree

    def test_augment_classes(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, (None, globals()), (None,)):
            for description, example in CLASSES_SOURCE_CODES.items():
                with self.subTest(msg=description, example=example):
                    tree = ast_module.parse(example)
                    if globals_ is None and 'external types' in description:
                        with self.assertRaises(NameError):
                            augment(tree, globals_, locals_, ast_module)
                        continue
                    tree = augment(tree, globals_, locals_, ast_module)
                    # TODO: validate tree

    def test_parse_functions(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, (None, globals()), (None,)):
            for description, example in FUNCTIONS_SOURCE_CODES.items():
                with self.subTest(msg=description, example=example):
                    if globals_ is None and 'external types' in description:
                        with self.assertRaises(NameError):
                            parse(example, globals_, locals_, ast_module)
                        continue
                    tree = parse(example, globals_, locals_, ast_module)
                    # TODO: validate tree

    def test_parse_classes(self):
        for ast_module, globals_, locals_ in itertools.product(
                AST_MODULES, (None, globals()), (None,)):
            for description, example in CLASSES_SOURCE_CODES.items():
                with self.subTest(msg=description, example=example):
                    if globals_ is None and 'external types' in description:
                        with self.assertRaises(NameError):
                            parse(example, globals_, locals_, ast_module)
                        continue
                    tree = parse(example, globals_, locals_, ast_module)
                    # TODO: validate tree

    '''
    @unittest.skip("not ready")
    def test_parse_examples(self):
        """Parse ASTs of examples correctly."""
        for description, example in EXAMPLES.items():
            with self.subTest(msg=description, example=example):
                if 'function' in example:
                    typed_tree = st.parse(example['function'], globals_=globals(), locals_=locals())
                    type_info = typed_tree.body[0].type_info
                    #self.assertEqual(
                    #    len(type_info), len(example['reference']),
                    #    (description, len(type_info), len(example['reference'])))
                    #self.assertEqual(
                    #    type_info, example['reference'],
                    #    (description, type_info, example['reference']))
                if 'class' in example:
                    typed_tree = st.parse(example['class'], globals_=globals(), locals_=locals())
                    type_info = typed_tree.body[0].type_info
                    #self.assertEqual(
                    #    len(type_info), len(example['reference']),
                    #    (description, len(type_info), len(example['reference'])))
                    #self.assertEqual(
                    #    type_info, example['reference'],
                    #    (description, type_info, example['reference']))
                ' ' '
                for (name, var), (ref_name, ref_var) in zip(typed_tree.body[0].local_vars.items(), reference.items()):
                    print(name, ref_name, ':', var, ref_var)
                for name, var in typed_tree.body[0].local_vars.items():
                    print(name, ':', var)
                typed_tree.body[0].local_vars, reference
                ' ' '
    '''

    '''
    def test_parse_invalid_examples(self):
        """Raise errors on ASTs of invalid examples as expected."""
        for description, example in INVALID_EXAMPLES.items():
            continue
    '''
