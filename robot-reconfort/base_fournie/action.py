def mettre_a_jour_memoire(memoire, action, argument):
    """Recopie dans la mémoire l'effet d'une action acceptée par le simulateur"""
    if action== "AVANCER":
        memoire.avancer(argument)
    elif action=="CHERCHER":
        memoire.armoire.deplacer(argument)
    elif action=="PRENDRE":
        memoire.porte = argument
    elif action =="DONNER":
        memoire.porte = None
def executer_pas(env,memoire,trace,demande, action,argument,perception,contenu):
    """Journalise le pas  l'envoie au simulateur, puis met la
    mémoire à jour. Si le simulateur refuse l'action, ActionIllegale remonte."""
    trace.ajouter_pas(
        demande= demande.numero,
        position =memoire.position,
        casier =memoire.armoire.selecteur,
        action =action,
        argument =argument,
        perception =perception,
        contenu_casier =contenu,
    )
    env.appliquer(action, argument)
    mettre_a_jour_memoire(memoire, action, argument)
def enregistrer_livraison(trace, demande, emotions, intensites, succes, motif=None):
    """Journalise l'issue d'une demande"""
    emotion = None
    intensite= None
    if demande.emotion is not None:
        emotion =emotions[demande.emotion]
        intensite= intensites[demande.intensite]
    trace.ajouter_livraison(
        demande= demande.numero,
        resident=demande.id_resident,
        emotion=emotion,
        intensite=intensite,
        casier_choisi=demande.casier_choisi,
        repli=demande.repli,
        objet=demande.objet,
        succes=succes,
        motif_echec=motif,
    )