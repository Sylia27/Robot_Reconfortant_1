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