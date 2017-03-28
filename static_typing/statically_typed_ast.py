
import ast
import logging
import typing as t

import typed_ast

from ._config import ast_module
from .ast_transcriber import AstTranscriber


class StaticallyTyped(ast_module.AST):

    @classmethod
    def clone(cls, node: ast_module.AST):
        node_fields = {k: v for k, v in ast_module.iter_fields(node)}
        return cls(**node_fields)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.type_info = {'vars': {}, 'scopes': []}
        self.local_vars = {}
        #self.scopes = []

    def add_type_info(self, var_name: str, type_info: t.Any, scope: t.Any=None):
        if var_name in self.local_vars:
            if type_info is None:
                return
            if self.local_vars[var_name] is not None:
                raise NotImplementedError()
        '''
        if type_info is not None:
            if isinstance(type_info, ast_module.AST):
                type_info = AstTranscriber[ast_module, ast]().visit(type_info)
                ast.fix_missing_locations(type_info)
            if isinstance(type_info, ast.AST):
                type_info = compile(ast.Expression(body=type_info), '<type-info>', 'eval')
                type_info = eval(type_info)
        #'''
        self.local_vars[var_name] = type_info

class StaticallyTypedFor(ast_module.For, StaticallyTyped):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    pass

class StaticallyTypedWhile(ast_module.While, StaticallyTyped):

    pass

class StaticallyTypedIf(ast_module.If, StaticallyTyped):

    pass

class StaticallyTypedFunctionDef(ast_module.FunctionDef, StaticallyTyped):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.augment()

    def _create_annotation_for(self, target, comment):
        if not isinstance(target, ast_module.Tuple):
            assert isinstance(target, ast_module.Name)
            #annotation = root_node.annotation if hasattr(root_node, 'annotation') else root_node.type_comment
            self.add_type_info(target.id, comment)
            return
        if comment is None:
            comment = ast_module.Tuple(elts=[None for _ in target.elts])
        if isinstance(comment, tuple):
            for elt, cmnt in zip(target.elts, comment):
                self._create_annotation_for(elt, cmnt)
            return
        assert isinstance(comment, (ast.Tuple, ast_module.Tuple)), type(comment)
        for elt, cmnt in zip(target.elts, comment.elts):
            self._create_annotation_for(elt, cmnt)

    def augment(self):
        #for node in typed_ast.ast3.iter_child_nodes(self):
        #    print(node.__class__, dict(typed_ast.ast3.iter_fields(node)))
        #print('walk')
        for node in ast_module.walk(self):
            if isinstance(node, ast_module.Assign):
                #if len(node.targets) == 1 and isinstance(node.targets[0], typed_ast.ast3.Name):
                #    self._update_annotation(node.targets[0].id, None)
                if node.type_comment is None:
                    for target in node.targets:
                        self._create_annotation_for(target, None)
                else:
                    #_LOG.warning('%s', typed_astunparse.dump(node))
                    #for target, comment in zip(node.targets, parse_type_comment(node.type_comment)): # TODO: don't assume that #vars == #comments
                    #    self._create_annotation_for(target, comment)
                    for target in node.targets:
                        self._create_annotation_for(target, node.type_comment)
                    """
                    if isinstance(target, typed_ast.ast3.Name):
                        self._update_annotation(target.id, node.type_comment)
                    elif isinstance(target, typed_ast.ast3.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, typed_ast.ast3.Name):
                                self._update_annotation(elt.id, node.type_comment)
                        #raise NotImplementedError((node.__class__, dict(typed_ast.ast3.iter_fields(node))))
                    """
            elif isinstance(node, ast_module.AnnAssign):
                assert isinstance(node.target, ast_module.Name)
                self.add_type_info(node.target.id, node.annotation)
            elif isinstance(node, ast_module.For):
                assert isinstance(node.target, ast_module.Name)
                self.add_type_info(node.target.id, node.type_comment)
                #raise NotImplementedError((node.__class__, dict(typed_ast.ast3.iter_fields(node))))
            #print(node.__class__, dict(typed_ast.ast3.iter_fields(node)))
        #typed_ast.ast3.AST.visit
        #visitor.visit(self)

class StaticallyTypedClassDef(ast_module.ClassDef, StaticallyTyped):

    pass
