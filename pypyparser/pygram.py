import os
from . import parser, pytoken, metaparser

class PythonGrammar(parser.Grammar):
    KEYWORD_TOKEN = pytoken.Token.NAME.value
    TOKENS = {k:v.value for k,v in pytoken.Token.__members__.items()}
    OPERATOR_MAP = pytoken.OPMAP

def _get_python_grammar():
    here = os.path.dirname(__file__)
    with open(os.path.join(here, "data", "Grammar3.5")) as fp:
        gram_source = fp.read()
    pgen = metaparser.ParserGenerator(gram_source)
    return pgen.build_grammar(PythonGrammar)

python_grammar = _get_python_grammar()


class _Symbols:
    pass
rev_lookup = {}
for sym_name, idx in python_grammar.symbol_ids.items():
    setattr(_Symbols, sym_name, idx)
    rev_lookup[idx] = sym_name
syms = _Symbols()
syms._rev_lookup = rev_lookup # for debugging

del _get_python_grammar, sym_name, idx
