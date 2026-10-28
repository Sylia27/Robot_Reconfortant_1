# Robot de réconfort — SAD & SAHNOUNE

Projet de semestre, master informatique. Un robot à perception locale
consulte un dictionnaire, fouille une armoire et rapporte un objet à un
résident.

Langage : *Pyhton* — Version : **

## Lancer

```
<votre commande> <carte.json> <scenario.json> <dossier_donnees> <trace_sortie.json>
```

Exemple :

```
python agent.py cartes/appartement_01.json cartes/scenario_01.json donnees sortie.json
```

Dépendances : *aucune*, ou la liste et comment les installer.

## Tester

``'
// depuis base_fournie
cd robot-reconfort
cd base_fournie
python -m unittest discover -s tests  
```

*Une phrase sur ce que couvrentn; les tests.*
les tets unitaires couvrent les régles de décisio
## Organisation du code

| Fichier | Rôle |
|'regles.py'| roue de Plutchik|
|'armoire.py'|mouvement selecteur et repli|
|'environnement.py'|simulateur|
|'memoire.py'|memoire du robot : carte mentale,armoire mentale, cases deja vus, mains libres ou pas |
| `agent.py` | point d'entrée, boucle de décision |
| `…` | … |

## État

**Ce qui marche.** *À compléter.*

**Ce qui ne marche pas.** *À compléter — soyez honnêtes, c'est noté en
votre faveur.*

## Vidéo

`demo.mp4` (ou le lien), également déclarée dans `rendu.json`.
