
import ast

#import ordered_set
import typed_ast.ast3

from .statically_typed import StaticallyTyped


def create_statically_typed_module(ast_module):

    class StaticallyTypedModuleClass(ast_module.Module, StaticallyTyped[ast_module]):

        #_type_fields = 'constants', 'classes', 'functions'
        _type_fields = 'classes', 'functions'

        def __init__(self, *args, **kwargs):
            #self._constants = {}
            self._classes = {}
            self._functions = {}
            super().__init__(*args, **kwargs)

        def _add_type_info(self):
            for node in self.body:
                '''
                if isinstance(node, (ast_module.Assign, ast_module.AnnAssign)):
                    if isinstance(node, ast_module.Assign):
                        variables = scan_Assign(node)
                    elif isinstance(node, ast_module.AnnAssign):
                        variables = scan_AnnAssign(node)
                    else:
                        TypeError('unhandled type')
                    for var, type_info in variables:
                        var_name = var.id
                        if var_name.isupper():
                            if var_name not in self._constants:
                                self._constants[var_name] = ordered_set.OrderedSet()
                            if type_info is not None:
                                self._constants[var_name].append(type_info)
                        else:
                            raise NotImplementedError('module-level variables are not supported')
                '''
                if isinstance(node, ast_module.FunctionDef):
                    self._functions[node.name] = node
                elif isinstance(node, ast_module.ClassDef):
                    self._classes[node.name] = node

        '''
        def _type_info_view(self, indent: int = 0, inline: bool = False):
            if inline:
                return str(self)
            lines = [f'{INDENT_STR * indent}<Module>:']
            lines += [f'{INDENT_STR * (indent + 1)}{len(self._constants)} constants:']
            lines += [
                f'{INDENT_STR * (indent + 2)}{var_name}: {tuple(type_info)}'
                for var_name, type_info in self._constants.items()]
            lines += [f'{INDENT_STR * (indent + 1)}{len(self._classes)} classes:']
            lines += [_._type_info_view(indent + 2) for __, _ in self._classes.items()]
            lines += [f'{INDENT_STR * (indent + 1)}{len(self._functions)} functions:']
            lines += [_._type_info_view(indent + 2) for __, _ in self._functions.items()]
            return '\n'.join(lines)
        '''

    return StaticallyTypedModuleClass


StaticallyTypedModule = {ast_module: create_statically_typed_module(ast_module)
                         for ast_module in (ast, typed_ast.ast3)}
