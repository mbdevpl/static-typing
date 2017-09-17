
import enum

import ordered_set


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


class FunctionKind(enum.IntEnum):
    Undetermined = 0
    Function = 1
    InstanceMethod = 1 + 2
    Constructor = 1 + 2 + 4
    ClassMethod = 1 + 8
    StaticMethod = 1 + 16
    Method = 1 + 2 + 4 + 8


class StaticallyTypedFunctionDef(ast_module.FunctionDef, StaticallyTyped[ast_module]):

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
            self._params[arg.arg] = type_info

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
