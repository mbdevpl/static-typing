"""Class definition node - ClassDef."""

import ast
import sys
import typing as t

import ordered_set
import typed_ast.ast3

from .statically_typed import StaticallyTyped
from .function_def import FunctionKind, StaticallyTypedFunctionDef
from .declaration import StaticallyTypedAssign, StaticallyTypedAnnAssign


def create_class_def(ast_module):
    """Create statically typed ClassDef AST node class based on a given AST module."""

    class StaticallyTypedClassDefClass(ast_module.ClassDef, StaticallyTyped[ast_module]):

        """Statically typed version of ClassDef AST node."""

        _type_fields = 'class_fields', 'instance_fields', 'methods', 'static_methods', \
            'class_methods', 'instance_methods'

        kind_mapping = {
            FunctionKind.StaticMethod: '_static_methods',
            FunctionKind.ClassMethod: '_class_methods',
            FunctionKind.Constructor: '_instance_methods',
            FunctionKind.InstanceMethod: '_instance_methods'}

        def __init__(self, *args, **kwargs):
            self._class_fields = {}
            self._instance_fields = {}
            self._methods = {}
            self._static_methods = {}
            self._class_methods = {}
            self._instance_methods = {}
            super().__init__(*args, **kwargs)

        def _add_method(self, method: StaticallyTypedFunctionDef[ast_module]):
            self._methods[method.name] = method
            getattr(self, self.kind_mapping[method._kind])[method.name] = method
            if method._kind is not FunctionKind.Constructor:
                return
            for k, v_set in method._nonlocal_assignments.items():
                if isinstance(k, ast_module.Attribute) \
                        and isinstance(k.value, ast_module.Name) \
                        and k.value.id == 'self':
                    if not v_set:
                        v_set = {None}
                    for v in v_set:
                        self._add_var('_instance_fields', k.attr, v)

        def _add_var(self, var_place: str, var_name: str, type_info: t.Any):
            # , scope: t.Any = None
            vars_ = getattr(self, var_place)
            if var_name not in vars_:
                vars_[var_name] = ordered_set.OrderedSet()
            var_type_info = vars_[var_name]
            if type_info is not None:
                var_type_info.add(type_info)

        def _add_type_info(self):
            if not getattr(self, 'body', None):
                return
            for node in self.body:
                if isinstance(node, ast_module.FunctionDef):
                    assert isinstance(node, StaticallyTypedFunctionDef[ast_module]), type(node)
                    self._add_method(node)
                elif isinstance(node, ast_module.Assign):
                    assert isinstance(node, StaticallyTypedAssign[ast_module]), type(node)
                    for k, v in node._vars.items():
                        if isinstance(k, ast_module.Name):
                            self._add_var('_class_fields', k.id, v)
                elif (ast_module is not ast or sys.version_info[:2] >= (3, 6)) \
                        and isinstance(node, ast_module.AnnAssign):
                    assert isinstance(node, StaticallyTypedAnnAssign[ast_module]), type(node)
                    for k, v in node._vars.items():
                        if isinstance(k, ast_module.Name):
                            self._add_var('_class_fields', k.id, v)

    return StaticallyTypedClassDefClass


StaticallyTypedClassDef = {ast_module: create_class_def(ast_module)
                           for ast_module in (ast, typed_ast.ast3)}
