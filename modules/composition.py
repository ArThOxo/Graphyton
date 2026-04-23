class OpenDigraphComposition:
    def comp_parallel(self, g):
        """
        Composition parallèle non-destructive : renvoie un nouveau graphe
        """
        # Copie des graphes pour en creer un nouveau (maniere non destructive)  
        new_graph = self.copy()
        g_copy = g.copy()
        
        # Calcule du décalage et application de shift indices
        if new_graph.nodes:
            shift = new_graph.max_id() - g_copy.min_id() + 1
            g_copy.shift_indices(shift)
            
        # Update des noeuds
        for id_noeud, obj_noeud in g_copy.nodes.items():
            new_graph.nodes[id_noeud] = obj_noeud
            
        # Concatenation des entres
        for id_entree in g_copy.inputs:
            new_graph.inputs.append(id_entree)
            
        # Concatenations des sorties
        for id_sortie in g_copy.outputs:
            new_graph.outputs.append(id_sortie)
            
        return new_graph

    def comp_sequentielle(self, g):
        """
        Composition séquentielle mutative : connecte les sorties de self aux entrées de g.
        """
        # vérification de compatibilité
        if len(self.outputs) != len(g.inputs):
            raise ValueError("Incompatibilité : le nombre de sorties de self ne correspond pas au nombre d'entrées de g.")
            
        # Préparation et évitement des collisions
        # On travaille sur des copies pour ne pas changer les anciens graphes
        new_graph = self.copy()
        g_copy = g.copy()
        if new_graph.nodes:
            shift = new_graph.max_id() - g_copy.min_id() + 1
            g_copy.shift_indices(shift)
            
        # Ajouts des noeuds de g_copy dans new_graph
        new_graph.nodes.update(g_copy.nodes)
        
        # Connexion sorties self -> entrées g_copy
        for out_id, in_id in zip(new_graph.outputs, g_copy.inputs):
            new_graph.add_edge(out_id, in_id)
            
        # entrées restent celles de self, mais les sorties deviennent celles de g_copy
        new_graph.outputs = g_copy.outputs
        return new_graph

    def connected_components(self):
        """
        Retourne la liste de toutes les composantes connexes du graphe.
        Chaque composante est une liste d'IDs de noeuds.
        """
        nodes_to_visit = set(self.get_node_ids())
        components = []
        
        while nodes_to_visit:
            # On pioche un noeud au hasard parmi ceux non visités
            start_node = nodes_to_visit.pop()
            
            # Initialisation du parcours en largeur (BFS) pour trouver son "île"
            comp = [start_node]
            queue = [start_node]
            visited = {start_node}
            
            while queue:
                curr_id = queue.pop(0)
                curr_node = self.get_node_by_id(curr_id)
                
                # On récupère tous les voisins en ignorant l'orientation (parents + enfants)
                voisins = list(curr_node.get_parents().keys()) + list(curr_node.get_children().keys())
                
                for v in voisins:
                    if v not in visited:
                        visited.add(v)
                        queue.append(v)
                        comp.append(v)
                        # On retire le voisin de la liste globale des noeuds à traiter
                        nodes_to_visit.discard(v)
            
            # On ajoute la composante trouvée à notre liste globale
            components.append(comp)
            
        return components

    def connected_components_graphs(self):
        """
        Sépare le graphe en plusieurs sous-graphes indépendant (composantes connexes) 
        et retourne une liste d'objets ouverts.
        """
        components_ids = self.connected_components()
        graphs = []
        
        for comp in components_ids:
            # On copie les noeuds appartenant à cette composante
            comp_nodes = [self.get_node_by_id(n_id).copy() for n_id in comp]
            
            # On filtre les entrées et sorties globales pour conserver l'ordre relatif
            comp_inputs = [i for i in self.get_input_ids() if i in comp]
            comp_outputs = [o for o in self.get_output_ids() if o in comp]
            
            # Utilisation de la méthode de classe pour éviter une dépendance circulaire stricte
            new_graph = self.__class__(comp_inputs, comp_outputs, comp_nodes)
            graphs.append(new_graph)
            
        return graphs

    def merge_nodes(self, id1, id2):
        """
        Fusionne le noeud id2 dans le noeud id1. Le noeud id1 hérite de tous les parents, enfants et statuts (input/output) de id2.
        Le noeud id2 est ensuite supprimé.
        """
        if id1 not in self.nodes or id2 not in self.nodes:
            raise ValueError("Les IDs fournis ne sont pas dans le graphe.")

        n1 = self.nodes[id1]
        n2 = self.nodes[id2]

        # on transfére les enfants de id2 vers id1
        for child_id, mult in n2.get_children().copy().items():
            if child_id != id1: # On évite de créer une auto-boucle sur id1
                n1.add_child_id(child_id, mult)
                self.nodes[child_id].add_parent_id(id1, mult)

        # on transfére les parents de id2 vers id1
        for parent_id, mult in n2.get_parents().copy().items():
            if parent_id != id1: # on évite l'auto-boucle
                n1.add_parent_id(parent_id, mult)
                self.nodes[parent_id].add_child_id(id1, mult)

        # on transfére les statuts d'entrée/sortie globales
        if id2 in self.inputs:
            if id1 not in self.inputs:
                self.inputs.append(id1)
                
        if id2 in self.outputs:
            if id1 not in self.outputs:
                self.outputs.append(id1)

        # pour supprimer proprement l'ancien noeud id2
        self.remove_node_by_id(id2)
