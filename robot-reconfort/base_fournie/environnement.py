from armoire import deplacer_selecteur

SYMBOLES = {"#": "mur", ".": "libre", "R": "libre",
            "A": "armoire", "D": "dictionnaire", "P": "resident"}
DEPLACEMENTS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "O": (0, -1)}


class ActionIllegale(Exception):
    """L'agent a demandé une action invalide"""
class Environnement:
    def __init__(self, carte, armoire):
        self.grille= carte["grille"]
        self.position= tuple(carte["depart_robot"])
        self.selecteur= tuple(armoire["casier_depart"])
        self.casiers = {}
        for c in armoire["casiers"]:
            cle = (c["ligne"], c["colonne"])
            self.casiers[cle] = c["objet"]
        self.porte=None
        self.residents = {}
        for r in carte["residents"]:
            self.residents[r["id"]] = tuple(r["position"])
        self.resident_cible = None
    def case(self, ligne, colonne):
                """renvoie la valeur associé au contenu(#,. etc..) de la case de la grille (mur,libre etc...) """
                if not (0 <= ligne < len(self.grille)
                    and 0 <= colonne < len(self.grille[0])):
                    return "mur"
                return SYMBOLES[self.grille[ligne][colonne]]
    def percevoir(self):
                """Renvoie la perception(le type des 4 cases voisines)"""
                ligne, colonne = self.position
                perception = {}
                for direction in DEPLACEMENTS:
                    dl, dc = DEPLACEMENTS[direction]
                    perception[direction] = self.case(ligne + dl, colonne + dc)
                return perception
    def _adjacent_a(self, symbole):
                """renvoi vrai si l'une des 4 voisins de la pos du robot est réellement un symbole"""
                return symbole in self.percevoir().values()
    def nouvelle_demande(self, id_resident):
                self.resident_cible = id_resident
    def contenu_casier(self):
                """Objet du casier sous le sélecteur"""
                if not self._adjacent_a("armoire"):
                    return None
                return self.casiers.get(self.selecteur)
    def appliquer(self, action, argument=None):
                """Applique une action, ou lève ActionIllegale."""
                if action == "ATTENDRE":
                    return
                elif action == "AVANCER":
                    self._avancer(argument)
                elif action == "CONSULTER":
                    if not self._adjacent_a("dictionnaire"):
                        raise ActionIllegale("CONSULTER : pas adjacent au dictionnaire")
                elif action == "CHERCHER":
                    self._chercher(argument)
                elif action == "PRENDRE":
                    self._prendre(argument)
                elif action == "DONNER":
                    self._donner(argument)
                else:
                    raise ActionIllegale("action inconnue : " + str(action))
    def _avancer(self, direction):
                if direction not in DEPLACEMENTS:
                    raise ActionIllegale("AVANCER : direction invalide " + str(direction))
                ligne, colonne = self.position
                dl, dc = DEPLACEMENTS[direction]
                if self.case(ligne + dl, colonne + dc) != "libre":
                    raise ActionIllegale("AVANCER " + direction + " : case non libre")
                self.position = (ligne + dl, colonne + dc)
    def _chercher(self, direction):
                if not self._adjacent_a("armoire"):
                    raise ActionIllegale("CHERCHER : pas adjacent à l'armoire")
                try:
                    self.selecteur = deplacer_selecteur(self.selecteur, direction)
                except ValueError as err:
                    raise ActionIllegale("CHERCHER : " + str(err))
    def _prendre(self, objet):
                if not self._adjacent_a("armoire"):
                    raise ActionIllegale("PRENDRE : pas adjacent à l'armoire")
                if self.porte is not None:
                    raise ActionIllegale("PRENDRE : le robot porte déjà " + self.porte)
                contenu = self.casiers.get(self.selecteur)
                if contenu is None:
                    raise ActionIllegale("PRENDRE : casier vide")
                if objet != contenu:
                    raise ActionIllegale("PRENDRE : le casier contient " + contenu)
                self.porte = objet
    def _donner(self, objet):
                if self.porte is None or objet != self.porte:
                    raise ActionIllegale("DONNER : le robot ne porte pas " + str(objet))
                if self.resident_cible is None:
                    raise ActionIllegale("DONNER : aucune demande en cours")
                lr, cr = self.residents[self.resident_cible]
                lp, cp = self.position
                if abs(lr - lp) + abs(cr - cp) != 1:
                    raise ActionIllegale("DONNER : pas adjacent au résident " + self.resident_cible)
                self.porte = None
