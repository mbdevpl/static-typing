
import ast

import typed_ast.ast3

from .ast_manipulation import RecursiveAstTransformer
from .nodes import \
    StaticallyTypedModule, StaticallyTypedFunctionDef, StaticallyTypedClassDef, \
    StaticallyTypedAssign, StaticallyTypedAnnAssign
# StaticallyTypedFor, StaticallyTypedWhile, StaticallyTypedIf, StaticallyTypedWith

def create_static_typer(ast_module):

    class StaticTyperClass(RecursiveAstTransformer[ast_module]):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, fields_first=True, **kwargs)

        nodes_to_be_typed = {
            ast_module.Module: StaticallyTypedModule,
            ast_module.FunctionDef: StaticallyTypedFunctionDef,
            ast_module.ClassDef: StaticallyTypedClassDef,
            ast_module.Assign: StaticallyTypedAssign,
            ast_module.AnnAssign: StaticallyTypedAnnAssign,
            # ast_module.For: StaticallyTypedFor,
            # ast_module.While: StaticallyTypedWhile,
            # ast_module.If: StaticallyTypedIf,
            # ast_module.With: StaticallyTypedWith
            }

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
