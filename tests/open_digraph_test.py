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
    
    def test_adder(self):
        # Test Adder0 (1 bit)
        adder0 = bool_circ.Adder(0)
        self.assertIsInstance(adder0, bool_circ)
        self.assertEqual(len(adder0.get_input_ids()), 3)
        self.assertEqual(len(adder0.get_output_ids()), 2)
        self.assertTrue(adder0.is_well_formed())
        
        # Test Adder1 (2 bits)
        adder1 = bool_circ.Adder(1)
        self.assertIsInstance(adder1, bool_circ)
        self.assertEqual(len(adder1.get_input_ids()), 5)
        self.assertEqual(len(adder1.get_output_ids()), 3)
        self.assertTrue(adder1.is_well_formed())
        
        # Test Adder2 (4 bits)
        adder2 = bool_circ.Adder(2)
        self.assertIsInstance(adder2, bool_circ)
        self.assertEqual(len(adder2.get_input_ids()), 9)
        self.assertEqual(len(adder2.get_output_ids()), 5)
        self.assertTrue(adder2.is_well_formed())

    def test_half_adder(self):
        # Test Half_Adder0 (1 bit, sans carry_in)
        ha0 = bool_circ.Half_Adder(0)
        self.assertIsInstance(ha0, bool_circ)
        self.assertEqual(len(ha0.get_input_ids()), 2)
        self.assertEqual(len(ha0.get_output_ids()), 2)
        self.assertTrue(ha0.is_well_formed())
        
        # Test Half_Adder1 (2 bits, sans carry_in)
        ha1 = bool_circ.Half_Adder(1)
        self.assertIsInstance(ha1, bool_circ)
        self.assertEqual(len(ha1.get_input_ids()), 4)
        self.assertEqual(len(ha1.get_output_ids()), 3)
        self.assertTrue(ha1.is_well_formed())


# TD11 Exercice 3 : tests des règles de transformation

class TransformTest(unittest.TestCase):
    """Tests unitaires pour chaque règle de transformation booléenne."""

    # _transform_copy

    def test_transform_copy_propagates_zero(self):
        n0 = node(0, '0', {}, {1: 1})
        n1 = node(1, '',  {0: 1}, {2: 1, 3: 1})
        n2 = node(2, '',  {1: 1}, {})
        n3 = node(3, '',  {1: 1}, {})
        g = open_digraph([], [2, 3], [n0, n1, n2, n3])
        bc = bool_circ.__new__(bool_circ)
        bc.__init__.__func__ if False else None
        open_digraph.__init__(bc, g.get_input_ids(), g.get_output_ids(),
                              [n.copy() for n in g.get_nodes()])

        result = bc._transform_copy(1)
        self.assertTrue(result)
        self.assertNotIn(0, bc.get_node_ids())
        self.assertNotIn(1, bc.get_node_ids())
        for out_id in [2, 3]:
            parents = bc.get_node_by_id(out_id).get_parents()
            parent_labels = [bc.get_node_by_id(pid).get_label() for pid in parents]
            self.assertIn('0', parent_labels)

    def test_transform_copy_propagates_one(self):
        n0 = node(0, '1', {}, {1: 1})
        n1 = node(1, '',  {0: 1}, {2: 1})
        n2 = node(2, '',  {1: 1}, {})
        g = open_digraph([], [2], [n0, n1, n2])
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [2], [n.copy() for n in g.get_nodes()])

        self.assertTrue(bc._transform_copy(1))
        self.assertNotIn(1, bc.get_node_ids())
        parent_labels = [bc.get_node_by_id(pid).get_label()
                         for pid in bc.get_node_by_id(2).get_parents()]
        self.assertIn('1', parent_labels)

    def test_transform_copy_no_const_parent(self):
        n0 = node(0, 'x', {}, {1: 1})
        n1 = node(1, '',  {0: 1}, {2: 1})
        n2 = node(2, '',  {1: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [2], [n0.copy(), n1.copy(), n2.copy()])
        self.assertFalse(bc._transform_copy(1))

    # _transform_not

    def test_transform_not_zero_gives_one(self):
        n0 = node(0, '0', {}, {1: 1})
        n1 = node(1, '~', {0: 1}, {2: 1})
        n2 = node(2, '',  {1: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [2], [n0.copy(), n1.copy(), n2.copy()])

        self.assertTrue(bc._transform_not(1))
        self.assertNotIn(1, bc.get_node_ids())
        parent_labels = [bc.get_node_by_id(pid).get_label()
                         for pid in bc.get_node_by_id(2).get_parents()]
        self.assertIn('1', parent_labels)

    def test_transform_not_one_gives_zero(self):
        n0 = node(0, '1', {}, {1: 1})
        n1 = node(1, '~', {0: 1}, {2: 1})
        n2 = node(2, '',  {1: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [2], [n0.copy(), n1.copy(), n2.copy()])

        self.assertTrue(bc._transform_not(1))
        parent_labels = [bc.get_node_by_id(pid).get_label()
                         for pid in bc.get_node_by_id(2).get_parents()]
        self.assertIn('0', parent_labels)

    def test_transform_not_wrong_label(self):
        n0 = node(0, '0', {}, {1: 1})
        n1 = node(1, '&', {0: 1}, {2: 1})
        n2 = node(2, '',  {1: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [2], [n0.copy(), n1.copy(), n2.copy()])
        self.assertFalse(bc._transform_not(1))

    # _transform_and

    def test_transform_and_zero_absorbing(self):
        n0 = node(0, '0', {}, {2: 1})
        n1 = node(1, 'x', {}, {2: 1})
        n2 = node(2, '&', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '',  {2: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [3], [n0.copy(), n1.copy(), n2.copy(), n3.copy()])

        self.assertTrue(bc._transform_and(2))
        self.assertNotIn(2, bc.get_node_ids())
        parent_labels = [bc.get_node_by_id(pid).get_label()
                         for pid in bc.get_node_by_id(3).get_parents()]
        self.assertIn('0', parent_labels)

    def test_transform_and_one_neutral(self):
        n0 = node(0, '1', {}, {2: 1})
        n1 = node(1, 'x', {}, {2: 1})
        n2 = node(2, '&', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '',  {2: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [3], [n0.copy(), n1.copy(), n2.copy(), n3.copy()])

        self.assertTrue(bc._transform_and(2))
        self.assertNotIn(0, bc.get_node_ids())
        self.assertIn(2, bc.get_node_ids())

    def test_transform_and_no_const(self):
        n0 = node(0, 'x', {}, {2: 1})
        n1 = node(1, 'y', {}, {2: 1})
        n2 = node(2, '&', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '',  {2: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [3], [n0.copy(), n1.copy(), n2.copy(), n3.copy()])
        self.assertFalse(bc._transform_and(2))

    # _transform_or

    def test_transform_or_one_absorbing(self):
        n0 = node(0, '1', {}, {2: 1})
        n1 = node(1, 'x', {}, {2: 1})
        n2 = node(2, '|', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '',  {2: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [3], [n0.copy(), n1.copy(), n2.copy(), n3.copy()])

        self.assertTrue(bc._transform_or(2))
        self.assertNotIn(2, bc.get_node_ids())
        parent_labels = [bc.get_node_by_id(pid).get_label()
                         for pid in bc.get_node_by_id(3).get_parents()]
        self.assertIn('1', parent_labels)

    def test_transform_or_zero_neutral(self):
        n0 = node(0, '0', {}, {2: 1})
        n1 = node(1, 'x', {}, {2: 1})
        n2 = node(2, '|', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '',  {2: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [3], [n0.copy(), n1.copy(), n2.copy(), n3.copy()])

        self.assertTrue(bc._transform_or(2))
        self.assertNotIn(0, bc.get_node_ids())
        self.assertIn(2, bc.get_node_ids())

    # _transform_xor

    def test_transform_xor_zero_neutral(self):
        n0 = node(0, '0', {}, {2: 1})
        n1 = node(1, 'x', {}, {2: 1})
        n2 = node(2, '^', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '',  {2: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [3], [n0.copy(), n1.copy(), n2.copy(), n3.copy()])

        self.assertTrue(bc._transform_xor(2))
        self.assertNotIn(0, bc.get_node_ids())
        self.assertIn(2, bc.get_node_ids())

    def test_transform_xor_one_negates(self):
        n0 = node(0, '1', {}, {2: 1})
        n1 = node(1, 'x', {}, {2: 1})
        n2 = node(2, '^', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '',  {2: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [3], [n0.copy(), n1.copy(), n2.copy(), n3.copy()])

        self.assertTrue(bc._transform_xor(2))
        self.assertNotIn(0, bc.get_node_ids())
        self.assertIn(2, bc.get_node_ids())
        xor_children = bc.get_node_by_id(2).get_children()
        not_labels = [bc.get_node_by_id(c).get_label() for c in xor_children]
        self.assertIn('~', not_labels)

    # _transform_neutral

    def test_transform_neutral_and_zero_inputs(self):
        n0 = node(0, '&', {}, {1: 1})
        n1 = node(1, '',  {0: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [1], [n0.copy(), n1.copy()])

        self.assertTrue(bc._transform_neutral(0))
        self.assertNotIn(0, bc.get_node_ids())
        parent_labels = [bc.get_node_by_id(pid).get_label()
                         for pid in bc.get_node_by_id(1).get_parents()]
        self.assertIn('1', parent_labels)

    def test_transform_neutral_or_zero_inputs(self):
        n0 = node(0, '|', {}, {1: 1})
        n1 = node(1, '',  {0: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [1], [n0.copy(), n1.copy()])

        self.assertTrue(bc._transform_neutral(0))
        parent_labels = [bc.get_node_by_id(pid).get_label()
                         for pid in bc.get_node_by_id(1).get_parents()]
        self.assertIn('0', parent_labels)

    def test_transform_neutral_single_input_becomes_wire(self):
        n0 = node(0, 'x', {}, {1: 1})
        n1 = node(1, '&', {0: 1}, {2: 1})
        n2 = node(2, '',  {1: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [2], [n0.copy(), n1.copy(), n2.copy()])

        self.assertTrue(bc._transform_neutral(1))
        self.assertIn(1, bc.get_node_ids())
        self.assertEqual(bc.get_node_by_id(1).get_label(), '')

    def test_transform_neutral_no_effect_two_inputs(self):
        n0 = node(0, 'x', {}, {2: 1})
        n1 = node(1, 'y', {}, {2: 1})
        n2 = node(2, '&', {0: 1, 1: 1}, {3: 1})
        n3 = node(3, '',  {2: 1}, {})
        bc = open_digraph.__new__(bool_circ)
        open_digraph.__init__(bc, [], [3], [n0.copy(), n1.copy(), n2.copy(), n3.copy()])
        self.assertFalse(bc._transform_neutral(2))


# TD11 Exercice 4 : evaluate

class EvaluateTest(unittest.TestCase):
    """Tests pour bool_circ.evaluate()."""

    def test_evaluate_not(self):
        circuit, _ = bool_circ.from_string("(~(x))")
        result = circuit.evaluate([0])
        self.assertEqual(result, [1])

    def test_evaluate_not_one(self):
        circuit, _ = bool_circ.from_string("(~(x))")
        result = circuit.evaluate([1])
        self.assertEqual(result, [0])

    def test_evaluate_and(self):
        circuit, _ = bool_circ.from_string("((x0)&(x1))")
        self.assertEqual(circuit.evaluate([0, 0]), [0])
        self.assertEqual(circuit.evaluate([0, 1]), [0])
        self.assertEqual(circuit.evaluate([1, 0]), [0])
        self.assertEqual(circuit.evaluate([1, 1]), [1])

    def test_evaluate_or(self):
        circuit, _ = bool_circ.from_string("((x0)|(x1))")
        self.assertEqual(circuit.evaluate([0, 0]), [0])
        self.assertEqual(circuit.evaluate([0, 1]), [1])
        self.assertEqual(circuit.evaluate([1, 0]), [1])
        self.assertEqual(circuit.evaluate([1, 1]), [1])

    def test_evaluate_xor(self):
        circuit, _ = bool_circ.from_string("((x0)^(x1))")
        self.assertEqual(circuit.evaluate([0, 0]), [0])
        self.assertEqual(circuit.evaluate([0, 1]), [1])
        self.assertEqual(circuit.evaluate([1, 0]), [1])
        self.assertEqual(circuit.evaluate([1, 1]), [0])

    def test_evaluate_multi_output(self):
        circuit, _ = bool_circ.from_string("((x0)&(x1))", "(~(x0))")
        result = circuit.evaluate([1, 0])
        self.assertEqual(result, [0, 0])
        result2 = circuit.evaluate([0, 1])
        self.assertEqual(result2, [0, 1])

    def test_evaluate_constant_circuit(self):
        bc = bool_circ.from_integer(0, size=1)
        result = bc.evaluate([])
        self.assertEqual(result, [0])

    def test_evaluate_constant_circuit_one(self):
        bc = bool_circ.from_integer(1, size=1)
        result = bc.evaluate([])
        self.assertEqual(result, [1])


# TD11 Exercice 5 : évaluation sur entiers encodés

class IntegerEvalTest(unittest.TestCase):
    """Tests pour l'évaluation du Half_Adder sur des entiers."""

    def _int_to_bits(self, n, size):
        return [int(b) for b in bin(n)[2:].zfill(size)]

    def test_half_adder0_all_cases(self):
        ha = bool_circ.Half_Adder(0)
        for a in range(2):
            for b in range(2):
                expected_sum = (a + b) % 2
                expected_carry = (a + b) // 2
                result = ha.evaluate([a, b])
                self.assertEqual(result, [expected_sum, expected_carry],
                                 msg=f"HA(0)({a},{b}) attendu [{expected_sum},{expected_carry}] obtenu {result}")

    def test_half_adder1_addition(self):
        ha = bool_circ.Half_Adder(1)
        test_cases = [(0, 0), (1, 2), (3, 1), (2, 2)]
        for a, b in test_cases:
            bits_a = [int(x) for x in bin(a)[2:].zfill(2)[::-1]]
            bits_b = [int(x) for x in bin(b)[2:].zfill(2)[::-1]]
            result = ha.evaluate(bits_a + bits_b)
            r_bits = result[:-1]
            carry = result[-1]
            r_val = int(''.join(str(x) for x in r_bits[::-1]), 2)
            total = r_val + carry * (2 ** len(r_bits))
            self.assertEqual(total, a + b,
                             msg=f"HA(1)({a}+{b}): attendu {a+b}, obtenu {total}")

    def test_from_integer_encoding(self):
        for n in range(8):
            bc = bool_circ.from_integer(n, size=8)
            result = bc.evaluate([])
            expected = self._int_to_bits(n, 8)
            self.assertEqual(result, expected, msg=f"from_integer({n}) : {result} != {expected}")

    # TD11 Exercice 6 : Évaluation de l'additionneur

    def test_adder0_all_cases(self):
        adder = bool_circ.Adder(0)
        for a in range(2):
            for b in range(2):
                for cin in range(2):
                    expected_sum = (a + b + cin) % 2
                    expected_carry = (a + b + cin) // 2
                    result = adder.evaluate([a, b, cin])
                    self.assertEqual(result, [expected_sum, expected_carry],
                                     msg=f"Adder(0)({a}+{b}+{cin}) attendu [{expected_sum},{expected_carry}] obtenu {result}")

    def test_adder1_addition(self):
        adder = bool_circ.Adder(1)
        test_cases = [(0, 0, 0), (1, 2, 0), (3, 1, 1), (2, 2, 1), (3, 3, 1)]
        for a, b, cin in test_cases:
            bits_a = [int(x) for x in bin(a)[2:].zfill(2)[::-1]]
            bits_b = [int(x) for x in bin(b)[2:].zfill(2)[::-1]]
            
            result = adder.evaluate(bits_a + bits_b + [cin])
            
            r_bits = result[:-1]
            carry = result[-1]
            r_val = int(''.join(str(x) for x in r_bits[::-1]), 2)
            total = r_val + carry * (4) # 2^2 = 4
            self.assertEqual(total, a + b + cin,
                             msg=f"Adder(1)({a}+{b}+{cin}): attendu {a+b+cin}, obtenu {total}")

    def test_adder2_addition(self):
        adder = bool_circ.Adder(2)
        import random
        random.seed(42)
        test_cases = [(0, 0, 0), (15, 15, 1), (15, 0, 1), (7, 8, 0)]
        for _ in range(10):
            test_cases.append((random.randint(0, 15), random.randint(0, 15), random.randint(0, 1)))
            
        for a, b, cin in test_cases:
            bits_a = [int(x) for x in bin(a)[2:].zfill(4)[::-1]]
            bits_b = [int(x) for x in bin(b)[2:].zfill(4)[::-1]]
            
            result = adder.evaluate(bits_a + bits_b + [cin])
            
            r_bits = result[:-1]
            carry = result[-1]
            r_val = int(''.join(str(x) for x in r_bits[::-1]), 2)
            total = r_val + carry * (16)
            self.assertEqual(total, a + b + cin,
                             msg=f"Adder(2)({a}+{b}+{cin}): attendu {a+b+cin}, obtenu {total}")


if __name__ == '__main__':
    unittest.main(verbosity=2)