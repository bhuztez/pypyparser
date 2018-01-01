from ..automata import DFA, DEFAULT
from . import TestCase


class TestAutomata(TestCase):

    def test_states(self):
        d = DFA([{"\x00": 1}, {"\x01": 0}], [False, True])
        self.assertEqual(d.states, "\x01\xff\xff\x00")
        self.assertEqual(d.defaults, "\xff\xff")
        self.assertEqual(d.max_char, 2)

        d = DFA([{"\x00": 1}, {DEFAULT: 0}], [False, True])
        self.assertEqual(d.states, "\x01\x00")
        self.assertEqual(d.defaults, "\xff\x00")
        self.assertEqual(d.max_char, 1)
