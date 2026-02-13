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
        self.assertEqual(n0.label, '1')
        self.assertEqual(n0.parents, {})
        self.assertEqual(n0.children, {1:1})
        self.assertIsInstance(n0, node)
        self.assertIsNot(n0.copy(),n0)
        self.assertEqual(n0.get_id(),0)
        self.assertEqual(n0.get_label(),"1")
        self.assertEqual(n0.get_children(), {1: 1})


    def test_init_open_digraph(self):
        n0 = node(0, 'i', {}, {1: 1})
        n1 = node(1, 'o', {0: 1}, {})
        g = open_digraph([0], [1], [n0, n1])    
        self.assertEqual(g.inputs, [0])
        self.assertEqual(g.outputs, [1])
        self.assertEqual(g.nodes[0], n0)
        self.assertEqual(g.nodes[1], n1)
        self.assertIsInstance(g, open_digraph)

class NodeTest(unittest.TestCase):
    def setUp(self):
        self.n0 = node(0, 'a', {}, {1: 1})

    def test_get_id(self):
        self.assertEqual(self.n0.get_id(), 0)

    def test_get_label(self):
        self.assertEqual(self.n0.get_label(), 'a')

    def test_get_parents(self):
        self.assertEqual(self.n0.get_parents(), {})

    def test_get_children(self):
        self.assertEqual(self.n0.get_children(), {1: 1})

    def test_set_id(self):
        self.n0.set_id(5)
        self.assertEqual(self.n0.get_id(), 5)

    def test_set_label(self):
        self.n0.set_label('b')
        self.assertEqual(self.n0.get_label(), 'b')

    def test_set_parents(self):
        new_parents = {2: 1}
        self.n0.set_parent(new_parents)
        self.assertEqual(self.n0.get_parents(), new_parents)

    def test_set_children(self):
        new_children = {3: 2}
        self.n0.set_children(new_children)
        self.assertEqual(self.n0.get_children(), new_children)

    def test_add_child_id(self):
        self.n0.add_child_id(2, 1)
        self.assertEqual(self.n0.children[2], 1)
        self.n0.add_child_id(1, 2)
        self.assertEqual(self.n0.children[1], 3)

    def test_add_parents_id(self):
        self.n0.add_parents_id(2, 1)
        self.assertEqual(self.n0.parents[2], 1)

class OpenDigraphTest(unittest.TestCase):
    def setUp(self):
        self.n0 = node(0, 'i', {}, {1: 1})
        self.n1 = node(1, 'o', {0: 1}, {})
        self.g = open_digraph([0], [1], [self.n0, self.n1])

    def test_get_inputs_ids(self):
        self.assertEqual(self.g.get_inputs_ids(), [0])

    def test_get_node_by_id(self):
        self.assertEqual(self.g.get_node_by_id(0), self.n0)
        self.assertEqual(self.g.get_node_by_id(1), self.n1)

    def test_get_nodes_by_ids(self):
        nodes = self.g.get_nodes_by_ids([0, 1])
        self.assertIn(self.n0, nodes)
        self.assertIn(self.n1, nodes)
        self.assertEqual(len(nodes), 2)

    def test_get_id_node_map(self):
        self.assertEqual(self.g.get_id_node_map(), {0: self.n0, 1: self.n1})

    def test_get_nodes(self):
        nodes_list = self.g.get_nodes()
        self.assertIn(self.n0, nodes_list)
        self.assertIn(self.n1, nodes_list)

    def test_get_nodes_ids(self):
        ids = self.g.get_nodes_ids()
        self.assertIn(0, ids)
        self.assertIn(1, ids)

    def test_set_inputs(self):
        self.g.set_inputs([1])
        self.assertEqual(self.g.get_inputs_ids(), [1])

    def test_set_outputs(self):
        self.g.set_outputs([0])
        self.assertEqual(self.g.outputs, [0])

    def test_add_input_id(self):
        self.g.add_input_id(5)
        self.assertIn(5, self.g.get_inputs_ids())
        self.g.add_input_id(5)
        self.assertEqual(self.g.get_inputs_ids().count(5), 1)

    def test_add_output_id(self):
        self.g.add_output_id(5)
        self.assertIn(5, self.g.outputs)

if __name__ == '__main__':
    unittest.main()