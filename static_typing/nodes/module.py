"""Python module node - Module."""

import ast
import sys
import typing as t

import ordered_set
import typed_ast.ast3

from .statically_typed import StaticallyTyped
from .function_def import find_all_stores
from .declaration import StaticallyTypedAssign, StaticallyTypedAnnAssign
from .context import StaticallyTypedFor, StaticallyTypedWith


def create_module(ast_module):
    """Create statically typed AST Module node class based on a given AST module."""

    class StaticallyTypedModuleClass(ast_module.Module, StaticallyTyped[ast_module]):

        """Statically typed version of Module AST node."""

        _type_fields = 'module_vars', 'nonlocal_assignments', 'classes', 'functions'

        def __init__(self, *args, **kwargs):
            self._module_vars = {}
            self._nonlocal_assignments = {}
            self._classes = {}
            self._functions = {}
            super().__init__(*args, **kwargs)

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

            classes, functions = {}, {}
            variables = []
            for stmt in self.body:
                if isinstance(stmt, ast_module.ClassDef):
                    classes[stmt.name] = stmt
                elif isinstance(stmt, ast_module.FunctionDef):
                    functions[stmt.name] = stmt
                elif isinstance(stmt, ast_module.Assign):
                    assert isinstance(stmt, StaticallyTypedAssign[ast_module]), type(stmt)
                    variables += list(stmt._vars.items())
                elif (ast_module is not ast or sys.version_info[:2] >= (3, 6)) \
                        and isinstance(stmt, ast_module.AnnAssign):
                    assert isinstance(stmt, StaticallyTypedAnnAssign[ast_module]), type(stmt)
                    variables += list(stmt._vars.items())
                elif isinstance(stmt, ast_module.For):
                    assert isinstance(stmt, StaticallyTypedFor[ast_module]), type(stmt)
                    variables += find_all_stores[ast_module](stmt)
                elif isinstance(stmt, ast_module.With):
                    assert isinstance(stmt, StaticallyTypedWith[ast_module]), type(stmt)
                    variables += find_all_stores[ast_module](stmt)

            for var, values in variables:
                if isinstance(var, ast_module.Name):
                    self._add_var_type_info(self._module_vars, var.id, values)
                else:
                    self._add_var_type_info(self._nonlocal_assignments, var, values)

            self._classes, self._functions = classes, functions

    return StaticallyTypedModuleClass


StaticallyTypedModule = {ast_module: create_module(ast_module)
                         for ast_module in (ast, typed_ast.ast3)}
