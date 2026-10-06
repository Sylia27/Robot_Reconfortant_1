

NB_EMOTIONS = 8
DISTANCE_MAX = 2 
NB_INTENSITES = 3 
def emotion_to_indice (emotion,emotions):
    return emotions.index(emotion)


def distance_roue(e1,e2):
    ecart = abs(e1-e2)
    distance= NB_EMOTIONS - ecart
    return min(ecart,distance)
 
def sens_horaire(e1,e2):
    """renvoie le sens dans lequel il faut aller 1 pour horaire et -1 pour anti horaire"""  
    decalage_up =(e2-e1)%NB_EMOTIONS
    decalage_down=NB_EMOTIONS-decalage_up
    if (decalage_up <= decalage_down):
        return 1
    else:
        return -1
def emotions_candidates(e):
    """reçoit indice emotion et return la liste des indices des emotions candidates """
    candidates=[]
    for e_prime in range(NB_EMOTIONS):
        if distance_roue(e, e_prime) <= DISTANCE_MAX:
            candidates.append(e_prime)
    return candidates
 


def liste_candidats(e, i):
    """Renvoie casiers candidats pour une demande (e, i) triés selon
    les 4 critéres donnés"""
    candidats = []
    for e_prime in emotions_candidates(e):
        distance = distance_roue(e, e_prime)
        sens = sens_horaire(e, e_prime)
        for i_prime in range(NB_INTENSITES):
            ecart = abs(i - i_prime)
            #-sens pour faire passer l'horaire avant anti horaire vu qu'on renvoie 1 pr horaire qui est > -1 du anti horaire 
            cle = (distance, ecart, i_prime, -sens)
            candidats.append((cle, e_prime))

    candidats.sort()

    resultat = []
    for cle, e_prime in candidats:
        if cle[0]== 0 and cle[2]==i:
            repli ="aucun"
        elif cle[0] == 0:
            repli= "intensite"
        else:
            repli="voisine_" + str(cle[0])
        resultat.append({"casier": (cle[2], e_prime), "repli": repli})
    return resultat
#print(liste_candidats(3, 2)[:5] ) 
def construire_index(dictionnaire):
    """Retranscrit les formes et les émotions/intensités correspondantes 
    dans un dictionnaire en associant à chaque forme (indice emtion,indice intensité) """
    
    emotions=dictionnaire["emotions"]
    intensites= dictionnaire["intensites"]

    index_formes= {}
    for entree in dictionnaire["entrees"]:
        e = emotion_to_indice(entree["emotion"], emotions)
        i = intensites.index(entree["intensite"])
        for forme in entree["formes"]:
            # (e indice de l'emotion sur la roue, i indice intensité {0,1,2})
            index_formes[forme] = (e, i)
    return index_formes
def lire_emotion(mots, index_formes):
    """ Prends en paramétre la phrase normalisée et le dictionnaire formes->(e,i);
        Renvoie (indice emotion, rang intensité) du premier mot
        reconnu dans la phrase , ou None si aucun ne l'est."""
    for mot in mots:
        if mot in index_formes:
            return index_formes[mot]
    return None