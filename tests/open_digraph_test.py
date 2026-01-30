import sys
import os
root = os.path.normpath(os.path.join(__file__, "./../.."))
sys.path.append(root)
import unittest
from modules.open_digraph import *


class InitTest(unittest.TestCase):
    def test_init_node(self):
        n0 = node(0, '1', {}, {1:1})
        self.assertEqual(n0.id, 0)
        self.assertEqual(n0.label, 'i')
        self.assertEqual(n0.parents, {})
        self.assertEqual(n0.children, {1:1})
        self.assertIsInstance(n0, node)


if __name__ == '__main__':
    unittest.main()