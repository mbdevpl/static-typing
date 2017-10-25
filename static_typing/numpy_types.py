"""Type annotations for numpy.ndarray type."""

import typing as t

import numpy as np


def create_typed_numpy_ndarray(
        dims: int, data_type: t.ClassVar, required_shape: t.Optional[t.Sequence[int]] = None):
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

        if required_shape is not None:
            if any((req_dim is not Ellipsis and dim != req_dim)
                   for dim, req_dim in zip(shape, required_shape)):
                raise ValueError('actual ndarray shape {} conflicts with its required shape of {}'
                                 .format(shape, required_shape))

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
            raise TypeError('key={} of bad type {} was given'.format(repr(key), type(key)))
        if len(key) < 2 or len(key) > 3:
            raise ValueError('{}'.format(key))
        if not isinstance(key[0], int):
            raise TypeError()
        if key[0] <= 0:
            raise ValueError()
        if not isinstance(key[1], type):
            raise TypeError()
        if len(key) == 3:
            if not isinstance(key[2], tuple):
                raise TypeError()
            if len(key[2]) != key[0]:
                raise ValueError()
            if any(k is not Ellipsis and not isinstance(k, int) for k in key[2]):
                raise TypeError()
            if any(k is not Ellipsis and k <= 0 for k in key[2]):
                raise ValueError()
        value = create_typed_numpy_ndarray(*key)
        self[key] = value
        return value


ndarray = typed_numpy_ndarray_factory()
