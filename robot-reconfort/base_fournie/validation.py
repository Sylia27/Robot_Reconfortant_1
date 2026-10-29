
from reconfort_io import ErreurFichier, charger_carte, charger_armoire, charger_dictionnaire   # [CHANGÉ] 3 imports ajoutés (avant : seulement ErreurFichier)
from armoire import NB_LIGNES, NB_COLONNES

SYMBOLES_VALIDES = {"#", ".", "R", "A", "D", "P"}     # la légende de la section 3.1SYMBOLES_VALIDES = {"#", ".", "R", "A", "D", "P"}     # la légende de la section 3.1
NOMS_TYPES = {int: "un entier", str: "un texte", list: "une liste", dict: "un objet"}




def _entier(valeur):
    """Un booléen n'est pas un entier valide """
    return isinstance(valeur, int) and not isinstance(valeur, bool)


def _exiger(contenant, cle, type_attendu, ou):
    """Renvoie contenant[cle] après avoir vérifié sa présence et son type"""
    if not isinstance(contenant, dict):
        raise ErreurFichier(ou + " : un objet JSON est attendu")
    if cle not in contenant:
        raise ErreurFichier(ou + " : champ obligatoire '" + cle + "' absent")
    valeur =contenant[cle]
    if type_attendu is int:
        correct= _entier(valeur)
    else:
        correct=isinstance(valeur, type_attendu)
    if not correct:
        raise ErreurFichier(ou + " : le champ '" + cle + "' doit être "+ NOMS_TYPES[type_attendu])
    return valeur


def _lire_position(contenant, cle, ou):
    """Lit une position [ligne, colonne] et la renvoie sous forme de tuple"""
    valeur = _exiger(contenant, cle, list, ou)
    if len(valeur) != 2 or not _entier(valeur[0]) or not _entier(valeur[1]):
        raise ErreurFichier(ou + " : '" + cle + "' doit être [ligne, colonne]")
    return (valeur[0], valeur[1])



def _verifier_grille(grille, hauteur, largeur):
    if hauteur <= 0 or largeur <= 0:
        raise ErreurFichier("carte : les dimensions doivent être positives")
    if len(grille) != hauteur:
        raise ErreurFichier("carte : la hauteur annoncée est " + str(hauteur)
                            + " mais la grille a " + str(len(grille)) + " lignes")
    for i in range(len(grille)):
        ligne = grille[i]
        if not isinstance(ligne, str):
            raise ErreurFichier("carte : la ligne " + str(i) + " de la grille doit être un texte")
        if len(ligne) != largeur:
            raise ErreurFichier("carte : grille non rectangulaire ou largeur incohérente : la ligne "
                                + str(i) + " a " + str(len(ligne)) + " caractères, attendu "
                                + str(largeur))
        for caractere in ligne:
            if caractere not in SYMBOLES_VALIDES:
                raise ErreurFichier("carte : symbole inconnu '" + caractere
                                    + "' dans la ligne " + str(i) + " de la grille")
    for i in range(hauteur):
        for j in range(largeur):
            sur_le_bord = i in (0, hauteur - 1) or j in (0, largeur - 1)
            if sur_le_bord and grille[i][j] != "#":
                raise ErreurFichier("carte : le bord de la grille doit être fait de murs (case ("
                                    + str(i) + ", " + str(j) + "))")


def _verifier_case(position, symbole, grille, nom):
    ligne, colonne = position
    if not (0 <= ligne < len(grille) and 0 <= colonne < len(grille[0])):
        raise ErreurFichier("carte : " + nom + " en " + str(list(position))
                            + " est hors de la grille")
    if grille[ligne][colonne] != symbole:
        raise ErreurFichier("carte : " + nom + " en " + str(list(position))
                            + " : la grille contient '" + grille[ligne][colonne]
                            + "' à cet endroit au lieu de '" + symbole + "'")


def valider_carte(carte):
    _exiger(carte, "nom", str, "carte")
    dimensions = _exiger(carte, "dimensions", dict, "carte")
    hauteur = _exiger(dimensions, "hauteur", int, "carte.dimensions")
    largeur = _exiger(dimensions, "largeur", int, "carte.dimensions")
    grille = _exiger(carte, "grille", list, "carte")
    _verifier_grille(grille, hauteur, largeur)

    depart = _lire_position(carte, "depart_robot", "carte")
    _verifier_case(depart, "R", grille, "le départ du robot")

    armoire = _exiger(carte, "armoire", dict, "carte")
    _verifier_case(_lire_position(armoire, "position", "carte.armoire"),
                   "A", grille, "l'armoire")

    dictionnaire = _exiger(carte, "dictionnaire", dict, "carte")
    _verifier_case(_lire_position(dictionnaire, "position", "carte.dictionnaire"),
                   "D", grille, "le dictionnaire")

    residents = _exiger(carte, "residents", list, "carte")
    vus = set()
    for r in residents:
        id_resident = _exiger(r, "id", str, "carte.residents")
        _exiger(r, "nom", str, "carte.residents")
        if id_resident in vus:
            raise ErreurFichier("carte : deux résidents ont le même identifiant '"
                                + id_resident + "'")
        vus.add(id_resident)
        _verifier_case(_lire_position(r, "position", "carte.residents"),
                       "P", grille, "le résident " + id_resident)




def _lire_liste_de_textes(contenant, cle, ou, longueur):
    liste = _exiger(contenant, cle, list, ou)
    if len(liste) != longueur:
        raise ErreurFichier(ou + " : '" + cle + "' doit contenir " + str(longueur)
                            + " éléments, il en contient " + str(len(liste)))
    for element in liste:
        if not isinstance(element, str):
            raise ErreurFichier(ou + " : '" + cle + "' ne doit contenir que des textes")
    return liste


def valider_armoire(armoire):
    _exiger(armoire, "nom", str, "armoire")
    emotions = _lire_liste_de_textes(armoire, "emotions", "armoire", NB_COLONNES)
    intensites = _lire_liste_de_textes(armoire, "intensites", "armoire", NB_LIGNES)
    casier_depart = _lire_position(armoire, "casier_depart", "armoire")
    casiers = _exiger(armoire, "casiers", list, "armoire")

    ligne, colonne = casier_depart
    if not (0 <= ligne < NB_LIGNES and 0 <= colonne < NB_COLONNES):
        raise ErreurFichier("armoire : casier_depart " + str(list(casier_depart))
                            + " est hors de l'armoire (" + str(NB_LIGNES) + " lignes, "
                            + str(NB_COLONNES) + " colonnes)")

    vus = set()
    for c in casiers:
        l = _exiger(c, "ligne", int, "armoire.casiers")
        col = _exiger(c, "colonne", int, "armoire.casiers")
        emotion = _exiger(c, "emotion", str, "armoire.casiers")
        intensite = _exiger(c, "intensite", str, "armoire.casiers")
        if "objet" not in c:
            raise ErreurFichier("armoire.casiers : champ obligatoire 'objet' absent")
        if c["objet"] is not None and not isinstance(c["objet"], str):
            raise ErreurFichier("armoire.casiers : 'objet' doit être un texte ou null")
        if not (0 <= l < NB_LIGNES and 0 <= col < NB_COLONNES):
            raise ErreurFichier("armoire : le casier [" + str(l) + ", " + str(col)
                                + "] est hors des dimensions de l'armoire")
        if (l, col) in vus:
            raise ErreurFichier("armoire : le casier [" + str(l) + ", " + str(col)
                                + "] apparaît deux fois")
        vus.add((l, col))
        if emotion not in emotions:
            raise ErreurFichier("armoire : émotion inconnue '" + emotion + "'")
        if intensite not in intensites:
            raise ErreurFichier("armoire : intensité inconnue '" + intensite + "'")
        if emotions[col] != emotion or intensites[l] != intensite:
            raise ErreurFichier("armoire : l'étiquette du casier [" + str(l) + ", "
                                + str(col) + "] (" + emotion + "/" + intensite
                                + ") ne correspond pas à sa position")



def valider_dictionnaire(dictionnaire):
    _exiger(dictionnaire, "nom", str, "dictionnaire")
    emotions = _lire_liste_de_textes(dictionnaire, "emotions", "dictionnaire", NB_COLONNES)
    intensites = _lire_liste_de_textes(dictionnaire, "intensites", "dictionnaire", NB_LIGNES)
    entrees = _exiger(dictionnaire, "entrees", list, "dictionnaire")

    deja_vues = {}
    for numero in range(len(entrees)):
        entree = entrees[numero]
        formes = _exiger(entree, "formes", list, "dictionnaire.entrees")
        emotion = _exiger(entree, "emotion", str, "dictionnaire.entrees")
        intensite = _exiger(entree, "intensite", str, "dictionnaire.entrees")
        if len(formes) == 0:
            raise ErreurFichier("dictionnaire : l'entrée " + str(numero) + " n'a aucune forme")
        if emotion not in emotions:
            raise ErreurFichier("dictionnaire : émotion inconnue '" + emotion + "'")
        if intensite not in intensites:
            raise ErreurFichier("dictionnaire : intensité inconnue '" + intensite + "'")
        for forme in formes:
            if not isinstance(forme, str) or forme == "":
                raise ErreurFichier("dictionnaire : les formes doivent être des textes non vides")
            if forme in deja_vues:
                raise ErreurFichier("dictionnaire : le mot '" + forme
                                    + "' apparaît dans deux entrées (" + str(deja_vues[forme])
                                    + " et " + str(numero) + ")")
            deja_vues[forme] = numero



def valider_scenario(scenario):
    
    _exiger(scenario, "nom", str, "scenario")
    _exiger(scenario, "carte", str, "scenario")
    nom_armoire = _exiger(scenario, "armoire", str, "scenario")
    if nom_armoire == "":
        raise ErreurFichier("scenario : le nom de l'armoire est vide")
    demandes = _exiger(scenario, "demandes", list, "scenario")
    numeros = set()
    for d in demandes:
        numero = _exiger(d, "numero", int, "scenario.demandes")
        _exiger(d, "resident", str, "scenario.demandes")
        _exiger(d, "message", str, "scenario.demandes")
        if numero in numeros:
            raise ErreurFichier("scenario : le numéro de demande " + str(numero)
                                + " apparaît deux fois")
        numeros.add(numero)




def valider_coherence(carte, scenario, dictionnaire, armoire):
    if scenario["carte"] != carte["nom"]:
        raise ErreurFichier("scenario : prévu pour la carte '" + scenario["carte"]
                            + "', mais la carte chargée est '" + carte["nom"] + "'")
    ids = set()
    for r in carte["residents"]:
        ids.add(r["id"])
    for d in scenario["demandes"]:
        if d["resident"] not in ids:
            raise ErreurFichier("scenario : la demande " + str(d["numero"])
                                + " vise le résident '" + d["resident"]
                                + "', absent de la carte")
    if dictionnaire["emotions"] != armoire["emotions"]:
        raise ErreurFichier("dictionnaire et armoire n'ont pas la même liste d'émotions")
    if dictionnaire["intensites"] != armoire["intensites"]:
        raise ErreurFichier("dictionnaire et armoire n'ont pas la même liste d'intensités")



def valider_fichiers(chemin_carte, chemin_armoire, chemin_dictionnaire, scenario):
    """Charge la carte, l'armoire et le dictionnaire, puis valide les quatre fichiers"""
    carte = charger_carte(chemin_carte)
    armoire = charger_armoire(chemin_armoire)
    dictionnaire = charger_dictionnaire(chemin_dictionnaire)
    valider_carte(carte)
    valider_dictionnaire(dictionnaire)
    valider_armoire(armoire)
    valider_coherence(carte, scenario, dictionnaire, armoire)