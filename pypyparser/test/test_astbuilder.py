import random
import string
import sys
from .. import pyparse
from ..error import SyntaxError
from ..astbuilder import ast_from_node
from .. import ast, consts
from . import TestCase


class TestAstBuilder(TestCase):


    def get_ast(self, source, p_mode=None, flags=None):
        if p_mode is None:
            p_mode = "exec"
        if flags is None:
            flags = consts.CO_FUTURE_WITH_STATEMENT
        info = pyparse.CompileInfo("<test>", p_mode, flags)
        tree = pyparse.parse_source(source.encode() if isinstance(source, str) else source, info)
        ast_node = ast_from_node(tree, info)
        return ast_node

    def get_first_expr(self, source, p_mode=None, flags=None):
        mod = self.get_ast(source, p_mode, flags)
        self.assertEqual(len(mod.body), 1)
        expr = mod.body[0]
        self.assertIsInstance(expr, ast.Expr)
        return expr.value

    def get_first_stmt(self, source):
        mod = self.get_ast(source)
        self.assertEqual(len(mod.body), 1)
        return mod.body[0]

    def test_top_level(self):
        mod = self.get_ast("hi = 32")
        self.assertIsInstance(mod, ast.Module)
        body = mod.body
        self.assertEqual(len(body), 1)

        mod = self.get_ast("hi", p_mode="eval")
        self.assertIsInstance(mod, ast.Expression)
        self.assertIsInstance(mod.body, ast.expr)

        mod = self.get_ast("x = 23", p_mode="single")
        self.assertIsInstance(mod, ast.Interactive)
        self.assertEqual(len(mod.body), 1)
        mod = self.get_ast("x = 23; y = 23; b = 23", p_mode="single")
        self.assertIsInstance(mod, ast.Interactive)
        self.assertEqual(len(mod.body), 3)
        for stmt in mod.body:
            self.assertIsInstance(stmt, ast.Assign)
        self.assertEqual(mod.body[-1].targets[0].id, "b")

        mod = self.get_ast("x = 23; y = 23; b = 23")
        self.assertIsInstance(mod, ast.Module)
        self.assertEqual(len(mod.body), 3)
        for stmt in mod.body:
            self.assertIsInstance(stmt, ast.Assign)

    def test_del(self):
        d = self.get_first_stmt("del x")
        self.assertIsInstance(d, ast.Delete)
        self.assertEqual(len(d.targets), 1)
        self.assertIsInstance(d.targets[0], ast.Name)
        self.assertEqual(d.targets[0].ctx, ast.Del)
        d = self.get_first_stmt("del x, y")
        self.assertEqual(len(d.targets), 2)
        self.assertEqual(d.targets[0].ctx, ast.Del)
        self.assertEqual(d.targets[1].ctx, ast.Del)
        d = self.get_first_stmt("del x.y")
        self.assertEqual(len(d.targets), 1)
        attr = d.targets[0]
        self.assertIsInstance(attr, ast.Attribute)
        self.assertEqual(attr.ctx, ast.Del)
        d = self.get_first_stmt("del x[:]")
        self.assertEqual(len(d.targets), 1)
        sub = d.targets[0]
        self.assertIsInstance(sub, ast.Subscript)
        self.assertEqual(sub.ctx, ast.Del)

    def test_break(self):
        br = self.get_first_stmt("while True: break").body[0]
        self.assertIsInstance(br, ast.Break)

    def test_continue(self):
        cont = self.get_first_stmt("while True: continue").body[0]
        self.assertIsInstance(cont, ast.Continue)

    def test_return(self):
        ret = self.get_first_stmt("def f(): return").body[0]
        self.assertIsInstance(ret, ast.Return)
        self.assertIsNone(ret.value)
        ret = self.get_first_stmt("def f(): return x").body[0]
        self.assertIsInstance(ret.value, ast.Name)

    def test_raise(self):
        ra = self.get_first_stmt("raise")
        self.assertIsNone(ra.exc)
        self.assertIsNone(ra.cause)
        ra = self.get_first_stmt("raise x")
        self.assertIsInstance(ra.exc, ast.Name)
        self.assertIsNone(ra.cause)
        ra = self.get_first_stmt("raise x from 3")
        self.assertIsInstance(ra.exc, ast.Name)
        self.assertIsInstance(ra.cause, ast.Num)

    def test_import(self):
        im = self.get_first_stmt("import x")
        self.assertIsInstance(im, ast.Import)
        self.assertEqual(len(im.names), 1)
        alias = im.names[0]
        self.assertIsInstance(alias, ast.alias)
        self.assertEqual(alias.name, "x")
        self.assertIsNone(alias.asname)
        im = self.get_first_stmt("import x.y")
        self.assertEqual(len(im.names), 1)
        alias = im.names[0]
        self.assertEqual(alias.name, "x.y")
        self.assertIsNone(alias.asname)
        im = self.get_first_stmt("import x as y")
        self.assertEqual(len(im.names), 1)
        alias = im.names[0]
        self.assertEqual(alias.name, "x")
        self.assertEqual(alias.asname, "y")
        im = self.get_first_stmt("import x, y as w")
        self.assertEqual(len(im.names), 2)
        a1, a2 = im.names
        self.assertEqual(a1.name, "x")
        self.assertIsNone(a1.asname)
        self.assertEqual(a2.name, "y")
        self.assertEqual(a2.asname, "w")
        exc = self.assertRaises(SyntaxError, self.get_ast, "import x a b")

    def test_from_import(self):
        im = self.get_first_stmt("from x import y")
        self.assertIsInstance(im, ast.ImportFrom)
        self.assertEqual(im.module, "x")
        self.assertEqual(im.level, 0)
        self.assertEqual(len(im.names), 1)
        a = im.names[0]
        self.assertIsInstance(a, ast.alias)
        self.assertEqual(a.name, "y")
        self.assertIsNone(a.asname)
        im = self.get_first_stmt("from . import y")
        self.assertEqual(im.level, 1)
        self.assertIsNone(im.module)
        im = self.get_first_stmt("from ... import y")
        self.assertEqual(im.level, 3)
        self.assertIsNone(im.module)
        im = self.get_first_stmt("from .x import y")
        self.assertEqual(im.level, 1)
        self.assertEqual(im.module, "x")
        im = self.get_first_stmt("from ..x.y import m")
        self.assertEqual(im.level, 2)
        self.assertEqual(im.module, "x.y")
        im = self.get_first_stmt("from x import *")
        self.assertEqual(len(im.names), 1)
        a = im.names[0]
        self.assertEqual(a.name, "*")
        self.assertIsNone(a.asname)
        for input in ("from x import x, y", "from x import (x, y)"):
            im = self.get_first_stmt(input)
            self.assertEqual(len(im.names), 2)
            a1, a2 = im.names
            self.assertEqual(a1.name, "x")
            self.assertIsNone(a1.asname)
            self.assertEqual(a2.name, "y")
            self.assertIsNone(a2.asname)
        for input in ("from x import a as b, w", "from x import (a as b, w)"):
            im = self.get_first_stmt(input)
            self.assertEqual(len(im.names), 2)
            a1, a2 = im.names
            self.assertEqual(a1.name, "a")
            self.assertEqual(a1.asname, "b")
            self.assertEqual(a2.name, "w")
            self.assertIsNone(a2.asname)
        input = "from x import y a b"
        exc = self.assertRaises(SyntaxError, self.get_ast, input)
        input = "from x import a, b,"
        exc = self.assertRaises(SyntaxError, self.get_ast, input)
        self.assertEqual(exc.msg,
                         "trailing comma is only allowed with surronding "
                         "parenthesis")

    def test_global(self):
        glob = self.get_first_stmt("global x")
        self.assertIsInstance(glob, ast.Global)
        self.assertEqual(glob.names, ["x"])
        glob = self.get_first_stmt("global x, y")
        self.assertEqual(glob.names, ["x", "y"])

    def test_nonlocal(self):
        nonloc = self.get_first_stmt("nonlocal x")
        self.assertIsInstance(nonloc, ast.Nonlocal)
        self.assertEqual(nonloc.names, ["x"])
        nonloc = self.get_first_stmt("nonlocal x, y")
        self.assertEqual(nonloc.names, ["x", "y"])

    def test_assert(self):
        asrt = self.get_first_stmt("assert x")
        self.assertIsInstance(asrt, ast.Assert)
        self.assertIsInstance(asrt.test, ast.Name)
        self.assertIsNone(asrt.msg)
        asrt = self.get_first_stmt("assert x, 'hi'")
        self.assertIsInstance(asrt.test, ast.Name)
        self.assertIsInstance(asrt.msg, ast.Str)

    def test_suite(self):
        suite = self.get_first_stmt("while x: n;").body
        self.assertEqual(len(suite), 1)
        self.assertIsInstance(suite[0].value, ast.Name)
        suite = self.get_first_stmt("while x: n").body
        self.assertEqual(len(suite), 1)
        suite = self.get_first_stmt("while x: \n    n;").body
        self.assertEqual(len(suite), 1)
        suite = self.get_first_stmt("while x: n;").body
        self.assertEqual(len(suite), 1)
        suite = self.get_first_stmt("while x:\n    n; f;").body
        self.assertEqual(len(suite), 2)

    def test_if(self):
        if_ = self.get_first_stmt("if x: 4")
        self.assertIsInstance(if_, ast.If)
        self.assertIsInstance(if_.test, ast.Name)
        self.assertEqual(if_.test.ctx, ast.Load)
        self.assertEqual(len(if_.body), 1)
        self.assertIsInstance(if_.body[0].value, ast.Num)
        self.assertIsNone(if_.orelse)
        if_ = self.get_first_stmt("if x: 4\nelse: 'hi'")
        self.assertIsInstance(if_.test, ast.Name)
        self.assertEqual(len(if_.body), 1)
        self.assertIsInstance(if_.body[0].value, ast.Num)
        self.assertEqual(len(if_.orelse), 1)
        self.assertIsInstance(if_.orelse[0].value, ast.Str)
        if_ = self.get_first_stmt("if x: 3\nelif 'hi': pass")
        self.assertIsInstance(if_.test, ast.Name)
        self.assertEqual(len(if_.orelse), 1)
        sub_if = if_.orelse[0]
        self.assertIsInstance(sub_if, ast.If)
        self.assertIsInstance(sub_if.test, ast.Str)
        self.assertIsNone(sub_if.orelse)
        if_ = self.get_first_stmt("if x: pass\nelif 'hi': 3\nelse: ()")
        self.assertIsInstance(if_.test, ast.Name)
        self.assertEqual(len(if_.body), 1)
        self.assertIsInstance(if_.body[0], ast.Pass)
        self.assertEqual(len(if_.orelse), 1)
        sub_if = if_.orelse[0]
        self.assertIsInstance(sub_if, ast.If)
        self.assertIsInstance(sub_if.test, ast.Str)
        self.assertEqual(len(sub_if.body), 1)
        self.assertIsInstance(sub_if.body[0].value, ast.Num)
        self.assertEqual(len(sub_if.orelse), 1)
        self.assertIsInstance(sub_if.orelse[0].value, ast.Tuple)

    def test_while(self):
        wh = self.get_first_stmt("while x: pass")
        self.assertIsInstance(wh, ast.While)
        self.assertIsInstance(wh.test, ast.Name)
        self.assertEqual(wh.test.ctx, ast.Load)
        self.assertEqual(len(wh.body), 1)
        self.assertIsInstance(wh.body[0], ast.Pass)
        self.assertIsNone(wh.orelse)
        wh = self.get_first_stmt("while x: pass\nelse: 4")
        self.assertIsInstance(wh.test, ast.Name)
        self.assertEqual(len(wh.body), 1)
        self.assertIsInstance(wh.body[0], ast.Pass)
        self.assertEqual(len(wh.orelse), 1)
        self.assertIsInstance(wh.orelse[0].value, ast.Num)

    def test_for(self):
        fr = self.get_first_stmt("for x in y: pass")
        self.assertIsInstance(fr, ast.For)
        self.assertIsInstance(fr.target, ast.Name)
        self.assertEqual(fr.target.ctx, ast.Store)
        self.assertIsInstance(fr.iter, ast.Name)
        self.assertEqual(fr.iter.ctx, ast.Load)
        self.assertEqual(len(fr.body), 1)
        self.assertIsInstance(fr.body[0], ast.Pass)
        self.assertIsNone(fr.orelse)
        fr = self.get_first_stmt("for x, in y: pass")
        tup = fr.target
        self.assertIsInstance(tup, ast.Tuple)
        self.assertEqual(tup.ctx, ast.Store)
        self.assertEqual(len(tup.elts), 1)
        self.assertIsInstance(tup.elts[0], ast.Name)
        self.assertEqual(tup.elts[0].ctx, ast.Store)
        fr = self.get_first_stmt("for x, y in g: pass")
        tup = fr.target
        self.assertIsInstance(tup, ast.Tuple)
        self.assertEqual(tup.ctx, ast.Store)
        self.assertEqual(len(tup.elts), 2)
        for elt in tup.elts:
            self.assertIsInstance(elt, ast.Name)
            self.assertEqual(elt.ctx, ast.Store)
        fr = self.get_first_stmt("for x in g: pass\nelse: 4")
        self.assertEqual(len(fr.body), 1)
        self.assertIsInstance(fr.body[0], ast.Pass)
        self.assertEqual(len(fr.orelse), 1)
        self.assertIsInstance(fr.orelse[0].value, ast.Num)

    def test_try(self):
        tr = self.get_first_stmt("try: x" + "\n" +
                                 "finally: pass")
        self.assertIsInstance(tr, ast.Try)
        self.assertEqual(len(tr.body), 1)
        self.assertIsInstance(tr.body[0].value, ast.Name)
        self.assertEqual(len(tr.finalbody), 1)
        self.assertIsInstance(tr.finalbody[0], ast.Pass)
        self.assertIsNone(tr.orelse)
        tr = self.get_first_stmt("try: x" + "\n" +
                                 "except: pass")
        self.assertIsInstance(tr, ast.Try)
        self.assertEqual(len(tr.body), 1)
        self.assertIsInstance(tr.body[0].value, ast.Name)
        self.assertEqual(len(tr.handlers), 1)
        handler = tr.handlers[0]
        self.assertIsInstance(handler, ast.excepthandler)
        self.assertIsNone(handler.type)
        self.assertIsNone(handler.name)
        self.assertEqual(len(handler.body), 1)
        self.assertIsInstance(handler.body[0], ast.Pass)
        self.assertIsNone(tr.orelse)
        self.assertIsNone(tr.finalbody)
        tr = self.get_first_stmt("try: x" + "\n" +
                                 "except Exception: pass")
        self.assertEqual(len(tr.handlers), 1)
        handler = tr.handlers[0]
        self.assertIsInstance(handler.type, ast.Name)
        self.assertEqual(handler.type.ctx, ast.Load)
        self.assertIsNone(handler.name)
        self.assertEqual(len(handler.body), 1)
        self.assertIsNone(tr.orelse)
        tr = self.get_first_stmt("try: x" + "\n" +
                                 "except Exception as e: pass")
        self.assertEqual(len(tr.handlers), 1)
        handler = tr.handlers[0]
        self.assertIsInstance(handler.type, ast.Name)
        self.assertEqual(handler.type.id, "Exception")
        self.assertEqual(handler.name, "e")
        self.assertEqual(len(handler.body), 1)
        tr = self.get_first_stmt("try: x" + "\n" +
                                 "except: pass" + "\n" +
                                 "else: 4")
        self.assertEqual(len(tr.body), 1)
        self.assertIsInstance(tr.body[0].value, ast.Name)
        self.assertEqual(len(tr.handlers), 1)
        self.assertIsInstance(tr.handlers[0].body[0], ast.Pass)
        self.assertEqual(len(tr.orelse), 1)
        self.assertIsInstance(tr.orelse[0].value, ast.Num)
        tr = self.get_first_stmt("try: x" + "\n" +
                                 "except Exc as a: 5" + "\n" +
                                 "except F: pass")
        self.assertEqual(len(tr.handlers), 2)
        h1, h2 = tr.handlers
        self.assertIsInstance(h1.type, ast.Name)
        self.assertEqual(h1.name, "a")
        self.assertIsInstance(h1.body[0].value, ast.Num)
        self.assertIsInstance(h2.type, ast.Name)
        self.assertIsNone(h2.name)
        self.assertIsInstance(h2.body[0], ast.Pass)
        tr = self.get_first_stmt("try: x" + "\n" +
                                 "except Exc as a: 5" + "\n" +
                                 "except F: pass")
        self.assertEqual(len(tr.handlers), 2)
        h1, h2 = tr.handlers
        self.assertIsInstance(h1.type, ast.Name)
        self.assertEqual(h1.name, "a")
        self.assertIsInstance(h1.body[0].value, ast.Num)
        self.assertIsInstance(h2.type, ast.Name)
        self.assertIsNone(h2.name)
        self.assertIsInstance(h2.body[0], ast.Pass)
        tr = self.get_first_stmt("try: x" + "\n" +
                                 "except: 4" + "\n" +
                                 "finally: pass")
        self.assertIsInstance(tr, ast.Try)
        self.assertEqual(len(tr.finalbody), 1)
        self.assertIsInstance(tr.finalbody[0], ast.Pass)
        self.assertEqual(len(tr.handlers), 1)
        self.assertEqual(len(tr.handlers[0].body), 1)
        self.assertIsInstance(tr.handlers[0].body[0].value, ast.Num)
        self.assertEqual(len(tr.body), 1)
        self.assertIsInstance(tr.body[0].value, ast.Name)
        tr = self.get_first_stmt("try: x" + "\n" +
                                 "except: 4" + "\n" +
                                 "else: 'hi'" + "\n" +
                                 "finally: pass")
        self.assertIsInstance(tr, ast.Try)
        self.assertEqual(len(tr.finalbody), 1)
        self.assertIsInstance(tr.finalbody[0], ast.Pass)
        self.assertEqual(len(tr.body), 1)
        self.assertEqual(len(tr.orelse), 1)
        self.assertIsInstance(tr.orelse[0].value, ast.Str)
        self.assertEqual(len(tr.body), 1)
        self.assertIsInstance(tr.body[0].value, ast.Name)
        self.assertEqual(len(tr.handlers), 1)

    def test_with(self):
        wi = self.get_first_stmt("with x: pass")
        self.assertIsInstance(wi, ast.With)
        self.assertEqual(len(wi.items), 1)
        self.assertIsInstance(wi.items[0], ast.withitem)
        self.assertIsInstance(wi.items[0].context_expr, ast.Name)
        self.assertIsNone(wi.items[0].optional_vars)
        self.assertEqual(len(wi.body), 1)
        wi = self.get_first_stmt("with x as y: pass")
        self.assertIsInstance(wi.items[0].context_expr, ast.Name)
        self.assertEqual(len(wi.body), 1)
        self.assertIsInstance(wi.items[0].optional_vars, ast.Name)
        self.assertEqual(wi.items[0].optional_vars.ctx, ast.Store)
        wi = self.get_first_stmt("with x as (y,): pass")
        self.assertIsInstance(wi.items[0].optional_vars, ast.Tuple)
        self.assertEqual(len(wi.items[0].optional_vars.elts), 1)
        self.assertEqual(wi.items[0].optional_vars.ctx, ast.Store)
        self.assertEqual(wi.items[0].optional_vars.elts[0].ctx, ast.Store)
        input = "with x hi y: pass"
        exc = self.assertRaises(SyntaxError, self.get_ast, input)
        wi = self.get_first_stmt("with x as y, b: pass")
        self.assertIsInstance(wi, ast.With)
        self.assertEqual(len(wi.items), 2)
        self.assertIsInstance(wi.items[0].context_expr, ast.Name)
        self.assertEqual(wi.items[0].context_expr.id, "x")
        self.assertIsInstance(wi.items[0].optional_vars, ast.Name)
        self.assertEqual(wi.items[0].optional_vars.id, "y")
        self.assertIsInstance(wi.items[1].context_expr, ast.Name)
        self.assertEqual(wi.items[1].context_expr.id, "b")
        self.assertIsNone(wi.items[1].optional_vars)
        self.assertEqual(len(wi.body), 1)
        self.assertIsInstance(wi.body[0], ast.Pass)

    def test_class(self):
        for input in ("class X: pass", "class X(): pass"):
            cls = self.get_first_stmt(input)
            self.assertIsInstance(cls, ast.ClassDef)
            self.assertEqual(cls.name, "X")
            self.assertEqual(len(cls.body), 1)
            self.assertIsInstance(cls.body[0], ast.Pass)
            self.assertIsNone(cls.bases)
            self.assertIsNone(cls.decorator_list)
        for input in ("class X(Y): pass", "class X(Y,): pass"):
            cls = self.get_first_stmt(input)
            self.assertEqual(len(cls.bases), 1)
            base = cls.bases[0]
            self.assertIsInstance(base, ast.Name)
            self.assertEqual(base.ctx, ast.Load)
            self.assertEqual(base.id, "Y")
            self.assertIsNone(cls.decorator_list)
        cls = self.get_first_stmt("class X(Y, Z): pass")
        self.assertEqual(len(cls.bases), 2)
        for b in cls.bases:
            self.assertIsInstance(b, ast.Name)
            self.assertEqual(b.ctx, ast.Load)

    def test_function(self):
        func = self.get_first_stmt("def f(): pass")
        self.assertIsInstance(func, ast.FunctionDef)
        self.assertEqual(func.name, "f")
        self.assertEqual(len(func.body), 1)
        self.assertIsInstance(func.body[0], ast.Pass)
        self.assertIsNone(func.decorator_list)
        args = func.args
        self.assertIsInstance(args, ast.arguments)
        self.assertIsNone(args.args)
        self.assertIsNone(args.defaults)
        self.assertIsNone(args.kwarg)
        self.assertIsNone(args.vararg)
        self.assertIsNone(func.returns)
        args = self.get_first_stmt("def f(a, b): pass").args
        self.assertEqual(len(args.args), 2)
        a1, a2 = args.args
        self.assertIsInstance(a1, ast.arg)
        self.assertEqual(a1.arg, "a")
        self.assertIsInstance(a2, ast.arg)
        self.assertEqual(a2.arg, "b")
        self.assertIsNone(args.vararg)
        self.assertIsNone(args.kwarg)
        args = self.get_first_stmt("def f(a=b): pass").args
        self.assertEqual(len(args.args), 1)
        arg = args.args[0]
        self.assertIsInstance(arg, ast.arg)
        self.assertEqual(arg.arg, "a")
        self.assertEqual(len(args.defaults), 1)
        default = args.defaults[0]
        self.assertIsInstance(default, ast.Name)
        self.assertEqual(default.id, "b")
        self.assertEqual(default.ctx, ast.Load)
        args = self.get_first_stmt("def f(*a): pass").args
        self.assertFalse(args.args)
        self.assertFalse(args.defaults)
        self.assertIsNone(args.kwarg)
        self.assertEqual(args.vararg.arg, "a")
        args = self.get_first_stmt("def f(**a): pass").args
        self.assertFalse(args.args)
        self.assertFalse(args.defaults)
        self.assertIsNone(args.vararg)
        self.assertEqual(args.kwarg.arg, "a")
        args = self.get_first_stmt("def f(a, b, c=d, *e, **f): pass").args
        self.assertEqual(len(args.args), 3)
        for arg in args.args:
            self.assertIsInstance(arg, ast.arg)
        self.assertEqual(len(args.defaults), 1)
        self.assertIsInstance(args.defaults[0], ast.Name)
        self.assertEqual(args.defaults[0].ctx, ast.Load)
        self.assertEqual(args.vararg.arg, "e")
        self.assertEqual(args.kwarg.arg, "f")
        input = "def f(a=b, c): pass"
        exc = self.assertRaises(SyntaxError, self.get_ast, input)
        self.assertEqual(exc.msg, "non-default argument follows default argument")

    def test_kwonly_arguments(self):
        fn = self.get_first_stmt("def f(a, b, c, *, kwarg): pass")
        self.assertIsInstance(fn, ast.FunctionDef)
        self.assertEqual(len(fn.args.kwonlyargs), 1)
        self.assertIsInstance(fn.args.kwonlyargs[0], ast.arg)
        self.assertEqual(fn.args.kwonlyargs[0].arg, "kwarg")
        self.assertEqual(fn.args.kw_defaults, [None])
        fn = self.get_first_stmt("def f(a, b, c, *args, kwarg): pass")
        self.assertIsInstance(fn, ast.FunctionDef)
        self.assertEqual(len(fn.args.kwonlyargs), 1)
        self.assertIsInstance(fn.args.kwonlyargs[0], ast.arg)
        self.assertEqual(fn.args.kwonlyargs[0].arg, "kwarg")
        self.assertEqual(fn.args.kw_defaults, [None])
        fn = self.get_first_stmt("def f(a, b, c, *, kwarg=2): pass")
        self.assertIsInstance(fn, ast.FunctionDef)
        self.assertEqual(len(fn.args.kwonlyargs), 1)
        self.assertIsInstance(fn.args.kwonlyargs[0], ast.arg)
        self.assertEqual(fn.args.kwonlyargs[0].arg, "kwarg")
        self.assertEqual(len(fn.args.kw_defaults), 1)
        self.assertIsInstance(fn.args.kw_defaults[0], ast.Num)
        input = "def f(p1, *, **k1):  pass"
        exc = self.assertRaises(SyntaxError, self.get_ast, input)
        self.assertEqual(exc.msg, "named arguments must follows bare *")

    def test_function_annotation(self):
        func = self.get_first_stmt("def f() -> X: pass")
        self.assertIsInstance(func.returns, ast.Name)
        self.assertEqual(func.returns.id, "X")
        self.assertEqual(func.returns.ctx, ast.Load)
        for stmt in "def f(x : 42): pass", "def f(x : 42=a): pass":
            func = self.get_first_stmt(stmt)
            self.assertIsInstance(func.args.args[0].annotation, ast.Num)
        self.assertIsInstance(func.args.defaults[0], ast.Name)
        func = self.get_first_stmt("def f(*x : 42): pass")
        self.assertIsInstance(func.args.vararg.annotation, ast.Num)
        func = self.get_first_stmt("def f(**kw : 42): pass")
        self.assertIsInstance(func.args.kwarg.annotation, ast.Num)
        func = self.get_first_stmt("def f(*, kw : 42=a): pass")
        self.assertIsInstance(func.args.kwonlyargs[0].annotation, ast.Num)

    def test_lots_of_kwonly_arguments(self):
        fundef = "def f("
        for i in range(255):
            fundef += "i%d, "%i
        fundef += "*, key=100):\n pass\n"
        self.assertRaises(SyntaxError, self.get_first_stmt, fundef)

        fundef2 = "def foo(i,*,"
        for i in range(255):
            fundef2 += "i%d, "%i
        fundef2 += "lastarg):\n  pass\n"
        self.assertRaises(SyntaxError, self.get_first_stmt, fundef)

        fundef3 = "def f(i,*,"
        for i in range(253):
            fundef3 += "i%d, "%i
        fundef3 += "lastarg):\n  pass\n"
        self.get_first_stmt(fundef3)

    def test_decorators(self):
        to_examine = (("def f(): pass", ast.FunctionDef),
                      ("class x: pass", ast.ClassDef))
        for stmt, node in to_examine:
            definition = self.get_first_stmt("@dec\n%s" % (stmt,))
            self.assertIsInstance(definition, node)
            self.assertEqual(len(definition.decorator_list), 1)
            dec = definition.decorator_list[0]
            self.assertIsInstance(dec, ast.Name)
            self.assertEqual(dec.id, "dec")
            self.assertEqual(dec.ctx, ast.Load)
            definition = self.get_first_stmt("@mod.hi.dec\n%s" % (stmt,))
            self.assertEqual(len(definition.decorator_list), 1)
            dec = definition.decorator_list[0]
            self.assertIsInstance(dec, ast.Attribute)
            self.assertEqual(dec.ctx, ast.Load)
            self.assertEqual(dec.attr, "dec")
            self.assertIsInstance(dec.value, ast.Attribute)
            self.assertEqual(dec.value.attr, "hi")
            self.assertIsInstance(dec.value.value, ast.Name)
            self.assertEqual(dec.value.value.id, "mod")
            definition = self.get_first_stmt("@dec\n@dec2\n%s" % (stmt,))
            self.assertEqual(len(definition.decorator_list), 2)
            for dec in definition.decorator_list:
                self.assertIsInstance(dec, ast.Name)
                self.assertEqual(dec.ctx, ast.Load)
            self.assertEqual(definition.decorator_list[0].id, "dec")
            self.assertEqual(definition.decorator_list[1].id, "dec2")
            definition = self.get_first_stmt("@dec()\n%s" % (stmt,))
            self.assertEqual(len(definition.decorator_list), 1)
            dec = definition.decorator_list[0]
            self.assertIsInstance(dec, ast.Call)
            self.assertIsInstance(dec.func, ast.Name)
            self.assertEqual(dec.func.id, "dec")
            self.assertIsNone(dec.args)
            self.assertIsNone(dec.keywords)
            definition = self.get_first_stmt("@dec(a, b)\n%s" % (stmt,))
            self.assertEqual(len(definition.decorator_list), 1)
            dec = definition.decorator_list[0]
            self.assertIsInstance(dec, ast.Call)
            self.assertEqual(dec.func.id, "dec")
            self.assertEqual(len(dec.args), 2)
            self.assertIsNone(dec.keywords)

    def test_augassign(self):
        aug_assigns = (
            ("+=", ast.Add),
            ("-=", ast.Sub),
            ("/=", ast.Div),
            ("//=", ast.FloorDiv),
            ("%=", ast.Mod),
            ("@=", ast.MatMult),
            ("<<=", ast.LShift),
            (">>=", ast.RShift),
            ("&=", ast.BitAnd),
            ("|=", ast.BitOr),
            ("^=", ast.BitXor),
            ("*=", ast.Mult),
            ("**=", ast.Pow)
        )
        for op, ast_type in aug_assigns:
            input = "x %s 4" % (op,)
            assign = self.get_first_stmt(input)
            self.assertIsInstance(assign, ast.AugAssign)
            self.assertIs(assign.op, ast_type)
            self.assertIsInstance(assign.target, ast.Name)
            self.assertEqual(assign.target.ctx, ast.Store)
            self.assertIsInstance(assign.value, ast.Num)

    def test_assign(self):
        assign = self.get_first_stmt("hi = 32")
        self.assertIsInstance(assign, ast.Assign)
        self.assertEqual(len(assign.targets), 1)
        name = assign.targets[0]
        self.assertIsInstance(name, ast.Name)
        self.assertEqual(name.ctx, ast.Store)
        value = assign.value
        self.assertEqual(value.n, 32)
        assign = self.get_first_stmt("hi, = something")
        self.assertEqual(len(assign.targets), 1)
        tup = assign.targets[0]
        self.assertIsInstance(tup, ast.Tuple)
        self.assertEqual(tup.ctx, ast.Store)
        self.assertEqual(len(tup.elts), 1)
        self.assertIsInstance(tup.elts[0], ast.Name)
        self.assertEqual(tup.elts[0].ctx, ast.Store)

    def test_assign_starred(self):
        assign = self.get_first_stmt("*a, b = x")
        self.assertIsInstance(assign, ast.Assign)
        self.assertEqual(len(assign.targets), 1)
        names = assign.targets[0]
        self.assertEqual(len(names.elts), 2)
        self.assertIsInstance(names.elts[0], ast.Starred)
        self.assertIsInstance(names.elts[1], ast.Name)
        self.assertIsInstance(names.elts[0].value, ast.Name)
        self.assertEqual(names.elts[0].value.id, "a")

    def test_name(self):
        name = self.get_first_expr("hi")
        self.assertIsInstance(name, ast.Name)
        self.assertEqual(name.ctx, ast.Load)

    def test_tuple(self):
        tup = self.get_first_expr("()")
        self.assertIsInstance(tup, ast.Tuple)
        self.assertIsNone(tup.elts)
        self.assertEqual(tup.ctx, ast.Load)
        tup = self.get_first_expr("(3,)")
        self.assertEqual(len(tup.elts), 1)
        self.assertEqual(tup.elts[0].n, 3)
        tup = self.get_first_expr("2, 3, 4")
        self.assertEqual(len(tup.elts), 3)

    def test_list(self):
        seq = self.get_first_expr("[]")
        self.assertIsInstance(seq, ast.List)
        self.assertIsNone(seq.elts)
        self.assertEqual(seq.ctx, ast.Load)
        seq = self.get_first_expr("[3,]")
        self.assertEqual(len(seq.elts), 1)
        self.assertEqual(seq.elts[0].n, 3)
        seq = self.get_first_expr("[3]")
        self.assertEqual(len(seq.elts), 1)
        seq = self.get_first_expr("[1, 2, 3, 4, 5]")
        self.assertEqual(len(seq.elts), 5)
        nums = range(1, 6)
        self.assertEqual([n.n for n in seq.elts], list(nums))

    def test_dict(self):
        d = self.get_first_expr("{}")
        self.assertIsInstance(d, ast.Dict)
        self.assertIsNone(d.keys)
        self.assertIsNone(d.values)
        d = self.get_first_expr("{4 : x, y : 7}")
        self.assertTrue(len(d.keys) == len(d.values) == 2)
        key1, key2 = d.keys
        self.assertIsInstance(key1, ast.Num)
        self.assertIsInstance(key2, ast.Name)
        self.assertEqual(key2.ctx, ast.Load)
        v1, v2 = d.values
        self.assertIsInstance(v1, ast.Name)
        self.assertEqual(v1.ctx, ast.Load)
        self.assertIsInstance(v2, ast.Num)

    def test_set(self):
        s = self.get_first_expr("{1}")
        self.assertIsInstance(s, ast.Set)
        self.assertEqual(len(s.elts), 1)
        self.assertIsInstance(s.elts[0], ast.Num)
        self.assertEqual(s.elts[0].n, 1)
        s = self.get_first_expr("{0, 1, 2, 3, 4, 5}")
        self.assertIsInstance(s, ast.Set)
        self.assertEqual(len(s.elts), 6)
        for i, elt in enumerate(s.elts):
            self.assertIsInstance(elt, ast.Num)
            self.assertEqual(elt.n, i)

    def test_set_unpack(self):
        s = self.get_first_expr("{*{1}}")
        self.assertIsInstance(s, ast.Set)
        self.assertEqual(len(s.elts), 1)
        sta0 = s.elts[0]
        self.assertIsInstance(sta0, ast.Starred)
        s0 = sta0.value
        self.assertIsInstance(s0, ast.Set)
        self.assertEqual(len(s0.elts), 1)
        self.assertIsInstance(s0.elts[0], ast.Num)
        self.assertEqual(s0.elts[0].n, 1)
        s = self.get_first_expr("{*{0, 1, 2, 3, 4, 5}}")
        self.assertIsInstance(s, ast.Set)
        self.assertEqual(len(s.elts), 1)
        sta0 = s.elts[0]
        self.assertIsInstance(sta0, ast.Starred)
        s0 = sta0.value
        self.assertIsInstance(s0, ast.Set)
        self.assertEqual(len(s0.elts), 6)
        for i, elt in enumerate(s0.elts):
            self.assertIsInstance(elt, ast.Num)
            self.assertEqual(elt.n, i)

    def test_set_context(self):
        tup = self.get_ast("(a, b) = c").body[0].targets[0]
        self.assertTrue(all(elt.ctx == ast.Store for elt in tup.elts))
        seq = self.get_ast("[a, b] = c").body[0].targets[0]
        self.assertTrue(all(elt.ctx == ast.Store for elt in seq.elts))
        invalid_stores = (
            ("(lambda x: x)", "lambda"),
            ("f()", "function call"),
            ("~x", "operator"),
            ("+x", "operator"),
            ("-x", "operator"),
            ("(x or y)", "operator"),
            ("(x and y)", "operator"),
            ("(not g)", "operator"),
            ("(x for y in g)", "generator expression"),
            ("(yield x)", "yield expression"),
            ("[x for y in g]", "list comprehension"),
            ("{x for x in z}", "set comprehension"),
            ("{x : x for x in z}", "dict comprehension"),
            ("'str'", "literal"),
            ("b'bytes'", "literal"),
            ("()", "()"),
            ("23", "literal"),
            ("{}", "literal"),
            ("{1, 2, 3}", "literal"),
            ("(x > 4)", "comparison"),
            ("(x if y else a)", "conditional expression"),
            ("...", "Ellipsis"),
        )
        test_contexts = (
            ("assign to", "%s = 23"),
            ("delete", "del %s")
        )
        for ctx_type, template in test_contexts:
            for expr, type_str in invalid_stores:
                input = template % (expr,)
                exc = self.assertRaises(SyntaxError, self.get_ast, input)
                self.assertEqual(exc.msg, "can't %s %s" % (ctx_type, type_str))

    def test_assignment_to_forbidden_names(self):
        invalid = (
            "%s = x",
            "%s, x = y",
            "def %s(): pass",
            "class %s(): pass",
            "def f(%s): pass",
            "def f(%s=x): pass",
            "def f(*%s): pass",
            "def f(**%s): pass",
            "f(%s=x)",
            "with x as %s: pass",
            "import %s",
            "import x as %s",
            "from x import %s",
            "from x import y as %s",
            "for %s in x: pass",
        )
        for name in "__debug__",:
            for template in invalid:
                input = template % (name,)
                exc = self.assertRaises(SyntaxError, self.get_ast, input)
                self.assertEqual(exc.msg, "cannot assign to %s" % (name,))

    def test_lambda(self):
        lam = self.get_first_expr("lambda x: expr")
        self.assertIsInstance(lam, ast.Lambda)
        args = lam.args
        self.assertIsInstance(args, ast.arguments)
        self.assertIsNone(args.vararg)
        self.assertIsNone(args.kwarg)
        self.assertFalse(args.defaults)
        self.assertEqual(len(args.args), 1)
        self.assertIsInstance(args.args[0], ast.arg)
        self.assertIsInstance(lam.body, ast.Name)
        lam = self.get_first_expr("lambda: True")
        args = lam.args
        self.assertFalse(args.args)
        lam = self.get_first_expr("lambda x=x: y")
        self.assertEqual(len(lam.args.args), 1)
        self.assertEqual(len(lam.args.defaults), 1)
        self.assertIsInstance(lam.args.defaults[0], ast.Name)
        input = "f(lambda x: x[0] = y)"
        exc = self.assertRaises(SyntaxError, self.get_ast, input)
        self.assertEqual(exc.msg, "lambda cannot contain assignment")

    def test_ifexp(self):
        ifexp = self.get_first_expr("x if y else g")
        self.assertIsInstance(ifexp, ast.IfExp)
        self.assertIsInstance(ifexp.test, ast.Name)
        self.assertEqual(ifexp.test.ctx, ast.Load)
        self.assertIsInstance(ifexp.body, ast.Name)
        self.assertEqual(ifexp.body.ctx, ast.Load)
        self.assertIsInstance(ifexp.orelse, ast.Name)
        self.assertEqual(ifexp.orelse.ctx, ast.Load)

    def test_boolop(self):
        for ast_type, op in ((ast.And, "and"), (ast.Or, "or")):
            bo = self.get_first_expr("x %s a" % (op,))
            self.assertIsInstance(bo, ast.BoolOp)
            self.assertEqual(bo.op, ast_type)
            self.assertEqual(len(bo.values), 2)
            self.assertIsInstance(bo.values[0], ast.Name)
            self.assertIsInstance(bo.values[1], ast.Name)
            bo = self.get_first_expr("x %s a %s b" % (op, op))
            self.assertEqual(bo.op, ast_type)
            self.assertEqual(len(bo.values), 3)

    def test_not(self):
        n = self.get_first_expr("not x")
        self.assertIsInstance(n, ast.UnaryOp)
        self.assertEqual(n.op, ast.Not)
        self.assertIsInstance(n.operand, ast.Name)
        self.assertEqual(n.operand.ctx, ast.Load)

    def test_comparison(self):
        compares = (
            (">", ast.Gt),
            (">=", ast.GtE),
            ("<", ast.Lt),
            ("<=", ast.LtE),
            ("==", ast.Eq),
            ("!=", ast.NotEq),
            ("in", ast.In),
            ("is", ast.Is),
            ("is not", ast.IsNot),
            ("not in", ast.NotIn)
        )
        for op, ast_type in compares:
            comp = self.get_first_expr("x %s y" % (op,))
            self.assertIsInstance(comp, ast.Compare)
            self.assertIsInstance(comp.left, ast.Name)
            self.assertEqual(comp.left.ctx, ast.Load)
            self.assertEqual(len(comp.ops), 1)
            self.assertEqual(comp.ops[0], ast_type)
            self.assertEqual(len(comp.comparators), 1)
            self.assertIsInstance(comp.comparators[0], ast.Name)
            self.assertEqual(comp.comparators[0].ctx, ast.Load)
        # Just for fun let's randomly combine operators. :)
        for j in range(10):
            vars = string.ascii_letters[:random.randint(3, 7)]
            ops = [random.choice(compares) for i in range(len(vars) - 1)]
            input = vars[0]
            for i, (op, _) in enumerate(ops):
                input += " %s %s" % (op, vars[i + 1])
            comp = self.get_first_expr(input)
            self.assertEqual(comp.ops, [tup[1] for tup in ops])
            names = comp.left.id + "".join(n.id for n in comp.comparators)
            self.assertEqual(names, vars)

    def test_flufl(self):
        source = "x <> y"
        self.assertRaises(SyntaxError, self.get_ast, source)
        comp = self.get_first_expr(source,
                                   flags=consts.CO_FUTURE_BARRY_AS_BDFL)
        self.assertIsInstance(comp, ast.Compare)
        self.assertIsInstance(comp.left, ast.Name)
        self.assertEqual(comp.left.ctx, ast.Load)
        self.assertEqual(len(comp.ops), 1)
        self.assertEqual(comp.ops[0], ast.NotEq)
        self.assertEqual(len(comp.comparators), 1)
        self.assertIsInstance(comp.comparators[0], ast.Name)
        self.assertEqual(comp.comparators[0].ctx, ast.Load)

    def test_binop(self):
        binops = (
            ("|", ast.BitOr),
            ("&", ast.BitAnd),
            ("^", ast.BitXor),
            ("<<", ast.LShift),
            (">>", ast.RShift),
            ("+", ast.Add),
            ("-", ast.Sub),
            ("/", ast.Div),
            ("*", ast.Mult),
            ("//", ast.FloorDiv),
            ("%", ast.Mod),
            ("@", ast.MatMult)
        )
        for op, ast_type in binops:
            bin = self.get_first_expr("a %s b" % (op,))
            self.assertIsInstance(bin, ast.BinOp)
            self.assertEqual(bin.op, ast_type)
            self.assertIsInstance(bin.left, ast.Name)
            self.assertIsInstance(bin.right, ast.Name)
            self.assertEqual(bin.left.ctx, ast.Load)
            self.assertEqual(bin.right.ctx, ast.Load)
            bin = self.get_first_expr("a %s b %s c" % (op, op))
            self.assertIsInstance(bin.left, ast.BinOp)
            self.assertEqual(bin.left.op, ast_type)
            self.assertIsInstance(bin.right, ast.Name)

    def test_yield(self):
        expr = self.get_first_expr("yield")
        self.assertIsInstance(expr, ast.Yield)
        self.assertIsNone(expr.value)
        expr = self.get_first_expr("yield x")
        self.assertIsInstance(expr.value, ast.Name)
        assign = self.get_first_stmt("x = yield x")
        self.assertIsInstance(assign, ast.Assign)
        self.assertIsInstance(assign.value, ast.Yield)

    def test_yield_from(self):
        expr = self.get_first_expr("yield from x")
        self.assertIsInstance(expr, ast.YieldFrom)
        self.assertIsInstance(expr.value, ast.Name)

    def test_unaryop(self):
        unary_ops = (
            ("+", ast.UAdd),
            ("-", ast.USub),
            ("~", ast.Invert)
        )
        for op, ast_type in unary_ops:
            unary = self.get_first_expr("%sx" % (op,))
            self.assertIsInstance(unary, ast.UnaryOp)
            self.assertEqual(unary.op, ast_type)
            self.assertIsInstance(unary.operand, ast.Name)
            self.assertEqual(unary.operand.ctx, ast.Load)

    def test_power(self):
        power = self.get_first_expr("x**5")
        self.assertIsInstance(power, ast.BinOp)
        self.assertEqual(power.op, ast.Pow)
        self.assertIsInstance(power.left , ast.Name)
        self.assertEqual(power.left.ctx, ast.Load)
        self.assertIsInstance(power.right, ast.Num)

    def test_call(self):
        call = self.get_first_expr("f()")
        self.assertIsInstance(call, ast.Call)
        self.assertIsNone(call.args)
        self.assertIsNone(call.keywords)
        self.assertIsInstance(call.func, ast.Name)
        self.assertEqual(call.func.ctx, ast.Load)
        call = self.get_first_expr("f(2, 3)")
        self.assertEqual(len(call.args), 2)
        self.assertIsInstance(call.args[0], ast.Num)
        self.assertIsInstance(call.args[1], ast.Num)
        self.assertIsNone(call.keywords)
        call = self.get_first_expr("f(a=3)")
        self.assertIsNone(call.args)
        self.assertEqual(len(call.keywords), 1)
        keyword = call.keywords[0]
        self.assertIsInstance(keyword, ast.keyword)
        self.assertEqual(keyword.arg, "a")
        self.assertIsInstance(keyword.value, ast.Num)
        call = self.get_first_expr("f(*a, **b)")
        self.assertIsInstance(call.args[0], ast.Starred)
        self.assertIsInstance(call.keywords[0], ast.keyword)
        self.assertEqual(call.args[0].value.id, "a")
        self.assertEqual(call.args[0].ctx, ast.Load)
        self.assertEqual(call.keywords[0].value.id, "b")
        call = self.get_first_expr("f(a, b, x=4, *m, **f)")
        self.assertEqual(len(call.args), 3)
        self.assertIsInstance(call.args[0], ast.Name)
        self.assertIsInstance(call.args[1], ast.Name)
        self.assertIsInstance(call.args[2], ast.Starred)
        self.assertEqual(len(call.keywords), 2)
        self.assertEqual(call.keywords[0].arg, "x")
        self.assertEqual(call.args[2].value.id, "m")
        self.assertEqual(call.keywords[1].value.id, "f")
        call = self.get_first_expr("f(x for x in y)")
        self.assertEqual(len(call.args), 1)
        self.assertIsInstance(call.args[0], ast.GeneratorExp)
        input = "f(x for x in y, 1)"
        exc = self.assertRaises(SyntaxError, self.get_ast, input)
        self.assertEqual(exc.msg,
                         "Generator expression must be parenthesized if not "
                         "sole argument")
        many_args = ", ".join("x%i" % i for i in range(256))
        input = "f(%s)" % (many_args,)
        exc = self.assertRaises(SyntaxError, self.get_ast, input)
        self.assertEqual(exc.msg, "more than 255 arguments")
        exc = self.assertRaises(SyntaxError, self.get_ast, "f((a+b)=c)")
        self.assertEqual(exc.msg, "keyword can't be an expression")
        exc = self.assertRaises(SyntaxError, self.get_ast, "f(a=c, a=d)")
        self.assertEqual(exc.msg, "keyword argument repeated")

    def test_attribute(self):
        attr = self.get_first_expr("x.y")
        self.assertIsInstance(attr, ast.Attribute)
        self.assertIsInstance(attr.value, ast.Name)
        self.assertEqual(attr.value.ctx, ast.Load)
        self.assertEqual(attr.attr, "y")
        self.assertEqual(attr.ctx, ast.Load)
        assign = self.get_first_stmt("x.y = 54")
        self.assertIsInstance(assign, ast.Assign)
        self.assertEqual(len(assign.targets), 1)
        attr = assign.targets[0]
        self.assertIsInstance(attr, ast.Attribute)
        self.assertEqual(attr.value.ctx, ast.Load)
        self.assertEqual(attr.ctx, ast.Store)

    def test_subscript_and_slices(self):
        sub = self.get_first_expr("x[y]")
        self.assertIsInstance(sub, ast.Subscript)
        self.assertIsInstance(sub.value, ast.Name)
        self.assertEqual(sub.value.ctx, ast.Load)
        self.assertEqual(sub.ctx, ast.Load)
        self.assertIsInstance(sub.slice, ast.Index)
        self.assertIsInstance(sub.slice.value, ast.Name)
        slc = self.get_first_expr("x[:]").slice
        self.assertIsNone(slc.upper)
        self.assertIsNone(slc.lower)
        self.assertIsNone(slc.step)
        slc = self.get_first_expr("x[::]").slice
        self.assertIsNone(slc.upper)
        self.assertIsNone(slc.lower)
        self.assertIsNone(slc.step)
        slc = self.get_first_expr("x[1:]").slice
        self.assertIsInstance(slc.lower, ast.Num)
        self.assertIsNone(slc.upper)
        self.assertIsNone(slc.step)
        slc = self.get_first_expr("x[1::]").slice
        self.assertIsInstance(slc.lower, ast.Num)
        self.assertIsNone(slc.upper)
        self.assertIsNone(slc.step)
        slc = self.get_first_expr("x[:2]").slice
        self.assertIsNone(slc.lower)
        self.assertIsInstance(slc.upper, ast.Num)
        self.assertIsNone(slc.step)
        slc = self.get_first_expr("x[:2:]").slice
        self.assertIsNone(slc.lower)
        self.assertIsInstance(slc.upper, ast.Num)
        self.assertIsNone(slc.step)
        slc = self.get_first_expr("x[2:2]").slice
        self.assertIsInstance(slc.lower, ast.Num)
        self.assertIsInstance(slc.upper, ast.Num)
        self.assertIsNone(slc.step)
        slc = self.get_first_expr("x[2:2:]").slice
        self.assertIsInstance(slc.lower, ast.Num)
        self.assertIsInstance(slc.upper, ast.Num)
        self.assertIsNone(slc.step)
        slc = self.get_first_expr("x[::2]").slice
        self.assertIsNone(slc.lower)
        self.assertIsNone(slc.upper)
        self.assertIsInstance(slc.step, ast.Num)
        slc = self.get_first_expr("x[2::2]").slice
        self.assertIsInstance(slc.lower, ast.Num)
        self.assertIsNone(slc.upper)
        self.assertIsInstance(slc.step, ast.Num)
        slc = self.get_first_expr("x[:2:2]").slice
        self.assertIsNone(slc.lower)
        self.assertIsInstance(slc.upper, ast.Num)
        self.assertIsInstance(slc.step, ast.Num)
        slc = self.get_first_expr("x[1:2:3]").slice
        for field in (slc.lower, slc.upper, slc.step):
            self.assertIsInstance(field, ast.Num)
        sub = self.get_first_expr("x[1,2,3]")
        slc = sub.slice
        self.assertIsInstance(slc, ast.Index)
        self.assertIsInstance(slc.value, ast.Tuple)
        self.assertEqual(len(slc.value.elts), 3)
        self.assertEqual(slc.value.ctx, ast.Load)
        slc = self.get_first_expr("x[1,3:4]").slice
        self.assertIsInstance(slc, ast.ExtSlice)
        self.assertEqual(len(slc.dims), 2)
        complex_slc = slc.dims[1]
        self.assertIsInstance(complex_slc, ast.Slice)
        self.assertIsInstance(complex_slc.lower, ast.Num)
        self.assertIsInstance(complex_slc.upper, ast.Num)
        self.assertIsNone(complex_slc.step)

    def test_ellipsis(self):
        e = self.get_first_expr("...")
        self.assertIsInstance(e, ast.Ellipsis)
        sub = self.get_first_expr("x[...]")
        self.assertIsInstance(sub.slice.value, ast.Ellipsis)

    def test_bytes(self):
        exc = self.assertRaises(SyntaxError, self.get_first_expr, "b'字符'")
        self.assertEqual(exc.msg, "bytes can only contain ASCII literal characters.")

    def test_string(self):
        s = self.get_first_expr("'hi'")
        self.assertIsInstance(s, ast.Str)
        self.assertEqual(s.s, "hi")
        s = self.get_first_expr("'hi' ' implicitly' ' extra'")
        self.assertIsInstance(s, ast.Str)
        self.assertEqual(s.s, "hi implicitly extra")
        s = self.get_first_expr("b'hi' b' implicitly' b' extra'")
        self.assertIsInstance(s, ast.Bytes)
        self.assertEqual(s.s, b"hi implicitly extra")
        self.assertRaises(SyntaxError, self.get_first_expr, "b'hello' 'world'")
        sentence = u"Die Männer ärgen sich!"
        source = u"# coding: utf-7\nstuff = '%s'" % (sentence,)
        info = pyparse.CompileInfo("<test>", "exec")
        tree = pyparse.parse_source(source.encode("utf-7"), info)
        self.assertEqual(info.encoding, "utf-7")
        s = ast_from_node(tree, info).body[0].value
        self.assertIsInstance(s, ast.Str)
        self.assertEqual(s.s, sentence)

    def test_string_pep3120(self):
        japan = u'日本'
        source = u"foo = '%s'" % japan
        info = pyparse.CompileInfo("<test>", "exec")
        tree = pyparse.parse_source(source.encode("utf-8"), info)
        self.assertEqual(info.encoding, "utf-8")
        s = ast_from_node(tree, info).body[0].value
        self.assertIsInstance(s, ast.Str)
        self.assertEqual(s.s, japan)

    def test_name_pep3131(self):
        assign = self.get_first_stmt("日本 = 32")
        self.assertIsInstance(assign, ast.Assign)
        name = assign.targets[0]
        self.assertIsInstance(name, ast.Name)
        self.assertEqual(name.id, "日本")

    def test_function_pep3131(self):
        fn = self.get_first_stmt("def µ(µ='foo'): pass")
        self.assertIsInstance(fn, ast.FunctionDef)
        # µ normalized to NFKC
        expected = '\u03bc'
        self.assertEqual(fn.name, expected)
        self.assertEqual(fn.args.args[0].arg, expected)

    def test_import_pep3131(self):
        im = self.get_first_stmt("from packageµ import modµ as µ")
        self.assertIsInstance(im, ast.ImportFrom)
        expected = '\u03bc'
        self.assertEqual(im.module, 'package' + expected)
        alias = im.names[0]
        self.assertEqual(alias.name, 'mod' + expected)
        self.assertEqual(alias.asname, expected)

    def test_issue3574(self):
        source = '# coding: Latin-1\nu = "Ç"\n'
        info = pyparse.CompileInfo("<test>", "exec")
        tree = pyparse.parse_source(source.encode("Latin-1"), info)
        self.assertEqual(info.encoding, "iso-8859-1")
        s = ast_from_node(tree, info).body[0].value
        self.assertIsInstance(s, ast.Str)
        self.assertEqual(s.s, 'Ç')

    def test_string_bug(self):
        source = b'# -*- encoding: utf8 -*-\nstuff = "x \xc3\xa9 \\n"\n'
        info = pyparse.CompileInfo("<test>", "exec")
        tree = pyparse.parse_source(source, info)
        self.assertEqual(info.encoding, "utf8")
        s = ast_from_node(tree, info).body[0].value
        self.assertIsInstance(s, ast.Str)
        self.assertEqual(s.s, 'x \xe9 \n')

    def test_number(self):
        def get_num(s):
            node = self.get_first_expr(s)
            self.assertIsInstance(node, ast.Num)
            return node.n
        self.assertEqual(get_num("32"), 32)
        self.assertEqual(get_num("32.5"), 32.5)
        self.assertEqual(get_num("2"), 2)
        self.assertEqual(get_num("13j"), 13j)
        self.assertEqual(get_num("13J"), 13J)
        self.assertEqual(get_num("0o53"), 0o53)
        self.assertEqual(get_num("0o0053"), 0o53)
        for num in ("0x53", "0X53", "0x0000053", "0X00053"):
            self.assertEqual(get_num(num), 0x53)
        self.assertEqual(get_num("0Xb0d2"), 0xb0d2)
        self.assertEqual(get_num("0X53"), 0x53)
        self.assertEqual(get_num("0"), 0)
        self.assertEqual(get_num("00000"), 0)
        for num in ("0o53", "0O53", "0o0000053", "0O00053"):
            self.assertEqual(get_num(num), 0o53)
        for num in ("0b00101", "0B00101", "0b101", "0B101"):
            self.assertEqual(get_num(num), 5)

        self.assertRaises(SyntaxError, self.get_ast, "0x")
        self.assertRaises(SyntaxError, self.get_ast, "0b")
        self.assertRaises(SyntaxError, self.get_ast, "0o")
        self.assertRaises(SyntaxError, self.get_ast, "32L")
        self.assertRaises(SyntaxError, self.get_ast, "32l")
        self.assertRaises(SyntaxError, self.get_ast, "0L")
        self.assertRaises(SyntaxError, self.get_ast, "-0xAAAAAAL")
        self.assertRaises(SyntaxError, self.get_ast, "053")
        self.assertRaises(SyntaxError, self.get_ast, "00053")

    def check_comprehension(self, brackets, ast_type):
        def brack(s):
            return brackets % s
        gen = self.get_first_expr(brack("x for x in y"))
        self.assertIsInstance(gen, ast_type)
        self.assertIsInstance(gen.elt, ast.Name)
        self.assertEqual(gen.elt.ctx, ast.Load)
        self.assertEqual(len(gen.generators), 1)
        comp = gen.generators[0]
        self.assertIsInstance(comp, ast.comprehension)
        self.assertIsNone(comp.ifs)
        self.assertIsInstance(comp.target, ast.Name)
        self.assertIsInstance(comp.iter, ast.Name)
        self.assertEqual(comp.target.ctx, ast.Store)
        gen = self.get_first_expr(brack("x for x in y if w"))
        comp = gen.generators[0]
        self.assertEqual(len(comp.ifs), 1)
        test = comp.ifs[0]
        self.assertIsInstance(test, ast.Name)
        gen = self.get_first_expr(brack("x for x, in y if w"))
        tup = gen.generators[0].target
        self.assertIsInstance(tup, ast.Tuple)
        self.assertEqual(len(tup.elts), 1)
        self.assertEqual(tup.ctx, ast.Store)
        gen = self.get_first_expr(brack("a for w in x for m in p if g"))
        gens = gen.generators
        self.assertEqual(len(gens), 2)
        comp1, comp2 = gens
        self.assertIsNone(comp1.ifs)
        self.assertEqual(len(comp2.ifs), 1)
        self.assertIsInstance(comp2.ifs[0], ast.Name)
        gen = self.get_first_expr(brack("x for x in y if m if g"))
        comps = gen.generators
        self.assertEqual(len(comps), 1)
        self.assertEqual(len(comps[0].ifs), 2)
        if1, if2 = comps[0].ifs
        self.assertIsInstance(if1, ast.Name)
        self.assertIsInstance(if2, ast.Name)
        gen = self.get_first_expr(brack("x for x in y or z"))
        comp = gen.generators[0]
        self.assertIsInstance(comp.iter, ast.BoolOp)
        self.assertEqual(len(comp.iter.values), 2)
        self.assertIsInstance(comp.iter.values[0], ast.Name)
        self.assertIsInstance(comp.iter.values[1], ast.Name)

    def test_genexp(self):
        self.check_comprehension("(%s)", ast.GeneratorExp)

    def test_listcomp(self):
        self.check_comprehension("[%s]", ast.ListComp)

    def test_setcomp(self):
        self.check_comprehension("{%s}", ast.SetComp)

    def test_dictcomp(self):
        gen = self.get_first_expr("{x : z for x in y}")
        self.assertIsInstance(gen, ast.DictComp)
        self.assertIsInstance(gen.key, ast.Name)
        self.assertEqual(gen.key.ctx, ast.Load)
        self.assertIsInstance(gen.value, ast.Name)
        self.assertEqual(gen.value.ctx, ast.Load)
        self.assertEqual(len(gen.generators), 1)
        comp = gen.generators[0]
        self.assertIsInstance(comp, ast.comprehension)
        self.assertIsNone(comp.ifs)
        self.assertIsInstance(comp.target, ast.Name)
        self.assertIsInstance(comp.iter, ast.Name)
        self.assertEqual(comp.target.ctx, ast.Store)
        gen = self.get_first_expr("{x : z for x in y if w}")
        comp = gen.generators[0]
        self.assertEqual(len(comp.ifs), 1)
        test = comp.ifs[0]
        self.assertIsInstance(test, ast.Name)
        gen = self.get_first_expr("{x : z for x, in y if w}")
        tup = gen.generators[0].target
        self.assertIsInstance(tup, ast.Tuple)
        self.assertEqual(len(tup.elts), 1)
        self.assertEqual(tup.ctx, ast.Store)
        gen = self.get_first_expr("{a : b for w in x for m in p if g}")
        gens = gen.generators
        self.assertEqual(len(gens), 2)
        comp1, comp2 = gens
        self.assertIsNone(comp1.ifs)
        self.assertEqual(len(comp2.ifs), 1)
        self.assertIsInstance(comp2.ifs[0], ast.Name)
        gen = self.get_first_expr("{x : z for x in y if m if g}")
        comps = gen.generators
        self.assertEqual(len(comps), 1)
        self.assertEqual(len(comps[0].ifs), 2)
        if1, if2 = comps[0].ifs
        self.assertIsInstance(if1, ast.Name)
        self.assertIsInstance(if2, ast.Name)

    def test_cpython_issue12983(self):
        self.assertRaises(SyntaxError, self.get_ast, r"""b'\x'""")
        self.assertRaises(SyntaxError, self.get_ast, r"""b'\x0'""")

    def test_matmul(self):
        mod = self.get_ast("a @ b")
        self.assertIsInstance(mod, ast.Module)
        body = mod.body
        self.assertEqual(len(body), 1)
        expr = body[0].value
        self.assertEqual(expr.op, ast.MatMult)
        self.assertIsInstance(expr.left, ast.Name)
        self.assertIsInstance(expr.right, ast.Name)
        # imatmul is tested earlier search for @=
    
    def test_asyncFunctionDef(self):
        mod = self.get_ast("async def f():\n await something()")
        self.assertIsInstance(mod, ast.Module)
        self.assertEqual(len(mod.body), 1)
        asyncdef = mod.body[0]
        self.assertIsInstance(asyncdef, ast.AsyncFunctionDef)
        self.assertEqual(asyncdef.name, 'f')
        self.assertEqual(asyncdef.args.args, None)
        self.assertEqual(len(asyncdef.body), 1)
        expr = asyncdef.body[0]
        self.assertIsInstance(expr, ast.Expr)
        exprvalue = expr.value
        self.assertIsInstance(exprvalue, ast.Await)
        awaitvalue = exprvalue.value
        self.assertIsInstance(awaitvalue, ast.Call)
        func = awaitvalue.func
        self.assertIsInstance(func, ast.Name)
        self.assertEqual(func.id, 'something')
        self.assertEqual(func.ctx, ast.Load)
    
    def test_asyncFor(self):
        mod = self.get_ast("async def f():\n async for e in i: 1\n else: 2")
        self.assertIsInstance(mod, ast.Module)
        self.assertEqual(len(mod.body), 1)
        asyncdef = mod.body[0]
        self.assertIsInstance(asyncdef, ast.AsyncFunctionDef)
        self.assertEqual(asyncdef.name, 'f')
        self.assertEqual(asyncdef.args.args, None)
        self.assertEqual(len(asyncdef.body), 1)
        asyncfor = asyncdef.body[0]
        self.assertIsInstance(asyncfor, ast.AsyncFor)
        self.assertIsInstance(asyncfor.target, ast.Name)
        self.assertIsInstance(asyncfor.iter, ast.Name)
        self.assertEqual(len(asyncfor.body), 1)
        self.assertIsInstance(asyncfor.body[0], ast.Expr)
        self.assertIsInstance(asyncfor.body[0].value, ast.Num)
        self.assertEqual(len(asyncfor.orelse), 1)
        self.assertIsInstance(asyncfor.orelse[0], ast.Expr)
        self.assertIsInstance(asyncfor.orelse[0].value, ast.Num)
    
    def test_asyncWith(self):
        mod = self.get_ast("async def f():\n async with a as b: 1")
        self.assertIsInstance(mod, ast.Module)
        self.assertEqual(len(mod.body), 1)
        asyncdef = mod.body[0]
        self.assertIsInstance(asyncdef, ast.AsyncFunctionDef)
        self.assertEqual(asyncdef.name, 'f')
        self.assertEqual(asyncdef.args.args, None)
        self.assertEqual(len(asyncdef.body), 1)
        asyncwith = asyncdef.body[0]
        self.assertIsInstance(asyncwith, ast.AsyncWith)
        self.assertEqual(len(asyncwith.items), 1)
        asyncitem = asyncwith.items[0]
        self.assertIsInstance(asyncitem, ast.withitem)
        self.assertIsInstance(asyncitem.context_expr, ast.Name)
        self.assertIsInstance(asyncitem.optional_vars, ast.Name)
        self.assertEqual(len(asyncwith.body), 1)
        self.assertIsInstance(asyncwith.body[0], ast.Expr)
        self.assertIsInstance(asyncwith.body[0].value, ast.Num)

    def test_decode_error_in_string_literal(self):
        input = "u'\\x'"
        exc = self.assertRaises(SyntaxError, self.get_ast, input)
        # self.assertEqual(exc.msg,
        #                  "(unicode error) 'unicodeescape' codec can't decode"
        #                  " bytes in position 0-1: truncated \\xXX escape")
        input = "u'\\x1'"
        exc = self.assertRaises(SyntaxError, self.get_ast, input)
        # self.assertEqual(exc.msg, 
        #                  "(unicode error) 'unicodeescape' codec can't decode"
        #                  " bytes in position 0-2: truncated \\xXX escape")
