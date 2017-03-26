
import ast
import logging
import typing as t

import typed_ast

from .recursive_ast_transformer import RecursiveAstTransformer

_LOG = logging.getLogger(__name__)


def create_ast_transcriber(from_ast_module: t.ClassVar, to_ast_module: t.ClassVar) -> t.ClassVar:

    def remap(tree: from_ast_module.AST) -> to_ast_module.AST:
        _LOG.info('remapping %s from %s to %s', tree, from_ast_module, to_ast_module)
        target_type = getattr(to_ast_module, type(tree).__name__)
        _LOG.debug('target type is %s', target_type)
        node_fields = {k: v for k, v in from_ast_module.iter_fields(tree)}
        _LOG.debug('constructor params are %s', node_fields)
        return target_type(**node_fields)

    class AstTranscriberClass(RecursiveAstTransformer[from_ast_module]):

        """Transcribe one AST into another.

        Assume that the classes, apart from having different base package, are identical.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, transformer=remap, **kwargs)

    return AstTranscriberClass

AstTranscriber = {
    (from_ast_module, to_ast_module): create_ast_transcriber(from_ast_module, to_ast_module)
    for from_ast_module, to_ast_module in [(ast, typed_ast.ast3), (typed_ast.ast3, ast)]}
