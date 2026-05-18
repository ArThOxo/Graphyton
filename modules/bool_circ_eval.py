from modules.open_digraph import open_digraph

class BoolCircEval:
    # TD11 Exercice 3 
    # Méthodes pour les transformations
    
    def _get_constant_parents(self, node):
        """Retourne la liste des parents du noeud qui sont des constante"""
        constants = []
        for pid in node.get_parents():
            p = self.get_node_by_id(pid)
            if p.get_label() in ('0', '1') and p.indegree() == 0:
                constants.append(p)
        return constants
        
    def _replace_node_with_constant(self, node, value):
        """
        Remplace un noeud par une constante 
        Reconnecte tous ses enfants à cette nouvelle constante
        et nettoie les parents qui n'ont plus d'utilité
        """
        node_id = node.get_id()
        children = list(node.get_children().items())
        parents = list(node.get_parents().keys())
        self.remove_node_by_id(node_id)
        for pid in parents:
            if pid in self.nodes:
                p = self.get_node_by_id(pid)
                if p.get_label() in ('0', '1') and p.indegree() == 0 and p.outdegree() == 0:
                    self.remove_node_by_id(pid)         
        for child_id, mult in children:
            for _ in range(mult):
                new_const = self.add_node(label=value)
                self.add_edge(new_const, child_id)  
                
    def _remove_constant_parent(self, node, const_parent):
        """remove le lien entre une constante et un noeud"""
        self.remove_parallel_edges(const_parent.get_id(), node.get_id())
        if const_parent.outdegree() == 0:
            self.remove_node_by_id(const_parent.get_id())

    def _insert_not_gate_after(self, node):
        """Insère une porte NON après le node"""
        node_id = node.get_id()
        children = list(node.get_children().items())
        for child_id, mult in children:
            self.remove_parallel_edges(node_id, child_id)
            not_id = self.add_node(label='~')
            self.add_edge(node_id, not_id)
            for _ in range(mult):
                self.add_edge(not_id, child_id)

    # Transformation

    def _transform_copy(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.get_label() != '' or node_id in self.get_input_ids() or node_id in self.get_output_ids():
            return False
        const_parents = self._get_constant_parents(node)
        if not const_parents or len(node.get_parents()) != 1:
            return False
        const_value = const_parents[0].get_label()
        self._replace_node_with_constant(node, const_value)
        return True

    def _transform_not(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.get_label() != '~':
            return False    
        const_parents = self._get_constant_parents(node)
        if not const_parents or len(node.get_parents()) != 1:
            return False   
        #Remplace constante inverse
        const = const_parents[0].get_label()
        if const == '1':
            inverse = '0'
        else: 
            inverse = '1'
        self._replace_node_with_constant(node,inverse)
        return True

    def _transform_and(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.get_label() != '&':
            return False   
        const_parents = self._get_constant_parents(node)
        if not const_parents:
            return False  
        const_parent = const_parents[0]
        if const_parent.get_label() == '0':
            # 0 est absorbant pour le ET : tout le noeud devient 0
            self._replace_node_with_constant(node, '0')
        else:
            # 1 est neutre pour le ET : on ignore juste cette entrée
            self._remove_constant_parent(node, const_parent)
        return True

    def _transform_or(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.get_label() != '|':
            return False    
        const_parents = self._get_constant_parents(node)
        if not const_parents:
            return False   
        const_parent = const_parents[0]
        if const_parent.get_label() == '1':
            #  tout le noeud devient 1
            self._replace_node_with_constant(node, '1')
        else:
            # 0 est neutre
            self._remove_constant_parent(node, const_parent)
        return True

    def _transform_xor(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.get_label() != '^':
            return False
        const_parents = self._get_constant_parents(node)
        if not const_parents:
            return False
        const_parent = const_parents[0]
        if const_parent.get_label() == '0':
            # 0 est neutre 
            self._remove_constant_parent(node, const_parent)
        else:
            # 1 inverse 
            self._remove_constant_parent(node, const_parent)
            self._insert_not_gate_after(node)
        return True

    def _transform_neutral(self, node_id):
        node = self.get_node_by_id(node_id)
        label = node.get_label()
        if label not in ('&', '|', '^'):
            return False
        indeg = node.indegree()
        if indeg == 0:
            # S'il ne reste plus aucune entrée, on remplace la porte par l'élément neutre de son opération
            if label == '&':
                neutre = '1'
            else:
                neutre = '0'
            self._replace_node_with_constant(node, neutre)
            return True
        elif indeg == 1:
            # Si une seule entrée:  fil
            node.set_label('')
            return True
        
        return False

    def _transform_assoc_xor(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.get_label() != '^':
            return False
        for parent_id in list(node.get_parents().keys()):
            parent_node = self.get_node_by_id(parent_id)
            if parent_node.get_label() == '^':
                for grand_parent_id, mult in list(parent_node.get_parents().items()):
                    for _ in range(mult):
                        self.add_edge(grand_parent_id, node_id)
                self.remove_node_by_id(parent_id)
                return True
        return False

    def _transform_assoc_copy(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.get_label() != '' or node_id in self.get_input_ids() or node_id in self.get_output_ids():
            return False
        if len(node.get_parents()) != 1:
            return False
        parent_id = list(node.get_parents().keys())[0]
        parent_node = self.get_node_by_id(parent_id)
        if parent_node.get_label() != '' or parent_id in self.get_input_ids() or parent_id in self.get_output_ids():
            return False
        for child_id, mult in list(node.get_children().items()):
            self.remove_parallel_edges(node_id, child_id)
            for _ in range(mult):
                self.add_edge(parent_id, child_id)
        self.remove_node_by_id(node_id)
        return True

    def _transform_inv_xor(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.get_label() != '^':
            return False
        changed = False
        for parent_id, mult in list(node.get_parents().items()):
            if mult > 1:
                self.remove_parallel_edges(parent_id, node_id)
                if mult % 2 != 0:
                    self.add_edge(parent_id, node_id)
                changed = True
        return changed

    def _transform_erasure(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.outdegree() == 0 and node_id not in self.get_output_ids():
            self.remove_node_by_id(node_id)
            return True
        return False

    def _transform_not_through_xor(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.get_label() != '^':
            return False
        for parent_id in list(node.get_parents().keys()):
            parent_node = self.get_node_by_id(parent_id)
            if parent_node.get_label() == '~':
                grand_parent_id = list(parent_node.get_parents().keys())[0]
                self.remove_node_by_id(parent_id)
                self.add_edge(grand_parent_id, node_id)
                self._insert_not_gate_after(node)
                return True
        return False

    def _transform_not_through_copy(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.get_label() != '' or node_id in self.get_input_ids() or node_id in self.get_output_ids():
            return False
        if len(node.get_parents()) != 1:
            return False
        parent_id = list(node.get_parents().keys())[0]
        parent_node = self.get_node_by_id(parent_id)
        if parent_node.get_label() == '~':
            grand_parent_id = list(parent_node.get_parents().keys())[0]
            self.remove_node_by_id(parent_id)
            self.add_edge(grand_parent_id, node_id)
            self._insert_not_gate_after(node)
            return True
        return False

    def _transform_inv_not(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.get_label() != '~':
            return False
        if len(node.get_parents()) != 1:
            return False
        parent_id = list(node.get_parents().keys())[0]
        parent_node = self.get_node_by_id(parent_id)
        if parent_node.get_label() == '~':
            if len(parent_node.get_parents()) != 1:
                return False
            grand_parent_id = list(parent_node.get_parents().keys())[0]
            if len(node.get_children()) != 1:
                return False
            child_id = list(node.get_children().keys())[0]
            self.remove_node_by_id(parent_id)
            self.remove_node_by_id(node_id)
            self.add_edge(grand_parent_id, child_id)
            return True
        return False

    def _transform_useless_copy(self, node_id):
        node = self.get_node_by_id(node_id)
        if node.get_label() != '' or node_id in self.get_input_ids() or node_id in self.get_output_ids():
            return False
        if len(node.get_parents()) == 1 and node.outdegree() == 1:
            parent_id = list(node.get_parents().keys())[0]
            child_id = list(node.get_children().keys())[0]
            self.remove_node_by_id(node_id)
            self.add_edge(parent_id, child_id)
            return True
        return False

    def evaluate_rewriting(self):
        """
        Applique toutes les règles de réécriture algébrique et d'évaluation tant qu'au moins une s'applique sur le graphe.
        """
        changed = True
        while changed:
            changed = False
            for node_id in list(self.get_node_ids()):
                if node_id not in self.nodes:
                    continue
                if (self._transform_copy(node_id)
                        or self._transform_not(node_id)
                        or self._transform_and(node_id)
                        or self._transform_or(node_id)
                        or self._transform_xor(node_id)
                        or self._transform_neutral(node_id)
                        or self._transform_assoc_xor(node_id)
                        or self._transform_assoc_copy(node_id)
                        or self._transform_useless_copy(node_id)
                        or self._transform_inv_xor(node_id)
                        or self._transform_erasure(node_id)
                        or self._transform_not_through_xor(node_id)
                        or self._transform_not_through_copy(node_id)
                        or self._transform_inv_not(node_id)):
                    changed = True



    def evaluate(self, inputs):
        """
        Évalue le circuit booléen sur une liste de valeurs d'entrée (0 ou 1).

        """
        bc = open_digraph.__new__(self.__class__)
        open_digraph.__init__(bc,
                              self.inputs.copy(),
                              self.outputs.copy(),
                              [n.copy() for n in self.get_nodes()])

        input_ids = bc.get_input_ids()[:]
        for i, in_id in enumerate(input_ids):
            val = str(inputs[i])
            in_node = bc.get_node_by_id(in_id)
            child_id = list(in_node.get_children().keys())[0]
            bc.remove_node_by_id(in_id)
            const_id = bc.add_node(label=val)
            bc.add_edge(const_id, child_id)

        changed = True
        while changed:
            changed = False
            for node_id in list(bc.get_node_ids()):
                if node_id not in bc.get_node_ids():
                    continue
                if (bc._transform_copy(node_id)
                        or bc._transform_not(node_id)
                        or bc._transform_and(node_id)
                        or bc._transform_or(node_id)
                        or bc._transform_xor(node_id)
                        or bc._transform_neutral(node_id)):
                    changed = True

        result = []
        for out_id in bc.get_output_ids():
            out_node = bc.get_node_by_id(out_id)
            parent_id = list(out_node.get_parents().keys())[0]
            parent_label = bc.get_node_by_id(parent_id).get_label()
            result.append(int(parent_label))
        return result


    def evaluate_integer(self, *integers, size=8):
        """
        Évalue le circuit booléen en fournissant des entiers encodés en binaire.

        """
        input_bits = []
        for n in integers:
            input_bits += [int(b) for b in bin(n)[2:].zfill(size)]

        output_bits = self.evaluate(input_bits)
        result = int(''.join(str(b) for b in output_bits), 2) if output_bits else 0
        return result
