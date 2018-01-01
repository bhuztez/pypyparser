from ..automata import DFA, DEFAULT
from ..gendfa import output
from .import TestCase

class TestGenDFA(TestCase):

    def test_states(self):
        states = [{"\x00": 1}, {"\x01": 0}]
        d = DFA(states[:], [False, True])
        self.assertEqual(
            output('test', "%s.%s"%(DFA.__module__, DFA.__name__), d, states),
            """\
accepts = [False, True]
states = [
    # 0
    {'\\x00': 1},
    # 1
    {'\\x01': 0},
    ]
test = automata.pypyparser.automata.DFA(states, accepts)
""")
