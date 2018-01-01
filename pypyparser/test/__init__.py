import unittest

class TestCase(unittest.TestCase):
    def assertRaises(self, exception, callable, *args, **kwds):
        with unittest.TestCase.assertRaises(self, exception) as cm:
            callable(*args, **kwds)
        return cm.exception
