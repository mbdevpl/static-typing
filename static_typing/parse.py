"""High-level functions for parsing and adding static type information to AST."""

#import inspect
import logging

import typed_ast.ast3

from .augment import augment

_LOG = logging.getLogger(__name__)


def parse(source: str, globals_=None, locals_=None, ast_module=typed_ast.ast3, *args, **kwargs):
    """Act like ast_module.parse() but also put static type info into AST."""

    #if not isinstance(source, str):
    #    source = inspect.getsource(source)
    if globals_ is None:
        pass # TODO: get globals from caller
    if locals_ is None:
        pass # TODO: get locals from caller

    tree = ast_module.parse(source, *args, **kwargs)
    _LOG.debug('%s', ast_module.dump(tree))

    tree = augment(tree, globals_, locals_, ast_module)
    _LOG.debug('%s', ast_module.dump(tree))

    return tree
