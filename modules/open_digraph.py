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
        y = node(self.id, self.label, self.parents, self.children)
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
    def set_labels(self , newLABEL):
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
        y = open_digraph(self.inputs, self.outputs, self.nodes)
        return y
    
    def newID(self):
        


    # GETTERQS

    def get_inputs_ids(self):
        return self.inputs
    def get_node_by_id(self, id):
        for ids in self.nodes:
            if ids.get_id()== id:
                return ids
    def get_nodes_by_ids (self, ids):
        resultat = []
        for elem in self.nodes:
            if elem.get_id() in ids:
                resultat.append(elem)
        return elem
    def get_id_node_map(self):
        return self.nodes 
    def get_nodes(self):
        return list(self.nodes)

                
    #
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



