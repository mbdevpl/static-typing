
import ast

import typed_ast.ast3

from .ast_manipulation import RecursiveAstTransformer
from .nodes import StaticallyTypedModule
#from .nodes import StaticallyTyped
#    StaticallyTypedModule, StaticallyTypedFor, StaticallyTypedWhile, StaticallyTypedIf, \
#    StaticallyTypedFunctionDef, StaticallyTypedClassDef


def create_static_typer(ast_module):

    class StaticTyperClass(RecursiveAstTransformer[ast_module]):

        nodes_to_be_typed = {
            ast_module.Module: StaticallyTypedModule,
            #ast_module.For, ast_module.While, ast_module.If,
            #ast_module.FunctionDef, ast_module.ClassDef
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
