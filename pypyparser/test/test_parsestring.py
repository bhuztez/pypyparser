import sys
from .. import parsestring
from . import TestCase


class TestParsetring(TestCase):
    def parse_and_compare(self, literal, value):
        self.assertEqual(parsestring.parsestr(literal), value)

    def test_simple(self):
        for s in [b'hello world', b'hello\n world']:
            self.parse_and_compare(repr(s), s)

        self.parse_and_compare("b'''hello\\x42 world'''", b'hello\x42 world')

        # octal
        self.parse_and_compare(r'b"\0"', b"\0")
        self.parse_and_compare(r'br"\0"', br"\0")
        self.parse_and_compare(r'rb"\0"', rb"\0")
        self.parse_and_compare(r'b"\07"', b"\07")
        self.parse_and_compare(r'b"\123"', b"\123")
        self.parse_and_compare(r'b"\400"', b"\400")
        self.parse_and_compare(r'b"\9"', b"\9")
        self.parse_and_compare(r'b"\08"', b"\08")

        # hexadecimal
        self.parse_and_compare(r'b"\xfF"', b"\xfF")
        self.parse_and_compare(r'b"\""', b"\"")
        self.parse_and_compare(r"b'\''", b'\'')
        for s in (r'b"\x"', r'b"\x7"', r'b"\x7g"'):
            self.assertRaises(ValueError, parsestring.parsestr, s)

        # only ASCII characters are allowed in bytes literals (but of course
        # you can use escapes to get the non-ASCII ones (note that in the
        # second case we use a raw string, the the parser actually sees the
        # chars '\' 'x' 'e' '9'
        self.assertRaises(SyntaxError, parsestring.parsestr, "b'\xe9'")
        self.parse_and_compare(r"b'\xe9'", b'\xe9')


    def test_unicode(self):
        for s in ['hello world', 'hello\n world']:
            self.parse_and_compare(repr(s), s)

        self.parse_and_compare("'''hello\\x42 world'''",
                               'hello\x42 world')
        self.parse_and_compare("'''hello\\u0842 world'''",
                               'hello\u0842 world')

        # s = "u'\x81'"
        # s = s.decode("koi8-u").encode("utf8")[1:]
        # w_ret = parsestring.parsestr(self.space, 'koi8-u', s)
        # ret = space.unwrap(w_ret)
        # assert ret == eval("# -*- coding: koi8-u -*-\nu'\x81'")

    def test_unicode_pep414(self):
        for s in ['hello world', 'hello\n world']:
            self.parse_and_compare(repr(s), s)

        self.parse_and_compare("u'''hello\\x42 world'''",
                               'hello\x42 world')
        self.parse_and_compare("u'''hello\\u0842 world'''",
                               'hello\u0842 world')

        self.assertRaises(ValueError, parsestring.parsestr, "ur'foo'")

    def test_unicode_literals(self):
        self.assertIsInstance(parsestring.parsestr(repr("hello")), str)
        self.assertIsInstance(parsestring.parsestr("b'hi'"), bytes)
        self.assertIsInstance(parsestring.parsestr("r'hi'"), str)

    def test_raw_unicode_literals(self):
        self.assertEqual(len(parsestring.parsestr(r"r'\u'")), 2)

    def test_bytes(self):
        b = "b'hello'"
        self.assertEqual(parsestring.parsestr(b), b"hello")
        b = "b'''hello'''"
        self.assertEqual(parsestring.parsestr(b), b"hello")

    # def test_simple_enc_roundtrip(self):
    #     space = self.space
    #     s = "'\x81\\t'"
    #     s = s.decode("koi8-u").encode("utf8")
    #     w_ret = parsestring.parsestr(self.space, 'koi8-u', s)
    #     ret = space.unwrap(w_ret)
    #     assert ret == eval("# -*- coding: koi8-u -*-\nu'\x81\\t'")

    def test_multiline_unicode_strings_with_backslash(self):
        s = '"""' + '\\' + '\n"""'
        self.assertEqual(parsestring.parsestr(s), '')

    def test_bug1(self):
        expected = ['x', ' ', chr(0xc3), chr(0xa9), ' ', '\n']
        input = ["'", 'x', ' ', chr(0xc3), chr(0xa9), ' ', chr(92), 'n', "'"]
        w_ret = parsestring.parsestr(''.join(input))
        self.assertEqual(w_ret, ''.join(expected))

    # def test_wide_unicode_in_source(self):
    #     self.parse_and_compare('"\xf0\x9f\x92\x8b"',
    #                            chr(0x1f48b))

    # def test_decode_unicode_utf8(self):
    #     buf = parsestring.decode_unicode_utf8(self.space,
    #                                           'u"\xf0\x9f\x92\x8b"', 2, 6)
    #     if sys.maxunicode == 65535:
    #         assert buf == r"\U0000d83d\U0000dc8b"
    #     else:
    #         assert buf == r"\U0001f48b"
