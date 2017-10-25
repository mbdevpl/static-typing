"""Type annotations for numpy.ndarray type."""

import typing as t

import numpy as np


def create_typed_numpy_ndarray(dims: int, data_type: t.ClassVar):
    """Create a statically typed version of numpy.ndarray."""

    def typed_ndarray(*args, **kwargs):
        """Create an instance of numpy.ndarray which must conform to declared type constraints."""

        shape_loc = (args, 0) if len(args) > 0 else (kwargs, 'shape')
        dtype_loc = (args, 1) if len(args) > 1 else (kwargs, 'dtype')

        shape = shape_loc[0][shape_loc[1]]
        if shape is not None and (dims != 1 if isinstance(shape, int) else len(shape) != dims):
            raise ValueError(
                'actual ndarray shape {} conflicts with its declared dimensionality of {}'
                .format(shape, dims))

        try:
            dtype = dtype_loc[0][dtype_loc[1]]
        except KeyError:
            dtype = None
        if dtype is not None and dtype is not data_type:
            raise TypeError('actual ndarray dtype {} conflicts with its declared dtype {}'
                            .format(dtype, data_type))
        dtype_loc[0][dtype_loc[1]] = data_type

        # print('np.ndarray', args, kwargs)
        return np.ndarray(*args, **kwargs)

    return typed_ndarray


class typed_numpy_ndarray_factory(dict):

    """Factory of statically typed versions of numpy.ndarray."""

    def __missing__(self, key: t.Union[t.Tuple[int, type], t.Tuple[int, type, t.Sequence[int]]]):
        if not isinstance(key, tuple):
            raise TypeError()
        if 2 <= len(key) <= 3:
            value = create_typed_numpy_ndarray(*key)
            self[key] = value
            return value
        raise ValueError()


ndarray = typed_numpy_ndarray_factory()

'''
for data_type in (int, np.int8, np.int16, np.int32, np.int64,
                  float, np.float16, np.float32, np.float64,
                  bool, np.bool):
    for dims in (1, 2, 3):
        ndarray[dims, data_type] = create_typed_numpy_ndarray(dims, data_type)
'''
