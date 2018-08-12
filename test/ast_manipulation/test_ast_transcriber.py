"""Unit tests for ast_manipulation module."""

import ast
# timport collections.abc
# import itertools
import logging
# import sys
import unittest

import typed_ast.ast3 as typed_ast3

from static_typing.ast_manipulation.ast_transcriber import AstTranscriber
# from test.examples import \
#    AST_MODULES, SOURCE_CODES

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    def test_preserve_custom_fields(self):
        example = typed_ast3.Name('spam', typed_ast3.Load())
        typed_ast3.fix_missing_locations(example)
        example.custom_field = 'some value'
        transcriber = AstTranscriber[typed_ast3, ast]()
        result = transcriber.visit(example)

        _LOG.debug('%s', vars(example))
        self.assertTrue(hasattr(example, 'lineno'), msg=vars(example))
        self.assertTrue(hasattr(example, 'custom_field'), msg=vars(example))

        _LOG.debug('%s', vars(result))
        self.assertTrue(hasattr(result, 'lineno'), msg=vars(result))
        self.assertTrue(hasattr(result, 'custom_field'), msg=vars(result))
