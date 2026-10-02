NB_EMOTIONS = 8
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



    