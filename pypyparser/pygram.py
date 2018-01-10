import os
from . import parser, pytoken, metaparser

class PythonGrammar(parser.Grammar):
    KEYWORD_TOKEN = pytoken.Token.NAME
    TOKENS = pytoken.Token.__dict__
    OPERATOR_MAP = pytoken.OPMAP

def get_python_grammar(filename):
    here = os.path.dirname(__file__)
    with open(os.path.join(here, "data", filename)) as fp:
        gram_source = fp.read()
    pgen = metaparser.ParserGenerator(gram_source)
    return pgen.build_grammar(PythonGrammar)

def get_symbols(grammar):
    class _Symbols:
        pass
    rev_lookup = {}
    for sym_name, idx in grammar.symbol_ids.items():
        setattr(_Symbols, sym_name, idx)
        rev_lookup[idx] = sym_name
    syms = _Symbols()
    syms._rev_lookup = rev_lookup
    return syms
