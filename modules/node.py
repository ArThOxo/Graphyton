class node:
    def __init__(self, identity, label, parents, children):
        """
        identity : int identifiant unique dans le graphe
        label    : str étiquette du nœud
        parents  : dict[int, int] id parent → multiplicité
        children : dict[int, int] id enfant → multiplicité
        """
        self.id       = identity
        self.label    = label
        self.parents  = parents
        self.children = children

    def __str__(self):
        return (f"node(id={self.id}, label={self.label!r}, "
                f"parents={self.parents}, children={self.children})")

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return node(self.id, self.label, self.parents.copy(), self.children.copy())

    # getters

    def get_id(self):
        return self.id

    def get_label(self):
        return self.label

    def get_parents(self):
        return self.parents

    def get_children(self):
        return self.children

    # setters

    def set_id(self, v):
        self.id = v

    def set_label(self, v):
        self.label = v

    def set_parents(self, v):
        self.parents = v

    def set_children(self, v):
        self.children = v

    def add_child_id(self, child_id, mult=1):
        self.children[child_id] = self.children.get(child_id, 0) + mult

    def add_parent_id(self, parent_id, mult=1):
        self.parents[parent_id] = self.parents.get(parent_id, 0) + mult

    def remove_child_once(self, child_id):
        if child_id not in self.children:
            raise KeyError(f"L'enfant {child_id} n'est pas dans les enfants du nœud.")
        self.children[child_id] -= 1
        if self.children[child_id] == 0:
            del self.children[child_id]

    def remove_parent_once(self, parent_id):
        if parent_id not in self.parents:
            raise KeyError(f"Le parent {parent_id} n'est pas dans les parents du nœud.")
        self.parents[parent_id] -= 1
        if self.parents[parent_id] == 0:
            del self.parents[parent_id]

    def remove_child_id(self, child_id):
        if child_id not in self.children:
            raise KeyError(f"L'enfant {child_id} n'est pas dans les enfants du nœud.")
        del self.children[child_id]

    def remove_parent_id(self, parent_id):
        if parent_id not in self.parents:
            raise KeyError(f"Le parent {parent_id} n'est pas dans les parents du nœud.")
        del self.parents[parent_id]

    # degrés

    def indegree(self):
        return sum(self.parents.values())

    def outdegree(self):
        return sum(self.children.values())

    def degree(self):
        return self.indegree() + self.outdegree()
