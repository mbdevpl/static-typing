"""Tests for statically declared types for various objects."""

import unittest

import numpy as np

from static_typing.numpy_types import ndarray

class Tests(unittest.TestCase):

    maxDiff = None

    def test_numpy_1d_ndarray(self):
        for data_type in (bool, int, float):
            with self.subTest(data_type=data_type):
                ordinary = np.ndarray(10, dtype=data_type)
                statically_typed = ndarray[1, data_type](10)
                self.assertEqual(ordinary.shape, statically_typed.shape)
                self.assertEqual(ordinary.dtype, statically_typed.dtype)
                with self.assertRaises(ValueError):
                    ndarray[1, data_type]((10, 10))
                with self.assertRaises(TypeError):
                    ndarray[1, data_type](10, dtype=object)

    def test_numpy_ndarray_identity(self):
        with self.assertRaises(TypeError):
            _ = ndarray[1]
        with self.assertRaises(ValueError):
            _ = ndarray[2, int, 100, 100]
        self.assertIs(ndarray[1, int], ndarray[1, int])

    def test_numpy_general_ndarray(self):
        for data_type in (bool, int, float):
            for dimensionality in (1, 2, 3):
                with self.subTest(data_type=data_type, dimensionality=dimensionality):
                    shape = tuple([10 for _ in range(dimensionality)])
                    ordinary = np.ndarray(shape, dtype=data_type)
                    statically_typed_a = ndarray[dimensionality, data_type](shape)
                    self.assertEqual(ordinary.shape, statically_typed_a.shape)
                    self.assertEqual(ordinary.dtype, statically_typed_a.dtype)
                    statically_typed_b = ndarray[dimensionality, data_type](shape, dtype=data_type)
                    self.assertEqual(ordinary.shape, statically_typed_b.shape)
                    self.assertEqual(ordinary.dtype, statically_typed_b.dtype)
                    with self.assertRaises(ValueError):
                        ndarray[dimensionality, data_type](shape + (10,))
                    with self.assertRaises(TypeError):
                        ndarray[dimensionality, data_type](shape, dtype=object)
