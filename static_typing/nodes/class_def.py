"""Class definition node - ClassDef."""

import ast
import typing as t

import ordered_set
import typed_ast.ast3

from .statically_typed import StaticallyTyped
from .function_def import FunctionKind, StaticallyTypedFunctionDef
from .declaration import StaticallyTypedAssign, StaticallyTypedAnnAssign


def create_statically_typed_class_def(ast_module):

    class StaticallyTypedClassDefClass(ast_module.ClassDef, StaticallyTyped[ast_module]):

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

        def _add_var(self, var_place: str, var_name: str, type_info: t.Any, scope: t.Any=None):
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
                    if not isinstance(node, StaticallyTypedFunctionDef[ast_module]):
                        raise TypeError('expected a statically typed AST node')
                    self._methods[node.name] = node
                    getattr(self, self.kind_mapping[node._kind])[node.name] = node
                    if node._kind is FunctionKind.Constructor:
                        for k, v_set in node._nonlocal_assignments.items():
                            if isinstance(k, ast_module.Attribute) \
                                    and isinstance(k.value, ast_module.Name) \
                                    and k.value.id == 'self':
                                self._add_var('_instance_fields', k.attr, None)
                                for v in v_set:
                                    self._add_var('_instance_fields', k.attr, v)
                elif isinstance(node, ast_module.Assign):
                    if not isinstance(node, StaticallyTypedAssign[ast_module]):
                        raise TypeError('expected a statically typed AST node')
                    for k, v in node._vars.items():
                        if isinstance(k, ast_module.Name):
                            self._add_var('_class_fields', k.id, v)
                elif isinstance(node, ast_module.AnnAssign):
                    if not isinstance(node, StaticallyTypedAnnAssign[ast_module]):
                        raise TypeError('expected a statically typed AST node')
                    for k, v in node._vars.items():
                        if isinstance(k, ast_module.Name):
                            self._add_var('_class_fields', k.id, v)

    return StaticallyTypedClassDefClass


StaticallyTypedClassDef = {ast_module: create_statically_typed_class_def(ast_module)
                           for ast_module in (ast, typed_ast.ast3)}
