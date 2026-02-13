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
    



