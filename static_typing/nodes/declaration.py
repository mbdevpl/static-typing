"""Declaration nodes, i.e. Assign and AnnAssign."""

import ast
import collections
import logging
import sys

import typed_ast.ast3

from .statically_typed import StaticallyTyped

_LOG = logging.getLogger(__name__)


def create_declaration(ast_module):
    """Create statically typed AST declaration node class based on a given AST module."""

    class StaticallyTypedDeclarationClass(StaticallyTyped[ast_module]):

        """Statically typed declaration AST node."""

        _type_fields = ('vars',)

        def __init__(self, *args, **kwargs):
            self._vars = collections.OrderedDict()
            super().__init__(*args, **kwargs)

        def _add_declaration(self, target, type_hint):
            if isinstance(target, ast_module.Tuple):
                if type_hint is None:
                    type_hint = [None for _ in target.elts]
                if isinstance(type_hint, ast_module.AST):
                    raise TypeError('unresolved type hint: {}'.format(ast_module.dump(type_hint)))
                if not isinstance(type_hint, collections.abc.Iterable):
                    raise TypeError('expected iterable type hint but got {}: {}'
                                    .format(type(type_hint), type_hint))
                for elt, elt_hint in zip(target.elts, type_hint):
                    self._add_declaration(elt, elt_hint)
                return
            self._vars[target] = type_hint

        def _add_declarations(self, targets, type_hint):
            if len(targets) == 1:
                self._add_declaration(targets[0], type_hint)
            for target in targets:
                self._add_declaration(target, type_hint)

    return StaticallyTypedDeclarationClass


StaticallyTypedDeclaration = {ast_module: create_declaration(ast_module)
                              for ast_module in (ast, typed_ast.ast3)}


def create_assign(ast_module):
    """Create statically typed AST Assign node class based on a given AST module."""

    class StaticallyTypedAssignClass(ast_module.Assign, StaticallyTypedDeclaration[ast_module]):

        """Statically typed version of Assign AST node."""

        def _add_type_info(self):
            if not getattr(self, 'targets', None):
                return
            self._add_declarations(self.targets, getattr(self, 'type_comment', None))

    return StaticallyTypedAssignClass


StaticallyTypedAssign = {ast_module: create_assign(ast_module)
                         for ast_module in (ast, typed_ast.ast3)}


def create_ann_assign(ast_module):
    """Create statically typed AST AnnAssign node class based on a given AST module."""

    class StaticallyTypedAnnAssignClass(
            ast_module.AnnAssign, StaticallyTypedDeclaration[ast_module]):

        """Statically typed version of AnnAssign AST node."""

        def _add_type_info(self):
            if not getattr(self, 'target', None):
                return
            self._add_declaration(self.target, self.annotation)

    return StaticallyTypedAnnAssignClass


StaticallyTypedAnnAssign = {ast_module: create_ann_assign(ast_module)
                            for ast_module in (
                                (ast, typed_ast.ast3) if sys.version_info[:2] >= (3, 6)
                                else (typed_ast.ast3,))}
