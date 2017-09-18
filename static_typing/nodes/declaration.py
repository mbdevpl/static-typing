
import ast
import collections
import typing as t
import warnings

import typed_ast.ast3

from .statically_typed import StaticallyTyped


def scan_Assign_target(
        target: 't.Union[ast_module.Name, ast_module.Tuple]',
        type_comment: t.Optional[tuple], ast_module) -> t.Sequence[t.Tuple[str, t.Sequence[type]]]:
    """Scan target of Assign node."""
    if isinstance(target, ast_module.Tuple):
        if type_comment is None:
            type_comment = [None for _ in target.elts]
        elif isinstance(type_comment, ast_module.Tuple):
            warnings.warn('wtf', FutureWarning)
            type_comment = type_comment.elts
        variables = []
        for elt, cmnt in zip(target.elts, type_comment):
            variables += scan_Assign_target(elt, cmnt)
        return variables

    #if isinstance(target, ast_module.Attribute):
    #    return [(target, type_comment)]
    #assert isinstance(target, ast_module.Name), type(target)
    return [(target, type_comment)]


def scan_Assign(assign, ast_module) -> t.Sequence[t.Tuple[str, t.Sequence[type]]]:
    """Scan Assign node."""
    variables = []
    for target in assign.targets:
        variables += scan_Assign_target(target, getattr(assign, 'type_comment', None), ast_module)
    return variables


def scan_AnnAssign(ann_assign, ast_module) -> t.Sequence[t.Tuple[str, t.Sequence[type]]]:
    """Scan AnnAssign node."""
    assert isinstance(ann_assign.target, ast_module.Name)
    return [(ann_assign.target, ann_assign.annotation)]


def create_statically_typed_declaration(ast_module):

    class StaticallyTypedDeclarationClass(StaticallyTyped[ast_module]):

        _type_fields = 'vars', 'value_types'

        def __init__(self, *args, **kwargs):
            self._vars = []
            self._value_types = collections.OrderedDict()
            super().__init__(*args, **kwargs)

        def _add_declarations(self, targets, type_hint):
            if len(targets) == 1:
                pass
            for target in targets:
                continue
            # TODO: implementation
            #raise NotImplementedError()

    return StaticallyTypedDeclarationClass


StaticallyTypedDeclaration = {ast_module: create_statically_typed_declaration(ast_module)
                              for ast_module in (ast, typed_ast.ast3)}


def create_statically_typed_assign(ast_module):

    class StaticallyTypedAssignClass(ast_module.Assign, StaticallyTypedDeclaration[ast_module]):

        def _add_type_info(self):
            self._add_declarations(self.targets, getattr(self, 'type_comment', None))

    return StaticallyTypedAssignClass


StaticallyTypedAssign = {ast_module: create_statically_typed_assign(ast_module)
                         for ast_module in (ast, typed_ast.ast3)}


def create_statically_typed_ann_assign(ast_module):

    class StaticallyTypedAnnAssignClass(ast_module.AnnAssign, StaticallyTypedDeclaration[ast_module]):

        def _add_type_info(self):
            #assert isinstance(self.target, ast_module.Name), type(self.target)
            self._add_declarations([self.target], self.annotation)

    return StaticallyTypedAnnAssignClass


StaticallyTypedAnnAssign = {ast_module: create_statically_typed_ann_assign(ast_module)
                            for ast_module in (ast, typed_ast.ast3)}
