"""Add static type information to a given AST."""

import ast
import sys

import typed_ast.ast3

from .ast_manipulation import RecursiveAstTransformer
from .nodes import \
    StaticallyTypedModule, StaticallyTypedFunctionDef, StaticallyTypedClassDef, \
    StaticallyTypedAssign, StaticallyTypedAnnAssign, StaticallyTypedFor, StaticallyTypedWith
# , StaticallyTypedWhile, StaticallyTypedIf


def create_static_typer(ast_module):
    """Create StaticTyper class based on a given AST module."""

    class StaticTyperClass(RecursiveAstTransformer[ast_module]):

        """Add static type information.

        Substitute all nodes that are supposed to be statically typed (i.e. nodes_to_be_typed)
        with their statically typed versions.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, fields_first=True, **kwargs)

        nodes_to_be_typed = {
            ast_module.Module: StaticallyTypedModule,
            ast_module.FunctionDef: StaticallyTypedFunctionDef,
            ast_module.ClassDef: StaticallyTypedClassDef,
            ast_module.Assign: StaticallyTypedAssign,
            ast_module.For: StaticallyTypedFor,
            # ast_module.While: StaticallyTypedWhile,
            # ast_module.If: StaticallyTypedIf,
            ast_module.With: StaticallyTypedWith
            }

        if ast_module is not ast or sys.version_info[:2] >= (3, 6):
            nodes_to_be_typed[ast_module.AnnAssign] = StaticallyTypedAnnAssign

        def visit_node(self, node):
            """Introduce static typing information to compatible nodes of the AST."""
            node_type = type(node)
            if node_type in self.nodes_to_be_typed:
                return self.nodes_to_be_typed[node_type][ast_module].from_other(node)
            return node

    return StaticTyperClass


StaticTyper = {
    ast_module: create_static_typer(ast_module)
    for ast_module in (ast, typed_ast.ast3)}
