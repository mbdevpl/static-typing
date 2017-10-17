"""Validate examples for tests."""

import unittest

from .examples import function_a6, FUNCTIONS, class_1, CLASSES

class Tests(unittest.TestCase):

    maxDiff = None

    def test_functions(self):
        for function in FUNCTIONS:
            function()

    def test_call(self):
        function_a6(True)
        function_a6(False)

    def test_classes(self):
        for cls in CLASSES:
            cls()

    def test_instance(self):
        instance_1 = class_1()
        instance_1.do_nothing()
        class_1.do_something()
        class_1.make_noise()
