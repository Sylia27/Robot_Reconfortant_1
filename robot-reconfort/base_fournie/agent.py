
import sys
from pathlib import Path

import reconfort_io as rio
from environnement import charger_environnement, ActionIllegale   
from infos_initiales import charger_infos_initiales               
from dictionnaire import Dictionnaire                             
from validation import valider_scenario, valider_fichiers          
from memoire import Memoire
from decision import Demande, choisir_action
from action import executer_pas, enregistrer_livraison

EQUIPE = ["SAD Sylia", "SAHNOUNE Rayanne"]     
MAX_TOURS_PAR_DEMANDE = 5000             


def traiter_demande(env, memoire, trace, demande, dictionnaire):      
    """Joue une demande jusqu'à sa livraison ou son échec"""
    env.nouvelle_demande(demande.id_resident)
    for _ in range(MAX_TOURS_PAR_DEMANDE):
        perception= env.percevoir()
        contenu= env.contenu_casier()
        memoire.integrer(perception, contenu)

        action, argument= choisir_action(memoire, demande, dictionnaire.index_formes)   

        if action =="ECHEC":
            enregistrer_livraison(trace, demande, dictionnaire.emotions,                 
                                  dictionnaire.intensites, False, argument)
            return
        executer_pas(env, memoire, trace, demande, action, argument, perception, contenu)

        if action =="CONSULTER":                                                        
            dictionnaire.consulter()       
        if action=="DONNER":
            enregistrer_livraison(trace, demande, dictionnaire.emotions,                 
                                  dictionnaire.intensites, True)
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
        scenario = rio.charger_scenario(chemin_scenario)
        valider_scenario(scenario)          
        chemin_armoire = dossier / (scenario["armoire"] + ".json")     
        chemin_dictionnaire = dossier / "dictionnaire.json"             

        valider_fichiers(chemin_carte, chemin_armoire, chemin_dictionnaire, scenario)   
        env = charger_environnement(chemin_carte, chemin_armoire)                      
        infos = charger_infos_initiales(chemin_carte, chemin_armoire)                   

    except rio.ErreurFichier as err:
        print("erreur de fichier : " + str(err), file=sys.stderr)
        return 1

    memoire= Memoire(infos)                                       
    dictionnaire =Dictionnaire(chemin_dictionnaire)                
    
    trace= rio.Trace(scenario["carte"], scenario["nom"], EQUIPE)    

    try:
        for d in scenario["demandes"]:
            demande = Demande(d["numero"], d["resident"], rio.normaliser(d["message"]))
            traiter_demande(env, memoire, trace, demande, dictionnaire)  
    except (ActionIllegale, RuntimeError) as err:
        print("erreur interne de l'agent : " + str(err), file=sys.stderr)
        return 3
    except Exception as err:              
        print("erreur inattendue : " + type(err).__name__ + " : " + str(err), file=sys.stderr)
        return 4

    trace.ecrire(chemin_trace)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))