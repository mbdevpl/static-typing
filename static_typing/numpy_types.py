"""Type annotations for numpy.ndarray type."""

import typing as t

import numpy as np

def create_typed_numpy_ndarray(dims: int, data_type: t.ClassVar):

    def typed_ndarray(*args, **kwargs):
        """Create an instance of numpy.ndarray which must conform to declared type constraints."""

        shape_loc = (args, 0) if len(args) > 0 else (kwargs, 'shape')
        dtype_loc = (args, 1) if len(args) > 1 else (kwargs, 'dtype')

        shape = shape_loc[0][shape_loc[1]]
        if shape is not None and (dims != 1 if isinstance(shape, int) else len(shape) != dims):
            raise ValueError(f'actual ndarray shape {shape} conflicts'
                            f' with its declared dimensionality of {dims}')

        try:
            dtype = dtype_loc[0][dtype_loc[1]]
        except KeyError:
            dtype = None
        if dtype is not None and dtype is not data_type:
            raise TypeError(f'actual ndarray dtype {dtype} conflicts'
                            f' with its declared dtype {data_type}')
        dtype_loc[0][dtype_loc[1]] = data_type

        #print('np.ndarray', args, kwargs)
        return np.ndarray(*args, **kwargs)

    return typed_ndarray

ndarray = {
    (dims, data_type): create_typed_numpy_ndarray(dims, data_type)
    for data_type in [int, np.int8, np.int16, np.int32, np.int64,
                  float, np.float16, np.float32, np.float64,
                  bool, np.bool]
    for dims in [1, 2, 3]}
