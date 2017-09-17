"""Unit tests for ast_manipulation module."""

import ast
import itertools
import logging
import typing as t
import unittest

import numpy as np
import typed_ast.ast3

import static_typing as st
from static_typing.ast_manipulation.recursive_ast_visitor import RecursiveAstVisitor
from static_typing.ast_manipulation.recursive_ast_transformer import RecursiveAstTransformer
from static_typing.ast_manipulation.ast_transcriber import AstTranscriber
from static_typing.ast_manipulation.type_hint_resolver import TypeHintResolver
from .examples import CODE_EXAMPLES

_LOG = logging.getLogger(__name__)

AST_MODULES = (ast, typed_ast.ast3)


class Tests(unittest.TestCase):

    maxDiff = None

    def test_recursive_ast_visitor(self):
        for ast_module in AST_MODULES:
            for description, example in CODE_EXAMPLES.items():
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    class visitor_class(RecursiveAstVisitor[ast_module]):
                        visited_node = False
                        visited_field = False
                        def visit_node(self, *_):
                            type(self).visited_node = True
                        def visit_field(self, *_):
                            type(self).visited_field = True
                    visitor = visitor_class()
                    tree = ast_module.parse(example)
                    visitor.visit(tree)
                    self.assertTrue(visitor_class.visited_node)
                    self.assertTrue(visitor_class.visited_field)

    def test_recursive_ast_transformer(self):
        for ast_module in AST_MODULES:
            for description, example in CODE_EXAMPLES.items():
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    class transformer_class(RecursiveAstTransformer[ast_module]):
                        transformed_node = False
                        transformed_field = False
                        def visit_node(self, node):
                            type(self).transformed_node = True
                            node.lineno = -1
                            return node
                        def visit_field(self, node, name, value):
                            type(self).transformed_field = True
                            return value
                    transformer = transformer_class()
                    tree = ast_module.parse(example)
                    tree = transformer.visit(tree)
                    self.assertTrue(transformer_class.transformed_node)
                    self.assertTrue(transformer_class.transformed_field)
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
            for description, example in CODE_EXAMPLES.items():
                with self.subTest(from_ast_module=from_ast_module, to_ast_module=to_ast_module,
                                  msg=description, example=example):
                    transcriber = AstTranscriber[from_ast_module, to_ast_module]()
                    tree = from_ast_module.parse(example)
                    tree = transcriber.visit(tree)
                    class visitor_class(RecursiveAstVisitor[to_ast_module]):
                        testcase = self
                        def visit_node(self, node):
                            type(self).testcase.assertIsInstance(node, to_ast_module.AST)
                    visitor = visitor_class()
                    visitor.visit(tree)

    def test_type_hint_resolver(self):
        for ast_module, parser_ast_module, eval_, globals_, locals_ in itertools.product(
                AST_MODULES, AST_MODULES, (False, True), (None, globals()), (None,)):
            if parser_ast_module is not ast and eval_:
                with self.assertRaises(NotImplementedError):
                    TypeHintResolver[typed_ast.ast3, parser_ast_module](eval_)
                continue
            for description, example in CODE_EXAMPLES.items():
                with self.subTest(ast_module=ast_module, parser_ast_module=parser_ast_module,
                                  eval=eval_, globals_is_none=globals_ is None,
                                  locals_is_none=locals_ is None, msg=description, example=example):
                    resolver = TypeHintResolver[ast_module, parser_ast_module](
                        eval_, globals_, locals_)
                    tree = ast_module.parse(example)
                    if eval_ and globals_ is None and 'external types' in description:
                        with self.assertRaises(NameError):
                            resolver.visit(tree)
                        continue
                    tree = resolver.visit(tree)
