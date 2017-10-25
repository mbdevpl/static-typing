"""Resolve type hints present in a given AST."""

import ast
import itertools
import logging

import typed_ast.ast3

from .recursive_ast_transformer import RecursiveAstTransformer
from .ast_transcriber import AstTranscriber

_LOG = logging.getLogger(__name__)


def create_type_hint_resolver(ast_module, parser_ast_module):
    """Create TypeHintResolver class based on given AST modules."""

    class TypeHintResolverClass(RecursiveAstTransformer[ast_module]):

        """Resolve type hints.

        Transform type comments from strings (and type annotations from strings or ASTs)
        into evaluated and compiled ASTs according to given snapshot of globally and locally
        available types.
        """

        def __init__(self, eval_: bool = True, globals_=None, locals_=None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._eval = eval_
            if self._eval and parser_ast_module is not ast:
                raise NotImplementedError(
                    'Only built-in ast module has capability to compile() and eval() Python.')
            if globals_ is None:
                globals_ = {'__builtins__': globals()['__builtins__']}
            self._globals = globals_
            if locals_ is None:
                locals_ = {}
            self._locals = locals_
            if ast_module is not parser_ast_module:
                self._transcriber = AstTranscriber[ast_module, parser_ast_module]()

        def resolve_type_hint(self, hint):
            """Resolve a given type hint.

            The procedure is as follows:
            1. If hint is a str, parse it into AST.
            2. If hint is AST, compile and evaluate it.

            For Python 3.6, nodes that can have type hints are:
            -  type comments: `FunctionDef`, `AsyncFunctionDef`, `Assign`, `For`, `AsyncFor`,
            `With`, `AsyncWith`, and `arg`
            - type annotations: `AnnAssign` and `arg`
            - return type annotations: `FunctionDef` and `AsyncFunctionDef`
            """
            if isinstance(hint, str):
                hint = ast_module.parse(hint, mode='eval').body
            if not isinstance(hint, (ast_module.AST, parser_ast_module.AST)):
                _LOG.warning('given type hint is not AST but %s', type(hint))
                return hint
            if ast_module is not parser_ast_module:
                hint = self._transcriber.visit(hint)
            hint = parser_ast_module.fix_missing_locations(hint)
            if not self._eval:
                return hint
            expression = compile(ast.Expression(body=hint), '<type-hint>', 'eval')
            return eval(expression, self._globals, self._locals)

        def visit_node(self, node):
            """Resolve type hints (if any) in a given node."""
            if getattr(node, 'type_comment', None) is not None:
                if not isinstance(node.type_comment, str):
                    _LOG.warning('type comment is not a str but %s', type(node.type_comment))
                _LOG.debug('resolving type comment "%s" of %s', node.type_comment, node)
                node.type_comment = self.resolve_type_hint(node.type_comment)
                _LOG.info('resolved type comment of %s', node)
            if getattr(node, 'annotation', None) is not None:
                _LOG.debug('resolving type annotation of %s', node)
                node.annotation = self.resolve_type_hint(node.annotation)
                _LOG.info('resolved type annotation of %s', node)
            if getattr(node, 'returns', None) is not None:
                _LOG.debug('resolving return type annotation of %s', node)
                node.returns = self.resolve_type_hint(node.returns)
                _LOG.info('resolved return type annotation of %s', node)
            return node

    return TypeHintResolverClass


TypeHintResolver = {
    (ast_module, parser_ast_module): create_type_hint_resolver(ast_module, parser_ast_module)
    for ast_module, parser_ast_module in itertools.product(
        (ast, typed_ast.ast3), (ast, typed_ast.ast3))}
