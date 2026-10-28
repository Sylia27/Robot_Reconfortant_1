import sys
from pathlib import Path

import reconfort_io as rio
from environnement import Environnement, ActionIllegale
from infos_initiales import extraire_infos_initiales
from memoire import Memoire
from regles import construire_index
from decision import Demande, choisir_action
from action import executer_pas, enregistrer_livraison

EQUIPE = ["SAD Sylia", "SAHNOUNE Rayanne"] 
MAX_TOURS_PAR_DEMANDE = 5000              


def traiter_demande(env, memoire, trace, demande, index_formes, emotions, intensites):
    """Joue une demande jusqu'à sa livraison ou son échec."""
    env.nouvelle_demande(demande.id_resident)
    for _ in range(MAX_TOURS_PAR_DEMANDE):
        perception = env.percevoir()
        contenu = env.contenu_casier()
        memoire.integrer(perception, contenu)

        action, argument = choisir_action(memoire, demande, index_formes)

        if action == "ECHEC":
            enregistrer_livraison(trace, demande, emotions, intensites, False, argument)
            return
        executer_pas(env, memoire, trace, demande, action, argument, perception, contenu)

        if action == "DONNER":
            enregistrer_livraison(trace, demande, emotions, intensites, True)
            return
    raise RuntimeError("demande " + str(demande.numero) + " : trop de tours, boucle probable")


def main(argv):
    if len(argv) != 5:
        print("usage : python agent.py <carte> <scenario> <dossier_donnees> <trace>",
              file=sys.stderr)
        return 2
    chemin_carte, chemin_scenario = Path(argv[1]), Path(argv[2])
    dossier, chemin_trace = Path(argv[3]), Path(argv[4])

    try:
        carte=rio.charger_carte(chemin_carte)
        scenario= rio.charger_scenario(chemin_scenario)
        dictionnaire= rio.charger_dictionnaire(dossier / "dictionnaire.json")
        armoire =rio.charger_armoire(dossier / (scenario["armoire"] + ".json"))
    except rio.ErreurFichier as err:
        print("erreur de chargement : " + str(err), file=sys.stderr)
        return 1

    env =Environnement(carte, armoire)
    memoire =Memoire(extraire_infos_initiales(carte, armoire))
    index_formes =construire_index(dictionnaire)
    emotions, intensites = dictionnaire["emotions"], dictionnaire["intensites"]
    trace = rio.Trace(carte["nom"], scenario["nom"], EQUIPE)

    try:
        for d in scenario["demandes"]:
            demande = Demande(d["numero"], d["resident"], rio.normaliser(d["message"]))
            traiter_demande(env, memoire, trace, demande, index_formes, emotions, intensites)
    except (ActionIllegale, RuntimeError) as err:
        print("erreur interne de l'agent : " + str(err), file=sys.stderr)
        return 3

    trace.ecrire(chemin_trace)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))