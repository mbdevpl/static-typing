"""Validate nodes and fields in a given AST recursively."""

import ast
import logging
import sys
import typing as t

import typed_ast.ast3

from .recursive_ast_visitor import RecursiveAstVisitor

_LOG = logging.getLogger(__name__)


def create_ast_validator(ast_module):
    """Create an AST validator for an AST module assumed to be compatible with latest AST."""

    if sys.version_info[:2] < (3, 6) and ast_module is ast:
        _LOG.warning('AST validation not supported for Python < 3.6')
        return RecursiveAstVisitor[ast_module]

    class AstValidatorClass(RecursiveAstVisitor[ast_module]):

        """Validate the contents of all nodes in a given AST.

        Assume the following AST:

        module Python
        {
        """

        module_types = (ast_module.Module, ast_module.Interactive, ast_module.Expression)
        """
            mod = Module(stmt* body)
                | Interactive(stmt* body)
                | Expression(expr body)

                -- not really an actual node but useful in Jython's typesystem.
                | Suite(stmt* body)
        """

        statement_types = (
            ast_module.FunctionDef, ast_module.AsyncFunctionDef, ast_module.ClassDef,
            ast_module.Return, ast_module.Delete, ast_module.Assign, ast_module.AugAssign,
            ast_module.AnnAssign, ast_module.For, ast_module.AsyncFor, ast_module.While,
            ast_module.If, ast_module.With, ast_module.AsyncWith, ast_module.Raise, ast_module.Try,
            ast_module.Assert, ast_module.Import, ast_module.ImportFrom, ast_module.Global,
            ast_module.Nonlocal, ast_module.Expr, ast_module.Pass, ast_module.Break,
            ast_module.Continue)
        """
            stmt = FunctionDef(identifier name, arguments args,
                               stmt* body, expr* decorator_list, expr? returns)
                  | AsyncFunctionDef(identifier name, arguments args,
                                     stmt* body, expr* decorator_list, expr? returns)

                  | ClassDef(identifier name,
                     expr* bases,
                     keyword* keywords,
                     stmt* body,
                     expr* decorator_list)
                  | Return(expr? value)

                  | Delete(expr* targets)
                  | Assign(expr* targets, expr value)
                  | AugAssign(expr target, operator op, expr value)
                  -- 'simple' indicates that we annotate simple name without parens
                  | AnnAssign(expr target, expr annotation, expr? value, int simple)

                  -- use 'orelse' because else is a keyword in target languages
                  | For(expr target, expr iter, stmt* body, stmt* orelse)
                  | AsyncFor(expr target, expr iter, stmt* body, stmt* orelse)
                  | While(expr test, stmt* body, stmt* orelse)
                  | If(expr test, stmt* body, stmt* orelse)
                  | With(withitem* items, stmt* body)
                  | AsyncWith(withitem* items, stmt* body)

                  | Raise(expr? exc, expr? cause)
                  | Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
                  | Assert(expr test, expr? msg)

                  | Import(alias* names)
                  | ImportFrom(identifier? module, alias* names, int? level)

                  | Global(identifier* names)
                  | Nonlocal(identifier* names)
                  | Expr(expr value)
                  | Pass | Break | Continue

                  -- XXX Jython will be different
                  -- col_offset is the byte offset in the utf8 string the parser uses
                  attributes (int lineno, int col_offset)

                  -- BoolOp() can use left & right?
        """

        assignment_target_types = (
            ast_module.Attribute, ast_module.Subscript, ast_module.Starred, ast_module.Name,
            ast_module.List, ast_module.Tuple)

        expression_types = (
            ast_module.BoolOp, ast_module.BinOp, ast_module.UnaryOp, ast_module.Lambda,
            ast_module.IfExp, ast_module.Dict, ast_module.Set, ast_module.ListComp,
            ast_module.SetComp, ast_module.DictComp, ast_module.GeneratorExp, ast_module.Await,
            ast_module.Yield, ast_module.YieldFrom, ast_module.Compare, ast_module.Call,
            ast_module.Num, ast_module.Str, ast_module.FormattedValue, ast_module.JoinedStr,
            ast_module.Bytes, ast_module.NameConstant, ast_module.Ellipsis, ast_module.Constant
            ) + assignment_target_types
        """
            expr = BoolOp(boolop op, expr* values)
                 | BinOp(expr left, operator op, expr right)
                 | UnaryOp(unaryop op, expr operand)
                 | Lambda(arguments args, expr body)
                 | IfExp(expr test, expr body, expr orelse)
                 | Dict(expr* keys, expr* values)
                 | Set(expr* elts)
                 | ListComp(expr elt, comprehension* generators)
                 | SetComp(expr elt, comprehension* generators)
                 | DictComp(expr key, expr value, comprehension* generators)
                 | GeneratorExp(expr elt, comprehension* generators)
                 -- the grammar constrains where yield expressions can occur
                 | Await(expr value)
                 | Yield(expr? value)
                 | YieldFrom(expr value)
                 -- need sequences for compare to distinguish between
                 -- x < 4 < 3 and (x < 4) < 3
                 | Compare(expr left, cmpop* ops, expr* comparators)
                 | Call(expr func, expr* args, keyword* keywords)
                 | Num(object n) -- a number as a PyObject.
                 | Str(string s) -- need to specify raw, unicode, etc?
                 | FormattedValue(expr value, int? conversion, expr? format_spec)
                 | JoinedStr(expr* values)
                 | Bytes(bytes s)
                 | NameConstant(singleton value)
                 | Ellipsis
                 | Constant(constant value)

                 -- the following expression can appear in assignment context
                 | Attribute(expr value, identifier attr, expr_context ctx)
                 | Subscript(expr value, slice slice, expr_context ctx)
                 | Starred(expr value, expr_context ctx)
                 | Name(identifier id, expr_context ctx)
                 | List(expr* elts, expr_context ctx)
                 | Tuple(expr* elts, expr_context ctx)

                  -- col_offset is the byte offset in the utf8 string the parser uses
                  attributes (int lineno, int col_offset)
        """

        expression_context_types = (
            ast_module.Load, ast_module.Store, ast_module.Del, ast_module.AugLoad,
            ast_module.AugStore, ast_module.Param)
        """
            expr_context = Load | Store | Del | AugLoad | AugStore | Param
        """

        slice_types = (ast_module.Slice, ast_module.ExtSlice, ast_module.Index)
        """
            slice = Slice(expr? lower, expr? upper, expr? step)
                  | ExtSlice(slice* dims)
                  | Index(expr value)
        """

        boolean_operator_types = (ast_module.And, ast_module.Or)
        """
            boolop = And | Or
        """

        binary_operator_types = (
            ast_module.Add, ast_module.Sub, ast_module.Mult, ast_module.MatMult, ast_module.Div,
            ast_module.Mod, ast_module.Pow, ast_module.LShift, ast_module.RShift, ast_module.BitOr,
            ast_module.BitXor, ast_module.BitAnd, ast_module.FloorDiv)
        """
            operator = Add | Sub | Mult | MatMult | Div | Mod | Pow | LShift
                         | RShift | BitOr | BitXor | BitAnd | FloorDiv
        """

        unary_operator_types = (ast_module.Invert, ast_module.Not, ast_module.UAdd, ast_module.USub)
        """
            unaryop = Invert | Not | UAdd | USub
        """

        comparison_operator_types = (
            ast_module.Eq, ast_module.NotEq, ast_module.Lt, ast_module.LtE, ast_module.Gt,
            ast_module.GtE, ast_module.Is, ast_module.IsNot, ast_module.In, ast_module.NotIn)
        """
            cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn

            comprehension = (expr target, expr iter, expr* ifs, int is_async)

            excepthandler = ExceptHandler(expr? type, identifier? name, stmt* body)
                            attributes (int lineno, int col_offset)

            arguments = (arg* args, arg? vararg, arg* kwonlyargs, expr* kw_defaults,
                         arg? kwarg, expr* defaults)

            arg = (identifier arg, expr? annotation)
                   attributes (int lineno, int col_offset)

            -- keyword arguments supplied to call (NULL identifier for **kwargs)
            keyword = (identifier? arg, expr value)

            -- import name with optional 'as' alias.
            alias = (identifier name, identifier? asname)

            withitem = (expr context_expr, expr? optional_vars)
        }
        """

        def __init__(self, *args, mode: t.Optional[str] = None, **kwargs):
            super().__init__(*args, **kwargs)
            assert mode is None or mode in {'exec', 'single', 'eval'}, mode
            self.mode = mode
            self._working = False

        # def validate_has_field(self, node, field):
        #    assert hasattr(node, field)

        # def validate_is_instance(self, value, type_):
        #    assert isinstance(value, type_)

        def validate_module(self, mod):
            assert isinstance(mod, self.module_types), type(mod)
            if self.mode is not None:
                assert isinstance(mod, {'exec': ast_module.Module, 'single': ast_module.Interactive,
                                        'eval': ast_module.Expression}[self.mode]), type(mod)

        def validate_Module(self, mod):
            assert hasattr(mod, 'body')
            assert isinstance(mod.body, list), type(mod.body)
            assert mod.body
            for stmt in mod.body:
                self.validate_statement(stmt)
            if self.mode is not None:
                assert self.mode == 'exec', self.mode

        def validate_Interactive(self, mod):
            assert hasattr(mod, 'body')
            assert isinstance(mod.body, list), type(mod.body)
            assert mod.body
            for stmt in mod.body:
                self.validate_statement(stmt)
            if self.mode is not None:
                assert self.mode == 'single', self.mode

        def validate_Expression(self, mod):
            assert hasattr(mod, 'body')
            self.validate_expression(mod.body)
            if self.mode is not None:
                assert self.mode == 'eval', self.mode

        def validate_statement(self, stmt):
            assert isinstance(stmt, self.statement_types), type(stmt)

        def validate_FunctionDef(self, fundef):
            assert hasattr(fundef, 'name')
            self.validate_identifier(fundef.name)
            assert hasattr(fundef, 'args')
            assert isinstance(fundef.args, ast_module.arguments), type(fundef.args)
            assert hasattr(fundef, 'body')
            assert isinstance(fundef.body, list), type(fundef.body)
            assert fundef.body
            for stmt in fundef.body:
                self.validate_statement(stmt)
            assert hasattr(fundef, 'decorator_list')
            assert isinstance(fundef.decorator_list, list), type(fundef.decorator_list)
            for decorator in fundef.decorator_list:
                self.validate_expression(decorator)
            assert hasattr(fundef, 'returns')
            if fundef.returns is not None:
                self.validate_expression(fundef.returns)

        def validate_AsyncFunctionDef(self, fundef):  # pylint: disable=invalid-name
            self.validate_FunctionDef(fundef)

        def validate_ClassDef(self, classdef):
            assert hasattr(classdef, 'name')
            self.validate_identifier(classdef.name)
            assert hasattr(classdef, 'bases')
            assert isinstance(classdef.bases, list), type(classdef.bases)
            for base in classdef.bases:
                self.validate_expression(base)
            assert hasattr(classdef, 'keywords')
            assert isinstance(classdef.keywords, list), type(classdef.keywords)
            for keyword in classdef.keywords:
                assert isinstance(keyword, ast_module.keyword)
            assert hasattr(classdef, 'body')
            assert isinstance(classdef.body, list), type(classdef.body)
            assert classdef.body
            for stmt in classdef.body:
                self.validate_statement(stmt)
            assert hasattr(classdef, 'decorator_list')
            assert isinstance(classdef.decorator_list, list), type(classdef.decorator_list)
            for decorator in classdef.decorator_list:
                self.validate_expression(decorator)

        def validate_Return(self, return_):
            assert hasattr(return_, 'value')
            if return_.value is not None:
                self.validate_expression(return_.value)

        def validate_Assign(self, assign):
            assert hasattr(assign, 'targets')
            assert isinstance(assign.targets, list), type(assign.targets)
            assert assign.targets
            for target in assign.targets:
                self.validate_assignment_target(target)
            assert hasattr(assign, 'value')
            self.validate_expression(assign.value)

        def validate_AnnAssign(self, assign):
            assert hasattr(assign, 'target')
            self.validate_assignment_target(assign.target)
            assert hasattr(assign, 'annotation')
            self.validate_expression(assign.annotation)
            assert hasattr(assign, 'value')
            if assign.value is not None:
                self.validate_expression(assign.value)
            assert hasattr(assign, 'simple')
            assert isinstance(assign.simple, int), type(assign.simple)
            assert assign.simple in {0, 1}

        def validate_For(self, for_):
            assert hasattr(for_, 'target')
            self.validate_expression(for_.target)
            assert hasattr(for_, 'iter')
            self.validate_expression(for_.iter)
            assert hasattr(for_, 'body')
            assert isinstance(for_.body, list), type(for_.body)
            assert for_.body
            for stmt in for_.body:
                self.validate_statement(stmt)
            assert hasattr(for_, 'orelse')
            assert isinstance(for_.orelse, list), type(for_.orelse)
            for stmt in for_.orelse:
                self.validate_statement(stmt)

        def validate_AsyncFor(self, for_):
            self.validate_For(for_)

        def validate_If(self, if_):
            assert hasattr(if_, 'test')
            self.validate_expression(if_.test)
            assert hasattr(if_, 'body')
            assert isinstance(if_.body, list), type(if_.body)
            assert if_.body
            for stmt in if_.body:
                self.validate_statement(stmt)
            assert hasattr(if_, 'orelse')
            assert isinstance(if_.orelse, list), type(if_.orelse)
            for stmt in if_.orelse:
                self.validate_statement(stmt)

        def validate_With(self, with_):
            assert hasattr(with_, 'items')
            assert isinstance(with_.items, list), type(with_.items)
            for item in with_.items:
                assert isinstance(item, ast_module.withitem)
            assert hasattr(with_, 'body')
            assert isinstance(with_.body, list), type(with_.body)
            assert with_.body
            for stmt in with_.body:
                self.validate_statement(stmt)

        def validate_AsyncWith(self, with_):
            self.validate_With(with_)

        def validate_Import(self, import_):
            assert hasattr(import_, 'names')
            assert isinstance(import_.names, list), type(import_.names)
            assert import_.names
            for name in import_.names:
                assert isinstance(name, ast_module.alias)

        def validate_Expr(self, expr):
            assert hasattr(expr, 'value')
            self.validate_expression(expr.value)

        def validate_expression(self, expr):
            assert isinstance(expr, self.expression_types), type(expr)

        def validate_BoolOp(self, boolop):
            assert hasattr(boolop, 'op'), vars(boolop)
            self.validate_boolean_operator(boolop.op)
            assert hasattr(boolop, 'values'), vars(boolop)
            assert isinstance(boolop.values, list), type(boolop.values)
            assert boolop.values
            for value in boolop.values:
                self.validate_expression(value)

        def validate_BinOp(self, binop):
            assert hasattr(binop, 'left')
            self.validate_expression(binop.left)
            assert hasattr(binop, 'op')
            self.validate_binary_operator(binop.op)
            assert hasattr(binop, 'right')
            self.validate_expression(binop.right)

        def validate_UnaryOp(self, unop):
            assert hasattr(unop, 'op')
            self.validate_unary_operator(unop.op)
            assert hasattr(unop, 'operand')
            self.validate_expression(unop.operand)

        def validate_Dict(self, dict_):
            assert hasattr(dict_, 'keys')
            assert isinstance(dict_.keys, list), type(dict_.keys)
            for key in dict_.keys:
                self.validate_expression(key)
            assert hasattr(dict_, 'values')
            assert isinstance(dict_.values, list), type(dict_.values)
            for value in dict_.values:
                self.validate_expression(value)
            assert len(dict_.keys) == len(dict_.values), (len(dict_.keys), len(dict_.values))

        def validate_Set(self, set_):
            assert hasattr(set_, 'elts')
            assert isinstance(set_.elts, list), type(set_.elts)
            for elt in set_.elts:
                self.validate_expression(elt)

        def validate_Compare(self, compare):
            assert hasattr(compare, 'left'), vars(compare)
            self.validate_expression(compare.left)
            assert hasattr(compare, 'ops'), vars(compare)
            assert isinstance(compare.ops, list), type(compare.ops)
            assert compare.ops
            for op in compare.ops:
                self.validate_comparison_operator(op)
            assert hasattr(compare, 'comparators'), vars(compare)
            assert isinstance(compare.comparators, list), type(compare.comparators)
            assert compare.comparators
            for comparator in compare.comparators:
                self.validate_expression(comparator)

        def validate_Call(self, call):
            assert hasattr(call, 'func')
            self.validate_expression(call.func)
            assert hasattr(call, 'args')
            assert isinstance(call.args, list), type(call.args)
            for arg in call.args:
                self.validate_expression(arg)
            assert hasattr(call, 'keywords')
            assert isinstance(call.keywords, list), type(call.keywords)
            for keyword in call.keywords:
                assert isinstance(keyword, ast_module.keyword)

        def validate_Num(self, num: ast_module.Num):
            assert hasattr(num, 'n')
            assert isinstance(num.n, (int, float))

        def validate_Str(self, str_: ast_module.Str):
            assert hasattr(str_, 's')
            assert isinstance(str_.s, str)

        def validate_Bytes(self, bytes_: ast_module.Bytes):
            assert hasattr(bytes_, 's')
            assert isinstance(bytes_.s, bytes)

        def validate_NameConstant(self, name_const: ast_module.NameConstant):
            assert hasattr(name_const, 'value')
            # self.validate_singleton(name_const.value)
            assert isinstance(name_const.value, (bool, type(None)))
            assert name_const.value in {True, False, None}

        # def validate_Ellipsis(self, ellipsis: ast_module.Ellipsis):
        #    pass

        # def validate_Constant(self, constant):
        #    assert hasattr(constant, 'value')
        #    # self.validate_constant(constant.value)
        #    raise NotImplementedError()

        def validate_assignment_target(self, target):
            assert isinstance(target, self.assignment_target_types), type(target)

        def validate_Attribute(self, attribute):
            assert hasattr(attribute, 'value'), vars(attribute)
            self.validate_expression(attribute.value)
            assert hasattr(attribute, 'attr'), vars(attribute)
            self.validate_identifier(attribute.attr)
            assert hasattr(attribute, 'ctx'), vars(attribute)
            self.validate_expression_context(attribute.ctx)

        def validate_Subscript(self, subscript):
            assert hasattr(subscript, 'value'), vars(subscript)
            self.validate_expression(subscript.value)
            assert hasattr(subscript, 'slice'), vars(subscript)
            self.validate_slice(subscript.slice)
            assert hasattr(subscript, 'ctx'), vars(subscript)
            self.validate_expression_context(subscript.ctx)

        def validate_Name(self, name: ast_module.Name):
            assert hasattr(name, 'id'), vars(name)
            self.validate_identifier(name.id)
            assert hasattr(name, 'ctx'), vars(name)
            self.validate_expression_context(name.ctx)

        def validate_List(self, list_: ast_module.List):
            assert hasattr(list_, 'elts'), vars(list_)
            assert isinstance(list_.elts, list), type(list_.elts)
            for elt in list_.elts:
                self.validate_expression(elt)
            assert hasattr(list_, 'ctx'), vars(list_)
            self.validate_expression_context(list_.ctx)

        def validate_Tuple(self, tuple_: ast_module.Tuple):
            assert hasattr(tuple_, 'elts'), vars(tuple_)
            assert isinstance(tuple_.elts, list), type(tuple_.elts)
            for elt in tuple_.elts:
                self.validate_expression(elt)
            assert hasattr(tuple_, 'ctx'), vars(tuple_)
            self.validate_expression_context(tuple_.ctx)

        def validate_expression_context(self, ctx):
            assert isinstance(ctx, self.expression_context_types), type(ctx)

        def validate_slice(self, slice_):
            assert isinstance(slice_, self.slice_types), type(slice_)

        def validate_Slice(self, slice_):
            assert hasattr(slice_, 'lower')
            if slice_.lower is not None:
                self.validate_expression(slice_.lower)
            assert hasattr(slice_, 'upper')
            if slice_.upper is not None:
                self.validate_expression(slice_.upper)
            assert hasattr(slice_, 'step')
            if slice_.step is not None:
                self.validate_expression(slice_.step)

        def validate_ExtSlice(self, ext_slice):
            assert hasattr(ext_slice, 'dims'), vars(ext_slice)
            assert isinstance(ext_slice.dims, list), type(ext_slice.dims)
            assert ext_slice.dims
            for dim in ext_slice.dims:
                self.validate_slice(dim)

        def validate_Index(self, index):
            assert hasattr(index, 'value')
            self.validate_expression(index.value)

        def validate_boolean_operator(self, boolop):
            assert isinstance(boolop, self.boolean_operator_types), type(boolop)

        def validate_binary_operator(self, operator):
            assert isinstance(operator, self.binary_operator_types), type(operator)

        def validate_unary_operator(self, unaryop):
            assert isinstance(unaryop, self.unary_operator_types), type(unaryop)

        def validate_comparison_operator(self, cmpop):
            assert isinstance(cmpop, self.comparison_operator_types), type(cmpop)

        def validate_arguments(self, arguments):
            assert hasattr(arguments, 'args')
            assert isinstance(arguments.args, list), type(arguments.args)
            for arg in arguments.args:
                assert isinstance(arg, ast_module.arg)
            assert hasattr(arguments, 'vararg')
            if arguments.vararg is not None:
                assert isinstance(arguments.vararg, ast_module.arg)
            assert hasattr(arguments, 'kwonlyargs')
            assert isinstance(arguments.kwonlyargs, list), type(arguments.kwonlyargs)
            for kwonlyarg in arguments.kwonlyargs:
                assert isinstance(kwonlyarg, ast_module.arg)
            assert hasattr(arguments, 'kw_defaults')
            assert isinstance(arguments.kw_defaults, list), type(arguments.kw_defaults)
            for kw_default in arguments.kw_defaults:
                self.validate_expression(kw_default)
            assert hasattr(arguments, 'kwarg')
            if arguments.kwarg is not None:
                assert isinstance(arguments.kwarg, ast_module.arg)
            assert hasattr(arguments, 'defaults')
            assert isinstance(arguments.defaults, list), type(arguments.defaults)
            for default in arguments.defaults:
                self.validate_expression(default)
            assert hasattr(arguments, 'kwarg')

        def validate_arg(self, arg):
            assert hasattr(arg, 'arg')
            self.validate_identifier(arg.arg)
            assert hasattr(arg, 'annotation')
            if arg.annotation is not None:
                self.validate_expression(arg.annotation)

        def validate_alias(self, alias):
            assert hasattr(alias, 'name')
            self.validate_identifier(alias.name)
            assert hasattr(alias, 'asname'), vars(alias)
            if alias.asname is not None:
                self.validate_identifier(alias.asname)

        def validate_withitem(self, withitem):
            assert hasattr(withitem, 'context_expr')
            self.validate_expression(withitem.context_expr)
            assert hasattr(withitem, 'optional_vars')
            if withitem.optional_vars is not None:
                self.validate_expression(withitem.optional_vars)

        def validate_identifier(self, identifier):
            assert isinstance(identifier, str), type(identifier)
            assert identifier

        def visit_node(self, node):
            """Validate given node."""
            assert isinstance(node, ast_module.AST)

            for type_name in (
                    'Module', 'Interactive', 'Expression',
                    'FunctionDef', 'AsyncFunctionDef', 'ClassDef', 'Return', 'Assign', 'AnnAssign',
                    'For', 'AsyncFor', 'If', 'With', 'AsyncWith', 'Import', 'Expr',
                    # 'Pass', 'Break', 'Continue',
                    'BoolOp', 'BinOp', 'UnaryOp', 'Dict', 'Set',
                    'Call', 'Compare', 'Num', 'Str', 'Bytes', 'NameConstant',
                    # 'Ellipsis', 'Constant',
                    'Attribute', 'Subscript', 'Name', 'List', 'Tuple',
                    'Slice', 'ExtSlice', 'Index',
                    'arguments', 'arg', 'alias', 'withitem'):
                if isinstance(node, getattr(ast_module, type_name)):
                    getattr(self, 'validate_{}'.format(type_name))(node)
                    return

            if isinstance(node, (ast_module.Pass, ast_module.Break, ast_module.Continue)):
                pass
            elif isinstance(node, self.expression_context_types):
                pass
            elif isinstance(node, self.boolean_operator_types):
                pass
            elif isinstance(node, self.binary_operator_types):
                pass
            elif isinstance(node, self.unary_operator_types):
                pass
            elif isinstance(node, self.comparison_operator_types):
                pass
            else:
                _LOG.warning('no validatation available for %s', type(node))
                # raise NotImplementedError()

        def visit(self, node):
            if self._working:
                super().visit(node)
                return
            self._working = True
            self.validate_module(node)
            super().visit(node)
            self._working = False

    return AstValidatorClass


AstValidator = {ast_module: create_ast_validator(ast_module)
                for ast_module in (ast, typed_ast.ast3)}
