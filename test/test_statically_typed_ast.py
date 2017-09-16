
import logging
import typing as t
import unittest

import numpy as np
import static_typing as st

from .examples import EXAMPLES#, INVALID_EXAMPLES

_LOG = logging.getLogger(__name__)


class StaticallyTypedFunctionDefTests(unittest.TestCase):

    """Unit tests for StaticallyTypedFunctionDef class."""

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

    @unittest.skip("not ready")
    def test_xu_script(self):
        import os
        path = os.path.expanduser(os.path.join('~', 'Projects', 'python', 'unique_access', 'unique_access_improved.py'))
        with open(path) as _:
            source = _.readlines()
            code = _.read()
        file_info = st.parse(''.join(source[14:20]), path)
        page_info = st.parse(''.join(source[20:48]), path)
        Node = st.parse(''.join(source[48:55]), path)
        address_queue = st.parse(''.join(source[55:98]), path)
        distance = st.parse(''.join(source[98:210]), path)
        classes = [file_info, page_info, Node, address_queue, distance]
        for cls in classes:
            #print(cls.body[0])
            cls.body[0].print_type_info()
            print(cls.body[0]._instance_fields)
        import pathlib
        import sys
        sys.path.append(pathlib.Path('~', 'Projects', 'python', 'unique_access').expanduser().as_posix())
        print(sys.path)
        from unique_access_improved import page_info, file_info, address_queue, distance
        tree = st.parse(code, globals_=globals(), locals_=locals())
        self.assertIsNotNone(tree)
        print(tree.type_info_view)

    def test_print_type_info(self):
        for description, example in EXAMPLES.items():
            with self.subTest(msg=description, example=example):
                if 'function' in example:
                    typed_tree = st.parse(example['function'], globals_=globals(), locals_=locals())
                if 'class' in example:
                    typed_tree = st.parse(example['class'], globals_=globals(), locals_=locals())
                print(description)
                print(typed_tree.type_info_view)
