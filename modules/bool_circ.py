from modules.open_digraph import open_digraph
import random

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
                    
            elif label == '&' or label == '|' or label == '^': 
                if outdeg != 1:
                    return False
                    
            elif label == '~': 
                if indeg != 1 or outdeg != 1:
                    return False
                    
            elif label == '0' or label == '1':
                if indeg != 0 or outdeg != 1:
                    return False
                    
        return True

    @classmethod
    def random_bool_circ(cls, n, bound):
        """
        TD10: Exercice 1
        Génère un circuit booléen aléatoire valide.
        """
        g = open_digraph.random(n, bound, form="DAG")
        
        # 1. Supprimer les noeuds isolés
        node_ids = set(g.get_node_ids())
        for node_id in node_ids:
            node = g.get_node_by_id(node_id)
            if node.indegree() == 0 and node.outdegree() == 0:
                g.remove_node_by_id(node_id)
                
        # On récupère les IDs des noeuds originels restants
        original_node_ids = g.get_node_ids()
        
        # S'il ne reste aucun noeud, on retourne un circuit vide
        if not original_node_ids:
            return cls(g)
        
        # 2. Ajouter les inputs et outputs
        for node_id in original_node_ids:
            node = g.get_node_by_id(node_id)
            if node.indegree() == 0:
                g.add_input_node(node_id)
            if node.outdegree() == 0:
                g.add_output_node(node_id)
        
        # 3. Assigner les labels et traiter les sorties multiples (fan-out)
        for node_id in original_node_ids:
            node = g.get_node_by_id(node_id)
            indeg = node.indegree()
            outdeg = node.outdegree()
            
            if indeg == 1:
                node.set_label(random.choice(['', '~']))
            elif indeg >= 2 and outdeg == 1:
                node.set_label(random.choice(['&', '|', '^']))
            elif indeg >= 2 and outdeg >= 2:
                # Porte logique avec fan-out
                node.set_label(random.choice(['&', '|', '^']))
                # On crée un noeud de copie
                copy_id = g.add_node(label='')
                # On déplace les enfants vers le noeud de copie
                children = list(node.get_children().items())
                for child_id, mult in children:
                    g.remove_parallel_edges(node_id, child_id)
                    for _ in range(mult):
                        g.add_edge(copy_id, child_id)
                # On relie la porte au noeud de copie
                g.add_edge(node_id, copy_id)
                
        return cls(g)

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