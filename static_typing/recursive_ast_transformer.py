
import ast
import logging
import typing as t

import typed_ast

_LOG = logging.getLogger(__name__)


def create_recursive_ast_transformer(ast_module: t.ClassVar) -> t.ClassVar:
    """Create a RecursiveAstTransformer based on a given AST module."""
    
    class RecursiveAstTransformerClass(ast_module.NodeTransformer):

        def __init__(self, *args, transformer: t.Callable[[ast_module.AST], ast_module.AST], **kwargs):
            super().__init__(*args, **kwargs)
            self._node_transformer = transformer

        def visit_fields(self, node: ast_module.AST) -> None:
            """Visit all fields of a given node."""
            _LOG.debug('visiting all fields of node %s', node)
            assert hasattr(node, '_fields'), (type(node), node, type(node).__mro__)
            for field_name, field_value in ast_module.iter_fields(node):
                _LOG.debug('visiting field %s of %s', field_name, node)
                if field_value is None \
                        or isinstance(field_value, (int, float, str, type, tuple)) \
                        or isinstance(type(field_value), t.TypingMeta):
                    continue
                if isinstance(field_value, list):
                    for i, field_value_elem in enumerate(field_value):
                        field_value[i] =  self.visit(field_value_elem)
                    continue
                setattr(node, field_name, self.visit(field_value))

        def generic_visit(self, node: ast_module.AST) -> ast_module.AST:
            self.visit_fields(node)
            return self._node_transformer(node)

    return RecursiveAstTransformerClass

RecursiveAstTransformer = {
    ast_module: create_recursive_ast_transformer(ast_module)
    for ast_module in [ast, typed_ast.ast3]}
