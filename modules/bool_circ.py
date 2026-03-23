from modules.open_digraph import open_digraph


class bool_circ(open_digraph):
    def __init__(self, g):
        super().__init__(g.get_input_ids().copy(), g.get_output_ids().copy(), [n.copy() for n in g.get_nodes()])