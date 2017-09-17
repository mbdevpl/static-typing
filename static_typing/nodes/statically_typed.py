
import ast

import typed_ast.ast3


def create_statically_typed(ast_module):

    class StaticallyTypedClass(ast_module.AST):

        _type_fields = ()

        @classmethod
        def from_other(cls, node: ast_module.AST):
            node_fields = {k: v for k, v in ast_module.iter_fields(node)}
            return cls(**node_fields)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._add_type_info()

        def _add_type_info(self):
            raise NotImplementedError()

        #@property
        #def type_info_view(self):
        #    return self._type_info_view()

        #def print_type_info(self):
        #    print(self)
        #    for node in ast_module.iter_child_nodes(self):
        #        if isinstance(node, StaticallyTyped):
        #            print(node)

        #def _type_info_view(self, indent: int = 0, inline: bool = False):
        #    raise NotImplementedError()

        def __repr__(self):
            return f'<{type(self).__name__}@{id(self)}>'

        #def __str__(self):
        #    return f'<{type(self).__name__}>'

        def __str__(self):
            short_type_name = type(self).__name__.replace('StaticallyTyped', '')
            fields = [f'{len(getattr(self, f"_{field_name}"))} {field_name}'
                      for field_name in type(self)._type_fields]
            return f'{short_type_name}({" ".join(fields)})'
            #return f'<Module>({len(self._constants)} constants, {len(self._classes)} classes,' \
            #    f' {len(self._functions)} functions)'

    return StaticallyTypedClass


StaticallyTyped = {ast_module: create_statically_typed(ast_module)
                   for ast_module in (ast, typed_ast.ast3)}
