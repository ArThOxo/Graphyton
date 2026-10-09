import os
import re
import urllib.parse
import webbrowser
import tempfile

from modules.node import node
from modules.matrix import OpenDigraphMatrix
from modules.composition import OpenDigraphComposition
from modules.algo_tout_genre import OpenDigraphAlgoToutGenre

class open_digraph(OpenDigraphMatrix, OpenDigraphComposition, OpenDigraphAlgoToutGenre):
    def __init__(self, inputs, outputs, nodes):
        self.inputs = inputs
        self.outputs = outputs
        self.nodes = {node.id:node for node in nodes}
    def __str__ (self):
        return "Input :" + str(self.inputs) + ", outputs:" + str(self.outputs) + ", Noeuds:" + str(self.nodes.__str__())
    def __repr__(self):
        return self.__str__()
    def copy(self):
        new_nodes = [n.copy() for n in self.nodes.values()]
        y = self.__class__(self.inputs.copy(), self.outputs.copy(), new_nodes)
        return y

    @classmethod
    def empty(cls):
        return cls([], [], [])

    # GETTERS

    def get_input_ids(self):
        return self.inputs
    
    def get_output_ids(self):
        return self.outputs

    def get_id_node_map(self):
        return self.nodes 
    
    def get_nodes(self):
        return list(self.nodes.values())
    
    def get_node_ids(self):
        return list(self.nodes.keys())
    
    def get_node_by_id(self, id):
        return self.nodes[id]

    def get_nodes_by_ids (self, ids):
        return [self.nodes[node_id] for node_id in ids]

     
    # SETTERS
    def set_inputs (self , newInputs):
        self.inputs = newInputs

    def set_outputs (self, newOuputs):
        self.outputs = newOuputs

    def add_input_id (self , inID):
        if inID not in self.inputs:
            self.inputs.append(inID)

    def add_output_id (self , outID):
        if outID not in self.outputs:
            self.outputs.append(outID)
    

    # AJOUT DE NOEUDS ET ARÊTES

    def new_id(self):
        ids = self.get_node_ids()
        if not ids:
            return 0
        return max(ids) + 1

    def add_node(self, label='', parents=None, children=None):
        if parents is None:
            parents = {}
        if children is None:
            children = {}

        new_id = self.new_id() 
        new_n = node(new_id, label, parents.copy(), children.copy()) 
        self.nodes[new_id] = new_n 

        for parent_id, multiplicity in parents.items():
            if parent_id in self.nodes:
                parent_node = self.nodes[parent_id]
                parent_node.add_child_id(new_id, multiplicity)
            
        for child_id, multiplicity in children.items():
            if child_id in self.nodes:
                child_node = self.nodes[child_id]
                child_node.add_parent_id(new_id, multiplicity) 

        return new_id

    def add_edge(self, src, tgt):
        self.nodes[src].add_child_id(tgt)
        self.nodes[tgt].add_parent_id(src)

    def add_edges(self, edges): 
        for src, tgt in edges:
            self.add_edge(src, tgt)


    def remove_edge(self, src, tgt):
        if src not in self.nodes:
            raise KeyError(f"Le noeud source {src} n'existe pas dans le graphe.")
        if tgt not in self.nodes:
            raise KeyError(f"Le noeud cible {tgt} n'existe pas dans le graphe.")
        
        self.nodes[src].remove_child_once(tgt)
        self.nodes[tgt].remove_parent_once(src)

    def remove_parallel_edges(self, src, tgt):
        if src not in self.nodes:
            raise KeyError(f"Le noeud source {src} n'existe pas dans le graphe.")
        if tgt not in self.nodes:
            raise KeyError(f"Le noeud cible {tgt} n'existe pas dans le graphe.")
            
        self.nodes[src].remove_child_id(tgt)
        self.nodes[tgt].remove_parent_id(src)

    def remove_edges(self, edges):
        for src, tgt in edges:
            self.remove_edge(src, tgt)
    
    def remove_several_parallel_edges(self, edges):
        for src, tgt in edges:
            self.remove_parallel_edges(src, tgt)


    def remove_node_by_id(self, id):
        n = self.nodes[id]
        for parent_id in list(n.get_parents().keys()):
            self.remove_parallel_edges(parent_id, id)
        for child_id in list(n.get_children().keys()):
            self.remove_parallel_edges(id, child_id)
            
        self.nodes.pop(id)
        if id in self.inputs:
            self.inputs.remove(id)
        if id in self.outputs:
            self.outputs.remove(id)

    def remove_nodes_by_id(self, ids):
        for id in ids:
            self.remove_node_by_id(id)


    # INTÉGRITÉ

    def is_well_formed(self):
        # Vérification des inputs
        for in_id in self.inputs:
            if in_id not in self.nodes:
                return False
            n = self.nodes[in_id]
            if len(n.get_parents()) != 0 or len(n.get_children()) != 1 or list(n.get_children().values())[0] != 1:
                return False

        # Vérification des outputs
        for out_id in self.outputs:
            if out_id not in self.nodes:
                return False
            n = self.nodes[out_id]
            if len(n.get_children()) != 0 or len(n.get_parents()) != 1 or list(n.get_parents().values())[0] != 1:
                return False
        
        # Vérification de la réciprocité de toutes les arêtes
        for node_id, n in self.nodes.items():
            if node_id != n.get_id():
                return False 
            
            for child_id, mult in n.get_children().items():
                if child_id not in self.nodes:
                    return False
                child_node = self.nodes[child_id]
                if node_id not in child_node.get_parents() or child_node.get_parents()[node_id] != mult:
                    return False

            for parent_id, mult in n.get_parents().items():
                if parent_id not in self.nodes:
                    return False
                parent_node = self.nodes[parent_id]
                if node_id not in parent_node.get_children() or parent_node.get_children()[node_id] != mult:
                    return False
        return True

    def assert_is_well_formed(self):
        if not self.is_well_formed():
            raise ValueError("Le graphe n'est pas bien formé.")



    def is_cyclic(self):
        out_degrees = {n.get_id(): n.outdegree() for n in self.get_nodes()}
        leaves = [node_id for node_id, deg in out_degrees.items() if deg == 0]
        visited_count = 0
        
        while leaves:
            leaf_id = leaves.pop()
            visited_count += 1
            leaf_node = self.get_node_by_id(leaf_id)
            for parent_id, multiplicity in leaf_node.get_parents().items():
                out_degrees[parent_id] -= multiplicity
                if out_degrees[parent_id] == 0:
                    leaves.append(parent_id)
                    
        return visited_count != len(self.get_nodes())
    


    def add_input_node(self, target_id):
        if target_id not in self.nodes:
            raise ValueError(f"Le noeud cible {target_id} n'existe pas.")
        new_id = self.add_node(label="") 
        self.add_edge(new_id, target_id)
        self.inputs.append(new_id)
        self.assert_is_well_formed()
        return new_id

    def add_output_node(self, source_id):
        if source_id not in self.nodes:
            raise ValueError(f"Le noeud source {source_id} n'existe pas.")
        new_id = self.add_node(label="") 
        self.add_edge(source_id, new_id)
        self.outputs.append(new_id)
        self.assert_is_well_formed()
        return new_id

    def get_node_id_to_index_map(self):
        return {node_id: index for index, node_id in enumerate(self.nodes.keys())}

    def save_as_dot_file(self, path, verbose=False):
        with open(path, 'w') as f:
            f.write("digraph G {\n")
            
            for n_id, n in self.nodes.items():
                label = n.get_label()
                if verbose:
                    label = f"ID:{n.get_id()} - {label}"
                
                attrs = [f'label="{label}"']
                
                if n_id in self.inputs:
                    attrs.append('is_input="True"')
                if n_id in self.outputs:
                    attrs.append('is_output="True"')
                
                f.write(f'    v{n_id} [{", ".join(attrs)}];\n')
                
            for n_id, n in self.nodes.items():
                for child_id, multiplicity in n.get_children().items():
                    for _ in range(multiplicity):
                        f.write(f'    v{n_id} -> v{child_id};\n')
                        
            f.write("}\n")


    @classmethod
    def from_dot_file(cls, path):
        g = cls.empty()
        with open(path, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            node_match = re.match(r'v(\d+)\s*\[(.*label="(.*?)".*)\];', line)
            if node_match:
                n_id = int(node_match.group(1))
                label = node_match.group(3)
                if n_id not in g.nodes:
                    g.nodes[n_id] = node(n_id, label, {}, {})
                else:
                    g.nodes[n_id].set_label(label)
                    
                if 'is_input="True"' in line:
                    g.add_input_id(n_id)
                if 'is_output="True"' in line:
                    g.add_output_id(n_id)
                    
            edge_match = re.match(r'v(\d+)\s*->\s*v(\d+);', line)
            if edge_match:
                src = int(edge_match.group(1))
                tgt = int(edge_match.group(2))
                if src not in g.nodes:
                    g.nodes[src] = node(src, "", {}, {})
                if tgt not in g.nodes:
                    g.nodes[tgt] = node(tgt, "", {}, {})
                g.add_edge(src, tgt)
        return g

    def display(self, verbose=False):
        temp_dir = tempfile.gettempdir()
        dot_path = os.path.join(temp_dir, "temp_graph.dot")
        self.save_as_dot_file(dot_path, verbose=verbose)
        
        with open(dot_path, 'r') as f:
            dot_content = f.read()
            
        encoded_dot = urllib.parse.quote(dot_content)
        url = f"https://dreampuf.github.io/GraphvizOnline/#{encoded_dot}"
        webbrowser.open(url)



    def min_id(self):
        if not self.nodes:
            return 0
        return min(self.nodes.keys())

    def max_id(self):
        if not self.nodes:
            return 0
        return max(self.nodes.keys())

    def shift_indices(self, n):
       
        self.inputs = [i + n for i in self.inputs]
        self.outputs = [i + n for i in self.outputs]

        new_nodes = {}
        
        for old_id, node_obj in self.nodes.items():
            new_id = old_id + n
            
            node_obj.set_id(new_id)
            
            new_parents = {p_id + n: mult for p_id, mult in node_obj.get_parents().items()}
            new_children = {c_id + n: mult for c_id, mult in node_obj.get_children().items()}
            
            node_obj.set_parents(new_parents)
            node_obj.set_children(new_children)
            
            new_nodes[new_id] = node_obj
            
        self.nodes = new_nodes