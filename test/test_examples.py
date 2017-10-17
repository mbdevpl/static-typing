"""Validate examples for tests."""

import sys
import unittest

from .examples import function_a6, FUNCTIONS, class_1, CLASSES

if sys.version_info[:2] >= (3, 6):
    from .examples_py36 import function_b6


class Tests(unittest.TestCase):

    maxDiff = None

    def test_functions(self):
        for function in FUNCTIONS:
            function()

    def test_call(self):
        function_a6(True)
        function_a6(False)

    @unittest.skipIf(sys.version_info[:2] < (3, 6), 'requires Python >= 3.6')
    def test_call2(self):
        function_b6(True)
        function_b6(False)

    def test_classes(self):
        for cls in CLASSES:
            cls()

    def test_instance(self):
        instance_1 = class_1()
        instance_1.do_nothing()
        class_1.do_something()
        class_1.make_noise()
