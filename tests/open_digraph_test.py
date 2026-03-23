import sys
import os
import tempfile
import unittest
from modules.open_digraph import node, open_digraph

root = os.path.normpath(os.path.join(__file__, "./../.."))
sys.path.append(root)



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
        self.n0 = node(0, 'a', {2: 1}, {1: 2})

    def test_getters(self):
        self.assertEqual(self.n0.get_id(), 0)
        self.assertEqual(self.n0.get_label(), 'a')
        self.assertEqual(self.n0.get_parents(), {2: 1})
        self.assertEqual(self.n0.get_children(), {1: 2})

    def test_copy(self):
        n_copy = self.n0.copy()
        self.assertIsNot(n_copy, self.n0)
        self.assertIsNot(n_copy.parents, self.n0.parents) 

    def test_setters(self):
        self.n0.set_id(5)
        self.assertEqual(self.n0.get_id(), 5)
        self.n0.set_label('b')
        self.assertEqual(self.n0.get_label(), 'b')

    def test_add_parent_child(self):
        self.n0.add_child_id(1, 1) 
        self.assertEqual(self.n0.children[1], 3)
        self.n0.add_parent_id(5, 2) 
        self.assertEqual(self.n0.parents[5], 2)

    def test_remove_parent_child_once(self):
        self.n0.remove_child_once(1) 
        self.assertEqual(self.n0.children[1], 1)
        self.n0.remove_child_once(1) 
        self.assertNotIn(1, self.n0.children)
        with self.assertRaises(KeyError):
            self.n0.remove_child_once(99) 

    def test_remove_parent_child_id(self):
        self.n0.remove_parent_id(2) 
        self.assertNotIn(2, self.n0.parents)
        with self.assertRaises(KeyError):
            self.n0.remove_parent_id(99)

class OpenDigraphTest(unittest.TestCase):
    def setUp(self):
        self.n0 = node(0, '', {}, {2: 1})
        self.n1 = node(1, '', {2: 1}, {})
        self.n2 = node(2, 'core', {0: 1}, {1: 1})
        self.g = open_digraph(inputs=[0], outputs=[1], nodes=[self.n0, self.n1, self.n2])

    def test_empty_and_copy(self):
        empty_g = open_digraph.empty()
        self.assertEqual(len(empty_g.get_nodes()), 0)
        g_copy = self.g.copy()
        self.assertIsNot(g_copy, self.g)
        self.assertIsNot(g_copy.nodes[0], self.g.nodes[0]) 

    def test_getters(self):
        self.assertEqual(self.g.get_input_ids(), [0])
        self.assertEqual(self.g.get_output_ids(), [1])
        self.assertEqual(len(self.g.get_node_ids()), 3)

    def test_add_node_and_edges(self):
        new_id = self.g.add_node(label='new')
        self.assertEqual(new_id, 3)
        self.g.add_edge(2, 3)
        self.assertIn(3, self.g.nodes[2].get_children())
        self.assertIn(2, self.g.nodes[3].get_parents())

    def test_remove_edge(self):
        self.g.remove_edge(0, 2)
        self.assertNotIn(2, self.g.nodes[0].get_children())
        self.assertNotIn(0, self.g.nodes[2].get_parents())

    def test_remove_node_by_id(self):
        self.g.remove_node_by_id(2)
        self.assertNotIn(2, self.g.get_node_ids())
        self.assertNotIn(2, self.g.nodes[0].get_children())

    def test_is_well_formed(self):
        self.assertTrue(self.g.is_well_formed())
        self.g.nodes[2].children[1] = 5
        self.assertFalse(self.g.is_well_formed())

    def test_add_input_output_node(self):
        in_id = self.g.add_input_node(2)
        self.assertIn(in_id, self.g.get_input_ids())
        self.assertTrue(self.g.is_well_formed()) 

    def test_adjacency_matrix(self):
        matrix = self.g.adjacency_matrix()
        self.assertEqual(len(matrix), 3)

    def test_graph_from_adjacency_matrix(self):
        mat = [[0, 1, 0], [0, 0, 2], [1, 0, 0]]
        g_mat = open_digraph.graph_from_adjacency_matrix(mat)
        self.assertEqual(len(g_mat.get_nodes()), 3)

    def test_random_graph(self):
        g_rand = open_digraph.random(n=5, bound=2, inputs=1, outputs=1, form="DAG")
        self.assertIsInstance(g_rand, open_digraph)

    def test_dot_file_saving_loading(self):
        fd, path = tempfile.mkstemp(suffix=".dot")
        os.close(fd)
        try:
            self.g.save_as_dot_file(path)
            g_loaded = open_digraph.from_dot_file(path)
            self.assertEqual(len(g_loaded.get_nodes()), len(self.g.get_nodes()))
        finally:
            os.remove(path)

if __name__ == '__main__':
    unittest.main(verbosity=2)