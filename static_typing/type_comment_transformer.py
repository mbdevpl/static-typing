
import ast
import functools
import logging
import typing as t

import typed_ast

from .recursive_ast_transformer import RecursiveAstTransformer

_LOG = logging.getLogger(__name__)


def create_type_comment_transformer(
        ast_module: t.Any=typed_ast.ast3, parser_ast_module: t.Any=ast) -> t.Any:
    """Create TypeCommentTransformer class based on given AST modules."""

    def transform_type_comment(
            node: ast_module.AST, eval_: bool=False, globals_=globals(), locals_=None) -> ast_module.AST:
        """Parse node's type comment from str into AST.

        If eval_ is true, the resulting AST will be also compile()'d and eval()'d after.

        For Python 3.6, nodes that can have type comments are:
        `FunctionDef`, `AsyncFunctionDef`, `Assign`, `For`, `AsyncFor`,
        `With`, `AsyncWith`, and `arg`
        """
        if not hasattr(node, 'type_comment') or node.type_comment is None:
            return node
        _LOG.debug('transforming type comment "%s" of %s', node.type_comment, node)
        if not isinstance(node.type_comment, str):
            _LOG.warning('type comment is not a str but %s', type(node.type_comment))
            return node
        node.type_comment = parser_ast_module.parse(node.type_comment, mode='eval').body
        if eval_ and parser_ast_module is ast:
            #assert isinstance(globals_, dict), type(globals_)
            expression = compile(ast.Expression(body=node.type_comment), '<type-comment>', 'eval')
            node.type_comment = eval(expression, globals_, locals_)
        _LOG.info('transformed type comment of %s', node)
        return node

    class TypeCommentTransformerClass(RecursiveAstTransformer[ast_module]):

        """Parse type comments from strings to ASTs."""

        def __init__(self, *args, globals_=None, locals_=None, **kwargs):
            transformer = functools.partial(
                transform_type_comment, eval_=True, globals_=globals_, locals_=locals_)
            super().__init__(*args, transformer=transformer, **kwargs)

        '''
        def _visit_node_with_type_comment(self, node):

        def generic_visit(self, node):
            return ast_module.generic_visit(self, node)

        def visit_FunctionDef(self, node):
            return self._visit_node_with_type_comment(node)

        def visit_AsyncFunctionDef(self, node):
            return self._visit_node_with_type_comment(node)

        def visit_Assign(self, node):
            return self._visit_node_with_type_comment(node)

        def visit_For(self, node):
            return self._visit_node_with_type_comment(node)

        def visit_AsyncFor(self, node):
            return self._visit_node_with_type_comment(node)

        def visit_With(self, node):
            return self._visit_node_with_type_comment(node)

        def visit_AsyncWith(self, node):
            return self._visit_node_with_type_comment(node)

        def visit_arg(self, node):
            return self._visit_node_with_type_comment(node)
        '''

    return TypeCommentTransformerClass

TypeCommentTransformer = {
    (typed_ast.ast3, ast_module): create_type_comment_transformer(typed_ast.ast3, ast_module)
    for ast_module in [ast, typed_ast.ast3]}
