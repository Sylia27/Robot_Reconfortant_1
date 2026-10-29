# [NOUVEAU FICHIER]
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import reconfort_io as rio
from infos_initiales import charger_infos_initiales
from memoire import Memoire


ROUGE = "\033[1;31m"
JAUNE = "\033[1;33m"
CYAN = "\033[36m"
FIN = "\033[0m"
EFFACER = "\033[H\033[J"


def sans_couleurs(texte):
    """Retire les codes de couleur (utile pour les tests)."""
    return re.sub(r"\033\[[0-9;]*[A-Za-z]", "", texte)


def caractere_de_la_case(case, infos, position, memoire, nouveaux, trajet):
    """Ce que le robot sait d'une case, sous forme d'un caractère."""
    ligne, colonne = case
    if case == position:
        return ROUGE + "R" + FIN
    if case == infos["armoire"]:
        return "A"
    if case == infos["dictionnaire"]:
        return "D"
    for id_resident in infos["residents"]:
        if infos["residents"][id_resident] == case:
            return id_resident[-1]                  
    if case in nouveaux:
        return JAUNE + "#" + FIN                    
    if case in memoire.carte.murs:
        return "#"
    if ligne in (0, infos["hauteur"] - 1) or colonne in (0, infos["largeur"] - 1):
        return "#"                                  
    if case in trajet:
        return CYAN + "+" + FIN                     
    if case in memoire.carte.libres:
        return "."
    return "?"


def dessiner_plan(infos, position, memoire, nouveaux, trajet):
    lignes = []
    for ligne in range(infos["hauteur"]):
        texte = ""
        for colonne in range(infos["largeur"]):
            texte += caractere_de_la_case((ligne, colonne), infos, position, memoire,
                                          nouveaux, trajet) + " "
        lignes.append(texte)
    return lignes


def dessiner_armoire(memoire):
    """L'armoire mentale : 3 lignes (intensités) x 8 colonnes (émotions)."""
    lignes = ["  " + " ".join(" " + str(c) + " " for c in range(8))]
    for ligne in range(3):
        texte = str(ligne) + " "
        for colonne in range(8):
            casier = (ligne, colonne)
            if casier not in memoire.armoire.vus:
                symbole = "?"
            elif memoire.armoire.vus[casier] is None:
                symbole = "_"
            else:
                symbole = "o"
            if casier == memoire.armoire.selecteur:
                texte += "[" + symbole + "] "
            else:
                texte += " " + symbole + "  "
        lignes.append(texte)
    return lignes


def construire_images(infos, scenario, trace):
    """Rejoue la trace et renvoie une liste d'images (t, demande, texte).
    Chaque image montre ce que le robot SAIT à ce pas : sa carte mentale, pas la réalité."""
    messages = {}
    for d in scenario["demandes"]:
        messages[d["numero"]] = d["message"]
    livraisons = {}
    for liv in trace["livraisons"]:
        livraisons[liv["demande"]] = liv
    nb_demandes = len(scenario["demandes"])

    memoire = Memoire(infos)
    pas_trace = trace["pas"]
    images = []
    trajet = set()
    demande_courante = None
    porte = None

    for k in range(len(pas_trace)):
        pas = pas_trace[k]
        if pas["demande"] != demande_courante:
            demande_courante = pas["demande"]
            trajet = set()
        memoire.position = tuple(pas["position"])
        memoire.armoire.selecteur = tuple(pas["casier"])
        murs_avant = set(memoire.carte.murs)
        memoire.integrer(pas["perception"], pas["contenu_casier"])
        nouveaux = set()
        for mur in memoire.carte.murs - murs_avant:
            if 0 < mur[0] < infos["hauteur"] - 1 and 0 < mur[1] < infos["largeur"] - 1:
                nouveaux.add(mur)            
        trajet.add(memoire.position)

        plan = dessiner_plan(infos, memoire.position, memoire, nouveaux, trajet)
        armoire = dessiner_armoire(memoire)

        argument = pas["argument"] if pas["argument"] is not None else ""
        resident = [d["resident"] for d in scenario["demandes"]
                    if d["numero"] == pas["demande"]][0]
        entete = [
            "demande " + str(pas["demande"]) + "/" + str(nb_demandes)
            + "  pour " + resident + "  (t=" + str(pas["t"]) + ")",
            "message : " + messages[pas["demande"]],
            "",
        ]
        etat = [
            "action     : " + pas["action"] + " " + argument,
            "objet porté: " + (porte if porte is not None else "-"),
            "sélecteur  : " + str(memoire.armoire.selecteur),
        ]
        if pas["contenu_casier"] is not None:
            etat.append("casier vu  : " + pas["contenu_casier"])
        for mur in sorted(nouveaux):
            etat.append(JAUNE + "mur découvert en " + str(mur) + FIN)

        est_dernier = (k + 1 == len(pas_trace)) or (pas_trace[k + 1]["demande"] != pas["demande"])
        if est_dernier:
            liv = livraisons[pas["demande"]]
            if liv["succes"]:
                etat.append("LIVRAISON : " + str(liv["objet"]) + " (" + str(liv["emotion"])
                            + "/" + str(liv["intensite"]) + ", repli " + liv["repli"] + ")")
            else:
                etat.append("ÉCHEC : " + str(liv["motif_echec"]))

        texte = "\n".join(entete + plan + [""] + armoire + [""] + etat)
        images.append((pas["t"], pas["demande"], texte))

        if pas["action"] == "PRENDRE":
            porte = pas["argument"]
        elif pas["action"] == "DONNER":
            porte = None
    return images


def selectionner(images, demande=None, depuis=None, jusqua=None):
    """Garde les images d'une demande et/ou d'un intervalle de pas."""
    choix = []
    for t, numero, texte in images:
        if demande is not None and numero != demande:
            continue
        if depuis is not None and t < depuis:
            continue
        if jusqua is not None and t > jusqua:
            continue
        choix.append((t, numero, texte))
    return choix


def main(argv):
    analyse = argparse.ArgumentParser(
        description="Rejoue une trace et affiche, pas à pas, la carte mentale du robot.")
    analyse.add_argument("carte")
    analyse.add_argument("scenario")
    analyse.add_argument("dossier_donnees")
    analyse.add_argument("trace")
    analyse.add_argument("--delai", type=float, default=0.3, help="secondes entre deux images")
    analyse.add_argument("--demande", type=int, help="ne rejouer que cette demande")
    analyse.add_argument("--depuis", type=int, help="premier pas (t) à afficher")
    analyse.add_argument("--jusqua", type=int, help="dernier pas (t) à afficher")
    analyse.add_argument("--pas-a-pas", action="store_true", help="attendre la touche Entrée")
    analyse.add_argument("--sans-effacer", action="store_true",
                         help="ne pas effacer l'écran entre deux images")
    options = analyse.parse_args(argv[1:])

    try:
        scenario = rio.charger_scenario(options.scenario)
        chemin_armoire = Path(options.dossier_donnees) / (scenario["armoire"] + ".json")
        infos = charger_infos_initiales(options.carte, chemin_armoire)
        trace = json.loads(Path(options.trace).read_text(encoding="utf-8"))
    except (rio.ErreurFichier, OSError, ValueError) as err:
        print("erreur de fichier : " + str(err), file=sys.stderr)
        return 1

    images = selectionner(construire_images(infos, scenario, trace),
                          options.demande, options.depuis, options.jusqua)
    if not images:
        print("aucune image à afficher avec ces options", file=sys.stderr)
        return 1

    os.system("")                       
    for t, numero, texte in images:
        if not options.sans_effacer:
            print(EFFACER, end="")
        print(texte)
        sys.stdout.flush()
        if options.pas_a_pas:
            input()
        else:
            time.sleep(options.delai)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))