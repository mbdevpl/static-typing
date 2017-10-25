"""Rewrite AST tree based on one AST module into a tree based on another (compatible) module."""

import ast
import logging

import typed_ast.ast3

from .recursive_ast_transformer import RecursiveAstTransformer

_LOG = logging.getLogger(__name__)


def create_ast_transcriber(from_ast_module, to_ast_module):
    """Create AstTranscriber class based on given AST modules."""

    class AstTranscriberClass(RecursiveAstTransformer[from_ast_module]):

        """Rewrite one AST tree into another.

        The point of rewriting is to convert the ASTs that come from different modules.
        In order for transcription to succeed, those modules have to be node-to-node compatible
        (at least in case of a given transcribed tree).
        """

        def visit_node(self, node):
            """Retype given node, assuming type compatibility."""
            _LOG.info('remapping %s from %s to %s', node, from_ast_module, to_ast_module)
            target_type = getattr(to_ast_module, type(node).__name__)
            _LOG.debug('target type is %s', target_type)
            node_fields = {k: v for k, v in from_ast_module.iter_fields(node)}
            _LOG.debug('constructor params are %s', node_fields)
            return target_type(**node_fields)

    return AstTranscriberClass


AstTranscriber = {
    (from_ast_module, to_ast_module): create_ast_transcriber(from_ast_module, to_ast_module)
    for from_ast_module, to_ast_module in ((typed_ast.ast3, ast), (ast, typed_ast.ast3))}
