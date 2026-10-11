NB_LIGNES = 3        
NB_COLONNES = 8      
VERTICAL_D_ABORD = True  


def deplacer_selecteur(casier, direction):
    """Applique un mouvement N/S/E/O à un casier(ligne, colonne) et renvoie
    le nouveau casier;ValueError si le mouvement illégal"""
    ligne, colonne= casier
    if direction== "N":
        if ligne==0:
            raise ValueError("N impossible depuis la ligne 0")
        return (ligne-1, colonne)
    elif direction== "S":
        if ligne ==NB_LIGNES - 1:
            raise ValueError("S impossible depuis la dernière ligne")
        return (ligne +1, colonne)
    elif direction=="E":
        return (ligne, (colonne+ 1) % NB_COLONNES)
    elif direction=="O":
        return (ligne, (colonne -1) % NB_COLONNES)
    else:
        raise ValueError("direction inconnue : " + str(direction))


def direction_verticale(ligne, ligne_cible):
    if ligne_cible > ligne:
        return "S"
    if ligne_cible < ligne:
        return "N"
    return None


def direction_horizontale(colonne, colonne_cible):
    vers_est= (colonne_cible - colonne) % NB_COLONNES
    if vers_est== 0:
        return None
    vers_ouest= NB_COLONNES - vers_est
    if vers_est<= vers_ouest:    
        return "E"
    return "O"


def prochaine_direction(casier, cible):
    """Renvoie prochaine direction à jouer pour aller de casier à cible,
    ou None si le sélecteur est déjà sur la cible."""
    ligne, colonne = casier
    ligne_cible, colonne_cible = cible
    vertical = direction_verticale(ligne, ligne_cible)
    horizontal = direction_horizontale(colonne, colonne_cible)
    if VERTICAL_D_ABORD:
        if vertical is not None:
            return vertical
        return horizontal
    else:
        if horizontal is not None:
            return horizontal
    return vertical