"""Certain compound statements - For, If, While, With."""

import ast

import typed_ast.ast3

from .statically_typed import StaticallyTyped


def create_for(ast_module):
    """Create statically typed AST For node class based on a given AST module."""

    class StaticallyTypedForClass(ast_module.For, StaticallyTyped[ast_module]):

        """Statically typed version of For AST node."""

        _type_fields = ('index_vars',)

        def __init__(self, *args, **kwargs):
            self._index_vars = {}
            # self._scope_vars = {}
            super().__init__(*args, **kwargs)

        def _add_type_info(self):
            if not getattr(self, 'body', None):
                return
            self._index_vars[self.target] = getattr(self, 'resolved_type_comment', None)
            # TODO: multiple index variables

    return StaticallyTypedForClass


StaticallyTypedFor = {ast_module: create_for(ast_module)
                      for ast_module in (ast, typed_ast.ast3)}


#class StaticallyTypedIf(ast_module.If, StaticallyTyped):
#
#    _type_fields = ('if_true_vars', 'if_false_vars')
#
#    def __init__(self, *args, **kwargs):
#        self._if_true_vars = {}
#        self._if_false_vars = {}
#        super().__init__(*args, **kwargs)
#
#    def add_type_info(self):
#        pass


#class StaticallyTypedWhile(ast_module.While, StaticallyTyped):
#
#    _type_fields = ()
#
#    def __init__(self, *args, **kwargs):
#        #self._scope_vars = {}
#        super().__init__(*args, **kwargs)
#
#    def add_type_info(self):
#        pass


def create_with(ast_module):
    """Create statically typed AST With node class based on a given AST module."""

    class StaticallyTypedWithClass(ast_module.With, StaticallyTyped[ast_module]):

        """Statically typed version of With AST node."""

        _type_fields = ('context_vars',)

        def __init__(self, *args, **kwargs):
            self._context_vars = {}
            # self._scope_vars = {}
            super().__init__(*args, **kwargs)

        def _add_type_info(self):
            if not getattr(self, 'body', None):
                return
            for item in self.items:
                if isinstance(item.optional_vars, ast_module.Name):
                    name = item.optional_vars
                    self._context_vars[name] = getattr(self, 'resolved_type_comment', None)
                # TODO: proper type hint decomposition in case of many context managers
                # TODO: multiple context variables from one context manager

    return StaticallyTypedWithClass


StaticallyTypedWith = {ast_module: create_with(ast_module)
                       for ast_module in (ast, typed_ast.ast3)}
