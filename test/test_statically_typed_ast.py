
import logging
import typing as t
import unittest

import static_typing as st

from .examples import EXAMPLES#, INVALID_EXAMPLES

_LOG = logging.getLogger(__name__)


class StaticallyTypedFunctionDefTests(unittest.TestCase):

    """Unit tests for StaticallyTypedFunctionDef class."""

    def test_parse_examples(self):
        """Parse ASTs of examples correctly."""
        for description, example in EXAMPLES.items():
            with self.subTest(msg=description, example=example):
                if 'function' in example:
                    typed_tree = st.parse(example['function'], globals_=globals(), locals_=locals())
                    type_info = typed_tree.body[0].type_info
                    self.assertEqual(
                        len(type_info), len(example['reference']),
                        (description, len(type_info), len(example['reference'])))
                    self.assertEqual(
                        type_info, example['reference'],
                        (description, type_info, example['reference']))
                if 'class' in example:
                    typed_tree = st.parse(example['class'], globals_=globals(), locals_=locals())
                    type_info = typed_tree.body[0].type_info
                    self.assertEqual(
                        len(type_info), len(example['reference']),
                        (description, len(type_info), len(example['reference'])))
                    self.assertEqual(
                        type_info, example['reference'],
                        (description, type_info, example['reference']))
                '''
                for (name, var), (ref_name, ref_var) in zip(typed_tree.body[0].local_vars.items(), reference.items()):
                    print(name, ref_name, ':', var, ref_var)
                for name, var in typed_tree.body[0].local_vars.items():
                    print(name, ':', var)
                typed_tree.body[0].local_vars, reference
                '''

    '''
    def test_parse_invalid_examples(self):
        """Raise errors on ASTs of invalid examples as expected."""
        for description, example in INVALID_EXAMPLES.items():
            continue
    '''

    def test_print_type_info(self):
        for description, example in EXAMPLES.items():
            with self.subTest(msg=description, example=example):
                if 'function' in example:
                    typed_tree = st.parse(example['function'], globals_=globals(), locals_=locals())
                if 'class' in example:
                    typed_tree = st.parse(example['class'], globals_=globals(), locals_=locals())
                print(description)
                typed_tree.body[0].print_type_info()
