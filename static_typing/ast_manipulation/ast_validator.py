"""Validate nodes and fields in a given AST recursively."""

# pylint: disable=invalid-name

import ast
import itertools
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
        """

        inner_types = (
            ast_module.comprehension, ast_module.excepthandler, ast_module.arguments,
            ast_module.arg, ast_module.keyword, ast_module.alias, ast_module.withitem)
        """
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

        empty_nodes = \
            (ast_module.Pass, ast_module.Break, ast_module.Continue, ast_module.Ellipsis) \
            + expression_context_types + boolean_operator_types + binary_operator_types \
            + unary_operator_types + comparison_operator_types
        """Nodes that have neither fields nor subnodes."""

        def __init__(self, *args, mode: t.Optional[str] = None, **kwargs):
            super().__init__(*args, **kwargs)
            assert mode is None or mode in {'exec', 'single', 'eval', 'strict'}, mode
            self.mode = mode
            self._working = False

        def _validate_items_in(
                self, syntax, field_name: str, item_validator: t.Union[type, callable],
                *, at_least_one: bool = False):
            """Validate all items of a syntax field assumed to be a sequence.

            The item_validator can be either a type (causing isinstance check) or a callable,
            which receives the item as an argument.
            """
            assert isinstance(syntax, ast_module.AST), type(syntax)
            assert isinstance(field_name, str), type(field_name)
            assert field_name
            assert isinstance(item_validator, type) or callable(item_validator), \
                type(item_validator)

            assert hasattr(syntax, field_name), vars(syntax)
            assert isinstance(getattr(syntax, field_name), list), type(getattr(syntax, field_name))
            if at_least_one:
                assert getattr(syntax, field_name)
            for item in getattr(syntax, field_name):
                if isinstance(item_validator, type):
                    assert isinstance(item, item_validator), type(item)
                else:
                    item_validator(item)

        def validate_module(self, mod):
            assert isinstance(mod, self.module_types), type(mod)
            if self.mode is not None and self.mode != 'strict':
                assert isinstance(mod, {'exec': ast_module.Module, 'single': ast_module.Interactive,
                                        'eval': ast_module.Expression}[self.mode]), type(mod)

        def validate_Module(self, mod):
            self._validate_items_in(mod, 'body', self.validate_statement, at_least_one=True)
            if self.mode is not None:
                assert self.mode in {'exec', 'strict'}, self.mode

        def validate_Interactive(self, mod):
            self._validate_items_in(mod, 'body', self.validate_statement, at_least_one=True)
            if self.mode is not None:
                assert self.mode in {'single', 'strict'}, self.mode

        def validate_Expression(self, mod):
            assert hasattr(mod, 'body')
            self.validate_expression(mod.body)
            if self.mode is not None:
                assert self.mode in {'eval', 'strict'}, self.mode

        def validate_statement(self, stmt):
            assert isinstance(stmt, self.statement_types), type(stmt)

        def validate_FunctionDef(self, fundef):
            """FunctionDef

            (identifier name, arguments args, stmt* body, expr* decorator_list, expr? returns)
            """
            assert hasattr(fundef, 'name')
            self.validate_identifier(fundef.name)
            assert hasattr(fundef, 'args')
            assert isinstance(fundef.args, ast_module.arguments), type(fundef.args)
            self._validate_items_in(fundef, 'body', self.validate_statement, at_least_one=True)
            self._validate_items_in(fundef, 'decorator_list', self.validate_expression)
            assert hasattr(fundef, 'returns')
            if fundef.returns is not None:
                self.validate_expression(fundef.returns)

        def validate_AsyncFunctionDef(self, fundef):  # pylint: disable=invalid-name
            self.validate_FunctionDef(fundef)

        def validate_ClassDef(self, classdef):
            """ClassDef

            (identifier name, expr* bases, keyword* keywords, stmt* body, expr* decorator_list)
            """
            assert hasattr(classdef, 'name')
            self.validate_identifier(classdef.name)
            self._validate_items_in(classdef, 'bases', self.validate_expression)
            self._validate_items_in(classdef, 'keywords', ast_module.keyword)
            self._validate_items_in(classdef, 'body', self.validate_statement, at_least_one=True)
            self._validate_items_in(classdef, 'decorator_list', self.validate_expression)

        def validate_Return(self, return_):
            assert hasattr(return_, 'value')
            if return_.value is not None:
                self.validate_expression(return_.value)

        def validate_Delete(self, delete):
            """Delete(expr* targets)"""
            self._validate_items_in(delete, 'targets', self.validate_expression, at_least_one=True)

        def validate_Assign(self, assign):
            self._validate_items_in(
                assign, 'targets', self.validate_assignment_target, at_least_one=True)
            assert hasattr(assign, 'value')
            self.validate_expression(assign.value)

        def validate_AugAssign(self, augassign):
            """AugAssign(expr target, operator op, expr value)"""
            assert hasattr(augassign, 'target')
            self.validate_expression(augassign.target)
            assert hasattr(augassign, 'op')
            self.validate_binary_operator(augassign.op)
            assert hasattr(augassign, 'value')
            self.validate_expression(augassign.value)

        def validate_AnnAssign(self, assign):
            """AnnAssign(expr target, expr annotation, expr? value, int simple)"""
            assert hasattr(assign, 'target')
            self.validate_assignment_target(assign.target)
            assert hasattr(assign, 'annotation')
            self.validate_expression(assign.annotation)
            assert hasattr(assign, 'value')
            if assign.value is not None:
                self.validate_expression(assign.value)
            assert hasattr(assign, 'simple')
            assert isinstance(assign.simple, int), type(assign.simple)
            assert assign.simple in {0, 1}, assign.simple

        def validate_For(self, for_):
            """For(expr target, expr iter, stmt* body, stmt* orelse)"""
            assert hasattr(for_, 'target')
            self.validate_expression(for_.target)
            assert hasattr(for_, 'iter')
            self.validate_expression(for_.iter)
            self._validate_items_in(for_, 'body', self.validate_statement, at_least_one=True)
            self._validate_items_in(for_, 'orelse', self.validate_statement)

        def validate_AsyncFor(self, for_):
            self.validate_For(for_)

        def validate_While(self, while_):
            """While(expr test, stmt* body, stmt* orelse)"""
            assert hasattr(while_, 'test'), vars(while_)
            self.validate_expression(while_.test)
            self._validate_items_in(while_, 'body', self.validate_statement, at_least_one=True)
            self._validate_items_in(while_, 'orelse', self.validate_statement)

        def validate_If(self, if_):
            """If(expr test, stmt* body, stmt* orelse)"""
            self.validate_While(if_)

        def validate_With(self, with_):
            self._validate_items_in(with_, 'items', ast_module.withitem)
            self._validate_items_in(with_, 'body', self.validate_statement, at_least_one=True)

        def validate_AsyncWith(self, with_):
            self.validate_With(with_)

        def validate_Raise(self, raise_):
            """Raise(expr? exc, expr? cause)"""
            assert hasattr(raise_, 'exc'), vars(raise_)
            if raise_.exc is not None:
                self.validate_expression(raise_.exc)
            assert hasattr(raise_, 'cause'), vars(raise_)
            if raise_.cause is not None:
                assert raise_.exc is not None
                self.validate_expression(raise_.cause)

        def validate_Try(self, try_):
            """Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)"""
            self._validate_items_in(try_, 'body', self.validate_statement, at_least_one=True)
            self._validate_items_in(try_, 'handlers', ast_module.excepthandler)
            self._validate_items_in(try_, 'orelse', self.validate_statement)
            self._validate_items_in(try_, 'finalbody', self.validate_statement)
            assert try_.handlers or try_.orelse or try_.finalbody

        def validate_Assert(self, assert_):
            """Assert(expr test, expr? msg)"""
            assert hasattr(assert_, 'test'), vars(assert_)
            self.validate_expression(assert_.test)
            assert hasattr(assert_, 'msg'), vars(assert_)
            if assert_.msg is not None:
                self.validate_expression(assert_.msg)

        def validate_Import(self, import_):
            self._validate_items_in(import_, 'names', ast_module.alias, at_least_one=True)

        def validate_ImportFrom(self, import_from):
            """ImportFrom(identifier? module, alias* names, int? level)"""
            assert hasattr(import_from, 'module'), vars(import_from)
            if import_from.module is not None:
                self.validate_identifier(import_from.module)
            self._validate_items_in(import_from, 'names', ast_module.alias, at_least_one=True)
            assert hasattr(import_from, 'level')
            if import_from.level is not None:
                assert isinstance(import_from.level, int), type(import_from.level)
                assert import_from.level >= 0, import_from.level

        def validate_Global(self, global_):
            """Global(identifier* names)"""
            self._validate_items_in(global_, 'names', self.validate_identifier, at_least_one=True)

        def validate_Nonlocal(self, nonlocal_):
            """Nonlocal(identifier* names)"""
            self._validate_items_in(nonlocal_, 'names', self.validate_identifier, at_least_one=True)

        def validate_Expr(self, expr):
            assert hasattr(expr, 'value')
            self.validate_expression(expr.value)

        def validate_expression(self, expr):
            assert isinstance(expr, self.expression_types), type(expr)

        def validate_BoolOp(self, boolop):
            """BoolOp(boolop op, expr* values)"""
            assert hasattr(boolop, 'op'), vars(boolop)
            self.validate_boolean_operator(boolop.op)
            self._validate_items_in(boolop, 'values', self.validate_expression, at_least_one=True)

        def validate_BinOp(self, binop):
            """BinOp(expr left, operator op, expr right)"""
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

        def validate_Lambda(self, lambda_):
            """Lambda(arguments args, expr body)"""
            assert hasattr(lambda_, 'args'), vars(lambda_)
            assert isinstance(lambda_.args, ast_module.arguments), type(lambda_.args)
            assert hasattr(lambda_, 'body'), vars(lambda_)
            self.validate_expression(lambda_.body)

        def validate_IfExp(self, ifexp):
            """IfExp(expr test, expr body, expr orelse)"""
            assert hasattr(ifexp, 'test')
            self.validate_expression(ifexp.test)
            assert hasattr(ifexp, 'body')
            self.validate_expression(ifexp.body)
            assert hasattr(ifexp, 'orelse')
            self.validate_expression(ifexp.orelse)

        def validate_Dict(self, dict_):
            self._validate_items_in(dict_, 'keys', self.validate_expression)
            self._validate_items_in(dict_, 'values', self.validate_expression)
            assert len(dict_.keys) == len(dict_.values), (len(dict_.keys), len(dict_.values))

        def validate_Set(self, set_):
            self._validate_items_in(set_, 'elts', self.validate_expression)

        def validate_ListComp(self, listcomp):
            """ListComp(expr elt, comprehension* generators)"""
            assert hasattr(listcomp, 'elt'), vars(listcomp)
            self.validate_expression(listcomp.elt)
            self._validate_items_in(
                listcomp, 'generators', ast_module.comprehension, at_least_one=True)

        def validate_SetComp(self, setcomp):
            """SetComp(expr elt, comprehension* generators)"""
            self.validate_ListComp(setcomp)

        def validate_DictComp(self, dictcomp):
            """DictComp(expr key, expr value, comprehension* generators)"""
            assert hasattr(dictcomp, 'key'), vars(dictcomp)
            self.validate_expression(dictcomp.key)
            assert hasattr(dictcomp, 'value'), vars(dictcomp)
            self.validate_expression(dictcomp.value)
            self._validate_items_in(
                dictcomp, 'generators', ast_module.comprehension, at_least_one=True)

        def validate_GeneratorExp(self, generator):
            """GeneratorExp(expr elt, comprehension* generators)"""
            self.validate_ListComp(generator)

        def validate_Await(self, await_):
            """Await(expr value)"""
            assert hasattr(await_, 'value')
            self.validate_expression(await_.value)

        def validate_Yield(self, yield_):
            """Yield(expr? value)"""
            assert hasattr(yield_, 'value')
            if yield_.value is not None:
                self.validate_expression(yield_.value)

        def validate_YieldFrom(self, yield_from):
            """YieldFrom(expr value)"""
            assert hasattr(yield_from, 'value')
            self.validate_expression(yield_from.value)

        def validate_Compare(self, compare):
            """Compare(expr left, cmpop* ops, expr* comparators)"""
            assert hasattr(compare, 'left'), vars(compare)
            self.validate_expression(compare.left)
            self._validate_items_in(
                compare, 'ops', self.validate_comparison_operator, at_least_one=True)
            self._validate_items_in(
                compare, 'comparators', self.validate_expression, at_least_one=True)

        def validate_Call(self, call):
            assert hasattr(call, 'func')
            self.validate_expression(call.func)
            self._validate_items_in(call, 'args', self.validate_expression)
            self._validate_items_in(call, 'keywords', ast_module.keyword)

        def validate_Num(self, num: ast_module.Num):
            assert hasattr(num, 'n')
            assert isinstance(num.n, (int, float)), type(num.n)

        def validate_Str(self, str_: ast_module.Str):
            assert hasattr(str_, 's')
            assert isinstance(str_.s, str), type(str_.s)

        def validate_FormattedValue(self, formatted):
            """FormattedValue(expr value, int? conversion, expr? format_spec)"""
            assert hasattr(formatted, 'value')
            self.validate_expression(formatted.value)
            assert hasattr(formatted, 'conversion')
            if formatted.conversion is not None:
                assert isinstance(formatted.conversion, int)
                assert formatted.conversion in {-1, 97, 114, 115}, formatted.conversion
            assert hasattr(formatted, 'format_spec')
            if formatted.format_spec is not None:
                self.validate_expression(formatted.format_spec)

        def validate_JoinedStr(self, joined):
            """JoinedStr(expr* values)"""
            self._validate_items_in(joined, 'values', self.validate_expression, at_least_one=True)

        def validate_Bytes(self, bytes_: ast_module.Bytes):
            assert hasattr(bytes_, 's')
            assert isinstance(bytes_.s, bytes)

        def validate_NameConstant(self, name_const: ast_module.NameConstant):
            assert hasattr(name_const, 'value')
            assert isinstance(name_const.value, (bool, type(None)))
            assert name_const.value in {True, False, None}, name_const.value

        # def validate_Constant(self, constant):
        #    """Constant(constant value)"""
        #    assert hasattr(constant, 'value')
        #    self.validate_constant(constant.value)

        def validate_assignment_target(self, target):
            assert isinstance(target, self.assignment_target_types), type(target)

        def validate_Attribute(self, attribute):
            """Attribute(expr value, identifier attr, expr_context ctx)"""
            assert hasattr(attribute, 'value'), vars(attribute)
            self.validate_expression(attribute.value)
            assert hasattr(attribute, 'attr'), vars(attribute)
            self.validate_identifier(attribute.attr)
            assert hasattr(attribute, 'ctx'), vars(attribute)
            self.validate_expression_context(attribute.ctx)

        def validate_Subscript(self, subscript):
            """Subscript(expr value, slice slice, expr_context ctx)"""
            assert hasattr(subscript, 'value'), vars(subscript)
            self.validate_expression(subscript.value)
            assert hasattr(subscript, 'slice'), vars(subscript)
            self.validate_slice(subscript.slice)
            assert hasattr(subscript, 'ctx'), vars(subscript)
            self.validate_expression_context(subscript.ctx)

        def validate_Starred(self, starred):
            """Starred(expr value, expr_context ctx)"""
            assert hasattr(starred, 'value'), vars(starred)
            self.validate_expression(starred.value)
            assert hasattr(starred, 'ctx'), vars(starred)
            self.validate_expression_context(starred.ctx)

        def validate_Name(self, name: ast_module.Name):
            assert hasattr(name, 'id'), vars(name)
            self.validate_identifier(name.id)
            assert hasattr(name, 'ctx'), vars(name)
            self.validate_expression_context(name.ctx)

        def validate_List(self, list_: ast_module.List):
            self._validate_items_in(list_, 'elts', self.validate_expression)
            assert hasattr(list_, 'ctx'), vars(list_)
            self.validate_expression_context(list_.ctx)

        def validate_Tuple(self, tuple_: ast_module.Tuple):
            self._validate_items_in(tuple_, 'elts', self.validate_expression)
            assert hasattr(tuple_, 'ctx'), vars(tuple_)
            self.validate_expression_context(tuple_.ctx)

        def validate_expression_context(self, ctx):
            assert isinstance(ctx, self.expression_context_types), type(ctx)

        def validate_slice(self, slice_):
            assert isinstance(slice_, self.slice_types), type(slice_)

        def validate_Slice(self, slice_):
            """Slice(expr? lower, expr? upper, expr? step)"""
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
            self._validate_items_in(ext_slice, 'dims', self.validate_slice, at_least_one=True)

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

        def validate_comprehension(self, comprehension):
            """comprehension = (expr target, expr iter, expr* ifs, int is_async)"""
            assert hasattr(comprehension, 'target')
            self.validate_expression(comprehension.target)
            assert hasattr(comprehension, 'iter')
            self.validate_expression(comprehension.iter)
            self._validate_items_in(comprehension, 'ifs', self.validate_expression)
            assert hasattr(comprehension, 'is_async')
            assert isinstance(comprehension.is_async, int), type(comprehension.is_async)
            assert comprehension.is_async in {0, 1}, comprehension.is_async

        def validate_excepthandler(self, excepthandler):
            """excepthandler = ExceptHandler(expr? type, identifier? name, stmt* body)"""
            assert hasattr(excepthandler, 'type')
            if excepthandler.type is not None:
                self.validate_expression(excepthandler.type)
            assert hasattr(excepthandler, 'name')
            if excepthandler.name is not None:
                self.validate_identifier(excepthandler.name)
            self._validate_items_in(
                excepthandler, 'body', self.validate_statement, at_least_one=True)

        def validate_arguments(self, arguments):
            """arguments =

            (arg* args, arg? vararg, arg* kwonlyargs, expr* kw_defaults, arg? kwarg, expr* defaults)
            """
            self._validate_items_in(arguments, 'args', ast_module.arg)
            assert hasattr(arguments, 'vararg')
            if arguments.vararg is not None:
                assert isinstance(arguments.vararg, ast_module.arg)
            self._validate_items_in(arguments, 'kwonlyargs', ast_module.arg)
            self._validate_items_in(arguments, 'kw_defaults', self.validate_expression)
            assert hasattr(arguments, 'kwarg')
            if arguments.kwarg is not None:
                assert isinstance(arguments.kwarg, ast_module.arg)
            self._validate_items_in(arguments, 'defaults', self.validate_expression)

        def validate_arg(self, arg):
            """arg = (identifier arg, expr? annotation)"""
            assert hasattr(arg, 'arg')
            self.validate_identifier(arg.arg)
            assert hasattr(arg, 'annotation')
            if arg.annotation is not None:
                self.validate_expression(arg.annotation)

        def validate_keyword(self, keyword):
            """keyword = (identifier? arg, expr value)"""
            assert hasattr(keyword, 'arg')
            if keyword.arg is not None:
                self.validate_identifier(keyword.arg)
            assert hasattr(keyword, 'value')
            self.validate_expression(keyword.value)

        def validate_alias(self, alias):
            """alias = (identifier name, identifier? asname)"""
            assert hasattr(alias, 'name')
            self.validate_identifier(alias.name)
            assert hasattr(alias, 'asname'), vars(alias)
            if alias.asname is not None:
                self.validate_identifier(alias.asname)

        def validate_withitem(self, withitem):
            """withitem = (expr context_expr, expr? optional_vars)"""
            assert hasattr(withitem, 'context_expr')
            self.validate_expression(withitem.context_expr)
            assert hasattr(withitem, 'optional_vars')
            if withitem.optional_vars is not None:
                self.validate_expression(withitem.optional_vars)

        def validate_identifier(self, identifier):
            assert isinstance(identifier, str), type(identifier)
            assert identifier

        def visit_node(self, node):
            """Validate just the given node."""
            assert isinstance(node, ast_module.AST), type(node)

            if isinstance(node, self.empty_nodes):
                return

            for node_type in itertools.chain(
                    self.module_types, self.statement_types, self.expression_types,
                    self.slice_types, self.inner_types):
                validator_name = 'validate_{}'.format(node_type.__name__)
                if isinstance(node, node_type) and hasattr(self, validator_name):
                    getattr(self, validator_name)(node)
                    return

            _LOG.warning('no validatation available for %s', type(node))

        def visit(self, node):
            """Entry point of the validator"""
            if self._working:
                super().visit(node)
                return
            self._working = True
            if self.mode is not None:
                self.validate_module(node)
            super().visit(node)
            self._working = False

    return AstValidatorClass


AstValidator = {ast_module: create_ast_validator(ast_module)
                for ast_module in (ast, typed_ast.ast3)}
