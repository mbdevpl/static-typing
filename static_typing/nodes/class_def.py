
import ast
import typing as t

import ordered_set
import typed_ast.ast3

from .statically_typed import StaticallyTyped
from .function_def import scan_FunctionDef, FunctionKind, StaticallyTypedFunctionDef
from .declaration import scan_Assign


def create_statically_typed_class_def(ast_module):

    class StaticallyTypedClassDefClass(ast_module.ClassDef, StaticallyTyped[ast_module]):

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
            #self.add_type_info()

        def _add_var(self, var_place: str, var_name: str, type_info: t.Any, scope: t.Any=None):
            vars_ = getattr(self, var_place)
            if var_name not in vars_:
                vars_[var_name] = ordered_set.OrderedSet()
            var_type_info = vars_[var_name]
            if type_info is not None:
                var_type_info.add(type_info)

        def _add_type_info(self):
            for node in self.body:
                if isinstance(node, StaticallyTypedFunctionDef[ast_module]):
                    self._methods[node.name] = node
                    getattr(self, self.kind_mapping[node._kind])[node.name] = node
                    if node._kind is FunctionKind.Constructor:
                        results = scan_FunctionDef(node, ast_module)
                        for k, v in results:
                            if isinstance(k, ast_module.Attribute):
                                if isinstance(k.value, ast_module.Name) and k.value.id == 'self':
                                    self._add_var('_instance_fields', k.attr, v)
                elif isinstance(node, ast_module.FunctionDef):
                    # TODO: raise error here
                    #raise NotImplementedError(node.name)
                    pass
                    #if node.decorator_list:
                    #    self.class_methods
                    #self.instance_methods node.
                    #node.
                elif isinstance(node, ast_module.Assign):
                    results = scan_Assign(node, ast_module)
                    for k, v in results:
                        if isinstance(k, ast_module.Name):
                            self._add_var('_class_fields', k.id, v)
                #elif isinstance(node, ast_module.AnnAssign):
                #    results = scan_AnnAssign(node)
                #    for k, v in results.items():
                #        self._add_var('_class_fields', k, v)

        '''
        def _type_info_view(self, indent: int = 0, inline: bool = False):
            if inline:
                return str(self)
            lines = [f'{INDENT_STR * indent}<ClassDef> {self.name}:']
            lines += [f'{INDENT_STR * (indent + 1)}{len(self._class_fields)} class fields:']
            lines += [
                f'{INDENT_STR * (indent + 2)}{var_name}: {tuple(type_info)}'
                for var_name, type_info in self._class_fields.items()]
            lines += [f'{INDENT_STR * (indent + 1)}{len(self._instance_fields)} instance fields:']
            lines += [
                f'{INDENT_STR * (indent + 2)}{var_name}: {tuple(type_info)}'
                for var_name, type_info in self._instance_fields.items()]
            lines += [f'{INDENT_STR * (indent + 1)}{len(self._methods)} methods:']
            lines += [_._type_info_view(indent + 2) for __, _ in self._methods.items()]
            return '\n'.join(lines)

        def __str__(self):
            return f'<ClassDef> {self.name}: {len(self._class_fields)} class fields,' \
                f' {len(self._instance_fields)} instance fields, {len(self._methods)} methods'
        '''

    return StaticallyTypedClassDefClass


StaticallyTypedClassDef = {ast_module: create_statically_typed_class_def(ast_module)
                              for ast_module in (ast, typed_ast.ast3)}
