from modules.open_digraph import open_digraph

class BoolCircParse:
    @classmethod
    def parse_from_string(cls, s):
        """
        Construit un arbre à partir d'une formule propositionnelle parenthésée.
        Retourne un open_digraph
        """
        circuit = open_digraph.empty()
        current_node = circuit.add_node(label="")
        circuit.add_output_id(current_node)
        s2 = ""
        for char in s:
            if char == '(':
                if s2:
                    noeud = circuit.get_node_by_id(current_node)
                    noeud.set_label(noeud.get_label() + s2)
                parent_id = circuit.add_node(label="")
                circuit.add_edge(parent_id, current_node)
                current_node = parent_id
                s2 = ""    
            elif char == ')':
                if s2:
                    noeud = circuit.get_node_by_id(current_node)
                    noeud.set_label(noeud.get_label() + s2)
                noeud = circuit.get_node_by_id(current_node)
                enfants = list(noeud.get_children().keys())
                if enfants:
                    current_node = enfants[0]
                    
                s2 = ""   
            else:
                s2 += char
                
        # Assurer que les noeuds de sortie sont des noeuds vides (fils) sans label
        out_ids = circuit.get_output_ids().copy()
        for out_id in out_ids:
            out_node = circuit.get_node_by_id(out_id)
            if out_node.get_label() != "":
                new_out_id = circuit.add_node(label="")
                circuit.add_edge(out_id, new_out_id)
                circuit.outputs.remove(out_id)
                circuit.add_output_id(new_out_id)
                
        return circuit

    @classmethod
    def from_string(cls, *args):
        """
        Construit un vrai circuit booléen à partir de plusieurs formules.
        Regroupe les variables identiques, et gère plusieurs sorties
        Prend un nombre variable de chaînes de caractères en argument
        """
        if not args:
            raise ValueError("Il faut au moins une formule en argument")
        arbre_global = cls.parse_from_string(args[0])

        for s in args[1:]:
            arbre_temp = cls.parse_from_string(s)
            arbre_global = arbre_global.comp_parallel(arbre_temp)
        variables_vues = {}
        noms_variables = []
        feuilles = [n.get_id() for n in arbre_global.get_nodes() if not n.get_parents()]
        for id_feuille in feuilles:
            noeud = arbre_global.get_node_by_id(id_feuille)
            nom_var = noeud.get_label()
            if not nom_var:
                continue
            if nom_var not in variables_vues:
                variables_vues[nom_var] = id_feuille
                noms_variables.append(nom_var)
                arbre_global.add_input_node(id_feuille)  
                noeud.set_label("")
            else:
                id_premier = variables_vues[nom_var]
                arbre_global.merge_nodes(id_premier, id_feuille)
                
        circuit_final = cls(arbre_global)
        
        return circuit_final, noms_variables
