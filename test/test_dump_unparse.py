"""Unit tests for unparser module."""

import ast
import itertools
import logging
import unittest

from static_typing.ast_manipulation import TypeHintResolver
from static_typing.static_typer import StaticTyper
from static_typing import augment, parse, dump, unparse
from .examples import AST_MODULES, SOURCE_CODES, GLOBALS_EXTERNAL, LOCALS_NONE

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    def _validate_dump_unparse(self, tree, ast_module, *args, **kwargs):
        with self.subTest(*args, ast_module=ast_module, **kwargs):
            tree_dump = dump(tree)
            self.assertIsInstance(tree_dump, str)
            code = unparse(tree)
            self.assertIsInstance(code, str)
            try:
                ast_module.parse(code)
            except SyntaxError:
                _LOG.warning('%s failed to parse unparsed code """%s"""', ast_module, code)

    def test_resolve(self):
        for ast_module, eval_ in itertools.product(AST_MODULES, (False, True)):
            resolver = TypeHintResolver[ast_module, ast](eval_=eval_, globals_=GLOBALS_EXTERNAL)
            for description, example in SOURCE_CODES.items():
                tree = ast_module.parse(example)
                tree = resolver.visit(tree)
                self._validate_dump_unparse(
                    tree, ast_module, description=description, example=example)

    def test_statically_type(self):
        for ast_module in AST_MODULES:
            resolver = TypeHintResolver[ast_module, ast](globals_=GLOBALS_EXTERNAL)
            typer = StaticTyper[ast_module]()
            for description, example in SOURCE_CODES.items():
                tree = ast_module.parse(example)
                tree = resolver.visit(tree)
                tree = typer.visit(tree)
                self._validate_dump_unparse(
                    tree, ast_module, description=description, example=example)

    def test_augment(self):
        for ast_module in AST_MODULES:
            for description, example in SOURCE_CODES.items():
                tree = ast_module.parse(example)
                tree = augment(tree, globals_=GLOBALS_EXTERNAL, locals_=LOCALS_NONE,
                               ast_module=ast_module)
                self._validate_dump_unparse(
                    tree, ast_module, description=description, example=example)

    def test_parse(self):
        for ast_module in AST_MODULES:
            for description, example in SOURCE_CODES.items():
                tree = parse(example, globals_=GLOBALS_EXTERNAL, locals_=LOCALS_NONE,
                             ast_module=ast_module)
                self._validate_dump_unparse(
                    tree, ast_module, description=description, example=example)
