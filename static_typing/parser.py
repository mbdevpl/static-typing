
import ast
import inspect
import logging

from ._config import ast_module
from .recursive_ast_transformer import RecursiveAstTransformer
from .type_comment_transformer import TypeCommentTransformer
from .type_annotation_transformer import TypeAnnotationTransformer
from .statically_typed_ast import StaticallyTyped, \
    StaticallyTypedModule, StaticallyTypedFor, StaticallyTypedWhile, StaticallyTypedIf, \
    StaticallyTypedFunctionDef, StaticallyTypedClassDef

_LOG = logging.getLogger(__name__)


def add_static_type_info(node: ast_module.AST) -> StaticallyTyped:
    """Introduce static typing information to compatible nodes of the AST."""

    nodes_to_be_typed = {
        ast_module.Module, ast_module.For, ast_module.While, ast_module.If, ast_module.FunctionDef,
        ast_module.ClassDef}
    node_type = type(node)
    if node_type in nodes_to_be_typed:
        return globals()[f'StaticallyTyped{node_type.__name__}'].from_other(node)

    return node

def parse(source: str, globals_=None, locals_=None, *args, **kwargs) -> ast_module.AST:

    if not isinstance(source, str):
        source = inspect.getsource(source)
    if globals_ is None:
        pass # TODO: get globals from caller
    if locals_ is None:
        pass # TODO: get locals from caller

    tree = ast_module.parse(source, *args, **kwargs)
    _LOG.debug('%s', ast_module.dump(tree))

    comment_transformer = TypeCommentTransformer[ast_module, ast](
        globals_=globals_, locals_=locals_)
    comment_tree = comment_transformer.visit(tree)
    _LOG.debug('%s', ast_module.dump(comment_tree))

    annotation_transformer = TypeAnnotationTransformer[ast_module, ast](
        globals_=globals_, locals_=locals_)
    annotation_tree = annotation_transformer.visit(comment_tree)
    _LOG.debug('%s', ast_module.dump(annotation_tree))

    typer = RecursiveAstTransformer[ast_module](transformer=add_static_type_info)
    typed_tree = typer.visit(annotation_tree)
    _LOG.debug('%s', ast_module.dump(typed_tree))

    return typed_tree
