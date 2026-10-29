import reconfort_io as rio
def extraire_infos_initiales(carte, armoire):
    """pour garder uniquement ce que l'agent a le droit de savoir au départ"""
    residents = {}
    for r in carte["residents"]:
        residents[r["id"]]=tuple(r["position"])
    return {
        "hauteur":carte["dimensions"]["hauteur"],
        "largeur":carte["dimensions"]["largeur"],
        "depart": tuple(carte["depart_robot"]),
        "armoire":tuple(carte["armoire"]["position"]),
        "dictionnaire": tuple(carte["dictionnaire"]["position"]),
        "residents":residents,
        "casier_depart":tuple(armoire["casier_depart"]),
    }
def charger_infos_initiales(chemin_carte, chemin_armoire):     
    """Charge la carte et l'armoire, puis ne renvoie que ce que le robot à le droit de savoir S"""
    carte =rio.charger_carte(chemin_carte)
    armoire= rio.charger_armoire(chemin_armoire)
    return extraire_infos_initiales(carte, armoire)