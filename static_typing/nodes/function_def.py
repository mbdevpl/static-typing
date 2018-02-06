"""Function definition node - FunctionDef."""

import ast
import enum
import logging
import sys
import typing as t

import ordered_set
import typed_ast.ast3

from .statically_typed import StaticallyTyped
from .declaration import StaticallyTypedAssign, StaticallyTypedAnnAssign
from .context import StaticallyTypedFor, StaticallyTypedWith

_LOG = logging.getLogger(__name__)


class FunctionKind(enum.IntEnum):

    """Kind of a statically typed version of FunctionDef AST node."""

    Undetermined = 0
    Function = 1
    InstanceMethod = 1 + 2
    Constructor = 1 + 2 + 4
    ClassMethod = 1 + 8
    StaticMethod = 1 + 16
    Method = 1 + 2 + 4 + 8


def create_function_def(ast_module):
    """Create statically typed AST FunctionDef node class based on a given AST module."""

    class StaticallyTypedFunctionDefClass(ast_module.FunctionDef, StaticallyTyped[ast_module]):

        """Statically typed version of FunctionDef AST node."""

        _type_fields = 'params', 'local_vars', 'nonlocal_assignments'

        def __init__(self, *args, resolved_returns=None, **kwargs):
            self.resolved_returns = resolved_returns
            self._kind = FunctionKind.Undetermined
            self._params = {}
            self._returns = ordered_set.OrderedSet()
            self._local_vars = {}
            self._nonlocal_assignments = {}
            # self._scopes = []
            super().__init__(*args, **kwargs)

        def _add_kind_info(self):
            if len(self.decorator_list) == 0:
                if len(self.args.args) == 0:
                    self._kind = FunctionKind.Function
                else:
                    first_arg = self.args.args[0].arg
                    if first_arg == 'self':
                        if self.name == '__init__':
                            self._kind = FunctionKind.Constructor
                        else:
                            self._kind = FunctionKind.InstanceMethod
                    else:
                        self._kind = FunctionKind.Function
            elif len(self.decorator_list) == 1:
                decorator = self.decorator_list[0]
                assert isinstance(decorator, ast_module.Name)
                self._kind = {
                    'classmethod': FunctionKind.ClassMethod,
                    'staticmethod': FunctionKind.StaticMethod}.get(
                        decorator.id, FunctionKind.Undetermined)
            else:
                raise NotImplementedError('no support for many decorators')
            if self._kind is FunctionKind.Undetermined:
                raise NotImplementedError('could not determine function kind')

        def _add_params_type_info(self):
            args, vararg, kwonlyargs, kw_defaults, kwarg, defaults = \
                self.args.args, self.args.vararg, self.args.kwonlyargs, self.args.kw_defaults, \
                self.args.kwarg, self.args.defaults
            if vararg or kwonlyargs or kwarg:
                raise NotImplementedError('only simple function definitions are supported')
            if kw_defaults or defaults:
                _LOG.warning('ignoring default parameter values in %s: %s and %s',
                             self.name, kw_defaults, defaults)
            for i, arg in enumerate(args):
                if i == 0:
                    if self._kind in (FunctionKind.Constructor, FunctionKind.InstanceMethod) \
                            and arg.arg == 'self':
                        continue
                    if self._kind is FunctionKind.ClassMethod and arg.arg == 'cls':
                        continue
                type_info = ordered_set.OrderedSet()
                if getattr(arg, 'resolved_annotation', None) is not None:
                    type_info.add(arg.resolved_annotation)
                if getattr(arg, 'resolved_type_comment', None) is not None:
                    type_info.add(arg.resolved_type_comment)
                self._params[arg.arg] = type_info

        def _add_var_type_info(self, fld, var_name: str, type_info: t.Any):
            # , scope: t.Any=None
            if var_name not in fld:
                fld[var_name] = ordered_set.OrderedSet()
            var_type_info = fld[var_name]
            if type_info is not None:
                var_type_info.add(type_info)

        def _add_type_info(self):
            if not getattr(self, 'body', None):
                return

            self._add_kind_info()
            self._add_params_type_info()

            if self.returns is not None:
                self._returns.add(self.resolved_returns)

            variables = []
            for stmt in self.body:
                for node in ast_module.walk(stmt):
                    if isinstance(node, ast_module.Assign):
                        assert isinstance(node, StaticallyTypedAssign[ast_module]), type(node)
                        variables += list(node._vars.items())
                    elif (ast_module is not ast or sys.version_info[:2] >= (3, 6)) \
                            and isinstance(node, ast_module.AnnAssign):
                        assert isinstance(node, StaticallyTypedAnnAssign[ast_module]), type(node)
                        variables += list(node._vars.items())
                    elif isinstance(node, ast_module.For):
                        assert isinstance(node, StaticallyTypedFor[ast_module]), type(node)
                        variables += list(node._index_vars.items())
                    elif isinstance(node, ast_module.With):
                        assert isinstance(node, StaticallyTypedWith[ast_module]), type(node)
                        variables += list(node._context_vars.items())

            for k, v in variables:
                if isinstance(k, ast_module.Name):
                    self._add_var_type_info(self._local_vars, k.id, v)
                else:
                    self._add_var_type_info(self._nonlocal_assignments, k, v)

    return StaticallyTypedFunctionDefClass


StaticallyTypedFunctionDef = {ast_module: create_function_def(ast_module)
                              for ast_module in (ast, typed_ast.ast3)}
