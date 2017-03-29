
import ast
import enum
import logging
import typing as t
import warnings

import ordered_set

from ._config import ast_module
#from .ast_transcriber import AstTranscriber

_LOG = logging.getLogger(__name__)


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

    assert isinstance(target, ast_module.Name)
    return [(target.id, type_comment)]


def scan_Assign(node: ast_module.Assign) -> t.Sequence[t.Tuple[str, t.Sequence[type]]]:
    """Scan Assign node."""
    variables = []
    for target in node.targets:
        variables += scan_Assign_target(target, node.type_comment)
    return variables


def scan_AnnAssign(node: ast_module.AnnAssign) -> t.Sequence[t.Tuple[str, t.Sequence[type]]]:
    """Scan AnnAssign node."""
    assert isinstance(node.target, ast_module.Name)
    return [(node.target.id, node.annotation)]

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
    def type_info(self):
        raise NotImplementedError()

    def print_type_info(self):
        print(self)
        for node in ast_module.iter_child_nodes(self):
            if isinstance(node, StaticallyTyped):
                print(node)

    def __str__(self):
        return f'{type(self).__name__}()'

class StaticallyTypedModule(ast_module.Module, StaticallyTyped):

    pass

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
        self._returns = None
        self._kind = FunctionKind.Undetermined
        self._local_vars = {}
        #self.scopes = []
        self.add_type_info()

    @property
    def type_info(self):
        return {k: tuple(v) for k, v in self._local_vars.items()}

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
            elif len(self.args.args) >= 1:
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
            #else:
            #    raise NotImplementedError('no support for many decorators')
        #for node in typed_ast.ast3.iter_child_nodes(self):
        #    print(node.__class__, dict(typed_ast.ast3.iter_fields(node)))
        #print('walk')
        for node in ast_module.walk(self):
            if isinstance(node, ast_module.Assign):
                results = scan_Assign(node)
                for k, v in results:
                    self._add_local_var(k, v)
            elif isinstance(node, ast_module.AnnAssign):
                results = scan_AnnAssign(node)
                for k, v in results:
                    self._add_local_var(k, v)
            elif isinstance(node, ast_module.For):
                assert isinstance(node.target, ast_module.Name)
                self._add_local_var(node.target.id, node.type_comment)
                #raise NotImplementedError((node.__class__, dict(typed_ast.ast3.iter_fields(node))))
            #print(node.__class__, dict(typed_ast.ast3.iter_fields(node)))

    def __str__(self):
        return f'<FunctionDef,{self._kind.name}> {self.name}(...) -> ...: {len(self._local_vars)} local vars'

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

    @property
    def type_info(self):
        return {_ for _ in self._methods}
        #return {_ for _ in self._static_methods} | {_ for _ in self._class_methods} \
        #    | {_ for _ in self._instance_methods}

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
                self._methods[node.name] = node._kind
                getattr(self, self.kind_mapping[node._kind])[node.name] = node
            elif isinstance(node, ast_module.FunctionDef):
                raise NotImplementedError(node.name)
                #if node.decorator_list:
                #    self.class_methods
                #self.instance_methods node.
                #node.
            elif isinstance(node, ast_module.Assign):
                results = scan_Assign(node)
                for k, v in results:
                    self._add_var('_class_fields', k, v)
            #elif isinstance(node, ast_module.AnnAssign):
            #    results = scan_AnnAssign(node)
            #    for k, v in results.items():
            #        self._add_var('_class_fields', k, v)

    def __str__(self):
        return f'<ClassDef> {self.name}: {len(self._class_fields)} class fields, {len(self._instance_fields)} instance fields, {len(self._methods)} methods'

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
