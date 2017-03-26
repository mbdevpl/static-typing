
import logging
import typing as t
import unittest

import static_typing as st

from .examples import EXAMPLES#, INVALID_EXAMPLES

_LOG = logging.getLogger(__name__)


class StaticallyTypedFunctionDefTests(unittest.TestCase):

    """Unit tests for StaticallyTypedFunctionDef class."""

    def test_parse_examples(self):
        """Unparse ASTs of examples correctly."""
        for description, example in EXAMPLES.items():
            if example['type'] == 'function':
                typed_tree = st.parse(example['function'], globals_=globals(), locals_=locals())
                self.assertEqual(
                    len(typed_tree.body[0].local_vars), len(example['reference']),
                    (description, len(typed_tree.body[0].local_vars), len(example['reference'])))
                self.assertEqual(
                    typed_tree.body[0].local_vars, example['reference'],
                    (description, typed_tree.body[0].local_vars, example['reference']))
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
