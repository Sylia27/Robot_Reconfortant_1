from armoire import deplacer_selecteur
DEPLACEMENTS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "O": (0, -1)}
class CarteMentale:
    def __init__(self, hauteur, largeur, obstacles):
        self.hauteur= hauteur
        self.largeur =largeur
        self.murs=set()                
        self.libres=set()              
        self.obstacles= set(obstacles)

    def sauvegarde(self, position, perception):
        """enregistre les murs ou cases libres perçues autour de position"""
        ligne, colonne = position
        for direction in perception:
            dl, dc = DEPLACEMENTS[direction]
            case = (ligne + dl, colonne + dc)
            if perception[direction]=="mur":
                self.murs.add(case)
            elif perception[direction]== "libre":
                self.libres.add(case)

    def est_traversable(self, case):
        """return vrai si la case est inconnue,libre, n'est pas un bord ou mur et n'est pas un obstaclee(resident,dict,armoire)"""
        ligne, colonne =case
        if not (0 <= ligne < self.hauteur and 0 <= colonne < self.largeur):
            return False
        if ligne in (0, self.hauteur - 1) or colonne in (0, self.largeur - 1):
            return False                 
        if case in self.murs or case in self.obstacles:
            return False
        return True

    def arrivees_autour(self, cible):
        """Préparer les cases adjacentes à la cible pour les envoyer au BFS"""
        ligne, colonne = cible
        arrivees = set()
        for dl, dc in DEPLACEMENTS.values():
            case = (ligne+ dl, colonne +dc)
            if self.est_traversable(case):
                arrivees.add(case)
        return arrivees
class ArmoireMentale:
    def __init__(self, casier_depart):
        self.selecteur= tuple(casier_depart)   
        self.vus = {}   

    def noter(self, casier, objet):
        """enregistrer ce que le robot a vu dans le casier"""
        self.vus[casier]= objet

    def deplacer(self, direction):
        """mettre à jour la position du selecteur"""
        self.selecteur= deplacer_selecteur(self.selecteur, direction)

    def est_vu_vide(self, casier):
        """return vrai si le le casier a été vu et est vide"""
        return casier in self.vus and self.vus[casier] is None

    def premier_candidat_utile(self, candidats):
        """1 er casier qui qui n'est pas vu vide"""
        for candidat in candidats:
            if not self.est_vu_vide(candidat["casier"]):
                return candidat
        return None
class Memoire:
    def __init__(self, infos_init):
        self.position= infos_init["depart"]
        self.porte= None
        self.pos_armoire= infos_init["armoire"]
        self.pos_dictionnaire =infos_init["dictionnaire"]
        self.residents =infos_init["residents"]
        self.residents_atteints = set()  
        obstacles= {self.pos_armoire, self.pos_dictionnaire}
        for id_resident in self.residents:
            obstacles.add(self.residents[id_resident])

        self.carte= CarteMentale(infos_init["hauteur"],
                                  infos_init["largeur"], obstacles)
        self.armoire= ArmoireMentale(infos_init["casier_depart"])

    def integrer(self, perception, contenu):
        """Mettre à jour la mémoire avec ce que le robot perçoit à sa position"""
        self.carte.sauvegarde(self.position, perception)
        for id_resident in self.residents:     
            ligne_r, colonne_r = self.residents[id_resident]
            if abs(ligne_r - self.position[0]) + abs(colonne_r - self.position[1]) == 1:
                self.residents_atteints.add(id_resident)
        if "armoire" in perception.values():
            self.armoire.noter(self.armoire.selecteur, contenu)

    def avancer(self, direction):
        """mettre à jour la pos du robot """
        dl, dc = DEPLACEMENTS[direction]
        ligne, colonne = self.position
        self.position = (ligne + dl, colonne + dc)
