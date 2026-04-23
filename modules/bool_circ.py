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
                if outdeg == 1:
                    node.set_label(random.choice(['', '~']))
                else:
                    node.set_label('')
            elif indeg >= 2 and outdeg == 1:
                node.set_label(random.choice(['&', '|', '^']))
            elif indeg >= 2 and outdeg != 1:
                # Porte logique avec fan-out ou sans sortie apparente
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

    @classmethod
    def random_bool_circ_with_io(cls, n, bound, nb_inputs, nb_outputs):
        """
        TD10: Exercice 2
        Génère un circuit booléen aléatoire avec un nombre fixe d'entrées et de sorties.
        """
        import random
        while True:
            g = open_digraph.random(n, bound, form="DAG")
            node_ids = set(g.get_node_ids())
            for node_id in node_ids:
                node = g.get_node_by_id(node_id)
                if node.indegree() == 0 and node.outdegree() == 0:
                    g.remove_node_by_id(node_id)
            original_node_ids = g.get_node_ids()
            if original_node_ids:
                break
                
        # 1. Ajouter les inputs pour les co-feuilles et outputs pour les feuilles
        for node_id in original_node_ids:
            node = g.get_node_by_id(node_id)
            if node.indegree() == 0:
                g.add_input_node(node_id)
            if node.outdegree() == 0:
                g.add_output_node(node_id)
                
        # 2. Ajuster le nombre d'entrées
        inputs = g.get_input_ids()
        while len(inputs) < nb_inputs:
            tgt = random.choice(original_node_ids)
            g.add_input_node(tgt)
            inputs = g.get_input_ids()
            
        while len(inputs) > nb_inputs:
            in_to_remove = inputs[-1]
            tgt_to_remove = list(g.get_node_by_id(in_to_remove).get_children().keys())[0]
            g.remove_node_by_id(in_to_remove)
            
            # Pour ne pas laisser une ancienne co-feuille avec indegree 0, on lui connecte une constante
            const_id = g.add_node(label=random.choice(['0', '1']))
            g.add_edge(const_id, tgt_to_remove)
            inputs = g.get_input_ids()
            
        # 3. Ajuster le nombre de sorties
        outputs = g.get_output_ids()
        while len(outputs) < nb_outputs:
            src = random.choice(original_node_ids)
            g.add_output_node(src)
            outputs = g.get_output_ids()
            
        while len(outputs) > nb_outputs:
            out_to_remove = outputs[-1]
            g.remove_node_by_id(out_to_remove)
            outputs = g.get_output_ids()
            
        # 4. Assigner les labels aux noeuds originaux
        for node_id in original_node_ids:
            node = g.get_node_by_id(node_id)
            indeg = node.indegree()
            outdeg = node.outdegree()
            
            if indeg == 1:
                if outdeg == 1:
                    node.set_label(random.choice(['', '~']))
                else:
                    node.set_label('')
            elif indeg >= 2 and outdeg == 1:
                node.set_label(random.choice(['&', '|', '^']))
            elif indeg >= 2 and outdeg != 1:
                node.set_label(random.choice(['&', '|', '^']))
                copy_id = g.add_node(label='')
                children = list(node.get_children().items())
                for child_id, mult in children:
                    g.remove_parallel_edges(node_id, child_id)
                    for _ in range(mult):
                        g.add_edge(copy_id, child_id)
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

#TD10

    @classmethod
    def _build_adder0(cls):
        """
        Construit le circuit de base Adder0 (additionneur 1 bit complet).
        Entrées : a, b, carry_in (3 entrées)
        Sorties : somme, carry_out (2 sorties)
        
        somme     = a ⊕ b ⊕ carry_in
        carry_out = (a & b) | ((a ⊕ b) & carry_in)
        
        Retourne un open_digraph (non validé comme bool_circ).
        """
        g = open_digraph.empty()
        
        # Noeuds internes
        copy_a = g.add_node(label='')       # distribue a vers xor1 et and1
        copy_b = g.add_node(label='')       # distribue b vers xor1 et and1
        copy_cin = g.add_node(label='')     # distribue carry_in vers xor2 et and2
        xor1 = g.add_node(label='^')        # a ⊕ b
        and1 = g.add_node(label='&')        # a & b
        copy_xor1 = g.add_node(label='')    # distribue (a⊕b) vers xor2 et and2
        xor2 = g.add_node(label='^')        # (a⊕b) ⊕ carry_in = somme
        and2 = g.add_node(label='&')        # (a⊕b) & carry_in
        or1 = g.add_node(label='|')         # (a&b) | ((a⊕b)&carry_in) = carry_out
        
        # Câblage interne
        g.add_edge(copy_a, xor1)
        g.add_edge(copy_a, and1)
        g.add_edge(copy_b, xor1)
        g.add_edge(copy_b, and1)
        g.add_edge(xor1, copy_xor1)
        g.add_edge(copy_xor1, xor2)
        g.add_edge(copy_xor1, and2)
        g.add_edge(copy_cin, xor2)
        g.add_edge(copy_cin, and2)
        g.add_edge(and1, or1)
        g.add_edge(and2, or1)
        
        # Interface d'entrée : a, b, carry_in
        g.add_input_node(copy_a)
        g.add_input_node(copy_b)
        g.add_input_node(copy_cin)
        
        # Interface de sortie : somme, carry_out
        g.add_output_node(xor2)
        g.add_output_node(or1)
        
        return g

    @classmethod
    def _build_adder(cls, n):
        """
        Construit récursivement un additionneur Adder_n.
        Taille du registre : s = 2^n bits.
        Entrées : a[0..s-1], b[0..s-1], carry_in   (total : 2s + 1)
        Sorties : r[0..s-1], carry_out               (total : s + 1)
        
        Construction inductive :
        - On compose en parallèle deux Adder_{n-1} (bits de poids faible et poids fort)
        - On connecte la retenue sortante du bloc bas vers l'entrée retenue du bloc haut
        
        Retourne un open_digraph (non validé comme bool_circ).
        """
        if n == 0:
            return cls._build_adder0()
        
        half = 2 ** (n - 1)  # taille du registre des sous-additionneurs
        
        adder_low = cls._build_adder(n - 1)
        adder_high = cls._build_adder(n - 1)
        
        # Composition parallèle des deux sous-additionneurs
        g = adder_low.comp_parallel(adder_high)
        
        inputs = g.get_input_ids()
        outputs = g.get_output_ids()
        
        # Identification des noeuds de retenue à connecter
        # carry_out du sous-additionneur bas = dernier output du bloc bas
        c_out_low_id = outputs[half]
        # carry_in du sous-additionneur haut = dernier input du bloc haut
        c_in_high_id = inputs[-1]
        
        # Trouver les noeuds internes connectés aux interfaces de retenue
        c_out_low_parent = list(g.get_node_by_id(c_out_low_id).get_parents().keys())[0]
        c_in_high_child = list(g.get_node_by_id(c_in_high_id).get_children().keys())[0]
        
        # Supprimer les noeuds d'interface de retenue (les retire aussi des listes inputs/outputs)
        g.remove_node_by_id(c_out_low_id)
        g.remove_node_by_id(c_in_high_id)
        
        # Connecter la retenue du bas vers l'entrée du haut en interne
        g.add_edge(c_out_low_parent, c_in_high_child)
        
        # Réordonner les entrées pour respecter la convention :
        # Actuel : [a_low(h), b_low(h), c_in, a_high(h), b_high(h)]
        # Voulu  : [a_low(h), a_high(h), b_low(h), b_high(h), c_in]
        inputs = g.get_input_ids()
        a_low = inputs[0:half]
        b_low = inputs[half:2*half]
        c_in = [inputs[2*half]]
        a_high = inputs[2*half+1:3*half+1]
        b_high = inputs[3*half+1:4*half+1]
        
        g.set_inputs(a_low + a_high + b_low + b_high + c_in)
        
        # Les sorties sont déjà dans le bon ordre : [r_low(h), r_high(h), c_out]
        
        return g

    @classmethod
    def Adder(cls, n):
        """
        Construit un additionneur Adder_n validé comme circuit booléen.
        Taille du registre : s = 2^n bits.
        Entrées : a[0..s-1], b[0..s-1], carry_in   (total : 2s + 1)
        Sorties : r[0..s-1], carry_out               (total : s + 1)
        """
        g = cls._build_adder(n)
        return cls(g)

    @classmethod
    def Half_Adder(cls, n):
        """
        Construit un Half_Adder_n : additionneur sans retenue d'entrée.
        La retenue d'entrée est remplacée par une constante 0.
        Taille du registre : s = 2^n bits.
        Entrées : a[0..s-1], b[0..s-1]   (total : 2s)
        Sorties : r[0..s-1], carry_out     (total : s + 1)
        """
        g = cls._build_adder(n)
        
        inputs = g.get_input_ids()
        c_in_id = inputs[-1]  # carry_in est toujours la dernière entrée
        
        # Trouver le noeud interne connecté au carry_in
        c_in_child = list(g.get_node_by_id(c_in_id).get_children().keys())[0]
        
        # Supprimer le noeud d'entrée carry_in
        g.remove_node_by_id(c_in_id)
        
        # Ajouter une constante 0 à la place
        zero_id = g.add_node(label='0')
        g.add_edge(zero_id, c_in_child)
        
        return cls(g)