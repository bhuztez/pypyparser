import os
import glob
import token
from . import TestCase
from ..metaparser import ParserGenerator, PgenError
from ..pygram import PythonGrammar
from .. import parser


class MyGrammar(parser.Grammar):
    TOKENS = token.__dict__
    OPERATOR_MAP = {
        "+" : token.OP,
        "-" : token.OP,
        }
    KEYWORD_TOKEN = token.NAME


class TestParserGenerator(TestCase):

    def gram_for(self, grammar_source):
        p = ParserGenerator(grammar_source + "\n")
        return p.build_grammar(MyGrammar)

    def test_multiple_rules(self):
        g = self.gram_for("foo: NAME bar\nbar: STRING")
        self.assertEqual(len(g.dfas), 2)
        self.assertEqual(g.start, g.symbol_ids["foo"])

    def test_simple(self):
        g = self.gram_for("eval: NAME\n")
        self.assertEqual(len(g.dfas), 1)
        eval_sym = g.symbol_ids["eval"]
        self.assertEqual(g.start, eval_sym)
        states, first = g.dfas[eval_sym - 256]
        self.assertEqual(states, [([(1, 1)], False), ([], True)])
        self.assertEqual(g.labels[0], 0)

    def test_load_python_grammars(self):
        gram_pat = os.path.join(os.path.dirname(__file__), "..", "data",
                                "Grammar*")
        for gram_file in glob.glob(gram_pat):
            fp = open(gram_file, "r")
            try:
                ParserGenerator(fp.read()).build_grammar(PythonGrammar)
            finally:
                fp.close()

    def test_items(self):
        g = self.gram_for("foo: NAME STRING OP '+'")
        self.assertEqual(len(g.dfas), 1)
        states = g.dfas[g.symbol_ids["foo"] - 256][0]
        last = states[0][0][0][1]
        for state in states[1:-1]:
            self.assertLess(last, state[0][0][1])
            last = state[0][0][1]

    def test_alternatives(self):
        g = self.gram_for("foo: STRING | OP")
        self.assertEqual(len(g.dfas), 1)

    def test_optional(self):
        g = self.gram_for("foo: [NAME]")

    def test_grouping(self):
        g = self.gram_for("foo: (NAME | STRING) OP")

    def test_keyword(self):
        g = self.gram_for("foo: 'some_keyword' 'for'")
        self.assertEqual(len(g.keyword_ids), 2)
        self.assertEqual(len(g.token_ids), 0)

    def test_token(self):
        g = self.gram_for("foo: NAME")
        self.assertEqual(len(g.token_ids), 1)

    def test_operator(self):
        g = self.gram_for("add: NUMBER '+' NUMBER")
        self.assertEqual(len(g.keyword_ids), 0)
        self.assertEqual(len(g.token_ids), 2)
        exc = self.assertRaises(PgenError, self.gram_for, "add: '/'")
        self.assertEqual(str(exc), "no such operator: '/'")

    def test_symbol(self):
        g = self.gram_for("foo: some_other_rule\nsome_other_rule: NAME")
        self.assertEqual(len(g.dfas), 2)
        self.assertEqual(len(g.labels), 3)

        exc = self.assertRaises(PgenError, self.gram_for, "foo: no_rule")
        self.assertEqual(str(exc), "no such rule: 'no_rule'")

    def test_repeaters(self):
        g1 = self.gram_for("foo: NAME+")
        g2 = self.gram_for("foo: NAME*")
        self.assertNotEqual(g1.dfas, g2.dfas)

        g = self.gram_for("foo: (NAME | STRING)*")
        g = self.gram_for("foo: (NAME | STRING)+")

    def test_error(self):
        exc = self.assertRaises(PgenError, self.gram_for, "hi")
        self.assertEqual(str(exc), "expected token OP but got NEWLINE")
        self.assertEqual(exc.location, ((1, 2), (1, 3), "hi\n"))
        exc = self.assertRaises(PgenError, self.gram_for, "hi+")
        self.assertEqual(str(exc), "expected ':' but got '+'")
        self.assertEqual(exc.location, ((1, 2), (1, 3), "hi+\n"))

    def test_comments_and_whitespace(self):
        self.gram_for("\n\n# comment\nrule: NAME # comment")
