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


#TD9

    @classmethod
    def parse_from_string(cls, s):
        """
        Construit un arbre à partir d'une formule propositionnelle parenthésée.
        Retourne un open_digraph
        """
        # On crée un open_digraph vide car l'arbre n'est pas encore un circuit booléen valide
        circuit = open_digraph.empty()
        
        # on crée un noeud initial et on l'ajoute aux sorties
        current_node = circuit.add_node(label="")
        circuit.add_output_id(current_node)
        
        s2 = ""
        
        for char in s:
            if char == '(':
                # Ajouter s2 au label de current_node
                if s2:
                    noeud = circuit.get_node_by_id(current_node)
                    noeud.set_label(noeud.get_label() + s2)
                
                # Créer un parent à current_node
                parent_id = circuit.add_node(label="")
                circuit.add_edge(parent_id, current_node)
                
                # Mettre ce nouveau parent dans current_node
                current_node = parent_id
                s2 = ""
                
            elif char == ')':
                # Ajouter s2 au label de current_node
                if s2:
                    noeud = circuit.get_node_by_id(current_node)
                    noeud.set_label(noeud.get_label() + s2)
                
                # Remplacer current_node par son fils
                noeud = circuit.get_node_by_id(current_node)
                enfants = list(noeud.get_children().keys())
                
                # Comme on construit un arbre vers le bas, il a toujours un seul enfant direct
                if enfants:
                    current_node = enfants[0]
                    
                s2 = ""
                
            else:
                # Ajouter le caractère à la fin de s2
                s2 += char
                
        return circuit


    @classmethod
    def from_string(cls, s):
        """
        Construit un vrai circuit booléen à partir d'une formule.
        Regroupe les variables identiques, nettoie les labels et retourne le tuple (bool_circ, liste_variables).
        """
        # on utilise notre méthode de l'exo 1 pour avoir l'arbre brut
        arbre = cls.parse_from_string(s)
        
        variables_vues = {} # Dict {nom_variable: id_noeud}
        noms_variables = [] # Liste pour garder le bon ordre
        
        # on identifie les feuilles de l'arbre  ce qui portent temporairement les noms des variables
        feuilles = [n.get_id() for n in arbre.get_nodes() if not n.get_parents()]
        
        for id_feuille in feuilles:
            noeud = arbre.get_node_by_id(id_feuille)
            nom_var = noeud.get_label()
            
            # Cas 1 :  nouvelle variable
            if nom_var not in variables_vues:
                variables_vues[nom_var] = id_feuille
                noms_variables.append(nom_var)
                
                # On la définit comme une entrée officielle du graphe
                arbre.add_input_node(id_feuille)
                
                # On supprime le texte pour que le circuit soit bien formé
                noeud.set_label("")
                
            # Cas 2 : on a déjà vu cette variable ailleurs
            else:
                id_premier = variables_vues[nom_var]
                # on fusionne le noeud actuel dans le premier noeud trouvé
                arbre.merge_nodes(id_premier, id_feuille)
                
        # le graphe est nettoyé et bien formé, donc on peut l'encapsuler dans notre classe bool_circ
        circuit_final = cls(arbre)
        
        return circuit_final, noms_variables