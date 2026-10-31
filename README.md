# Robot de réconfort — SAD & SAHNOUNE

Projet de semestre, master informatique. Un robot à perception locale
consulte un dictionnaire, fouille une armoire et rapporte un objet à un
résident.

Langage : *Pyhton* — Version : *3.11.5*

## Lancer
Lancer depuis Base_fournie: 
cd robot-reconfort
cd base_fournie

```
python agent.py <carte.json> <scenario.json> <dossier_donnees> <trace_sortie.json>
```

Exemple :

```
python agent.py cartes/appartement_01.json cartes/scenario_01.json donnees sortie.json
```

Dépendances : *aucune* 
Pour rejouer une trace à l'écran (utilisé pour la vidéo) :

```
python affichage.py cartes/appartement_01.json cartes/scenario_01.json donnees sorties/trace_01.json --delai 0.3
```

## Tester

``'
// depuis base_fournie
cd robot-reconfort
cd base_fournie
python -m unittest discover -s tests  
```


les tets  couvrent la mémoire,la décision et le simulateur.
## Organisation du code

| Fichier | Rôle |
| `agent.py` |  valide les fichiers, puis boucle perception → mémoire → décision → action |
| `validation.py` | validation des fichiers d'entrée  |
| `infos_initiales.py` | ne garde que ce que le robot a le droit de connaître au départ |
| `environnement.py` | simulateur : monde réel, répond aux perceptions et valide les actions |
| `memoire.py` | mémoire du robot : carte mentale, armoire mentale, position, objet porté, résidents atteints |
| `planification.py` | plus court chemin par parcours en largeur |
| `decision.py` | choix de l'action : dictionnaire, vérification du résident, armoire, livraison |
| `action.py` | exécution d'une action et journalisation dans la trace |
| `regles.py` | lecture du message  et liste ordonnée des casiers candidats sur la roue de Plutchik |
| `armoire.py` | déplacement du sélecteur  |
| `dictionnaire.py` | lecture du dictionnaire, après le `CONSULTER` |
| `reconfort_io.py` | lecture des fichiers et écriture de la trace  |
| `affichage.py` | rejoue une trace à l'écran |


## État

**Ce qui marche.** 
 Avec les cartes fournies  toutes les demandes sont livrées (29 sur 29).

- Résident inaccessible : le parcours en largeur ne trouve pas de chemin, sans rien prendre.
- Perception locale : l'agent ne lit ni la grille ni le contenu des casiers.
- Validation des fichiers d'entrée (section 5.6).
**Ce qui ne marche pas.**
 — Ce qui n'a pas été couvert par les tests: lecture du dictionnaire,régle de repli,déplacement du sélecteur et validations des fichiers (pour les fichiers ils ont été testé à la main)

## Vidéo

`https://youtu.be/ZBigNf5V4tk` (ou le lien), également déclarée dans `rendu.json`.
