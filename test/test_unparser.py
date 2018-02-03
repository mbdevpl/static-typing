"""Unit tests for unparser module."""

import io
import logging
import unittest

# from static_typing.augment import augment
from static_typing.parse import parse
from static_typing.unparser import Unparser
from .examples import AST_MODULES, SOURCE_CODES, GLOBALS_EXTERNAL, LOCALS_NONE

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    def test_unparser(self):
        for ast_module in AST_MODULES:
            # resolver = TypeHintResolver[ast_module, ast](globals_=GLOBALS_EXTERNAL)
            # typer = StaticTyper[ast_module]()
            for description, example in SOURCE_CODES.items():
                tree = parse(example, True, globals_=GLOBALS_EXTERNAL, locals_=LOCALS_NONE,
                             ast_module=ast_module)
                with self.subTest(ast_module=ast_module, msg=description, example=example):
                    sio = io.StringIO()
                    Unparser(tree, sio, globals_=GLOBALS_EXTERNAL, locals_=LOCALS_NONE)
                    code = sio.getvalue()
                    _LOG.debug('%s', code)
                    self.assertGreater(len(code), 0)
                    # TODO: validate unparsed code
