'''
Created on Mar 27, 2017

@author: mb
'''

import typing as t

import numpy as np

def create_typed_numpy_ndarray(dims: int, dtype: t.ClassVar):

    class typed_ndarray(np.ndarray):

        """Statically typed version of numpy.ndarray class."""

        _dims = dims

        _dtype = dtype

        def __init__(self, *args, **kwargs):

            shape = args[0] if len(args) > 0 else kwargs.get('shape', None)
            if shape is not None and len(shape) != self._dims:
                raise TypeError(f'actual ndarray shape {shape} conflicts with its declared dimensionality of {self._dims}')

            dtype = kwargs.get('dtype', None)
            if dtype is not None and dtype is not self._dtype:
                raise TypeError(f'actual ndarray dtype {dtype} conflicts with its declared dtype {self._dtype}')
            kwargs['dtype'] = self._dtype

            super().__init__(*args, **kwargs)

    return typed_ndarray

ndarray = {
    (dims, dtype): create_typed_numpy_ndarray(dims, type)
    for dtype in [int, np.int8, np.int16, np.int32, np.int64, float, np.float16, np.float32, np.float64, bool, np.bool]
    for dims in [1, 2, 3]}
