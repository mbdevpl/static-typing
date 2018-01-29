"""Experimental implementation of unparser for statically typed syntax trees."""

import typed_astunparse

from .nodes import StaticallyTyped

_STATICALLY_TYPED = tuple(StaticallyTyped.values())


class Unparser(typed_astunparse.Unparser):

    """Unparser based on the implementation from typed_astunparse packege."""

    def dispatch(self, tree):
        if isinstance(tree, _STATICALLY_TYPED):
            name = type(tree).__name__
            assert name.startswith('StaticallyTyped'), name
            assert name.endswith('Class'), name
            getattr(self, '_{}'.format(name[15:-5]))(tree)
            return
        super().dispatch(tree)
