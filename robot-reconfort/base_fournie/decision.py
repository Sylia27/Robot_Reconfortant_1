from memoire import DEPLACEMENTS
from planification import plus_court_chemin
from armoire import prochaine_direction
from regles import lire_emotion, liste_candidats
DICTIONNAIRE = "DICTIONNAIRE"
ARMOIRE = "ARMOIRE"
RESIDENT = "RESIDENT"
TERMINEE = "TERMINEE"
def direction(depart,suivante):
    """ renvoie la direction pour passer de la case depart à une case "voisine" suivante"""
    ecart=(suivante[0]-depart[0],suivante[1]-depart[1])
    for direction in DEPLACEMENTS:
        if DEPLACEMENTS[direction]==ecart:
            return direction
    raise ValueError("Cases non voisines  :" + str(depart) + " " + str(suivante))
def deplacer_vers(memoire,cible):
    """Un pas vers une case adjacente à `cible`.
    Renvoie (statut, direction) :
      ("avancer", "E") chemin existe (direction du prochain pas)
      ("arrive", None) le robot est déjà sur une case adjacente à la cible
      ("inaccessible", None)  aucun chemin n'existe sur la carte mentale"""
    arrives=memoire.carte.arrivees_autour(cible)
    chemin=plus_court_chemin(memoire.position,arrives,memoire.carte.est_traversable)
    if chemin is None:
        return("inaccessible",None)
    if len(chemin)== 1:
        return("arrive",None)
    return("avancer",direction(chemin[0],chemin[1]))



class Demande:
    """État d'une demande en cours. initialisée pour chaque demande."""

    def __init__(self, numero, id_resident, mots):
        self.numero=numero
        self.id_resident =id_resident
        self.mots =mots                
        self.phase= DICTIONNAIRE
        self.consulte= False            
        self.emotion=None             
        self.intensite=None            
        self.candidats =None            
        self.casier_choisi= None        
        self.repli= "aucun"
        self.objet= None
    

def _phase_dictionnaire(memoire, demande, index_formes):
        if not demande.consulte:
            statut, d= deplacer_vers(memoire, memoire.pos_dictionnaire)
            if statut=="avancer":
                return ("AVANCER", d)
            if statut== "inaccessible":
                return ("ECHEC", "emotion indeterminee")
            demande.consulte = True
            return ("CONSULTER", None)

        # CONSULTER a été joué au tour prcdnt dnc on lit l'émotion
        resultat = lire_emotion(demande.mots, index_formes)
        if resultat is None:
            return ("ECHEC", "emotion indeterminee")
        demande.emotion, demande.intensite = resultat
        demande.candidats= liste_candidats(demande.emotion, demande.intensite)
        demande.phase=ARMOIRE
        return _phase_armoire(memoire, demande)

def _phase_armoire(memoire, demande):
        statut, d = deplacer_vers(memoire, memoire.pos_armoire)
        if statut =="avancer":
            return ("AVANCER", d)
        if statut== "inaccessible":
            return ("ECHEC", "armoire vide")

        # le robot est adjacent à l'armoire dnc fouille
        if memoire.porte is not None:
            return ("ECHEC", "resident inaccessible")   

        cible = memoire.armoire.premier_candidat_utile(demande.candidats)
        if cible is None:
            return ("ECHEC", "armoire vide")

        casier = cible["casier"]
        if memoire.armoire.selecteur != casier:
            return ("CHERCHER", prochaine_direction(memoire.armoire.selecteur, casier))

        
        position_resident = memoire.residents[demande.id_resident]
        if deplacer_vers(memoire, position_resident)[0] == "inaccessible":
            return ("ECHEC", "resident inaccessible")   

        objet= memoire.armoire.vus[casier]
        demande.casier_choisi =casier
        demande.repli =cible["repli"]
        demande.objet= objet
        demande.phase= RESIDENT
        return ("PRENDRE", objet)
def _phase_resident(memoire, demande):
        position_resident = memoire.residents[demande.id_resident]
        statut, d = deplacer_vers(memoire, position_resident)
        if statut == "avancer":
            return ("AVANCER", d)
        if statut == "inaccessible":
            return ("ECHEC", "resident inaccessible")
        demande.phase = TERMINEE
        return ("DONNER", demande.objet)
def choisir_action(memoire, demande, index_formes):
        """Choisit UNE action pour ce tour. Renvoie (action, argument), ou
        ("ECHEC", motif) si la demande est impossible """
        if demande.phase==DICTIONNAIRE:
            return _phase_dictionnaire(memoire, demande, index_formes)
        if demande.phase== ARMOIRE:
            return _phase_armoire(memoire, demande)
        if demande.phase== RESIDENT:
            return _phase_resident(memoire, demande)
        raise ValueError("phase inattendue : " + str(demande.phase))