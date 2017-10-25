"""Inspect all nodes and fields in a given AST recursively."""

import ast
import logging
import typing as t

import typed_ast.ast3

_LOG = logging.getLogger(__name__)


def create_recursive_ast_visitor(ast_module):
    """Create RecursiveAstVisitor class based on a given AST module."""

    class RecursiveAstVisitorClass(ast_module.NodeVisitor):

        """Perform a custom action on all nodes in a given AST."""

        def __init__(self, fields_first: bool = False, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._fields_first = fields_first

        def generic_visit(self, node):
            """Visit a given node and all of its fields."""
            if not self._fields_first:
                _LOG.debug('visiting node %s', node)
                self.visit_node(node)
            _LOG.debug('visiting all fields of node %s', node)
            for name, value in ast_module.iter_fields(node):
                self.generic_visit_field(node, name, value)
            if self._fields_first:
                _LOG.debug('visiting node %s', node)
                self.visit_node(node)

        def generic_visit_field(self, node, name: str, value: t.Any):
            """Visit given field of a given node."""
            _LOG.debug('visiting field %s of %s', name, node)
            if isinstance(value, (str, tuple)):
                self.visit_field(node, name, value)
            elif isinstance(value, list):
                for subnode in value:
                    self.visit(subnode)
            elif hasattr(value, '_fields'):
                self.visit(value)
            else:
                self.visit_field(node, name, value)

        def visit_node(self, node):
            pass

        def visit_field(self, node, name: str, value: t.Any):
            pass

    return RecursiveAstVisitorClass


RecursiveAstVisitor = {ast_module: create_recursive_ast_visitor(ast_module)
                       for ast_module in (ast, typed_ast.ast3)}
