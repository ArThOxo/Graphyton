from modules.open_digraph import open_digraph
import random

class BoolCircGen:
    # Méthodes utilisé
    
    @staticmethod
    def supprime_noeuds_isoles(g):
        """Supprime tous les noeuds sans parents et sans enfants du graphe."""
        for node_id in list(g.get_node_ids()):
            node = g.get_node_by_id(node_id)
            if node.indegree() == 0 and node.outdegree() == 0:
                g.remove_node_by_id(node_id)

    @staticmethod
    def assigner_es_par_degre(g, node_ids):
        """Assigne les noeuds sans parents comme entrées et ceux sans enfants comme sorties"""
        for node_id in node_ids:
            node = g.get_node_by_id(node_id)
            if node.indegree() == 0:
                g.add_input_node(node_id)
            if node.outdegree() == 0:
                g.add_output_node(node_id)

    @staticmethod
    def assigner_logique_aux_noeuds(g, node_ids):
        """Assigne des étiquettes de portes logiques aux noeuds et gère les sorties multiples"""
        for node_id in node_ids:
            node = g.get_node_by_id(node_id)
            indeg = node.indegree()
            outdeg = node.outdegree() 
            if indeg == 1:
                # porte NON ou copie
                if outdeg == 1:
                    node.set_label(random.choice(['', '~']))
                else:
                    node.set_label('')
            elif indeg >= 2:
                #porte logique
                node.set_label(random.choice(['&', '|', '^']))
                #si plusieurs sorties
                if outdeg != 1:
                    copy_id = g.add_node(label='')
                    children = list(node.get_children().items())
                    for child_id, mult in children:
                        g.remove_parallel_edges(node_id, child_id)
                        for _ in range(mult):
                            g.add_edge(copy_id, child_id)
                    g.add_edge(node_id, copy_id)


    # générateurs

    @classmethod
    def from_dag(cls, g):
        """
        TD10: Exercice 1 - Transformateur
        Transforme un graphe dirigé acyclique en un circuit booléen valide.
        """
        cls.supprime_noeuds_isoles(g)
        node_ids = g.get_node_ids()
        if not node_ids:
            return cls(g)   
        cls.assigner_es_par_degre(g,node_ids)
        cls.assigner_logique_aux_noeuds(g,node_ids)
        return cls(g)

    @classmethod
    def random_bool_circ(cls, n, bound):
        """
        TD10: Exercice 1 - Génération
        Génère un circuit booléen aléatoire valide.
        """
        g = open_digraph.random(n, bound, form="DAG")
        return cls.from_dag(g)

    @classmethod
    def random_bool_circ_with_io(cls, n, bound, nb_inputs, nb_outputs):
        """
        TD10: Exercice 2
        Génère un circuit booléen aléatoire avec un nombre fixe d'entrées et de sorties.
        """
        while True:
            g = open_digraph.random(n, bound, form="DAG")
            cls.supprime_noeuds_isoles(g)
            node_ids = g.get_node_ids()
            if node_ids:
                break
        cls.assigner_es_par_degre(g, node_ids)
        inputs = g.get_input_ids()
        while len(inputs) < nb_inputs:
            g.add_input_node(random.choice(node_ids))
            inputs = g.get_input_ids()  

        while len(inputs) > nb_inputs:
            in_to_remove = inputs[-1]
            tgt_to_remove = list(g.get_node_by_id(in_to_remove).get_children().keys())[0]
            g.remove_node_by_id(in_to_remove)
            const_id = g.add_node(label=random.choice(['0', '1']))
            g.add_edge(const_id, tgt_to_remove)
            inputs = g.get_input_ids()

        outputs = g.get_output_ids()
        while len(outputs) < nb_outputs:
            g.add_output_node(random.choice(node_ids))
            outputs = g.get_output_ids()    
        while len(outputs) > nb_outputs:
            out_to_remove = outputs[-1]
            g.remove_node_by_id(out_to_remove)
            outputs = g.get_output_ids()
        cls.assigner_logique_aux_noeuds(g,node_ids)
                
        return cls(g)

    @classmethod
    def from_integer(cls, n, size=8):
        """
        TD11: Transforme un entier en un circuit booléen représentant ses bits.
        """
        if n < 0:
            raise ValueError("Seuls les entiers non signés sont acceptés")
        if n >= 2 ** size:
            raise ValueError(
                f"L'entier {n} ne tient pas dans un registre de {size} bits "
                f"(max = {2**size - 1})"
            )

        bits = bin(n)[2:].zfill(size)

        g = open_digraph.empty()
        for bit in bits:
            const_id = g.add_node(label=bit)
            g.add_output_node(const_id)

        return cls(g)

    @classmethod
    def hamming_encoder(cls):
        """
        Encode 4 bits d'entrée en 7 bits de sortie
        entrées : x0, x1, x2, x3
        sorties : x0, x1, x2, x3, p0, p1, p2
        """
        g = open_digraph.empty()
        
        # Entrées réparties avec des noeuds de copie
        cx0 = g.add_node(label='')
        cx1 = g.add_node(label='')
        cx2 = g.add_node(label='')
        cx3 = g.add_node(label='')
        # Bits de parité
        # p0 = x0 ^ x1 ^ x3
        xor_p0_a = g.add_node(label='^')
        xor_p0_b = g.add_node(label='^')
        g.add_edge(cx0, xor_p0_a)
        g.add_edge(cx1, xor_p0_a)
        g.add_edge(xor_p0_a, xor_p0_b)
        g.add_edge(cx3, xor_p0_b)
        # p1 = x0 ^ x2 ^ x3
        xor_p1_a = g.add_node(label='^')
        xor_p1_b = g.add_node(label='^')
        g.add_edge(cx0, xor_p1_a)
        g.add_edge(cx2, xor_p1_a)
        g.add_edge(xor_p1_a, xor_p1_b)
        g.add_edge(cx3, xor_p1_b)
        # p2 = x1 ^ x2 ^ x3
        xor_p2_a = g.add_node(label='^')
        xor_p2_b = g.add_node(label='^')
        g.add_edge(cx1, xor_p2_a)
        g.add_edge(cx2, xor_p2_a)
        g.add_edge(xor_p2_a, xor_p2_b)
        g.add_edge(cx3, xor_p2_b)
        # 4 noeuds d'entrée
        g.add_input_node(cx0)
        g.add_input_node(cx1)
        g.add_input_node(cx2)
        g.add_input_node(cx3)
        # 7 noeuds de sortie
        g.add_output_node(cx0)
        g.add_output_node(cx1)
        g.add_output_node(cx2)
        g.add_output_node(cx3)
        g.add_output_node(xor_p0_b)
        g.add_output_node(xor_p1_b)
        g.add_output_node(xor_p2_b)
        return cls(g)

    @classmethod
    def hamming_decoder(cls):
        """
        Décode 7 bits d'entrée en 4 bits de sortie en corrigeant au plus 1 erreur
        entrées : x0, x1, x2, x3, p0, p1, p2
        sorties : x0_corr, x1_corr, x2_corr, x3_corr
        """
        g = open_digraph.empty()
        # Entrées du circuit (les 7 bits reçus)
        cx0 = g.add_node(label='')
        cx1 = g.add_node(label='')
        cx2 = g.add_node(label='')
        cx3 = g.add_node(label='')
        cp0 = g.add_node(label='')
        cp1 = g.add_node(label='')
        cp2 = g.add_node(label='')
        # s0 = x0 ^ x1 ^ x3 ^ p0
        s0_1 = g.add_node(label='^')
        s0_2 = g.add_node(label='^')
        s0 = g.add_node(label='^')
        g.add_edge(cx0, s0_1)
        g.add_edge(cx1, s0_1)
        g.add_edge(s0_1, s0_2)
        g.add_edge(cx3, s0_2)
        g.add_edge(s0_2, s0)
        g.add_edge(cp0, s0)
        # s1 = x0 ^ x2 ^ x3 ^ p1
        s1_1 = g.add_node(label='^')
        s1_2 = g.add_node(label='^')
        s1 = g.add_node(label='^')
        g.add_edge(cx0, s1_1)
        g.add_edge(cx2, s1_1)
        g.add_edge(s1_1, s1_2)
        g.add_edge(cx3, s1_2)
        g.add_edge(s1_2, s1)
        g.add_edge(cp1, s1)
        # s2 = x1 ^ x2 ^ x3 ^ p2
        s2_1 = g.add_node(label='^')
        s2_2 = g.add_node(label='^')
        s2 = g.add_node(label='^')
        g.add_edge(cx1, s2_1)
        g.add_edge(cx2, s2_1)
        g.add_edge(s2_1, s2_2)
        g.add_edge(cx3, s2_2)
        g.add_edge(s2_2, s2)
        g.add_edge(cp2, s2)
        # Distribution
        cs0 = g.add_node(label='')
        cs1 = g.add_node(label='')
        cs2 = g.add_node(label='')
        g.add_edge(s0, cs0)
        g.add_edge(s1, cs1)
        g.add_edge(s2, cs2)
        # Négations
        not_s0 = g.add_node(label='~')
        not_s1 = g.add_node(label='~')
        not_s2 = g.add_node(label='~')
        g.add_edge(cs0, not_s0)
        g.add_edge(cs1, not_s1)
        g.add_edge(cs2, not_s2)
        cns0 = g.add_node(label='')
        cns1 = g.add_node(label='')
        cns2 = g.add_node(label='')
        g.add_edge(not_s0, cns0)
        g.add_edge(not_s1, cns1)
        g.add_edge(not_s2, cns2)
        # Décodage et Correction
        # e0 = s0 & s1 & ~s2 (Syndrome 3 -> Erreur x0)
        e0_1 = g.add_node(label='&')
        g.add_edge(cs0, e0_1)
        g.add_edge(cs1, e0_1)
        ce0_1 = g.add_node(label='') # On distribue e0_1 pour e3 aussi
        g.add_edge(e0_1, ce0_1)
        e0 = g.add_node(label='&')
        g.add_edge(ce0_1, e0)
        g.add_edge(cns2, e0)
        out_x0_xor = g.add_node(label='^')
        g.add_edge(cx0, out_x0_xor)
        g.add_edge(e0, out_x0_xor)
        # e1 = s0 & ~s1 & s2 (Syndrome 5 -> Erreur x1)
        e1_1 = g.add_node(label='&')
        g.add_edge(cs0, e1_1)
        g.add_edge(cns1, e1_1)
        e1 = g.add_node(label='&')
        g.add_edge(e1_1, e1)
        g.add_edge(cs2, e1)
        out_x1_xor = g.add_node(label='^')
        g.add_edge(cx1, out_x1_xor)
        g.add_edge(e1, out_x1_xor)
        # e2 = ~s0 & s1 & s2 (Syndrome 6 -> Erreur x2)
        e2_1 = g.add_node(label='&')
        g.add_edge(cns0, e2_1)
        g.add_edge(cs1, e2_1)
        e2 = g.add_node(label='&')
        g.add_edge(e2_1, e2)
        g.add_edge(cs2, e2)
        out_x2_xor = g.add_node(label='^')
        g.add_edge(cx2, out_x2_xor)
        g.add_edge(e2, out_x2_xor)
        # e3 = s0 & s1 & s2 (Syndrome 7 -> Erreur x3)
        e3 = g.add_node(label='&')
        g.add_edge(ce0_1, e3)
        g.add_edge(cs2, e3)
        out_x3_xor = g.add_node(label='^')
        g.add_edge(cx3, out_x3_xor)
        g.add_edge(e3, out_x3_xor)
        # Déclaration des 7 entrées dans le même ordre que la sortie de l'encodeur
        g.add_input_node(cx0)
        g.add_input_node(cx1)
        g.add_input_node(cx2)
        g.add_input_node(cx3)
        g.add_input_node(cp0)
        g.add_input_node(cp1)
        g.add_input_node(cp2)
        # Déclaration des 4 sorties (message corrigé)
        g.add_output_node(out_x0_xor)
        g.add_output_node(out_x1_xor)
        g.add_output_node(out_x2_xor)
        g.add_output_node(out_x3_xor)
        return cls(g)
