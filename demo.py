import time
from modules.open_digraph import open_digraph
from modules.bool_circ import bool_circ

def pause():
    input("\n[Appuyez sur ENTRÉE pour continuer la démonstration]")
    print("\n" + "-" * 60 + "\n")

def demo_soutenance():
    print("=" * 60)
    print("              GRAPHES ET CIRCUITS BOOLÉENS")
    print("=" * 60)
    pause()

    # PARTIE 1 : Parsing et Évaluation d'une formule
    print("PARTIE 1 : Parsing d'une expression logique")
    print("Objectif : Transformer une chaîne de caractères en un circuit de portes logiques")
    formule = "((x0)&(~(x1)))"
    print(f"\nFormule lue par le programme : {formule}")
    print("Explication : C'est un 'ET' logique entre 'x0' et la négation de 'x1'")
    
    circuit, variables = bool_circ.from_string(formule)
    print(f"Graphe généré avec succès en mémoire ! Variables extraites : {variables}")
    
    print("\nSimulation de la table de vérité :")
    for x0 in [0, 1]:
        for x1 in [0, 1]:
            resultat = circuit.evaluate([x0, x1])
            print(f"   [x0={x0}, x1={x1}]  ->  Sortie = {resultat[0]}")
            time.sleep(0.5)

    print("\nOuverture du navigateur pour visualiser l'architecture du graphe")
    circuit.display(verbose=True)
    pause()

    # PARTIE 2 : L'Additionneur (Complexité algorithmique)
    print("PARTIE 2 : L'Additionneur (Composant électronique)")
    print("Objectif : Prouver que notre graphe peut modéliser du hardware complexe")
    print("           en le construisant de manière récursive")
    
    print("\nGénération d'un Adder(1) (soit un additionneur de 2 bits)")
    adder = bool_circ.Adder(1)
    
    print(f"Circuit généré : {len(adder.get_nodes())} noeud")
    print(f"Ce circuit possède {len(adder.get_input_ids())} entrées et {len(adder.get_output_ids())} sorties")
    
    print("\nTestons le ! Faisons l'opération : 3 + 2")
    entrees = [1, 1, 0, 1, 0]
    print(f"  A = 3 (bits faibles en premier : 1, 1)")
    print(f"  B = 2 (bits faibles en premier : 0, 1)")
    print(f"  Retenue d'entrée (Carry In) = 0")
    print(f"  Injection du vecteur {entrees} dans les noeuds d'entrée du graphe")
    
    resultat = adder.evaluate(entrees)
    
    somme_binaire = resultat[:2]
    carry = resultat[2]
    val_decimale = somme_binaire[0] * 1 + somme_binaire[1] * 2 + carry * 4
    
    print(f"\nRésultat brut du graphe : Somme = {somme_binaire}, Retenue sortante = {carry}")
    print(f"Conversion en décimal   : {val_decimale}")
    if val_decimale == 5:
         print("Succès : Le circuit a propagé les bits et calculé 3 + 2 = 5")
    
    pause()

    # PARTIE 3 : Génération Aléatoire et Tri Topologique
    print("PARTIE 3 : Génération Aléatoire et Robustesse")
    print("Objectif : Démontrer la solidité de la librairie avec des graphes chaotiques")
    
    print("\nCréation d'un circuit aléatoire (15 noeuds, 3 entrées, 2 sorties)")
    circuit_rand = bool_circ.random_bool_circ_with_io(n=15, bound=2, nb_inputs=3, nb_outputs=2)
    print("Circuit généré avec succès ! Le graphe respecte les propriétés d'un DAG")
    
    print("\nCalcul algorithmique sur ce graphe (Tri Topologique) :")
    try:
        prof = circuit_rand.profondeur_graphe()
        print(f"Le graphe est bien organisé en {prof} niveaux de profondeur")
    except Exception as e:
         print("Erreur:", e)

    print("\nOuverture du navigateur pour visualiser ce circuit chaotique")
    circuit_rand.display(verbose=False)
    
    print("\n" + "=" * 60)
    print("FIN DE LA DÉMONSTRATION.")
    print("=" * 60)

if __name__ == "__main__":
    demo_soutenance()
