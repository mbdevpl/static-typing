"""Tests for statically declared types for various objects."""

import itertools
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
        self.assertIs(ndarray[1, int], ndarray[1, int])

    def test_numpy_ndarray_bad(self):
        examples = {
            1: TypeError,
            float: TypeError,
            (3,): ValueError,
            (2, int, 100, 100): ValueError,
            (None, int): TypeError,
            (0, int): ValueError,
            (-5, np.int64): ValueError,
            (3, 'int'): TypeError,
            (3, float, None): TypeError,
            (3, float, '10, 10, 10'): TypeError,
            (3, float, (10, 10)): ValueError,
            (3, float, ('?', 10, 10)): TypeError,
            (3, float, (0, 10, 10)): ValueError,
            (3, float, (10, 10, '?')): TypeError,
            (3, float, (10, 10, 0)): ValueError}
        for key, error in examples.items():
            with self.subTest(key=key, error=error):
                with self.assertRaises(error):
                    ndarray[key]()

    def test_numpy_general_ndarray(self):
        for data_type, dimensionality in itertools.product((bool, int, float), (1, 2, 3, 4, 5)):
            base_shape = tuple([10 for _ in range(dimensionality)])
            for required_shape, shape, kwargs in itertools.product(
                    [None, base_shape, base_shape[:-1] + (...,)],
                    [base_shape, base_shape[:-1] + (9,)],
                    [{}, {'dtype': data_type}]):
                key = (dimensionality, data_type)
                if required_shape is not None:
                    key += (required_shape,)
                    if required_shape[-1] is not Ellipsis and shape[-1] != 10:
                        with self.assertRaises(ValueError):
                            ndarray[key](shape)
                        continue
                ordinary = np.ndarray(shape, dtype=data_type)
                with self.subTest(data_type=data_type, dimensionality=dimensionality,
                                  required_shape=required_shape, shape=shape, init_kwargs=kwargs):
                    typed = ndarray[key](shape, **kwargs)
                    self.assertEqual(ordinary.shape, typed.shape)
                    self.assertEqual(ordinary.dtype, typed.dtype)
                    with self.assertRaises(ValueError):
                        ndarray[key](shape + (10,), **kwargs)
                    with self.assertRaises(TypeError):
                        ndarray[key](shape, dtype=object)
