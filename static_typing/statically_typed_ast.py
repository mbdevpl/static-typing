
import ast
import enum
import logging
import typing as t
import warnings

import ordered_set

from ._config import ast_module
#from .ast_transcriber import AstTranscriber

_LOG = logging.getLogger(__name__)

INDENT_STR = '  '


def scan_FunctionDef(
        function: ast_module.FunctionDef) -> t.Sequence[t.Tuple[str, t.Sequence[type]]]:
    """Scan FunctionDef node."""
    variables = []
    for node in ast_module.walk(function):
        if isinstance(node, ast_module.Assign):
            variables += scan_Assign(node)
        elif isinstance(node, ast_module.AnnAssign):
            variables += scan_AnnAssign(node)
        elif isinstance(node, ast_module.For):
            variables += [(node.target, node.type_comment)]
    return variables


def scan_Assign_target(
        target: t.Union[ast_module.Name, ast_module.Tuple],
        type_comment: t.Optional[tuple]) -> t.Sequence[t.Tuple[str, t.Sequence[type]]]:
    """Scan target of Assign node."""
    if isinstance(target, ast_module.Tuple):
        if type_comment is None:
            type_comment = [None for _ in target.elts]
        elif isinstance(type_comment, (ast.Tuple, ast_module.Tuple)):
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


def scan_Assign(node: ast_module.Assign) -> t.Sequence[t.Tuple[str, t.Sequence[type]]]:
    """Scan Assign node."""
    variables = []
    for target in node.targets:
        variables += scan_Assign_target(target, node.type_comment)
    return variables


def scan_AnnAssign(node: ast_module.AnnAssign) -> t.Sequence[t.Tuple[str, t.Sequence[type]]]:
    """Scan AnnAssign node."""
    #assert isinstance(node.target, ast_module.Name)
    return [(node.target, node.annotation)]


class StaticallyTyped(ast_module.AST):

    @classmethod
    def from_other(cls, node: ast_module.AST):
        node_fields = {k: v for k, v in ast_module.iter_fields(node)}
        return cls(**node_fields)

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)

    def add_type_info(self):
        raise NotImplementedError()

    @property
    def type_info_view(self):
        return self._type_info_view()

    #def print_type_info(self):
    #    print(self)
    #    for node in ast_module.iter_child_nodes(self):
    #        if isinstance(node, StaticallyTyped):
    #            print(node)

    def _type_info_view(self, indent: int = 0, inline: bool = False):
        raise NotImplementedError()

    def __repr__(self):
        return f'<{type(self).__name__}@{id(self)}>'

    def __str__(self):
        return f'<{type(self).__name__}>'


class StaticallyTypedModule(ast_module.Module, StaticallyTyped):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._constants = {}
        self._classes = {}
        self._functions = {}
        self.add_type_info()

    def add_type_info(self):
        for node in self.body:
            if isinstance(node, (ast_module.Assign, ast_module.AnnAssign)):
                if isinstance(node, ast_module.Assign):
                    variables = scan_Assign(node)
                elif isinstance(node, ast_module.AnnAssign):
                    variables = scan_AnnAssign(node)
                else:
                    TypeError('unhandled type')
                for var, type_info in variables:
                    var_name = var.id
                    if var_name.isupper():
                        if var_name not in self._constants:
                            self._constants[var_name] = ordered_set.OrderedSet()
                        if type_info is not None:
                            self._constants[var_name].append(type_info)
                    else:
                        raise NotImplementedError('module-level variables are not supported')
            elif isinstance(node, ast_module.FunctionDef):
                self._functions[node.name] = node
            elif isinstance(node, ast_module.ClassDef):
                self._classes[node.name] = node

    def _type_info_view(self, indent: int = 0, inline: bool = False):
        if inline:
            return str(self)
        lines = [f'{INDENT_STR * indent}<Module>:']
        lines += [f'{INDENT_STR * (indent + 1)}{len(self._constants)} constants:']
        lines += [
            f'{INDENT_STR * (indent + 2)}{var_name}: {tuple(type_info)}'
            for var_name, type_info in self._constants.items()]
        lines += [f'{INDENT_STR * (indent + 1)}{len(self._classes)} classes:']
        lines += [_._type_info_view(indent + 2) for __, _ in self._classes.items()]
        lines += [f'{INDENT_STR * (indent + 1)}{len(self._functions)} functions:']
        lines += [_._type_info_view(indent + 2) for __, _ in self._functions.items()]
        return '\n'.join(lines)

    def __str__(self):
        return f'<Module>: {len(self._constants)} constants, {len(self._classes)} classes,' \
            f' {len(self._functions)} functions'


class FunctionKind(enum.IntEnum):
    Undetermined = 0
    Function = 16
    Method = 1 + 2 + 4 + 8
    ClassMethod = 1 + 4
    StaticMethod = 1 + 8
    Constructor = 1 + 2 + 32
    InstanceMethod = 1 + 2


class StaticallyTypedFunctionDef(ast_module.FunctionDef, StaticallyTyped):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.type_info = {'vars': {}, 'scopes': []}
        self._params = {}
        self._returns = ordered_set.OrderedSet()
        self._kind = FunctionKind.Undetermined
        self._local_vars = {}
        #self.scopes = []
        self.add_type_info()

    def _add_local_var(self, var_name: str, type_info: t.Any, scope: t.Any=None):
        if var_name not in self._local_vars:
            self._local_vars[var_name] = ordered_set.OrderedSet()
        var_type_info = self._local_vars[var_name]
        if type_info is not None:
            var_type_info.add(type_info)

    def add_type_info(self):
        if len(self.decorator_list) == 0:
            if len(self.args.args) == 0:
                self._kind = FunctionKind.Function
            else:#if len(self.args.args) >= 1:
                first_arg = self.args.args[0].arg
                if first_arg == 'self':
                    if self.name == '__init__':
                        self._kind = FunctionKind.Constructor
                    else:
                        self._kind = FunctionKind.InstanceMethod
                else:
                    self._kind = FunctionKind.Function
        elif len(self.decorator_list) == 1:
            decorator = self.decorator_list[0]
            assert isinstance(decorator, ast_module.Name)
            self._kind = {
                'classmethod': FunctionKind.ClassMethod,
                'staticmethod': FunctionKind.StaticMethod}.get(
                    decorator.id, FunctionKind.Undetermined)
        else:
            raise NotImplementedError('no support for many decorators')
        if self._kind is FunctionKind.Undetermined:
            raise NotImplementedError('could not determine function kind')

        args, vararg, kwonlyargs, kw_defaults, kwarg, defaults = \
            self.args.args, self.args.vararg, self.args.kwonlyargs, self.args.kw_defaults, \
            self.args.kwarg, self.args.defaults
        if vararg or kwonlyargs or kw_defaults or kwarg or defaults:
            raise NotImplementedError('only simple function definitions are supported')
        for i, arg in enumerate(args):
            if i == 0:
                if self._kind in (FunctionKind.Constructor, FunctionKind.InstanceMethod) \
                        and arg.arg == 'self':
                    continue
                if self._kind is FunctionKind.ClassMethod and arg.arg == 'cls':
                    continue
            type_info = ordered_set.OrderedSet()
            if arg.annotation is not None:
                type_info.add(arg.annotation)
            if arg.type_comment is not None:
                type_info.add(arg.type_comment)
            self._params[arg.arg] =  type_info

        results = scan_FunctionDef(self)
        for k, v in results:
            if isinstance(k, ast_module.Name):
                self._add_local_var(k.id, v)

        '''
        for node in ast_module.walk(self):
            if isinstance(node, ast_module.Assign):
                results = scan_Assign(node)
                for k, v in results:
                    if isinstance(k, ast_module.Name):
                        self._add_local_var(k.id, v)
            elif isinstance(node, ast_module.AnnAssign):
                results = scan_AnnAssign(node)
                for k, v in results:
                    if isinstance(k, ast_module.Name):
                        self._add_local_var(k.id, v)
            elif isinstance(node, ast_module.For):
                assert isinstance(node.target, ast_module.Name)
                self._add_local_var(node.target.id, node.type_comment)
                #raise NotImplementedError((node.__class__, dict(typed_ast.ast3.iter_fields(node))))
            #print(node.__class__, dict(typed_ast.ast3.iter_fields(node)))
        '''
        if self.returns is not None:
            self._returns.add(self.returns)

    def _type_info_view(self, indent: int = 0, inline: bool = False):
        if inline:
            return str(self)
        lines = [f'{INDENT_STR * indent}<FunctionDef,{self._kind.name}> {self.name}:']
        lines += [f'{INDENT_STR * (indent + 1)}{len(self._params)} parameters:']
        lines += [
            f'{INDENT_STR * (indent + 2)}{var_name}: {tuple(type_info)}'
            for var_name, type_info in self._params.items()]
        lines += [f'{INDENT_STR * (indent + 1)}{len(self._local_vars)} local vars:']
        lines += [
            f'{INDENT_STR * (indent + 2)}{var_name}: {tuple(type_info)}'
            for var_name, type_info in self._local_vars.items()]
        lines += [f'{INDENT_STR * (indent + 1)}returns: {tuple(self._returns)}']
        return '\n'.join(lines)

    def __str__(self):
        return f'<FunctionDef,{self._kind.name}> {self.name}(...) -> ...:' \
            f' {len(self._local_vars)} local vars'


class StaticallyTypedClassDef(ast_module.ClassDef, StaticallyTyped):

    kind_mapping = {
        FunctionKind.StaticMethod: '_static_methods',
        FunctionKind.ClassMethod: '_class_methods',
        FunctionKind.Constructor: '_instance_methods',
        FunctionKind.InstanceMethod: '_instance_methods'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._class_fields = {}
        self._instance_fields = {}
        self._methods = {}
        self._static_methods = {}
        self._class_methods = {}
        self._instance_methods = {}
        self.add_type_info()

    def _add_var(self, var_place: str, var_name: str, type_info: t.Any, scope: t.Any=None):
        vars_ = getattr(self, var_place)
        if var_name not in vars_:
            vars_[var_name] = ordered_set.OrderedSet()
        var_type_info = vars_[var_name]
        if type_info is not None:
            var_type_info.add(type_info)

    def add_type_info(self):
        for node in self.body:
            if isinstance(node, StaticallyTypedFunctionDef):
                self._methods[node.name] = node
                getattr(self, self.kind_mapping[node._kind])[node.name] = node
                if node._kind is FunctionKind.Constructor:
                    results = scan_FunctionDef(node)
                    for k, v in results:
                        if isinstance(k, ast_module.Attribute):
                            if isinstance(k.value, ast_module.Name) and k.value.id == 'self':
                                self._add_var('_instance_fields', k.attr, v)
            elif isinstance(node, ast_module.FunctionDef):
                raise NotImplementedError(node.name)
                #if node.decorator_list:
                #    self.class_methods
                #self.instance_methods node.
                #node.
            elif isinstance(node, ast_module.Assign):
                results = scan_Assign(node)
                for k, v in results:
                    if isinstance(k, ast_module.Name):
                        self._add_var('_class_fields', k.id, v)
            #elif isinstance(node, ast_module.AnnAssign):
            #    results = scan_AnnAssign(node)
            #    for k, v in results.items():
            #        self._add_var('_class_fields', k, v)

    def _type_info_view(self, indent: int = 0, inline: bool = False):
        if inline:
            return str(self)
        lines = [f'{INDENT_STR * indent}<ClassDef> {self.name}:']
        lines += [f'{INDENT_STR * (indent + 1)}{len(self._class_fields)} class fields:']
        lines += [
            f'{INDENT_STR * (indent + 2)}{var_name}: {tuple(type_info)}'
            for var_name, type_info in self._class_fields.items()]
        lines += [f'{INDENT_STR * (indent + 1)}{len(self._instance_fields)} instance fields:']
        lines += [
            f'{INDENT_STR * (indent + 2)}{var_name}: {tuple(type_info)}'
            for var_name, type_info in self._instance_fields.items()]
        lines += [f'{INDENT_STR * (indent + 1)}{len(self._methods)} methods:']
        lines += [_._type_info_view(indent + 2) for __, _ in self._methods.items()]
        return '\n'.join(lines)

    def __str__(self):
        return f'<ClassDef> {self.name}: {len(self._class_fields)} class fields,' \
            f' {len(self._instance_fields)} instance fields, {len(self._methods)} methods'


class StaticallyTypedFor(ast_module.For, StaticallyTyped):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scope_vars = {}
        self.add_type_info()

    def add_type_info(self):
        pass


class StaticallyTypedWhile(ast_module.While, StaticallyTyped):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scope_vars = {}
        self.add_type_info()

    def add_type_info(self):
        pass


class StaticallyTypedIf(ast_module.If, StaticallyTyped):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.if_true_vars = {}
        self.if_false_vars = {}
        self.add_type_info()

    def add_type_info(self):
        pass


class StaticallyTypedWith(ast_module.With, StaticallyTyped):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scope_vars = {}
        self.add_type_info()

    def add_type_info(self):
        pass
