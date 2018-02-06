"""Unit tests for ast_manipulation module."""

import ast
import collections.abc
import itertools
import logging
import unittest

from static_typing.ast_manipulation.recursive_ast_visitor import RecursiveAstVisitor
from static_typing.ast_manipulation.recursive_ast_transformer import RecursiveAstTransformer
from static_typing.ast_manipulation.ast_transcriber import AstTranscriber
from static_typing.ast_manipulation.type_hint_resolver import TypeHintResolver
from .examples import \
    AST_MODULES, SOURCE_CODES, TYPE_HINTS, GLOBALS_EXTERNAL, GLOBALS_EXAMPLES, LOCALS_EXTERNAL, \
    LOCALS_EXAMPLES

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    maxDiff = None

    def test_recursive_ast_visitor(self):
        for ast_module, fields_first, (description, example) in itertools.product(
                AST_MODULES, (False, True), SOURCE_CODES.items()):
            with self.subTest(ast_module=ast_module, msg=description, example=example):
                class VisitorClass(RecursiveAstVisitor[ast_module]):
                    visited_node = False
                    visited_field = False

                    def visit_node(self, node):
                        type(self).visited_node = True
                        super().visit_node(node)

                    def visit_field(self, node, name, value):
                        type(self).visited_field = True
                        super().visit_field(node, name, value)
                visitor = VisitorClass(fields_first)
                tree = ast_module.parse(example)
                visitor.visit(tree)
                self.assertTrue(VisitorClass.visited_node)
                self.assertTrue(VisitorClass.visited_field)

    def test_recursive_ast_transformer(self):
        for ast_module, fields_first, (description, example) in itertools.product(
                AST_MODULES, (False, True), SOURCE_CODES.items()):
            with self.subTest(ast_module=ast_module, msg=description, example=example):
                class TransformerClass(RecursiveAstTransformer[ast_module]):
                    transformed_node = False
                    transformed_field = False

                    def visit_node(self, node):
                        type(self).transformed_node = True
                        node.lineno = -1
                        return super().visit_node(node)

                    def visit_field(self, node, name, value):
                        type(self).transformed_field = True
                        return super().visit_field(node, name, value)
                transformer = TransformerClass(fields_first)
                tree = ast_module.parse(example)
                tree = transformer.visit(tree)
                self.assertTrue(TransformerClass.transformed_node)
                self.assertTrue(TransformerClass.transformed_field)
                original_tree = ast_module.parse(example)
                self.assertEqual(ast_module.dump(tree), ast_module.dump(original_tree))
                self.assertEqual(
                    ast_module.dump(tree, annotate_fields=True),
                    ast_module.dump(original_tree, annotate_fields=True))
                self.assertNotEqual(
                    ast_module.dump(tree, include_attributes=True),
                    ast_module.dump(original_tree, include_attributes=True))

    def test_ast_transcriber(self):
        for from_ast_module, to_ast_module in itertools.product(AST_MODULES, AST_MODULES):
            if from_ast_module is to_ast_module:
                continue
            for description, example in SOURCE_CODES.items():
                with self.subTest(from_ast_module=from_ast_module, to_ast_module=to_ast_module,
                                  msg=description, example=example):
                    transcriber = AstTranscriber[from_ast_module, to_ast_module]()
                    tree = from_ast_module.parse(example)
                    tree = transcriber.visit(tree)

                    class VisitorClass(RecursiveAstVisitor[to_ast_module]):
                        testcase = self

                        def visit_node(self, node):
                            type(self).testcase.assertIsInstance(node, to_ast_module.AST)
                    visitor = VisitorClass()
                    visitor.visit(tree)

    def test_type_hint_resolver_resolve(self):
        for ast_module, parser_ast_module, eval_, globals_, locals_, preresolve \
                in itertools.product(AST_MODULES, AST_MODULES, (False, True), GLOBALS_EXAMPLES,
                                     LOCALS_EXAMPLES, (False, True)):
            preresolver = TypeHintResolver[ast_module, parser_ast_module](False, globals_, locals_)
            if parser_ast_module is not ast and eval_:
                with self.assertRaises(NotImplementedError):
                    TypeHintResolver[ast_module, parser_ast_module](eval_, globals_, locals_)
                continue
            resolver = TypeHintResolver[ast_module, parser_ast_module](
                eval_, globals_, locals_)
            for description, (hint, parsed_hint, static_type) in \
                    TYPE_HINTS[parser_ast_module].items():
                with self.subTest(ast_module=ast_module, parser_ast_module=parser_ast_module,
                                  eval=eval_, globals_is_none=globals_ is None,
                                  locals_is_none=locals_ is None):
                    resolvable = isinstance(hint, (str, ast_module.AST, parser_ast_module.AST))
                    if resolvable and preresolve:
                        hint = preresolver.resolve_type_hint(hint)
                    if resolvable and eval_ and 'external type' in description \
                            and globals_ is not GLOBALS_EXTERNAL and locals_ is not LOCALS_EXTERNAL:
                        with self.assertRaises(NameError):
                            resolver.resolve_type_hint(hint)
                        continue
                    resolved_hint = resolver.resolve_type_hint(hint)
                    if not resolvable:
                        self.assertIs(resolved_hint, hint)
                    elif eval_:
                        self.assertIsInstance(resolved_hint, type)
                        self.assertIs(resolved_hint, static_type)
                    else:
                        self.assertIsInstance(resolved_hint, parser_ast_module.AST)
                        self.assertEqual(parser_ast_module.dump(resolved_hint),
                                         parser_ast_module.dump(parsed_hint))

    def test_type_hint_resolver_visit(self):
        for ast_module, parser_ast_module, eval_, globals_, locals_, preresolve \
                in itertools.product(AST_MODULES, AST_MODULES, (False, True), GLOBALS_EXAMPLES,
                                     LOCALS_EXAMPLES, (False, True)):
            preresolver = TypeHintResolver[ast_module, parser_ast_module](False, globals_, locals_)
            if parser_ast_module is not ast and eval_:
                with self.assertRaises(NotImplementedError):
                    TypeHintResolver[ast_module, parser_ast_module](eval_, globals_, locals_)
                continue
            resolver = TypeHintResolver[ast_module, parser_ast_module](
                eval_, globals_, locals_)
            for description, example in SOURCE_CODES.items():
                with self.subTest(ast_module=ast_module, parser_ast_module=parser_ast_module,
                                  eval=eval_, globals_is_none=globals_ is None,
                                  locals_is_none=locals_ is None, msg=description, example=example):
                    tree = ast_module.parse(example)
                    if preresolve:
                        tree = preresolver.visit(tree)
                    if eval_ and 'external types' in description \
                            and globals_ is not GLOBALS_EXTERNAL and locals_ is not LOCALS_EXTERNAL:
                        if ast_module is not ast:
                            with self.assertRaises(NameError):
                                resolver.visit(tree)
                        continue
                    tree = resolver.visit(tree)
                    for node in ast_module.walk(tree):
                        type_comment = getattr(node, 'resolved_type_comment', None)
                        annotation = getattr(node, 'resolved_annotation', None)
                        returns = getattr(node, 'resolved_returns', None)
                        for hint in (type_comment, annotation, returns):
                            if hint is None:
                                continue
                            if eval_:
                                self.assertIsInstance(hint, (type, tuple, collections.abc.Callable))
                                if not isinstance(hint, type):
                                    _LOG.warning('resolved hint is instance of %s: %s',
                                                 type(hint), hint)
                                    # TODO: validate non-flat resolved hints
                            else:
                                self.assertIsInstance(hint, parser_ast_module.AST)
