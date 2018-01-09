# -*- coding: utf-8 -*-
from .. import pyparse, parser
from ..error import SyntaxError, IndentationError, TabError
from .. import consts
from . import TestCase


class TestPythonParserWithoutSpace(TestCase):

    def setUp(self):
        self.parser = parser.Parser(None)

    def parse(self, source, mode="exec", info=None):
        if info is None:
            info = pyparse.CompileInfo("<test>", mode)
        return pyparse.parse_source(source, info, parser=self.parser)

    def test_with_and_as(self):
        self.assertRaises(SyntaxError, self.parse, b"with = 23")
        self.assertRaises(SyntaxError, self.parse, b"as = 2")

    def test_dont_imply_dedent(self):
        info = pyparse.CompileInfo("<test>", "single",
                                   consts.PyCF_DONT_IMPLY_DEDENT)
        self.parse(b'if 1:\n  x\n', info=info)
        self.parse(b'x = 5 ', info=info)

    def test_clear_state(self):
        self.assertIsNone(self.parser.root)
        tree = self.parse(b"name = 32")
        self.assertIsNone(self.parser.root)

    def test_encoding_pep3120(self):
        info = pyparse.CompileInfo("<test>", "exec")
        tree = self.parse("""foo = '日本'""".encode('utf-8'), info=info)
        self.assertEqual(info.encoding, 'utf-8')

    def test_unicode_identifier(self):
        tree = self.parse("a日本 = 32".encode('utf-8'))
        tree = self.parse("日本 = 32".encode('utf-8'))

    def test_syntax_error(self):
        parse = self.parse
        exc = self.assertRaises(SyntaxError, parse, b"name another for")
        self.assertEqual(exc.msg, "invalid syntax")
        self.assertEqual(exc.lineno, 1)
        self.assertEqual(exc.offset, 5)
        self.assertTrue(exc.text.startswith("name another for"))
        exc = self.assertRaises(SyntaxError, parse, b"x = \"blah\n\n\n")
        self.assertEqual(exc.msg, "EOL while scanning string literal")
        self.assertEqual(exc.lineno, 1)
        self.assertEqual(exc.offset, 5)
        exc = self.assertRaises(SyntaxError, parse, b"x = '''\n\n\n")
        self.assertEqual(exc.msg, "EOF while scanning triple-quoted string literal")
        self.assertEqual(exc.lineno, 1)
        self.assertEqual(exc.offset, 5)
        self.assertEqual(exc.lastlineno, 3)
        for input in (b"())", b"(()", b"((", b"))"):
            self.assertRaises(SyntaxError, parse, input)
        exc = self.assertRaises(SyntaxError, parse, b"x = (\n\n(),\n(),")
        self.assertEqual(exc.msg, "parenthesis is never closed")
        self.assertEqual(exc.lineno, 1)
        self.assertEqual(exc.offset, 5)
        self.assertEqual(exc.lastlineno, 5)
        exc = self.assertRaises(SyntaxError, parse, b"abc)")
        self.assertEqual(exc.msg, "unmatched ')'")
        self.assertEqual(exc.lineno, 1)
        self.assertEqual(exc.offset, 4)

    def test_is(self):
        self.parse(b"x is y")
        self.parse(b"x is not y")

    def test_indentation_error(self):
        parse = self.parse
        input = b"""
def f():
pass"""
        exc = self.assertRaises(IndentationError, parse, input)
        self.assertEqual(exc.msg, "expected an indented block")
        self.assertEqual(exc.lineno, 3)
        self.assertTrue(exc.text.startswith("pass"))
        self.assertEqual(exc.offset, 0)
        input = b"hi\n    indented"
        exc = self.assertRaises(IndentationError, parse, input)
        self.assertEqual(exc.msg, "unexpected indent")
        input = b"def f():\n    pass\n  next_stmt"
        exc = self.assertRaises(IndentationError, parse, input)
        self.assertEqual(exc.msg, "unindent does not match any outer indentation level")
        self.assertEqual(exc.lineno, 3)

    def test_taberror(self):
        src = b"""
if 1:
        pass
    \tpass
"""
        exc = self.assertRaises(TabError, self.parse, src)
        self.assertEqual(exc.msg, "inconsistent use of tabs and spaces in indentation")
        self.assertEqual(exc.lineno, 4)
        self.assertEqual(exc.offset, 5)
        self.assertEqual(exc.text, "    \tpass\n")

    def test_mac_newline(self):
        self.parse(b"this_is\ra_mac\rfile")

    def test_mode(self):
        info = pyparse.CompileInfo("<test>", "exec")
        syms = info.parser.syms
        self.assertEqual(self.parse(b"x = 43*54").type, syms.file_input)
        tree = self.parse(b"43**54", "eval")
        self.assertEqual(tree.type, syms.eval_input)
        self.assertRaises(SyntaxError, self.parse, b"x = 54", "eval")
        tree = self.parse(b"x = 43", "single")
        self.assertEqual(tree.type, syms.single_input)

    def test_multiline_string(self):
        self.parse(b"''' \n '''")
        self.parse(b"r''' \n '''")

    def test_bytes_literal(self):
        self.parse(b'b" "')
        self.parse(b'br" "')
        self.parse(b'b""" """')
        self.parse(b"b''' '''")
        self.parse(b"br'\\\n'")

        self.assertRaises(SyntaxError, self.parse, b"b'a\\n")

    def test_new_octal_literal(self):
        self.parse(b'0o777')
        self.assertRaises(SyntaxError, self.parse, b'0o777L')
        self.assertRaises(SyntaxError, self.parse, b"0o778")

    def test_new_binary_literal(self):
        self.parse(b'0b1101')
        self.assertRaises(SyntaxError, self.parse, b'0b0l')
        self.assertRaises(SyntaxError, self.parse, b"0b112")

    def test_print_function(self):
        self.parse(b"from __future__ import print_function\nx = print\n")

    def test_universal_newlines(self):
        fmt = b'stuff = """hello%sworld"""'
        expected_tree = self.parse(fmt % b'\n')
        for linefeed in [b"\r\n",b"\r"]:
            tree = self.parse(fmt % linefeed)
            self.assertEqual(expected_tree, tree)

    def test_py3k_reject_old_binary_literal(self):
        self.assertRaises(SyntaxError, self.parse, b'0777')

    def test_py3k_extended_unpacking(self):
        self.parse(b'a, *rest, b = 1, 2, 3, 4, 5')
        self.parse(b'(a, *rest, b) = 1, 2, 3, 4, 5')

    def test_u_triple_quote(self):
        self.parse(b'u""""""')
        self.parse(b'U""""""')
        self.parse(b"u''''''")
        self.parse(b"U''''''")

    def test_bad_single_statement(self):
        self.assertRaises(SyntaxError, self.parse, b'1\n2', "single")
        self.assertRaises(SyntaxError, self.parse, b'a = 13\nb = 187', "single")
        self.assertRaises(SyntaxError, self.parse, b'del x\ndel y', "single")
        self.assertRaises(SyntaxError, self.parse, b'f()\ng()', "single")
        self.assertRaises(SyntaxError, self.parse, b'f()\n# blah\nblah()', "single")
        self.assertRaises(SyntaxError, self.parse, b'f()\nxy # blah\nblah()', "single")
        self.assertRaises(SyntaxError, self.parse, b'x = 5 # comment\nx = 6\n', "single")

    def test_unpack(self):
        self.parse(b'[*{2}, 3, *[4]]')
        self.parse(b'{*{2}, 3, *[4]}')
        self.parse(b'{**{}, 3:4, **{5:6, 7:8}}')
        self.parse(b'f(2, *a, *b, **b, **c, **d)')

    def test_async_await(self):
        self.parse(b"async def coro(): await func")
        self.assertRaises(SyntaxError, self.parse, b'await x')
        #Test as var and func name
        self.parse(b"async = 1")
        self.parse(b"await = 1")
        self.parse(b"def async(): pass")
        #async for
        self.parse(b"""async def foo():
    async for a in b:
        pass""")
        self.assertRaises(SyntaxError, self.parse, b'def foo(): async for a in b: pass')
        #async with
        self.parse(b"""async def foo():
    async with a:
        pass""")
        self.assertRaises(SyntaxError, self.parse, b'def foo(): async with a: pass')



class TestPythonParserWithSpace(TestCase):

    def setUp(self):
        self.parser = pyparse.PythonParser()

    def parse(self, source, mode="exec", info=None):
        if info is None:
            info = pyparse.CompileInfo("<test>", mode)
        return pyparse.parse_source(source, info)

    def test_encoding(self):
        info = pyparse.CompileInfo("<test>", "exec")
        syms = info.parser.syms
        tree = self.parse(b"""# coding: latin-1
stuff = "nothing"
""", info=info)
        self.assertEqual(tree.type, syms.file_input)
        self.assertEqual(info.encoding, "iso-8859-1")
        sentence = u"'Die Männer ärgen sich!'"
        input = (u"# coding: utf-7\nstuff = %s" % (sentence,)).encode("utf-7")
        tree = self.parse(input, info=info)
        self.assertEqual(info.encoding, "utf-7")
        input = b"# coding: iso-8859-15\nx"
        self.parse(input, info=info)
        self.assertEqual(info.encoding, "iso-8859-15")
        input = b"\xEF\xBB\xBF# coding: utf-8\nx"
        self.parse(input, info=info)
        self.assertEqual(info.encoding, "utf-8")
        #
        info.flags |= consts.PyCF_SOURCE_IS_UTF8
        input = b"#\nx"
        info.encoding = None
        self.parse(input, info=info)
        self.assertEqual(info.encoding, "utf-8")
        input = b"# coding: latin1\nquux"
        self.parse(input, info=info)
        self.assertEqual(info.encoding, "latin1")
        info.flags |= consts.PyCF_IGNORE_COOKIE
        self.parse(input, info=info)
        self.assertEqual(info.encoding, "utf-8")
        info.flags &= ~(consts.PyCF_SOURCE_IS_UTF8 | consts.PyCF_IGNORE_COOKIE)
        #
        input = b"\xEF\xBB\xBF# coding: latin-1\nx"
        exc = self.assertRaises(SyntaxError, self.parse, input)
        self.assertEqual(exc.msg, "UTF-8 BOM with latin-1 coding cookie")
        input = b"# coding: not-here"
        exc = self.assertRaises(SyntaxError, self.parse, input)
        self.assertEqual(exc.msg, "Unknown encoding: not-here")
        input = u"# coding: ascii\n\xe2".encode('utf-8')
        exc = self.assertRaises(SyntaxError, self.parse, input)
        self.assertEqual(exc.msg,
                         ("'ascii' codec can't decode byte 0xc3 "
                          "in position 16: ordinal not in range(128)"))
