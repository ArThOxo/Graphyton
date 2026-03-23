from modules.open_digraph import open_digraph

class bool_circ(open_digraph):
    def __init__(self, g):
        super().__init__(g.get_input_ids().copy(), 
                         g.get_output_ids().copy(), 
                         [n.copy() for n in g.get_nodes()])
        
        if not self.is_well_formed():
            raise ValueError("Le graphe fourni n'est pas un circuit booléen valide")

    def is_well_formed(self):
        if not super().is_well_formed():
            return False
            
        if self.is_cyclic():
            return False
            
        for n in self.get_nodes():
            if n.get_id() in self.get_input_ids() or n.get_id() in self.get_output_ids():
                continue
                
            label = n.get_label()
            indeg = n.indegree()
            outdeg = n.outdegree()
            
            if label == '': 
                if indeg != 1:
                    return False
                    
            elif label == '&' or label == '|': 
                if outdeg != 1:
                    return False
                    
            elif label == '~': 
                if indeg != 1 or outdeg != 1:
                    return False
                    
            elif label == '0' or label == '1':
                if indeg != 0 or outdeg != 1:
                    return False
                    
        return True