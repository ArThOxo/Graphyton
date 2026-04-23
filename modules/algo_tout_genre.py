class OpenDigraphAlgoToutGenre:
    def bfs(self, src, direction=None, tgt=None):
        """
        Calcule les distances depuis un noeud source en utilisant un BFS.
        Intègre un arrêt anticipé si tgt est atteint (Exercice 3).
        Renvoie les dictionnaires dist et prev.
        """
        dist = {src: 0}
        prev = {}
        
        # On utilise une liste comme file FIFO
        file = [src]
        
        while file:
            u = file.pop(0)
            if tgt is not None and u == tgt:
                break

            noeud_u = self.get_node_by_id(u)
            voisins = []
            
            # Choix voisins selon la direction
            if direction == 1:
                # Enfants
                voisins = list(noeud_u.get_children().keys())
            elif direction == -1:
                # Parents
                voisins = list(noeud_u.get_parents().keys())
            else:
                # Les deux
                voisins = list(noeud_u.get_children().keys()) + list(noeud_u.get_parents().keys())
                
            # Parcours des voisins
            for v in voisins:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    prev[v] = u
                    file.append(v)
                    
        return dist, prev

    def shortest_path(self, u, v):
        """
        Calcule et renvoie la liste des noeuds formant 
        le plus court chemin orienté de u vers v
        """
        # On lance le BFS avec direction=1 (car on cherche un chemin orienté) 
        # et tgt=v pour l'arrêt anticipé.
        dist, prev = self.bfs(src=u, direction=1, tgt=v)
        
        # Si v n'est pas dans dist, c'est qu'il est inatteignable depuis u
        if v not in dist:
            return []
            
        # Reconstruction du chemin en remontant le dictionnaire prev à l'envers
        path = [v]
        current = v
        while current in prev:
            current = prev[current]
            path.append(current)
            
        # On remet le chemin dans le bon sens (de u vers v)
        path.reverse()
        return path

    def common_ancestors(self, node_1, node_2):
        """
        Trouve les ancêtres communs à node_1 et node_2
        Renvoie un dictionnaire associant chaque ID d'ancêtre commun 
        à un tuple de distances : (dist_vers_node1, dist_vers_node2)
        """
        # On lance un parcours en largeur "à l'envers" depuis les deux noeuds
        dist1, _ = self.bfs(src=node_1, direction=-1)
        dist2, _ = self.bfs(src=node_2, direction=-1)
        
        common = {}
        
        # On parcourt les ancêtres du premier noeud
        for u in dist1:
            # Si cet ancêtre est aussi un ancêtre du deuxième noeud
            if u in dist2:
                # On ajoute au dictionnaire le tuple des distances
                common[u] = (dist1[u], dist2[u])
                
        return common

    def tri_topologique(self):
        """
        Calcule le tri topologique vers le haut du graphe
        Retourne une liste de listes d'ID de noeuds
        Erreur si le graphe contient un cycle
        """
        # On ignore les entrées et sorties globales du graphe
        node_ids = self.get_node_ids()
        # calcule le nombre de parents pour chaque noeud
        in_degrees = {}
        for n_id in node_ids:
            node = self.get_node_by_id(n_id)
            parents_internes = [p for p in node.get_parents().keys() if p in node_ids]
            in_degrees[n_id] = len(parents_internes)
 
        result = []
        while in_degrees:
            # indentif des co_feuilles
            co_feuilles = [n for n, deg in in_degrees.items() if deg == 0]
            if not co_feuilles:
                raise ValueError("Le graphe contient un cycle") # si il y a aucune co-feuilles mais qu'il reste des noeuds  = cycle
            result.append(co_feuilles)
            for n in co_feuilles:
                node = self.get_node_by_id(n)
                children = [c for c in node.get_children().keys() if c in in_degrees]
                for child in children:
                    in_degrees[child] -= 1
                del in_degrees[n]
 
        return result

    def profondeur_noeud(self, id_noeud):
        """
        Calcule la profondeur d'un noeud donné en utilisant le tri topologique.
        La profondeur correspond à l'indice du niveau dans lequel se trouve le noeud.
        """
        tri = self.tri_topologique()
        
        # On cherche dans quel niveau se trouve notre noeud
        for profondeur, noeuds_niveau in enumerate(tri):
            if id_noeud in noeuds_niveau:
                return profondeur
                
        raise ValueError(f"Le noeud {id_noeud} n'a pas été trouvé dans le tri topologique")
    
    def profondeur_graphe(self):
        """
        Calcule la profondeur totale du graphe.
        Correspond à la profondeur maximale de ses noeuds (nombre de niveaux - 1).
        """
        tri = self.tri_topologique()
        if not tri:
            return 0
        return len(tri) - 1

    def plus_long_chemin(self, u, v):
        """
        Calcule le plus long chemin entre le noeud u et le noeud v en utilisant le tri topologique
        Retourne la liste des ID des noeuds formant ce plus long chemin.
        """
        tri_niveaux = self.tri_topologique()
        ordre_topo = []
        for niveau in tri_niveaux:
            for noeud in niveau:
                ordre_topo.append(noeud)  
        distances = {u: 0}
        precedents = {}
        # Parcours des noeuds dans l'ordre topologique
        for id_noeud in ordre_topo:
            if id_noeud in distances:
                noeud_courant = self.get_node_by_id(id_noeud)
                enfants = noeud_courant.get_children().keys()
                for enfant in enfants:
                    nouvelle_distance = distances[id_noeud] + 1
                    if enfant not in distances or nouvelle_distance > distances[enfant]:
                        distances[enfant] = nouvelle_distance
                        precedents[enfant] = id_noeud               
        # Reconstruction du chemin
        if v not in distances:
            return []
        chemin = [v]
        courant = v
        while courant in precedents:
            courant = precedents[courant]
            chemin.append(courant) 
        chemin.reverse()
        return chemin
