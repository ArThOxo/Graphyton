from modules.open_digraph import open_digraph

from modules.bool_circ_eval import BoolCircEval
from modules.bool_circ_adders import BoolCircAdders
from modules.bool_circ_parse import BoolCircParse
from modules.bool_circ_gen import BoolCircGen

class bool_circ(open_digraph, BoolCircEval, BoolCircAdders, BoolCircParse, BoolCircGen):
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
                # Copie : indegree == 1, outdegree libre (0 = effacement de données)
                if indeg != 1:
                    return False      
            elif label in ('&', '|', '^'): 
                # Portes logiques : outdegree == 1
                if outdeg != 1:
                    return False       
            elif label == '~': 
                # Porte NON : indegree == 1, outdegree == 1
                if indeg != 1 or outdeg != 1:
                    return False      
            elif label in ('0', '1'):
                # Constantes : indegree == 0 (sources pures)
                if indeg != 0:
                    return False
                    
        return True