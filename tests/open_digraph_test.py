import sys
import os
import tempfile
import unittest
from modules.open_digraph import node, open_digraph
from modules.bool_circ import bool_circ

root = os.path.normpath(os.path.join(__file__, "./../.."))
sys.path.append(root)

#python3 -m unittest discover tests "*_test.py" pour tester

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


    def test_degrees(self):
        self.assertEqual(self.n0.indegree(), 1)
        self.assertEqual(self.n0.outdegree(), 2)
        self.assertEqual(self.n0.degree(), 3)

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

    def test_is_cyclic(self):
        self.assertFalse(self.g.is_cyclic())
        self.g.add_edge(2, 0)
        self.assertTrue(self.g.is_cyclic())

    def test_min_max_id(self):
        self.assertEqual(self.g.min_id(), 0)
        self.assertEqual(self.g.max_id(), 2)    
        g_empty = open_digraph.empty()
        self.assertEqual(g_empty.min_id(), 0)
        self.assertEqual(g_empty.max_id(), 0)

    def test_shift_indices(self):
        self.g.shift_indices(10)
        self.assertEqual(self.g.get_input_ids(), [10])
        self.assertEqual(self.g.get_output_ids(), [11])
        
        self.assertIn(12, self.g.get_node_ids())
        n12 = self.g.get_node_by_id(12)
        self.assertEqual(n12.get_id(), 12)
        
        self.assertEqual(n12.get_parents(), {10: 1})
        self.assertEqual(n12.get_children(), {11: 1})

    def test_identity(self):
        n = 3
        id_graph = open_digraph.identity(n)
        
        self.assertEqual(len(id_graph.get_input_ids()), n)
        self.assertEqual(len(id_graph.get_output_ids()), n)
        self.assertEqual(len(id_graph.get_nodes()), 2 * n)
        
        for i, in_id in enumerate(id_graph.get_input_ids()):
            out_id = id_graph.get_output_ids()[i]
            in_node = id_graph.get_node_by_id(in_id)
            self.assertIn(out_id, in_node.get_children())

    def test_compositions(self):
        n0 = node(0, 'A', {}, {1: 1})
        n1 = node(1, 'B', {0: 1}, {2: 1})
        n2 = node(2, 'C', {1: 1}, {})
        g1 = open_digraph([0], [2], [n0, n1, n2])
        
        n0_bis = node(0, 'X', {}, {1: 1})
        n1_bis = node(1, 'Y', {0: 1}, {2: 1})
        n2_bis = node(2, 'Z', {1: 1}, {})
        g2 = open_digraph([0], [2], [n0_bis, n1_bis, n2_bis])

        g_para = g1.comp_parallel(g2)
        self.assertEqual(len(g_para.get_nodes()), 6) 
        self.assertEqual(len(g_para.get_input_ids()), 2) 
        self.assertEqual(len(g_para.get_output_ids()), 2)
        self.assertTrue(g_para.is_well_formed())

        g_seq = g1.comp_sequentielle(g2)
        self.assertEqual(len(g_seq.get_nodes()), 6)
        self.assertEqual(len(g_seq.get_input_ids()), 1) 
        self.assertEqual(len(g_seq.get_output_ids()), 1) 
        self.assertTrue(g_seq.is_well_formed())
        
        id_graph = open_digraph.identity(3)
        with self.assertRaises(ValueError):
            g1.comp_sequentielle(id_graph)

    def test_connected_components(self):
        n0 = node(0, 'A', {}, {1: 1})
        n1 = node(1, 'B', {0: 1}, {})
        n2 = node(2, 'C', {}, {3: 1})
        n3 = node(3, 'D', {2: 1}, {})
        
        g = open_digraph([0, 2], [1, 3], [n0, n1, n2, n3])
        
        components = g.connected_components()
        self.assertEqual(len(components), 2) 
        
        
        list_of_sets = [set(c) for c in components]
        self.assertIn({0, 1}, list_of_sets)
        self.assertIn({2, 3}, list_of_sets)

        
        graphs = g.connected_components_graphs()
        self.assertEqual(len(graphs), 2)
        
        for sub_g in graphs:
            self.assertTrue(sub_g.is_well_formed())
            self.assertEqual(len(sub_g.get_nodes()), 2)
            self.assertEqual(len(sub_g.get_input_ids()), 1)
            self.assertEqual(len(sub_g.get_output_ids()), 1)


    def test_distances_and_paths(self):
        n0 = node(0, 'n0', {}, {1: 1, 2: 1})
        n1 = node(1, 'n1', {0: 1}, {3: 1})
        n2 = node(2, 'n2', {0: 1, 5: 1}, {3: 1})
        n3 = node(3, 'n3', {1: 1, 2: 1}, {4: 1})
        n4 = node(4, 'n4', {3: 1}, {})
        n5 = node(5, 'n5', {}, {2: 1})
        
        g = open_digraph([], [], [n0, n1, n2, n3, n4, n5])
        
        dist, prev = g.bfs(0, direction=1)
        self.assertEqual(dist[0], 0)
        self.assertEqual(dist[3], 2)
        self.assertEqual(dist[4], 3)
        self.assertNotIn(5, dist)
        
        dist_rev, prev_rev = g.bfs(3, direction=-1)
        self.assertEqual(dist_rev[3], 0)
        self.assertEqual(dist_rev[0], 2) 
        self.assertEqual(dist_rev[5], 2)
        
        dist_tgt, prev_tgt = g.bfs(0, direction=1, tgt=1)
        self.assertIn(1, dist_tgt)
        self.assertNotIn(4, dist_tgt) 
        
        path = g.shortest_path(0, 4)
        self.assertEqual(path[0], 0)
        self.assertEqual(path[-1], 4)
        self.assertEqual(len(path), 4)
        
        path_imp = g.shortest_path(4, 0)
        self.assertEqual(path_imp, [])
        
        ancestors = g.common_ancestors(3, 4)
        
        self.assertIn(3, ancestors)
        self.assertEqual(ancestors[3], (0, 1))
        
        self.assertIn(0, ancestors)
        self.assertEqual(ancestors[0], (2, 3))
        
        self.assertIn(5, ancestors)
        self.assertEqual(ancestors[5], (2, 3))

    def test_td8_and_merge(self):
        
        n0 = node(0, 'n0', {}, {1: 1, 2: 1})
        n1 = node(1, 'n1', {0: 1}, {3: 1})
        n2 = node(2, 'n2', {0: 1}, {3: 1})
        n3 = node(3, 'n3', {1: 1, 2: 1}, {4: 1})
        n4 = node(4, 'n4', {3: 1}, {})
        
        g = open_digraph([], [], [n0, n1, n2, n3, n4])
        
        tri = g.tri_topologique()
        self.assertIn(0, tri[0])
        self.assertIn(1, tri[1])
        self.assertIn(3, tri[2])
        self.assertIn(4, tri[3])
        
        
        g.add_edge(4, 0)
        with self.assertRaises(ValueError):
            g.tri_topologique()
        g.remove_edge(4, 0)
        
        self.assertEqual(g.profondeur_noeud(0), 0)
        self.assertEqual(g.profondeur_noeud(3), 2)
        self.assertEqual(g.profondeur_graphe(), 3)

        chemin = g.plus_long_chemin(0, 4)
        self.assertEqual(chemin[0], 0)
        self.assertEqual(chemin[-1], 4)
        self.assertEqual(len(chemin), 4)
        
        g.merge_nodes(1, 2)
        
        self.assertNotIn(2, g.get_node_ids())
        
        noeud1 = g.get_node_by_id(1)
        self.assertEqual(noeud1.get_parents()[0], 2)
        self.assertEqual(noeud1.get_children()[3], 2)

class BoolCircTest(unittest.TestCase):
    def test_bool_circ_validation(self):
        n0 = node(0, '', {}, {2: 1})
        n2 = node(2, '', {0: 1}, {3: 1})
        n3 = node(3, '~', {2: 1}, {1: 1}) 
        n1 = node(1, '', {3: 1}, {})
        g_valid = open_digraph([0], [1], [n0, n1, n2, n3])

        bc = bool_circ(g_valid)
        self.assertIsInstance(bc, bool_circ)
        
        n_and = node(4, '&', {0: 1}, {1: 2})
        g_invalid = open_digraph([0], [1], [n0, n1, n_and])
        
        with self.assertRaises(ValueError):
            bool_circ(g_invalid)
            
        n2_cycle = node(2, '', {3: 1}, {3: 1})
        n3_cycle = node(3, '~', {2: 1}, {2: 1})
        g_cycle = open_digraph([], [], [n2_cycle, n3_cycle])
        
        with self.assertRaises(ValueError):
            bool_circ(g_cycle)

    def test_random_bool_circ(self):
        for _ in range(10):
            bc = bool_circ.random_bool_circ(n=10, bound=2)
            self.assertIsInstance(bc, bool_circ)
            self.assertTrue(bc.is_well_formed())

    def test_random_bool_circ_with_io(self):
        for _ in range(10):
            bc = bool_circ.random_bool_circ_with_io(n=10, bound=2, nb_inputs=3, nb_outputs=2)
            self.assertIsInstance(bc, bool_circ)
            self.assertEqual(len(bc.get_input_ids()), 3)
            self.assertEqual(len(bc.get_output_ids()), 2)
            self.assertTrue(bc.is_well_formed())
    
    def test_parsing_formules(self):
        formule = "((x0)&(x1))"
        arbre = bool_circ.parse_from_string(formule)
        
        self.assertEqual(len(arbre.get_node_ids()), 4)
        self.assertEqual(len(arbre.get_output_ids()), 1)
        
        formule_repete = "((x0)&(x0))"
        circuit, variables = bool_circ.from_string(formule_repete)
        
        self.assertEqual(variables, ['x0'])
        self.assertEqual(len(circuit.get_node_ids()), 4)
        self.assertTrue(circuit.is_well_formed())
        self.assertEqual(len(circuit.get_input_ids()), 1)
        #ex4 Td9
        f1 = "((x0)&(x1))"
        f2 = "(~(x1))"
        circuit_multi, variables_multi = bool_circ.from_string(f1, f2)

        self.assertTrue(circuit_multi.is_well_formed())
        self.assertEqual(len(circuit_multi.get_output_ids()), 2)
        self.assertEqual(len(circuit_multi.get_input_ids()), 2)
        self.assertCountEqual(variables_multi, ['x0', 'x1'])
    


if __name__ == '__main__':
    unittest.main(verbosity=2)