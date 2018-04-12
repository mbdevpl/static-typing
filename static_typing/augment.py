"""Add static type information to a given AST."""

import ast
import logging

import typed_ast.ast3

from .ast_manipulation import TypeHintResolver
from .static_typer import StaticTyper

_LOG = logging.getLogger(__name__)


def augment(tree, eval_: bool = True, globals_=None, locals_=None, ast_module=typed_ast.ast3):
    """Add static type information to the given AST."""

    parser_ast_module = ast if eval_ else ast_module
    type_hint_resolver = TypeHintResolver[ast_module, parser_ast_module](
        eval_=eval_, globals_=globals_, locals_=locals_)
    tree = type_hint_resolver.visit(tree)
    _LOG.debug('%s', ast_module.dump(tree))

    typer = StaticTyper[ast_module]()
    tree = typer.visit(tree)
    _LOG.debug('%s', ast_module.dump(tree))

    return tree
