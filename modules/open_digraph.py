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




class open_digraph:
   def __init__(self, inputs, outputs, nodes):
       self.inputs = inputs
       self.outputs = outputs
       self.nodes = {node.id:node for node in nodes}
   def __str__ (self):
       return "Input :" + str(self.inputs) + ", outputs:" + str(self.outputs) + ", Noeuds:" + str(self.nodes.__str__())
   def __repr__(self):
       return self.__str__()
