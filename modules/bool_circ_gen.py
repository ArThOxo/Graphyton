from modules.open_digraph import open_digraph
import random

class BoolCircGen:
    # Méthodes utilisé
    
    @staticmethod
    def nettoyer_noeuds_isoles(g):
        """Supprime tous les noeuds sans parents et sans enfants du graphe."""
        for node_id in list(g.get_node_ids()):
            node = g.get_node_by_id(node_id)
            if node.indegree() == 0 and node.outdegree() == 0:
                g.remove_node_by_id(node_id)

    @staticmethod
    def assigner_es_par_degre(g, node_ids):
        """Assigne les noeuds sans parents comme entrées et ceux sans enfants comme sorties."""
        for node_id in node_ids:
            node = g.get_node_by_id(node_id)
            if node.indegree() == 0:
                g.add_input_node(node_id)
            if node.outdegree() == 0:
                g.add_output_node(node_id)

    @staticmethod
    def assigner_logique_aux_noeuds(g, node_ids):
        """Assigne des étiquettes de portes logiques aux noeuds et gère le fan-out (sorties multiples)."""
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
        cls._nettoyer_noeuds_isoles(g)
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
            cls.nettoyer_noeuds_isoles(g)
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
