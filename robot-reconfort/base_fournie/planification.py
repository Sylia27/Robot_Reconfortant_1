from collections import deque

def reconstruire_chemin(predecesseurs, case_cible):
    chemin = [case_cible]
    while predecesseurs[chemin[-1]] is not None:
        case_precedente = predecesseurs[chemin[-1]]
        chemin.append(case_precedente)
    
    chemin.reverse()
    return chemin

def obtenir_voisins(case):
    ligne, colonne = case
    return [
        (ligne - 1, colonne), 
        (ligne + 1, colonne), 
        (ligne, colonne + 1), 
        (ligne, colonne - 1)  
    ]

def plus_court_chemin(depart, arrivees, est_traversable):
    if depart in arrivees:
        return [depart]

    predecesseurs = {depart: None}
    file = deque([depart])

    while file:
        courant = file.popleft() 
        for voisin in obtenir_voisins(courant):
            if voisin in predecesseurs:
                continue
            
            if not est_traversable(voisin):
                continue

            predecesseurs[voisin] = courant

            if voisin in arrivees:
                return reconstruire_chemin(predecesseurs, voisin)

            file.append(voisin)

    return None