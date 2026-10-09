# ⚡ Graphython — Open Digraphs & Boolean Circuit Compiler

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=ArThOxo/Graphyton)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

> **Moteur de modélisation, manipulation et évaluation de graphes orientés ouverts (Open Digraphs) et circuits logiques booléens en pur Python, accompagné d'une interface web interactive.**

---

## Aperçu du Projet

**Graphython** implémente une structure de données rigoureuse pour les graphes orientés ouverts (*open directed graphs* avec entrées/sorties distinctes) et les applique à la compilation et simulation de circuits logiques :

- **Théorie des Graphes :** Graphes orientés ouverts, détection de cycles, tri topologique, composantes connexes, matrices d'adjacence, composition séquentielle & parallèle.
- **Circuits Booléens :** Portes logiques (`AND`, `OR`, `XOR`, `NOT`, `NAND`, `NOR`, `XNOR`), copie/effacement d'arêtes.
- **Arithmétique Binaire :** Génération automatique d'additionneurs demi-additionneur (*Half-Adder*), additionneur complet (*Full-Adder*) et additionneurs à propagation de retenue $N$-bits (*Ripple-Carry Adders*).
- **Compilateur d'Expressions :** Parseur syntaxique transformant des expressions booléennes complexes (ex: `((x0 & x1) | ~x2) ^ x3`) en graphes acycliques de portes logiques avec évaluation dynamique.
- **Démonstrateur Web Interactif :** Visualisation dynamique des graphes via Graphviz (DOT), simulation en temps réel des valeurs d'entrée/sortie, et explorateur de code source intégré.

---

## Tester en 1 clic (Sans rien installer)

### Option 1 : GitHub Codespaces (Recommandé)
Cliquez sur le bouton ci-dessous pour lancer l'environnement de démo complet directement dans votre navigateur :

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=ArThOxo/Graphyton)

*(Le serveur se lance automatiquement sur le port 8080 et ouvre directement la démo interactive !)*

---

### Option 2 : En local

Le projet n'a **aucune dépendance tierce obligatoire** (utilise la bibliothèque standard de Python) :

```bash
# 1. Cloner le dépôt
git clone https://github.com/ArThOxo/Graphyton.git
cd graphython

# 2. Lancer la démo interactive
python demo_web.py
```
Ouvrez ensuite [http://localhost:8080](http://localhost:8080) dans votre navigateur.

---

## Architecture Modulaire

```text
graphython/
├── demo_web.py                   # Serveur HTTP & API de démonstration
├── modules/                      # Cœur algorithmique
│   ├── node.py                   # Modélisation des nœuds (parents, enfants, données)
│   ├── open_digraph.py           # Structure de graphe ouvert (entrées, sorties, arêtes)
│   ├── composition.py            # Compositions parallèle et séquentielle
│   ├── matrix.py                 # Matrices d'adjacence et transformations algébriques
│   ├── algo_tout_genre.py        # Tri topologique, détection de cycles, composantes
│   ├── bool_circ.py              # Classe spécialisée BoolCircuit (circuits logiques)
│   ├── bool_circ_adders.py       # Génération d'additionneurs 1-bit à N-bits
│   ├── bool_circ_eval.py         # Moteur d'évaluation topologique des circuits
│   ├── bool_circ_gen.py          # Générateurs de circuits aléatoires
│   └── bool_circ_parse.py        # Parseur d'expressions logiques en graphe booléen
└── web/                          # Interface Web (HTML5 / Vanilla CSS / Viz.js / Highlight.js)
```

---

## Fonctionnalités Clés de la Démo

1. **Portes & Circuits de base :** Sélection et évaluation visuelle de toutes les portes booléennes élémentaires.
2. **Additionneurs N-bits paramétrables :** Choisissez le nombre de bits (1 à 8 bits), saisissez les entiers $A$ et $B$, et observez la propagation de retenue et le résultat binaire/décimal calculé par le graphe.
3. **Parseur d'Expressions Logiques :** Tapez n'importe quelle formule logique (opérateurs `&`, `|`, `^`, `~`) pour générer instantanément le graphe associé et évaluer les tables de vérité.
4. **Explorateur de Code Source :** Visualiseur des modules Python du projet.

---
