"""Base class of any statically typed node."""

import ast

import typed_ast.ast3


def create_statically_typed(ast_module):
    """Create statically typed AST node template class based on a given AST module."""

    class StaticallyTypedClass(ast_module.AST):

        """Base class of any statically typed node."""

        _type_fields = ()

        _resolved_fields = ('resolved_type_comment', 'resolved_annotation', 'resolved_returns')

        @classmethod
        def from_other(cls, node: ast_module.AST):
            node_fields = {k: v for k, v in ast_module.iter_fields(node)}
            for resolved_field in cls._resolved_fields:
                if hasattr(node, resolved_field):
                    node_fields[resolved_field] = getattr(node, resolved_field)
            return cls(**node_fields)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._add_type_info()

        def _add_type_info(self):
            raise NotImplementedError()

        def __repr__(self):
            return '<{}@{}>'.format(type(self).__name__, id(self))

        def __str__(self):
            short_type_name = type(self).__name__.replace('StaticallyTyped', '')
            fields = ['{} {}'.format(len(getattr(self, '_' + field_name)), field_name)
                      for field_name in type(self)._type_fields]
            return '{}({})'.format(short_type_name, ' '.join(fields))

    return StaticallyTypedClass


StaticallyTyped = {ast_module: create_statically_typed(ast_module)
                   for ast_module in (ast, typed_ast.ast3)}
