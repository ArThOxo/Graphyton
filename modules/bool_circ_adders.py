from modules.open_digraph import open_digraph

class BoolCircAdders:
    @classmethod
    def build_adder0(cls):
        """
        Construit le circuit de base Adder0 (additionneur 1 bit complet).
        Entrées : a, b, carry_in (3 entrées)
        Sorties : somme, carry_out (2 sorties)
        
        somme     = a ^ b ^ carry_in
        carry_out = (a & b) | ((a ^ b) & carry_in)
        
        return un open_digraph 
        """
        g = open_digraph.empty()
        copy_a = g.add_node(label='')       # distribue a vers xor1 et and1
        copy_b = g.add_node(label='')       # distribue b vers xor1 et and1
        copy_cin = g.add_node(label='')     # distribue carry_in vers xor2 et and2
        xor1 = g.add_node(label='^')        # a ^b
        and1 = g.add_node(label='&')        # a & b
        copy_xor1 = g.add_node(label='')    # distribue (a ^b) vers xor2 et and2
        xor2 = g.add_node(label='^')        # (a^b) ^ carry_in = somme
        and2 = g.add_node(label='&')        # (a^b) & carry_in
        or1 = g.add_node(label='|')         # (a&b) | ((a^b)&carry_in) = carry_out

        g.add_edge(copy_a, xor1)
        g.add_edge(copy_a, and1)
        g.add_edge(copy_b, xor1)
        g.add_edge(copy_b, and1)
        g.add_edge(xor1, copy_xor1)
        g.add_edge(copy_xor1, xor2)
        g.add_edge(copy_xor1, and2)
        g.add_edge(copy_cin, xor2)
        g.add_edge(copy_cin, and2)
        g.add_edge(and1, or1)
        g.add_edge(and2, or1)
        
        # Entrée a, b, carry_in
        g.add_input_node(copy_a)
        g.add_input_node(copy_b)
        g.add_input_node(copy_cin)
        # sortie : somme, carry_out
        g.add_output_node(xor2)
        g.add_output_node(or1)
        return g

    @classmethod
    def build_adder(cls, n):
        """
        Construit récursivement un additionneur Adder_n.
        Taille du registre : s = 2^n bits.
        Entrées : a[0..s-1], b[0..s-1], carry_in   (total : 2s + 1)
        Sorties : r[0..s-1], carry_out               (total : s + 1)
        
        Construction inductive :
        - On compose en parallèle deux Adder_{n-1} (bits de poids faible et poids fort)
        - On connecte la retenue sortante du bloc bas vers l'entrée retenue du bloc haut
        
        Retourne un open_digraph
        """
        if n == 0:
            return cls.build_adder0()
        
        half = 2 ** (n - 1)
        adder_bas = cls.build_adder(n - 1)
        adder_haut = cls.build_adder(n - 1)
        g = adder_bas.comp_parallel(adder_haut)
        inputs = g.get_input_ids()
        outputs = g.get_output_ids()
        # carry_out du sous-additionneur bas = dernier output du bloc bas
        c_out_bas_id = outputs[half]
        # carry_in du sous-additionneur haut = dernier input du bloc haut
        c_in_haut_id = inputs[-1]
        c_out_bas_parent = list(g.get_node_by_id(c_out_bas_id).get_parents().keys())[0]
        c_in_haut_child = list(g.get_node_by_id(c_in_haut_id).get_children().keys())[0]
        g.remove_node_by_id(c_out_bas_id)
        g.remove_node_by_id(c_in_haut_id)
        g.add_edge(c_out_bas_parent, c_in_haut_child)
        # Avant: [a_low(h), b_low(h), c_in, a_high(h), b_high(h)]
        inputs = g.get_input_ids()
        a_low = inputs[0:half]
        b_low = inputs[half:2*half]
        c_in = [inputs[2*half]]
        a_high = inputs[2*half+1:3*half+1]
        b_high = inputs[3*half+1:4*half+1]
         # Apres : [a_low(h), a_high(h), b_low(h), b_high(h), c_in]
        g.set_inputs(a_low + a_high + b_low + b_high + c_in)
        # Les sorties sont déjà dans le bon ordre : [r_low(h), r_high(h), c_out]
        return g

    @classmethod
    def Adder(cls, n):
        """
        Construit un additionneur Adder_n validé comme circuit booléen.
        Taille du registre : s = 2^n bits.
        Entrées : a[0..s-1], b[0..s-1], carry_in   (total : 2s + 1)
        Sorties : r[0..s-1], carry_out               (total : s + 1)
        """
        g = cls.build_adder(n)
        return cls(g)

    @classmethod
    def Half_Adder(cls, n):
        """
        Construit un Half_Adder_n : additionneur sans retenue d'entrée.
        La retenue d'entrée est remplacée par une constante 0.
        Taille du registre : s = 2^n bits.
        Entrées : a[0..s-1], b[0..s-1]   (total : 2s)
        Sorties : r[0..s-1], carry_out     (total : s + 1)
        """
        g = cls.build_adder(n)
        inputs = g.get_input_ids()
        c_in_id = inputs[-1]  # carry_in est toujours la dernière entrée
        # Trouver le noeud interne connecté au carry_in
        c_in_child = list(g.get_node_by_id(c_in_id).get_children().keys())[0]
        # Supprimer carry_in
        g.remove_node_by_id(c_in_id)
        # Ajouter une constante 0 à la place
        zero_id = g.add_node(label='0')
        g.add_edge(zero_id, c_in_child)
        return cls(g)
