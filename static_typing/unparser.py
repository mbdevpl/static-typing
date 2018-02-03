"""Experimental implementation of unparser for statically typed syntax trees."""

import ast
import logging
import sys
import types

import typed_ast
import typed_astunparse
from typed_astunparse.unparser import interleave

from .nodes import StaticallyTyped

_LOG = logging.getLogger(__name__)

_STATICALLY_TYPED = tuple(StaticallyTyped.values())


class Unparser(typed_astunparse.Unparser):

    """Unparser based on the implementation from typed_astunparse packege."""

    def __init__(self, tree, file=sys.stdout, globals_=None, locals_=None):
        if globals_ is None:
            globals_ = {}
        if locals_ is None:
            locals_ = {}
        # _LOG.warning('globals=%s', globals_)
        # _LOG.warning('locals=%s', locals_)
        # self._globals = globals_
        # self._locals = locals_
        self._builtins = {}
        self._modules = {}  # type: t.Dict[str, types.ModuleType]
        self._aliases = {}  # type: t.Dict[str, str]
        for collection, collection_name in ((globals_, 'globals'), (locals_, 'locals')):
            for name, obj in collection.items():
                if name == '__builtins__':
                    self._builtins = obj
                elif isinstance(obj, types.ModuleType):
                    _LOG.debug('found module %s as %s', obj.__name__, name)
                    self._modules[obj.__name__] = obj
                    self._aliases[obj.__name__] = name
                else:
                    _LOG.warning('ignoring %s named %s found in %s',
                                 type(obj), name, collection_name)
        super().__init__(tree, file=file)

    def dispatch(self, tree):
        if isinstance(tree, _STATICALLY_TYPED):
            name = type(tree).__name__
            assert name.startswith('StaticallyTyped'), name
            assert name.endswith('Class'), name
            getattr(self, '_{}'.format(name[15:-5]))(tree)
        elif isinstance(tree, (ast.AST, typed_ast.ast3.AST, list)):
            super().dispatch(tree)
        else:
            if isinstance(tree, type):
                self.dispatch_evaluated_type(tree)
            elif isinstance(tree, tuple):
                self.write('(')
                interleave(lambda: self.write(', '), self.dispatch, tree)
                self.write(')')
            else:
                _LOG.error('unparsing something else %s %s', type(tree), tree)
                self.write('"')
                self.write(str(tree))
                self.write('"')

    def dispatch_evaluated_type(self, type_obj: type):
        """Attempt correct unparsing of a type object."""
        candidates = (type_obj.__qualname__, str(type_obj), repr(type_obj))
        module_names = []
        _LOG.warning('unparsing type %s: %s', type_obj.__name__, ' '.join(candidates))
        for module_name in self._modules:
            dotted_name = '{}.'.format(module_name)
            for candidate in candidates:
                if dotted_name in candidate \
                        and hasattr(self._modules[module_name], type_obj.__name__):
                    _LOG.warning('found module %s matching type %s', module_name, type_obj.__name__)
                    module_names.append(module_name)
                    break
        if not module_names and type_obj.__name__ not in self._builtins:
            raise NotImplementedError('type {}, or any of {}, not found'
                                      .format(type_obj.__name__, candidates))
        if module_names:
            assert len(module_names) == 1
            module_name = module_names[0]
            self.write(self._aliases[module_name])
            self.write('.')
        self.write(type_obj.__name__)
