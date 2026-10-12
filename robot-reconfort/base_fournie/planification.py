from collections import deque

def reconstruire_chemin(predecesseurs, case_cible):
    """Remonte le dictionnaire des prédécesseurs pour créer la liste du trajet."""
    chemin = [case_cible]
    while predecesseurs[chemin[-1]] is not None:
        case_precedente = predecesseurs[chemin[-1]]
        chemin.append(case_precedente)
    
    chemin.reverse()
    return chemin

def obtenir_voisins(case):
    """Renvoie les 4 cases orthogonalement adjacentes (N, S, E, O)."""
    ligne, colonne = case
    return [
        (ligne - 1, colonne), # Nord
        (ligne + 1, colonne), # Sud
        (ligne, colonne + 1), # Est
        (ligne, colonne - 1)  # Ouest
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




#tester la grille 3B 
murs_interieurs = {(1, 3), (2, 2), (3, 4)}

def est_traversable(case):
    ligne, colonne = case
    
    if ligne <= 0 or ligne >= 4 or colonne <= 0 or colonne >= 5:
        return False
        
    if case in murs_interieurs:
        return False
        
    return True


if __name__ == "__main__":
    depart = (1, 1)
    cible = (1, 4)
    
    print(f"--- Test de la mini-grille ---")
    print(f"Robot en {depart}, Cible en {cible}")
    
    chemin = plus_court_chemin(depart, {cible}, est_traversable)
    
    if chemin:
        pas_total = len(chemin) - 1
        print(f"chemin trouvé en {pas_total} pas !")
        print(f"Itinéraire : {chemin}")
        
        attendu = [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3), (2, 3), (2, 4), (1, 4)]
        assert chemin == attendu, "Le chemin ne correspond pas à la solution de l'énoncé."
    else:
        print("Aucun chemin trouvé.")