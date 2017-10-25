"""Overwrite all nodes and fields in a given AST recursively."""

import ast
import logging
import typing as t

import typed_ast.ast3

from .recursive_ast_visitor import RecursiveAstVisitor

_LOG = logging.getLogger(__name__)


def create_recursive_ast_transformer(ast_module):
    """Create RecursiveAstTransformer class based on a given AST module."""

    class RecursiveAstTransformerClass(RecursiveAstVisitor[ast_module], ast_module.NodeTransformer):

        """Recursively overwrite all nodes in a given AST."""

        def generic_visit(self, node):
            """Transform all fields of a given node."""
            if not self._fields_first:
                _LOG.debug('visiting node %s', node)
                node = self.visit_node(node)
            _LOG.debug('visiting all fields of node %s', node)
            for name, value in ast_module.iter_fields(node):
                setattr(node, name, self.generic_visit_field(node, name, value))
            if self._fields_first:
                _LOG.debug('visiting node %s', node)
                node = self.visit_node(node)
            return node

        def generic_visit_field(self, node, name: str, value: t.Any):
            """Transform given field of a given node."""
            _LOG.debug('visiting field %s of %s', name, node)
            if isinstance(value, (str, tuple)):
                return self.visit_field(node, name, value)
            if isinstance(value, list):
                return [self.visit(subnode) for subnode in value]
            if hasattr(value, '_fields'):
                return self.visit(value)
            return self.visit_field(node, name, value)

        def visit_node(self, node):
            return node

        def visit_field(self, node, name: str, value: t.Any):
            return value

    return RecursiveAstTransformerClass


RecursiveAstTransformer = {ast_module: create_recursive_ast_transformer(ast_module)
                           for ast_module in (ast, typed_ast.ast3)}
