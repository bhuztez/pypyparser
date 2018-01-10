from .. import future, pytokenizer
from .. import stdlib___future__ as fut
from . import TestCase


class TestFuture(TestCase):

    def _run(self, s, expected_last_future=(0, 0)):
        source_lines = s.splitlines(True)
        tokens = pytokenizer.generate_tokens(source_lines, 0)
        #
        flags, last_future_import = future.add_future_flags(
            future.FUTURE_FLAGS["3.5"], tokens)
        self.assertEqual(last_future_import, expected_last_future)
        return flags

    def test_docstring(self):
        s = '"Docstring\\" "\nfrom  __future__ import division\n'
        self.assertEqual(self._run(s, (2, 24)), 0)

    def test_comment(self):
        s = '# A comment about nothing ;\n'
        self.assertEqual(self._run(s), 0)

    def test_tripledocstring(self):
        s = '''""" This is a
        docstring with line
        breaks in it. It even has a \n"""
        '''
        self.assertEqual(self._run(s), 0)

    def test_escapedquote_in_tripledocstring(self):
        s = '''""" This is a
        docstring with line
        breaks in it. \\"""It even has an escaped quote!"""
        '''
        self.assertEqual(self._run(s), 0)

    def test_empty_line(self):
        s = ' \t   \f \n   \n'
        self.assertEqual(self._run(s), 0)

    def test_from(self):
        s = 'from  __future__ import division\n'
        self.assertEqual(self._run(s, (1, 24)), 0)

    def test_froms(self):
        s = 'from  __future__ import division, generators, with_statement\n'
        self.assertEqual(self._run(s, (1, 24)), 0)

    def test_from_as(self):
        s = 'from  __future__ import division as b\n'
        self.assertEqual(self._run(s, (1, 24)), 0)

    def test_froms_as(self):
        s = 'from  __future__ import division as b, generators as c\n'
        self.assertEqual(self._run(s, (1, 24)), 0)

    def test_from_paren(self):
        s = 'from  __future__ import (division)\n'
        self.assertEqual(self._run(s, (1, 25)), 0)

    def test_froms_paren(self):
        s = 'from  __future__ import (division, generators)\n'
        self.assertEqual(self._run(s, (1, 25)), 0)

    def test_froms_paren_as(self):
        s = 'from  __future__ import (division as b, generators,)\n'
        self.assertEqual(self._run(s, (1, 25)), 0)

    def test_paren_with_newline(self):
        s = 'from __future__ import (division,\nabsolute_import)\n'
        self.assertEqual(self._run(s, (1, 24)), 0)

    def test_paren_with_newline_2(self):
        s = 'from __future__ import (\ndivision,\nabsolute_import)\n'
        self.assertEqual(self._run(s, (2, 0)), 0)

    def test_multiline(self):
        s = '"abc" #def\n  #ghi\nfrom  __future__ import (division as b, generators,)\nfrom __future__ import with_statement\n'
        self.assertEqual(self._run(s, (4, 23)), 0)

    def test_windows_style_lineendings(self):
        s = '"abc" #def\r\n  #ghi\r\nfrom  __future__ import (division as b, generators,)\r\nfrom __future__ import with_statement\r\n'
        self.assertEqual(self._run(s, (4, 23)), 0)

    def test_mac_style_lineendings(self):
        s = '"abc" #def\r  #ghi\rfrom  __future__ import (division as b, generators,)\rfrom __future__ import with_statement\r'
        self.assertEqual(self._run(s, (4, 23)), 0)

    def test_semicolon(self):
        s = '"abc" #def\n  #ghi\nfrom  __future__ import (division as b, generators,);  from __future__ import with_statement\n'
        self.assertEqual(self._run(s, (3, 78)), 0)

    def test_semicolon_2(self):
        s = 'from  __future__ import division; from foo import bar'
        self.assertEqual(self._run(s, expected_last_future=(1, 24)), 0)

    def test_full_chain(self):
        s = '"abc" #def\n  #ghi\nfrom  __future__ import (division as b, generators,);  from __future__ import with_statement\n'
        self.assertEqual(self._run(s, (3, 78)), 0)

    def test_intervening_code(self):
        s = 'from  __future__ import (division as b, generators,)\nfrom sys import modules\nfrom __future__ import with_statement\n'
        self.assertEqual(self._run(s, expected_last_future=(1, 25)), 0)

    def test_nonexisting(self):
        s = 'from  __future__ import non_existing_feature\n'
        self.assertEqual(self._run(s, (1, 24)), 0)

    def test_nonexisting_2(self):
        s = 'from  __future__ import non_existing_feature, with_statement\n'
        self.assertEqual(self._run(s, (1, 24)), 0)

    def test_from_import_abs_import(self):
        s = 'from  __future__ import absolute_import\n'
        self.assertEqual(self._run(s, (1, 24)), 0)

    def test_raw_doc(self):
        s = 'r"Doc"\nfrom __future__ import with_statement\n'
        self.assertEqual(self._run(s, (2, 23)), 0)

    def test_unicode_doc(self):
        s = 'u"Doc"\nfrom __future__ import with_statement\n'
        self.assertEqual(self._run(s, (2, 23)), 0)

    def test_raw_unicode_doc(self):
        s = 'ru"Doc"\nfrom __future__ import with_statement\n'
        self.assertEqual(self._run(s, (2, 23)), 0)

    def test_continuation_line(self):
        s = "\\\nfrom __future__ import with_statement\n"
        self.assertEqual(self._run(s, (2, 23)), 0)

    def test_continuation_lines(self):
        s = "\\\n  \t\\\nfrom __future__ import with_statement\n"
        self.assertEqual(self._run(s, (3, 23)), 0)

    def test_lots_of_continuation_lines(self):
        s = "\\\n\\\n\\\n\\\n\\\n\\\n\nfrom __future__ import with_statement\n"
        self.assertEqual(self._run(s, (8, 23)), 0)

    def test_continuation_lines_raise(self):
        s = "   \\\n  \t\\\nfrom __future__ import with_statement\n"
        # because of the INDENT
        self.assertEqual(self._run(s), 0)

    def test_continuation_lines_in_docstring_single_quoted(self):
        s = '"\\\n\\\n\\\n\\\n\\\n\\\n"\nfrom  __future__ import division\n'
        self.assertEqual(self._run(s, (8, 24)), 0)

    def test_continuation_lines_in_docstring_triple_quoted(self):
        s = '"""\\\n\\\n\\\n\\\n\\\n\\\n"""\nfrom  __future__ import division\n'
        self.assertEqual(self._run(s, (8, 24)), 0)

    def test_blank_lines(self):
        s = ('\n\t\n\nfrom __future__ import with_statement'
             '  \n  \n  \nfrom __future__ import division')
        self.assertEqual(self._run(s, (7, 23)), 0)

    def test_dummy_semicolons(self):
        s = ('from __future__ import division;\n'
             'from __future__ import with_statement;')
        self.assertEqual(self._run(s, (2, 23)), 0)
