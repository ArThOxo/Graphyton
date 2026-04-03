import random
import os
import re
import urllib.parse
import webbrowser
import tempfile



class node:
    # TD 1 
    def __init__(self, identity, label, parents, children):
        self.id = identity
        self.label = label
        self.parents = parents
        self.children = children
    def __str__ (self):
        return "ID :" + str(self.id) + ", LABEL:" + str(self.label) + ", Parents:" + str(self.parents) +", ENFANTS :" + str(self.children)
    def __repr__(self):
        return self.__str__()
    def copy(self):
        y = node(self.id, self.label, self.parents.copy(), self.children.copy())
        return y

    # GETTERS
    def get_id(self):
        return self.id
    def get_label(self):
        return self.label
    def get_parents(self):
        return self.parents
    def get_children(self):
        return self.children

    # SETTERS
    def set_id(self , newID):
        self.id = newID
    def set_label(self , newLABEL):
        self.label = newLABEL
    def set_parents(self , newParents):
        self.parents = newParents
    def set_children(self , newChildren):
        self.children = newChildren
    def add_child_id (self, id , multiplicity =1):
        if id in self.children:
            self.children[id] += multiplicity
        else:
            self.children[id] = multiplicity
    def add_parent_id (self, id , multiplicity =1):
        if id in self.parents:
            self.parents[id] += multiplicity
        else:
            self.parents[id] = multiplicity



#TD 2

    def remove_parent_once(self, id):
        if id in self.parents:
            self.parents[id] -= 1
            if self.parents[id] == 0: 
                self.parents.pop(id)
        else:
            raise KeyError(f"Le noeud {id} n'est pas un parent du noeud {self.id}.")

    def remove_child_once(self, id):
        if id in self.children:
            self.children[id] -= 1
            if self.children[id] == 0: 
                self.children.pop(id)
        else:
            raise KeyError(f"Le noeud {id} n'est pas un enfant du noeud {self.id}.")
    
    def remove_parent_id(self, id):
        if id in self.parents:
            self.parents.pop(id)
        else:
            raise KeyError(f"Le noeud {id} n'est pas un parent du noeud {self.id}.")


    def remove_child_id(self, id):
        if id in self.children:
            self.children.pop(id)
        else:
            raise KeyError(f"Le noeud {id} n'est pas un enfant du noeud {self.id}.")


    #TD 5
    
    def indegree(self):
        return sum(self.parents.values())

    def outdegree(self):
        return sum(self.children.values())

    def degree(self):
        return self.indegree() + self.outdegree()

class open_digraph:
    # TD 1
    def __init__(self, inputs, outputs, nodes):
        self.inputs = inputs
        self.outputs = outputs
        self.nodes = {node.id:node for node in nodes}
    def __str__ (self):
        return "Input :" + str(self.inputs) + ", outputs:" + str(self.outputs) + ", Noeuds:" + str(self.nodes.__str__())
    def __repr__(self):
        return self.__str__()
    def copy(self):
        new_nodes = [n.copy() for n in self.nodes.values()]
        y = open_digraph(self.inputs.copy(), self.outputs.copy(), new_nodes)
        return y

    @classmethod
    def empty(cls):
        return cls([], [], [])

    # GETTERS

    def get_input_ids(self):
        return self.inputs
    
    def get_output_ids(self):
        return self.outputs

    def get_id_node_map(self):
        return self.nodes 
    
    def get_nodes(self):
        return list(self.nodes.values())
    
    def get_node_ids(self):
        return list(self.nodes.keys())
    
    def get_node_by_id(self, id):
        return self.nodes[id]

    def get_nodes_by_ids (self, ids):
        return [self.nodes[node_id] for node_id in ids]

     
    # SETTERS
    def set_inputs (self , newInputs):
        self.inputs = newInputs

    def set_outputs (self, newOuputs):
        self.outputs = newOuputs

    def add_input_id (self , inID):
        if inID not in self.inputs:
            self.inputs.append(inID)

    def add_output_id (self , outID):
        if outID not in self.outputs:
            self.outputs.append(outID)
    

    # AJOUT DE NOEUDS ET ARÊTES

    def new_id(self):
        ids = self.get_node_ids()
        if not ids:
            return 0
        return max(ids) + 1

    def add_node(self, label='', parents=None, children=None):
        if parents is None:
            parents = {}
        if children is None:
            children = {}

        new_id = self.new_id() 
        new_n = node(new_id, label, parents.copy(), children.copy()) 
        self.nodes[new_id] = new_n #edit: remplacé 'id' par 'new_id'

        for parent_id, multiplicity in parents.items():
            if parent_id in self.nodes:
                parent_node = self.nodes[parent_id]
                parent_node.add_child_id(new_id, multiplicity)
            
        for child_id, multiplicity in children.items():
            if child_id in self.nodes:
                child_node = self.nodes[child_id]
                child_node.add_parent_id(new_id, multiplicity) #edit: enlevé le 's' de 'parents'

        return new_id

    def add_edge(self, src, tgt):
        self.nodes[src].add_child_id(tgt)
        self.nodes[tgt].add_parent_id(src)

    def add_edges(self, edges): 
        for src, tgt in edges:
            self.add_edge(src, tgt)


    #TD2

    def remove_edge(self, src, tgt):
        if src not in self.nodes:
            raise KeyError(f"Le noeud source {src} n'existe pas dans le graphe.")
        if tgt not in self.nodes:
            raise KeyError(f"Le noeud cible {tgt} n'existe pas dans le graphe.")
        
        self.nodes[src].remove_child_once(tgt)
        self.nodes[tgt].remove_parent_once(src)

    def remove_parallel_edges(self, src, tgt):
        if src not in self.nodes:
            raise KeyError(f"Le noeud source {src} n'existe pas dans le graphe.")
        if tgt not in self.nodes:
            raise KeyError(f"Le noeud cible {tgt} n'existe pas dans le graphe.")
            
        self.nodes[src].remove_child_id(tgt)
        self.nodes[tgt].remove_parent_id(src)

    def remove_edges(self, edges):
        for src, tgt in edges:
            self.remove_edge(src, tgt)
    
    def remove_several_parallel_edges(self, edges):
        for src, tgt in edges:
            self.remove_parallel_edges(src, tgt)


    def remove_node_by_id(self, id):
        n = self.nodes[id]
        for parent_id in list(n.get_parents().keys()):
            self.remove_parallel_edges(parent_id, id)
        for child_id in list(n.get_children().keys()):
            self.remove_parallel_edges(id, child_id)
            
        self.nodes.pop(id)
        if id in self.inputs:
            self.inputs.remove(id)
        if id in self.outputs:
            self.outputs.remove(id)

    def remove_nodes_by_id(self, ids):
        for id in ids:
            self.remove_node_by_id(id)


    # INTÉGRITÉ

    def is_well_formed(self):
        # Vérification des inputs
        for in_id in self.inputs:
            if in_id not in self.nodes:
                return False
            n = self.nodes[in_id]
            if len(n.get_parents()) != 0 or len(n.get_children()) != 1 or list(n.get_children().values())[0] != 1:
                return False

        # Vérification des outputs
        for out_id in self.outputs:
            if out_id not in self.nodes:
                return False
            n = self.nodes[out_id]
            if len(n.get_children()) != 0 or len(n.get_parents()) != 1 or list(n.get_parents().values())[0] != 1:
                return False
        
        # Vérification de la réciprocité de toutes les arêtes
        for node_id, n in self.nodes.items():
            if node_id != n.get_id():
                return False 
            
            for child_id, mult in n.get_children().items():
                if child_id not in self.nodes:
                    return False
                child_node = self.nodes[child_id]
                if node_id not in child_node.get_parents() or child_node.get_parents()[node_id] != mult:
                    return False

            for parent_id, mult in n.get_parents().items():
                if parent_id not in self.nodes:
                    return False
                parent_node = self.nodes[parent_id]
                if node_id not in parent_node.get_children() or parent_node.get_children()[node_id] != mult:
                    return False
        return True

    def assert_is_well_formed(self):
        if not self.is_well_formed():
            raise ValueError("Le graphe n'est pas bien formé.")



    def is_cyclic(self):
        out_degrees = {n.get_id(): n.outdegree() for n in self.get_nodes()}
        leaves = [node_id for node_id, deg in out_degrees.items() if deg == 0]
        visited_count = 0
        
        while leaves:
            leaf_id = leaves.pop()
            visited_count += 1
            leaf_node = self.get_node_by_id(leaf_id)
            for parent_id, multiplicity in leaf_node.get_parents().items():
                out_degrees[parent_id] -= multiplicity
                if out_degrees[parent_id] == 0:
                    leaves.append(parent_id)
                    
        return visited_count != len(self.get_nodes())
    


    def add_input_node(self, target_id):
        if target_id not in self.nodes:
            raise ValueError(f"Le noeud cible {target_id} n'existe pas.")
        new_id = self.add_node(label="") 
        self.add_edge(new_id, target_id)
        self.inputs.append(new_id)
        self.assert_is_well_formed()
        return new_id

    def add_output_node(self, source_id):
        if source_id not in self.nodes:
            raise ValueError(f"Le noeud source {source_id} n'existe pas.")
        new_id = self.add_node(label="") 
        self.add_edge(source_id, new_id)
        self.outputs.append(new_id)
        self.assert_is_well_formed()
        return new_id


    #TD 3
    @staticmethod
    def random_int_list(n,bound):
        return [random.randint(0, bound) for _ in range(n)]
    
    @staticmethod
    def random_int_matrix(n, bound, null_diag=False):
        matrix = [open_digraph.random_int_list(n, bound) for _ in range(n)]
        if null_diag:
            for j in range(n):
                matrix[j][j] = 0
        return matrix
    
    @staticmethod    
    def random_symetric_int_matrix(n, bound, null_diag=True):
        matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i, n):
                if i == j and null_diag:
                    matrix[i][j] = 0
                else:
                    ran = random.randint(0, bound)
                    matrix[i][j] = ran
                    matrix[j][i] = ran
        return matrix

    @staticmethod
    def random_oriented_int_matrix(n, bound, null_diag=True):
        matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i, n):
                if i == j:
                    if not null_diag:
                        matrix[i][i] = random.randint(0, bound)
                else:
                    ran = random.randint(0, bound)
                    if ran > 0:
                        if random.choice([True, False]):
                            matrix[i][j] = ran
                        else:
                            matrix[j][i] = ran
        return matrix

    @staticmethod
    def random_triangular_int_matrix(n, bound, null_diag=True):
        matrix = open_digraph.random_int_matrix(n, bound, null_diag)
        for i in range(n):
            for j in range(0, i):
                matrix[i][j] = 0
        return matrix



    @classmethod
    def graph_from_adjacency_matrix(cls, matrix):
        n = len(matrix)
        g = cls.empty()

        ids = [g.add_node(label=f"v{i}") for i in range(n)]
        
        for i in range(n):
            for j in range(n):
                if matrix[i][j] > 0:
                    g.nodes[ids[i]].add_child_id(ids[j], matrix[i][j])
                    g.nodes[ids[j]].add_parent_id(ids[i], matrix[i][j])
        return g


    @classmethod
    def random(cls, n, bound, inputs=0, outputs=0, form="free"):
        if form == "free":
            matrix = cls.random_int_matrix(n, bound)
        elif form == "DAG":
            matrix = cls.random_triangular_int_matrix(n, bound)
        elif form == "oriented":
            matrix = cls.random_oriented_int_matrix(n, bound)
        elif form == "loop-free":
            matrix = cls.random_int_matrix(n, bound, null_diag=True)
        elif form == "undirected":
            matrix = cls.random_symetric_int_matrix(n, bound, null_diag=False)
        elif form == "loop-free undirected":
            matrix = cls.random_symetric_int_matrix(n, bound, null_diag=True)
        else:
            raise ValueError("Erreur de forme de graphe demandée.")
        
        g = cls.graph_from_adjacency_matrix(matrix)
        node_ids = g.get_node_ids()

        input_targets = random.sample(node_ids, min(inputs, len(node_ids)))
        output_sources = random.sample(node_ids, min(outputs, len(node_ids)))
        
        for t_id in input_targets:
            g.add_input_node(t_id)
        for s_id in output_sources:
            g.add_output_node(s_id)
            
        return g



    def get_node_id_to_index_map(self):
        return {node_id: index for index, node_id in enumerate(self.nodes.keys())}


    def adjacency_matrix(self):
        mapping = self.get_node_id_to_index_map()
        n = len(self.nodes)
        matrix = [[0] * n for _ in range(n)]
        
        for src_id, src_node in self.nodes.items():
            i = mapping[src_id]
            for tgt_id, multiplicity in src_node.get_children().items():
                if tgt_id in mapping:
                    j = mapping[tgt_id]
                    matrix[i][j] += multiplicity
        return matrix


    #TD 4
    def save_as_dot_file(self, path, verbose=False):
        with open(path, 'w') as f:
            f.write("digraph G {\n")
            
            for n_id, n in self.nodes.items():
                label = n.get_label()
                if verbose:
                    label = f"ID:{n.get_id()} - {label}"
                
                attrs = [f'label="{label}"']
                
                if n_id in self.inputs:
                    attrs.append('is_input="True"')
                if n_id in self.outputs:
                    attrs.append('is_output="True"')
                
                f.write(f'    v{n_id} [{", ".join(attrs)}];\n')
                
            for n_id, n in self.nodes.items():
                for child_id, multiplicity in n.get_children().items():
                    for _ in range(multiplicity):
                        f.write(f'    v{n_id} -> v{child_id};\n')
                        
            f.write("}\n")


    @classmethod
    def from_dot_file(cls, path):
        g = cls.empty()
        with open(path, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            node_match = re.match(r'v(\d+)\s*\[(.*label="(.*?)".*)\];', line)
            if node_match:
                n_id = int(node_match.group(1))
                label = node_match.group(3)
                if n_id not in g.nodes:
                    g.nodes[n_id] = node(n_id, label, {}, {})
                else:
                    g.nodes[n_id].set_label(label)
                    
                if 'is_input="True"' in line:
                    g.add_input_id(n_id)
                if 'is_output="True"' in line:
                    g.add_output_id(n_id)
                    
            edge_match = re.match(r'v(\d+)\s*->\s*v(\d+);', line)
            if edge_match:
                src = int(edge_match.group(1))
                tgt = int(edge_match.group(2))
                if src not in g.nodes:
                    g.nodes[src] = node(src, "", {}, {})
                if tgt not in g.nodes:
                    g.nodes[tgt] = node(tgt, "", {}, {})
                g.add_edge(src, tgt)
        return g

    def display(self, verbose=False):
        temp_dir = tempfile.gettempdir()
        dot_path = os.path.join(temp_dir, "temp_graph.dot")
        self.save_as_dot_file(dot_path, verbose=verbose)
        
        with open(dot_path, 'r') as f:
            dot_content = f.read()
            
        encoded_dot = urllib.parse.quote(dot_content)
        url = f"https://dreampuf.github.io/GraphvizOnline/#{encoded_dot}"
        webbrowser.open(url)


    # TD 5

    def min_id(self):
        if not self.nodes:
            return 0
        return min(self.nodes.keys())

    def max_id(self):
        if not self.nodes:
            return 0
        return max(self.nodes.keys())

    def shift_indices(self, n):
       
        self.inputs = [i + n for i in self.inputs]
        self.outputs = [i + n for i in self.outputs]

        new_nodes = {}
        
        for old_id, node_obj in self.nodes.items():
            new_id = old_id + n
            
            node_obj.set_id(new_id)
            
            new_parents = {p_id + n: mult for p_id, mult in node_obj.get_parents().items()}
            new_children = {c_id + n: mult for c_id, mult in node_obj.get_children().items()}
            
            node_obj.set_parents(new_parents)
            node_obj.set_children(new_children)
            
            new_nodes[new_id] = node_obj
            
        self.nodes = new_nodes

    def comp_parallel(self, g):
        """
        Composition parallèle non-destructive : renvoie un nouveau graphe
        """
        #Copie des graphes pour en creer un nouveau (maniere non destructive)  
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
    

    @classmethod
    def identity(cls, n):
        """
        Crée un graphe 'Identité' de taille n, agissant comme l'élément neutre de la composition séquentielle

        Structure attendue :
        - Le graphe contient 2n nœuds au total
        - n nœuds servent d'entrées (indices i_in)
        - n nœuds servent de sorties (indices i_out)
        - Pour chaque i allant de 0 à n-1, une arête unique est créée reliant le nœud d'entrée i au nœud de sortie i
        
        Propriétés :
        - Les listes 'inputs' et 'outputs' du graphe ont une longueur de n
        - Ce graphe ne modifie pas l'information mais se contente de la transmettre d'une couche à l'autre
        """
        # On commence par un graphe vide
        g = cls.empty()
        inputs = []
        outputs = []
        
        for i in range(n):
            # On crée un noeud pour l'entrée et un pour la sortie
            in_id = g.add_node(label=f"in_{i}")
            out_id = g.add_node(label=f"out_{i}")
            
            # On crée l'arête entre l'entrée et la sortie
            g.add_edge(in_id, out_id)
            
            # On enregistre ces noeuds comme interfaces
            inputs.append(in_id)
            outputs.append(out_id)
            
        # On définit les listes d'entrées et de sorties du graphe
        g.set_inputs(inputs)
        g.set_outputs(outputs)
        
        return g
    

    def connected_components(self):
        """
        Retourne la liste de toutes les composantes connexes du graphe.
        Chaque composante est une liste d'IDs de noeuds.
        
        Exercice 6 : Définition d'une composante connexe
        Dans le cadre de nos graphes ouverts (open_digraph), une composante 
        connexe est un sous-ensemble maximal de noeuds reliés entre eux par 
        un chemin d'arêtes.
        
        - Orientation des arêtes : L'orientation n'est pas prise en compte. 
          Deux noeuds sont considérés comme connectés s'il y a un lien entre 
          eux, peu importe qui est le parent ou l'enfant.
          
        - Traitement des entrées/sorties : Les noeuds d'entrée et de sortie 
          sont traités exactement comme des noeuds internes normaux. Puisqu'ils 
          sont stockés dans le dictionnaire 'self.nodes', l'algorithme les 
          visite et les inclut naturellement dans les composantes auxquelles 
          ils sont physiquement reliés.
          
        - Motivation : Cette définition est surtout motivée par des raisons 
          applicatives. Dans un circuit booléen, un fil relie 
          deux composants. Si on ignore le sens du courant (l'orientation), 
          une composante connexe représente un "morceau de circuit" physique 
          totalement indépendant des autres morceaux. 
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
        et retourne une liste d'objets open_digraph
        
        Difficultés propres aux graphes ouverts (Ordre des interfaces):
        Contrairement aux graphes classiques, décomposer un graphe ouvert pose un 
        problème conceptuel majeur : la perte de l'ordre global des entrées et sorties.
        
        Rôle de l'ordre : Dans un open_digraph, la liste des inputs et outputs définit 
        l'interface stricte du circuit (sa signature). En séparant le graphe en 
        plusieurs composantes (A, B, etc.), on conserve l'ordre relatif des entrées 
        à l'intérieur de A ou de B, mais on perd leur ordre absolu (global).
        
        Conséquence : Si l'on essaie de reconstruire le graphe d'origine en effectuant 
        une composition parallèle (ex: A.comp_parallel(B)), les entrées et sorties 
        seront simplement concaténées. Si l'entrée n°1 du graphe initial allait dans B 
        et la n°2 dans A, la composition parallèle inversera cet ordre. La décomposition 
        est donc "destructive" d'un point de vue de l'interface globale, à moins de 
        stocker en parallèle des graphes de permutation (ou de routage) pour mémoriser 
        l'indice exact de chaque fil d'interface.
        """
        # 1. On récupère les listes d'IDs des composantes
        components_ids = self.connected_components()
        graphs = []
        
        for comp in components_ids:
            # 2. On copie les noeuds appartenant à cette composante
            comp_nodes = [self.get_node_by_id(n_id).copy() for n_id in comp]
            
            # 3. On filtre les entrées et sorties globales pour conserver l'ordre relatif
            # (L'utilisation de la liste d'origine garantit que l'ordre interne est gardé)
            comp_inputs = [i for i in self.get_input_ids() if i in comp]
            comp_outputs = [o for o in self.get_output_ids() if o in comp]
            
            # 4. On instancie le nouveau sous-graphe
            new_graph = open_digraph(comp_inputs, comp_outputs, comp_nodes)
            graphs.append(new_graph)
            
        return graphs
    
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
    

    '''
    Exo 3 TD7
    Dans un algorithme de Parcours en Largeur,
    les nœuds sont explorés par niveaux successifs de distance.
    La distance d'un nœud découvert est strictement croissante.
    Donc la toute première fois que l'algorithme extrait le nœud cible (tgt) de la file,
    il est garanti que le chemin emprunté pour l'atteindre est le plus court possible.
    C' est donc inutile d'explorer le reste de la file, ce qui permet d'économiser du temps de calcul.
    '''

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
    

    '''
    Exo 4 TD7
    Pour implémenter cette fonction,
    nous avons réutilisé notre méthode bfs avec son paramètre de direction.
    Au lieu de rechercher les ancêtres de manière descendante,
    nous avons adopté une approche ascendante :

    Nous appelons bfs depuis le premier noeud cible avec direction = -1.
    Cela nous retourne un dictionnaire contenant tous ses ancêtres et leur distance respective.
    On fait de même pour le deuxième noeud cible
    Il suffit ensuite de calculer l'intersection des clés de ces deux dictionnaires pour isoler les ancêtres communs.

    Avantage : Cette méthode est performante car elle limite l'exploration à la stricte "généalogie" des deux nœuds,
    sans avoir à parcourir ou vérifier le reste du graphe. Elle permet d'obtenir les deux distances en seulement deux parcours BFS
    '''

    '''
    Exo 5 TD7
    Contrairement à l'algorithme de Dijkstra envisagé à l'Exercice 1 pour sa robustesse,
    nous avons implémenté un BFS avec dictionnaires, parfaitement adapté à nos distances de 1.
    L'utilisation d'une simple liste (file FIFO) et d'un dictionnaire dist pour marquer les nœuds visités
    rend le code très court et naturel à lire, évitant les lourdeurs de la recherche de minimum de Dijkstra
    Le dictionnaire prev agit comme une trace GPS. En retenant le parent de chaque nœud,
    il permet de reconstruire le plus court chemin par une simple remontée vers la source
    Le paramètre de direction agit comme un simple filtre (enfants, parents ou les deux)
    juste avant l'ajout des voisins dans la file, sans modifier la logique de l'algorithme.
    '''

        #TD8
 
    def tri_topologique(self):
        """
        Calcule le tri topologique vers le haut du graphe
        Retourne une liste de listes d'ID de noeuds
        Erreur si le graphe contient un cycle
        """
        # On ignore les entrées et sorties globales du graphe
        node_ids = self.get_node_ids()
        #calcule le nombre de parents pour chaque noeud
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