
import ast
import functools
import logging
import typing as t

import typed_ast

from .recursive_ast_transformer import RecursiveAstTransformer
from .ast_transcriber import AstTranscriber

_LOG = logging.getLogger(__name__)


def create_type_annotation_transformer(
        ast_module: t.Any=typed_ast.ast3, parser_ast_module: t.Any=ast) -> t.Any:
    """Create TypeAnnotationTransformer class based on given AST modules."""

    def transform_normal_type_annotation(
            node: ast_module.AST, globals_=globals(), locals_=None) -> ast_module.AST:
        """Compile and evaluate node's type annotation.

        The field `annotation` of the given AST node will be compile()'d and eval()'d.

        For Python 3.6, nodes that can have type annotations are:
        `AnnAssign` and `arg`
        """
        
        if not hasattr(node, 'annotation') or node.annotation is None:
            return node
        _LOG.debug('transforming type annotation of %s', node)
        if not isinstance(node.annotation, ast_module.AST):
            _LOG.warning('type annotation is not AST but %s', type(node.annotation))
            return node
        if parser_ast_module is ast:
            annotation = AstTranscriber[ast_module, ast]().visit(node.annotation)
            ast.fix_missing_locations(annotation)
            expression = compile(ast.Expression(body=annotation), '<type-annotation>', 'eval')
            node.annotation = eval(expression, globals_, locals_)
        else:
            raise NotImplementedError()
        _LOG.info('transformed type annotation of %s', node)
        return node

    def transform_return_type_annotation(
            node: ast_module.AST, globals_=globals(), locals_=None) -> ast_module.AST:
        """Compile and evaluate node's return type annotation.

        The field `returns` of the given AST node will be compile()'d and eval()'d.

        For Python 3.6, nodes that can have return type annotations are:
        `FunctionDef` and `AsyncFunctionDef`
        """
        if not hasattr(node, 'returns') or node.returns is None:
            return node
        _LOG.debug('transforming return type annotation of %s', node)
        if not isinstance(node.returns, ast_module.AST):
            _LOG.warning('return type annotation is not AST but %s', type(node.returns))
            return node
        if parser_ast_module is ast:
            returns = AstTranscriber[ast_module, ast]().visit(node.returns)
            ast.fix_missing_locations(returns)
            expression = compile(ast.Expression(body=returns), '<return-type-annotation>', 'eval')
            node.returns = eval(expression, globals_, locals_)
        else:
            raise NotImplementedError()
        _LOG.info('transformed return type annotation of %s', node)
        return node

    def transform_type_annotation(
            node: ast_module.AST, globals_=globals(), locals_=None) -> ast_module.AST:
        """Compile and evaluate node's type annotations."""

        node = transform_normal_type_annotation(node, globals_, locals_)
        node = transform_return_type_annotation(node, globals_, locals_)
        return node

        node.type_comment = parser_ast_module.parse(node.type_comment, mode='eval').body

    class TypeAnnotationTransformerClass(RecursiveAstTransformer[ast_module]):

        """Parse type comments from strings to ASTs."""

        def __init__(self, *args, globals_=None, locals_=None, **kwargs):
            transformer = functools.partial(
                transform_type_annotation, globals_=globals_, locals_=locals_)
            super().__init__(*args, transformer=transformer, **kwargs)

    return TypeAnnotationTransformerClass

TypeAnnotationTransformer = {
    (typed_ast.ast3, ast_module): create_type_annotation_transformer(typed_ast.ast3, ast_module)
    for ast_module in [ast, typed_ast.ast3]}
