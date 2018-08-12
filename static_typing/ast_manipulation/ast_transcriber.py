"""Rewrite AST tree based on one AST module into a tree based on another (compatible) module."""

import ast
import collections.abc
import logging

import typed_ast.ast3

from .recursive_ast_transformer import RecursiveAstTransformer

_LOG = logging.getLogger(__name__)


def transcribe(from_ast_module, node: object, to_ast_module, target_type: type,
               extra_fields: collections.abc.Iterable = ()) -> object:
    """Forcibly instantiate new AST node type with data from given AST node."""
    node_fields = {k: v for k, v in from_ast_module.iter_fields(node)}
    for extra_field in extra_fields:
        if hasattr(node, extra_field):
            node_fields[extra_field] = getattr(node, extra_field)
    _LOG.debug('constructor params are %s', node_fields)
    transcribed_node = target_type(**node_fields)
    to_ast_module.copy_location(transcribed_node, node)
    custom_fields = set(vars(node)) - set(node._fields) - set(node._attributes)
    for custom_field in custom_fields:
        setattr(transcribed_node, custom_field, getattr(node, custom_field))
    return transcribed_node


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
            transcribed_node = transcribe(from_ast_module, node, to_ast_module, target_type)
            return transcribed_node

    return AstTranscriberClass


AstTranscriber = {
    (from_ast_module, to_ast_module): create_ast_transcriber(from_ast_module, to_ast_module)
    for from_ast_module, to_ast_module in ((typed_ast.ast3, ast), (ast, typed_ast.ast3))}
