import random

class OpenDigraphMatrix:
    @staticmethod
    def random_int_list(n,bound):
        return [random.randint(0, bound) for _ in range(n)]
    
    @staticmethod
    def random_int_matrix(n, bound, null_diag=False):
        matrix = [OpenDigraphMatrix.random_int_list(n, bound) for _ in range(n)]
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
        matrix = OpenDigraphMatrix.random_int_matrix(n, bound, null_diag)
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

    @classmethod
    def identity(cls, n):
        """
        Crée un graphe 'Identité' de taille n, agissant comme l'élément neutre de la composition séquentielle

        """
        g = cls.empty()
        inputs = []
        outputs = []
        
        for i in range(n):
            in_id = g.add_node(label=f"in_{i}")
            out_id = g.add_node(label=f"out_{i}")
            g.add_edge(in_id, out_id)
            inputs.append(in_id)
            outputs.append(out_id)
            
        g.set_inputs(inputs)
        g.set_outputs(outputs)
        return g
