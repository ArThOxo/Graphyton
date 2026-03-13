import random

class node:
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



    #GETTERS
    def get_id(self):
        return self.id
    def get_label(self):
        return self.label
    def get_parents(self):
        return self.parents
    def get_children(self):
        return self.children

    #Setters 
    def set_id(self , newID):
        self.id = newID
    def set_label(self , newLABEL):
        self.label = newLABEL
    def set_parent(self , newParents):
        self.parents = newParents
    def set_children(self , newChildren):
        self.children = newChildren
    def add_child_id (self, id , multiplicity =1):
        if id in self.children:
            self.children[id] += multiplicity
        else:
            self.children[id] = multiplicity
    def add_parents_id (self, id , multiplicity =1):
        if id in self.parents:
            self.parents[id] += multiplicity
        else:
            self.parents[id] = multiplicity


###############################################################################
#### TD 2
#########################################################
    def remove_parent_once(self, id):
        if id in self.parents:
            if self.parents[id] > 0:
                self.parents[id] -= 1
            else:
                self.parents.pop(id)
        else:
            raise KeyError(f"le noeud id n'est pas celui d'un daddy")


    def remove_child_once(self, id):
        if id in self.children:
            if self.children[id] > 0:
                self.children[id] -= 1
            else:
                self.children.pop(id)
        else:
            raise KeyError(f"le noeud id n'est pas celui d'un child")
    
    def remove_parent_id(self, id):
        if id in self.parents:
            self.parents.pop(id)
        else:
            raise KeyError(f"le noeud id n'est pas celui d'un daddy")


    def remove_child_id(self, id):
        if id in self.children:
            self.children.pop(id)
        else:
            raise KeyError(f"le noeud id n'est pas celui d'un child")


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


class open_digraph:
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

    def is_well_formed(self):

        inputnodes = self.inputs.get_nodes_by_ids()
        outputnodes = self.outputs.get_node_by_ids()
        if len(inputnodes) != len(self.inputs) or  len(outputnodes) != len(self.outputs):
            return False
        for elem in inputnodes:
            if len(elem.get_parents()) >= 1 or len(elem.get_children()) > 1 or len(elem.get_children()) < 1 or  list(elem.get_children().values())[0] != 1 :
                return False
        for elem in outputnodes:
            if len(elem.get_children()) >= 1 or len(elem.get_parents()) > 1 or len(elem.get_parents()) < 1 or list(elem.get_parents().values())[0] != 1:
                return False
        
        for elem in self.nodes :
            if elem != self.nodes[elem].get_id():
                return False 
            #Dictionnaire des enfants de la node d'id ELEM
            elemchild = self.nodes[elem].get_children()
            #Dictionnaire des parents de la node d'id ELEM
            elemparents = self.nodes[elem].get_parents()
            #
            for ch,multiplicityCH in elemchild.items():
                childparents = self.get_node_by_id(ch).get_parents()
                #Recupere les parents des enfants de la node d'id ELEM

                #ASSURE QUE NOTRE NODE est presente dans la liste des partens de ses enfants
                if not elem in childparents:
                    return False
                #SI la node est bien presente on s'assure que la multiplicit
                else:
                    if childparents[elem] != multiplicityCH:
                        return False

            for pr,multiplicityPR in elemparents.items():
                parentchildren = self.get_node_by_id(pr).get_children()
                #Recupere les enfants des parents de la node d'id ELEM

                #ASSURE QUE NOTRE NODE est presente dans la liste des enfants de ses partents
                if not elem in parentchildren:
                    return False
                #SI la node est bien presente on s'assure que la multiplicit
                else:
                    if parentchildren[elem] != multiplicityPR:
                        return False
        return True


    def add_input_node(self, target_id):
        if target_id not in self.nodes:
            raise ValueError(f"Le noeud n'existe pas dans le graphe")
        new_id = self.add_node(label="") 
        self.add_edge(new_id, target_id)
        self.inputs.append(new_id)
        
        return new_id

    def add_output_node(self, source_id):
        if source_id not in self.nodes:
            raise ValueError(f"Le noeud n'existe pas dans le graphe.")
        new_id = self.add_node(label="") 
        self.add_edge(source_id, new_id)
        self.outputs.append(new_id)
        
        return new_id



    def new_id(self):
        ids = self.get_nodes_ids()
        if len(ids) == 0:
            return 0
        return max(ids) +1
    
    def add_edge(self, src ,trgt):
        src2 = self.get_node_by_id(src)
        trgt2= self.get_node_by_id(trgt)
        src2.add_child_id(trgt)
        trgt2.add_parents_id(src)

    def add_edges(self, edges): 
        for src, tgt in edges:
            self.add_edge(src, tgt)


    # GETTERQS

    def get_inputs_ids(self):
        return self.inputs

    def get_node_by_id(self, id):
        return self.nodes[id]

    def get_nodes_by_ids (self, ids):
        resultat = []
        for elem in ids:
            resultat.append(self.nodes[elem])
        return resultat

    def get_id_node_map(self):
        return self.nodes 
    def get_nodes(self):
        return list(self.nodes.values())

    def get_nodes_ids(self):
        return list(self.nodes.keys())
                
    # SETTERS
    def set_inputs (self , newInputs):
        self.inputs = newInputs
    def set_outputs (self, newOuputs):
        self.outputs = newOuputs
    def add_output_id (self , outID):
        if outID not in self.outputs:
            self.outputs.append(outID)
    def add_input_id (self , inID):
        if inID not in self.inputs:
            self.inputs.append(inID)

    def add_node(self, label='', parents=None, children=None):
        if parents is None:
            parents = {}
        if children is None:
            children = {}
        id = self.new_id() 
        new_n = node(id, label, parents, children) 
        self.nodes[id] = new_n 
        for parent_id, multiplicity in parents.items():
            if parent_id in self.nodes:
                parent_node = self.nodes[parent_id]
                parent_node.add_child_id(id, multiplicity)
            
    
        for child_id, multiplicity in children.items():
            if child_id in self.nodes:
                child_node = self.nodes[child_id]
                child_node.add_parents_id(id, multiplicity)
    #TD 3
    def random_int_list(n,bound):
        res = []
        for i in range(n):
            res.append(random.randint(0,bound))
        return res
    def random_matrix(n, bound, null_diag=False): 
        matrix = [[random_int_list(n,bound)] for i in range(n)]
        if null_diag:
            for j in range(n):
                matrix[j][j] = 0
        return matrix
    
        
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

    def random_triangular_int_matrix(n, bound, null_diag=True):
        matrix = random_matrix(n,bound)
        for i in range(n):
            for j in range(0,i):
                matrix[i][j]=0
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
                    g.nodes[ids[j]].add_parents_id(ids[i], matrix[i][j])
        return g


    @classmethod
    def random(cls, n, bound, inputs=0, outputs=0, form="free"):
        if form == "free":
            matrix = random_int_matrix(n, bound)
        elif form == "DAG":
            matrix = random_triangular_int_matrix(n, bound)
        elif form == "oriented":
            matrix = random_oriented_int_matrix(n, bound)
        elif form == "loop-free":
            matrix = random_int_matrix(n, bound, null_diag=True)
        elif form == "undirected":
            matrix = random_symetric_int_matrix(n, bound, null_diag=False)
        elif form == "loop-free undirected":
            matrix = random_symetric_int_matrix(n, bound, null_diag=True)
        else:
            raise ValueError("erreur forme")
        
        g = cls.graph_from_adjacency_matrix(matrix)
        
        node_ids = g.get_nodes_ids()
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