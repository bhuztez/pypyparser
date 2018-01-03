from . import misc

class UnacceptableExpressionContext(Exception):

    def __init__(self, node, msg):
        self.node = node
        self.msg = msg

class AST:
    _fields = ()


class mod(AST):
    pass


class Module(mod):
    _fields = ('body',)

    def __init__(self, body):
        self.body = body


class Interactive(mod):
    _fields = ('body',)

    def __init__(self, body):
        self.body = body


class Expression(mod):
    _fields = ('body',)

    def __init__(self, body):
        self.body = body


class Suite(mod):
    _fields = ('body',)

    def __init__(self, body):
        self.body = body


class stmt(AST):
    def __init__(self, lineno, col_offset):
        self.lineno = lineno
        self.col_offset = col_offset

class FunctionDef(stmt):
    _fields = ('name', 'args', 'body', 'decorator_list', 'returns')

    def __init__(self, name, args, body, decorator_list, returns, lineno, col_offset):
        self.name = name
        self.args = args
        self.body = body
        self.decorator_list = decorator_list
        self.returns = returns
        stmt.__init__(self, lineno, col_offset)


class AsyncFunctionDef(stmt):
    _fields = ('name', 'args', 'body', 'decorator_list', 'returns')

    def __init__(self, name, args, body, decorator_list, returns, lineno, col_offset):
        self.name = name
        self.args = args
        self.body = body
        self.decorator_list = decorator_list
        self.returns = returns
        stmt.__init__(self, lineno, col_offset)


class ClassDef(stmt):
    _fields = ('name', 'bases', 'keywords', 'body', 'decorator_list')

    def __init__(self, name, bases, keywords, body, decorator_list, lineno, col_offset):
        self.name = name
        self.bases = bases
        self.keywords = keywords
        self.body = body
        self.decorator_list = decorator_list
        stmt.__init__(self, lineno, col_offset)


class Return(stmt):
    _fields = ('value',)

    def __init__(self, value, lineno, col_offset):
        self.value = value
        stmt.__init__(self, lineno, col_offset)


class Delete(stmt):
    _fields = ('targets',)

    def __init__(self, targets, lineno, col_offset):
        self.targets = targets
        stmt.__init__(self, lineno, col_offset)


class Assign(stmt):
    _fields = ('targets', 'value')

    def __init__(self, targets, value, lineno, col_offset):
        self.targets = targets
        self.value = value
        stmt.__init__(self, lineno, col_offset)


class AugAssign(stmt):
    _fields = ('target', 'op', 'value')

    def __init__(self, target, op, value, lineno, col_offset):
        self.target = target
        self.op = op
        self.value = value
        stmt.__init__(self, lineno, col_offset)


class For(stmt):
    _fields = ('target', 'iter', 'body', 'orelse')

    def __init__(self, target, iter, body, orelse, lineno, col_offset):
        self.target = target
        self.iter = iter
        self.body = body
        self.orelse = orelse
        stmt.__init__(self, lineno, col_offset)


class AsyncFor(stmt):
    _fields = ('target', 'iter', 'body', 'orelse')

    def __init__(self, target, iter, body, orelse, lineno, col_offset):
        self.target = target
        self.iter = iter
        self.body = body
        self.orelse = orelse
        stmt.__init__(self, lineno, col_offset)


class While(stmt):
    _fields = ('test', 'body', 'orelse')

    def __init__(self, test, body, orelse, lineno, col_offset):
        self.test = test
        self.body = body
        self.orelse = orelse
        stmt.__init__(self, lineno, col_offset)


class If(stmt):
    _fields = ('test', 'body', 'orelse')

    def __init__(self, test, body, orelse, lineno, col_offset):
        self.test = test
        self.body = body
        self.orelse = orelse
        stmt.__init__(self, lineno, col_offset)


class With(stmt):
    _fields = ('items', 'body')

    def __init__(self, items, body, lineno, col_offset):
        self.items = items
        self.body = body
        stmt.__init__(self, lineno, col_offset)


class AsyncWith(stmt):
    _fields = ('items', 'body')

    def __init__(self, items, body, lineno, col_offset):
        self.items = items
        self.body = body
        stmt.__init__(self, lineno, col_offset)


class Raise(stmt):
    _fields = ('exc', 'cause')

    def __init__(self, exc, cause, lineno, col_offset):
        self.exc = exc
        self.cause = cause
        stmt.__init__(self, lineno, col_offset)


class Try(stmt):
    _fields = ('body', 'handlers', 'orelse', 'finalbody')

    def __init__(self, body, handlers, orelse, finalbody, lineno, col_offset):
        self.body = body
        self.handlers = handlers
        self.orelse = orelse
        self.finalbody = finalbody
        stmt.__init__(self, lineno, col_offset)


class Assert(stmt):
    _fields = ('test', 'msg')

    def __init__(self, test, msg, lineno, col_offset):
        self.test = test
        self.msg = msg
        stmt.__init__(self, lineno, col_offset)


class Import(stmt):
    _fields = ('names',)

    def __init__(self, names, lineno, col_offset):
        self.names = names
        stmt.__init__(self, lineno, col_offset)


class ImportFrom(stmt):
    _fields = ('module', 'names', 'level')

    def __init__(self, module, names, level, lineno, col_offset):
        self.module = module
        self.names = names
        self.level = level
        stmt.__init__(self, lineno, col_offset)


class Global(stmt):
    _fields = ('names',)

    def __init__(self, names, lineno, col_offset):
        self.names = names
        stmt.__init__(self, lineno, col_offset)


class Nonlocal(stmt):
    _fields = ('names',)

    def __init__(self, names, lineno, col_offset):
        self.names = names
        stmt.__init__(self, lineno, col_offset)


class Expr(stmt):
    _fields = ('value',)

    def __init__(self, value, lineno, col_offset):
        self.value = value
        stmt.__init__(self, lineno, col_offset)


class Pass(stmt):
    def __init__(self, lineno, col_offset):
        stmt.__init__(self, lineno, col_offset)


class Break(stmt):
    def __init__(self, lineno, col_offset):
        stmt.__init__(self, lineno, col_offset)


class Continue(stmt):
    def __init__(self, lineno, col_offset):
        stmt.__init__(self, lineno, col_offset)


class expr(AST):
    _description = None

    def __init__(self, lineno, col_offset):
        self.lineno = lineno
        self.col_offset = col_offset

    def set_context(self, ctx):
        d = self._description
        if d is None:
            d = "%r" % (self,)
        if ctx == Del:
            msg = "can't delete %s" % (d,)
        else:
            msg = "can't assign to %s" % (d,)
        raise UnacceptableExpressionContext(self, msg)


class BoolOp(expr):
    _description = 'operator'
    _fields = ('op', 'values')

    def __init__(self, op, values, lineno, col_offset):
        self.op = op
        self.values = values
        expr.__init__(self, lineno, col_offset)


class BinOp(expr):
    _description = 'operator'
    _fields = ('left', 'op', 'right')

    def __init__(self, left, op, right, lineno, col_offset):
        self.left = left
        self.op = op
        self.right = right
        expr.__init__(self, lineno, col_offset)


class UnaryOp(expr):
    _description = 'operator'
    _fields = ('op', 'operand')

    def __init__(self, op, operand, lineno, col_offset):
        self.op = op
        self.operand = operand
        expr.__init__(self, lineno, col_offset)


class Lambda(expr):
    _description = 'lambda'
    _fields = ('args', 'body')

    def __init__(self, args, body, lineno, col_offset):
        self.args = args
        self.body = body
        expr.__init__(self, lineno, col_offset)


class IfExp(expr):
    _description = 'conditional expression'
    _fields = ('test', 'body', 'orelse')

    def __init__(self, test, body, orelse, lineno, col_offset):
        self.test = test
        self.body = body
        self.orelse = orelse
        expr.__init__(self, lineno, col_offset)


class Dict(expr):
    _description = 'literal'
    _fields = ('keys', 'values')

    def __init__(self, keys, values, lineno, col_offset):
        self.keys = keys
        self.values = values
        expr.__init__(self, lineno, col_offset)


class Set(expr):
    _description = 'literal'
    _fields = ('elts',)

    def __init__(self, elts, lineno, col_offset):
        self.elts = elts
        expr.__init__(self, lineno, col_offset)


class ListComp(expr):
    _description = 'list comprehension'
    _fields = ('elt', 'generators')

    def __init__(self, elt, generators, lineno, col_offset):
        self.elt = elt
        self.generators = generators
        expr.__init__(self, lineno, col_offset)


class SetComp(expr):
    _description = 'set comprehension'
    _fields = ('elt', 'generators')

    def __init__(self, elt, generators, lineno, col_offset):
        self.elt = elt
        self.generators = generators
        expr.__init__(self, lineno, col_offset)


class DictComp(expr):
    _description = 'dict comprehension'
    _fields = ('key', 'value', 'generators')

    def __init__(self, key, value, generators, lineno, col_offset):
        self.key = key
        self.value = value
        self.generators = generators
        expr.__init__(self, lineno, col_offset)


class GeneratorExp(expr):
    _description = 'generator expression'
    _fields = ('elt', 'generators')

    def __init__(self, elt, generators, lineno, col_offset):
        self.elt = elt
        self.generators = generators
        expr.__init__(self, lineno, col_offset)


class Await(expr):
    _fields = ('value',)

    def __init__(self, value, lineno, col_offset):
        self.value = value
        expr.__init__(self, lineno, col_offset)


class Yield(expr):
    _description = 'yield expression'
    _fields = ('value',)

    def __init__(self, value, lineno, col_offset):
        self.value = value
        expr.__init__(self, lineno, col_offset)


class YieldFrom(expr):
    _fields = ('value',)

    def __init__(self, value, lineno, col_offset):
        self.value = value
        expr.__init__(self, lineno, col_offset)


class Compare(expr):
    _description = 'comparison'
    _fields = ('left', 'ops', 'comparators')

    def __init__(self, left, ops, comparators, lineno, col_offset):
        self.left = left
        self.ops = ops
        self.comparators = comparators
        expr.__init__(self, lineno, col_offset)


class Call(expr):
    _description = 'function call'
    _fields = ('func', 'args', 'keywords')

    def __init__(self, func, args, keywords, lineno, col_offset):
        self.func = func
        self.args = args
        self.keywords = keywords
        expr.__init__(self, lineno, col_offset)


class Num(expr):
    _description = 'literal'
    _fields = ('n',)

    def __init__(self, n, lineno, col_offset):
        self.n = n
        expr.__init__(self, lineno, col_offset)


class Str(expr):
    _description = 'literal'
    _fields = ('s',)

    def __init__(self, s, lineno, col_offset):
        self.s = s
        expr.__init__(self, lineno, col_offset)


class FormattedValue(expr):
    _fields = ('value', 'conversion', 'format_spec')

    def __init__(self, value, conversion, format_spec, lineno, col_offset):
        self.value = value
        self.conversion = conversion
        self.format_spec = format_spec
        expr.__init__(self, lineno, col_offset)


class JoinedStr(expr):
    _fields = ('values',)

    def __init__(self, values, lineno, col_offset):
        self.values = values
        expr.__init__(self, lineno, col_offset)


class Bytes(expr):
    _description = 'literal'
    _fields = ('s',)

    def __init__(self, s, lineno, col_offset):
        self.s = s
        expr.__init__(self, lineno, col_offset)


class NameConstant(expr):
    _fields = ('value',)

    def __init__(self, value, lineno, col_offset):
        self.value = value
        expr.__init__(self, lineno, col_offset)


class Ellipsis(expr):
    _description = 'Ellipsis'

    def __init__(self, lineno, col_offset):
        expr.__init__(self, lineno, col_offset)


class Attribute(expr):
    _fields = ('value', 'attr', 'ctx')

    def __init__(self, value, attr, ctx, lineno, col_offset):
        self.value = value
        self.attr = attr
        self.ctx = ctx
        expr.__init__(self, lineno, col_offset)

    def set_context(self, ctx):
        if ctx == Store:
            misc.check_forbidden_name(self.attr, self)
        self.ctx = ctx


class Subscript(expr):
    _fields = ('value', 'slice', 'ctx')

    def __init__(self, value, slice, ctx, lineno, col_offset):
        self.value = value
        self.slice = slice
        self.ctx = ctx
        expr.__init__(self, lineno, col_offset)

    def set_context(self, ctx):
        self.ctx = ctx


class Starred(expr):
    _fields = ('value', 'ctx')

    def __init__(self, value, ctx, lineno, col_offset):
        self.value = value
        self.ctx = ctx
        expr.__init__(self, lineno, col_offset)

    def set_context(self, ctx):
        self.ctx = ctx
        self.value.set_context(ctx)


class Name(expr):
    _fields = ('id', 'ctx')

    def __init__(self, id, ctx, lineno, col_offset):
        self.id = id
        self.ctx = ctx
        expr.__init__(self, lineno, col_offset)

    def set_context(self, ctx):
        if ctx == Store:
            misc.check_forbidden_name(self.id, self)
        self.ctx = ctx


class List(expr):
    _fields = ('elts', 'ctx')

    def __init__(self, elts, ctx, lineno, col_offset):
        self.elts = elts
        self.ctx = ctx
        expr.__init__(self, lineno, col_offset)

    def set_context(self, ctx):
        if self.elts:
            for elt in self.elts:
                elt.set_context(ctx)
        self.ctx = ctx


class Tuple(expr):
    _description = '()'
    _fields = ('elts', 'ctx')

    def __init__(self, elts, ctx, lineno, col_offset):
        self.elts = elts
        self.ctx = ctx
        expr.__init__(self, lineno, col_offset)

    def set_context(self, ctx):
        if self.elts:
            for elt in self.elts:
                elt.set_context(ctx)
            self.ctx = ctx
        else:
            # Assignment to () raises an error.
            expr.set_context(self, ctx)


class Const(expr):
    _fields = ('obj',)

    def __init__(self, obj, lineno, col_offset):
        self.obj = obj
        expr.__init__(self, lineno, col_offset)


class expr_context(AST):
    pass

class Load(expr_context):
    pass


class Store(expr_context):
    pass


class Del(expr_context):
    pass


class AugLoad(expr_context):
    pass


class AugStore(expr_context):
    pass


class Param(expr_context):
    pass


class slice(AST):
    pass

class Slice(slice):
    _fields = ('lower', 'upper', 'step')

    def __init__(self, lower, upper, step):
        self.lower = lower
        self.upper = upper
        self.step = step


class ExtSlice(slice):
    _fields = ('dims',)

    def __init__(self, dims):
        self.dims = dims


class Index(slice):
    _fields = ('value',)

    def __init__(self, value):
        self.value = value


class boolop(AST):
    pass

class And(boolop):
    pass


class Or(boolop):
    pass


class operator(AST):
    pass

class Add(operator):
    pass


class Sub(operator):
    pass


class Mult(operator):
    pass


class MatMult(operator):
    pass


class Div(operator):
    pass


class Mod(operator):
    pass


class Pow(operator):
    pass


class LShift(operator):
    pass


class RShift(operator):
    pass


class BitOr(operator):
    pass


class BitXor(operator):
    pass


class BitAnd(operator):
    pass


class FloorDiv(operator):
    pass


class unaryop(AST):
    pass

class Invert(unaryop):
    pass


class Not(unaryop):
    pass


class UAdd(unaryop):
    pass


class USub(unaryop):
    pass


class cmpop(AST):
    pass

class Eq(cmpop):
    pass


class NotEq(cmpop):
    pass


class Lt(cmpop):
    pass


class LtE(cmpop):
    pass


class Gt(cmpop):
    pass


class GtE(cmpop):
    pass


class Is(cmpop):
    pass


class IsNot(cmpop):
    pass


class In(cmpop):
    pass


class NotIn(cmpop):
    pass


class comprehension(AST):
    _fields = ('target', 'iter', 'ifs')

    def __init__(self, target, iter, ifs):
        self.target = target
        self.iter = iter
        self.ifs = ifs


class excepthandler(AST):
    def __init__(self, lineno, col_offset):
        self.lineno = lineno
        self.col_offset = col_offset

class ExceptHandler(excepthandler):
    _fields = ('type', 'name', 'body')

    def __init__(self, type, name, body, lineno, col_offset):
        self.type = type
        self.name = name
        self.body = body
        excepthandler.__init__(self, lineno, col_offset)


class arguments(AST):
    _fields = ('args', 'vararg', 'kwonlyargs', 'kw_defaults', 'kwarg', 'defaults')

    def __init__(self, args, vararg, kwonlyargs, kw_defaults, kwarg, defaults):
        self.args = args
        self.vararg = vararg
        self.kwonlyargs = kwonlyargs
        self.kw_defaults = kw_defaults
        self.kwarg = kwarg
        self.defaults = defaults


class arg(AST):
    _fields = ('arg', 'annotation')

    def __init__(self, arg, annotation, lineno, col_offset):
        self.arg = arg
        self.annotation = annotation
        self.lineno = lineno
        self.col_offset = col_offset


class keyword(AST):
    _fields = ('arg', 'value')

    def __init__(self, arg, value):
        self.arg = arg
        self.value = value


class alias(AST):
    _fields = ('name', 'asname')

    def __init__(self, name, asname):
        self.name = name
        self.asname = asname


class withitem(AST):
    _fields = ('context_expr', 'optional_vars')

    def __init__(self, context_expr, optional_vars):
        self.context_expr = context_expr
        self.optional_vars = optional_vars


