import os
import time

from planification import plus_court_chemin, est_traversable
from reconfort_io import charger_carte
class Affichage:
    def __init__(self, donnees_carte):
        self.grille = donnees_carte["grille"]
        self.hauteur = donnees_carte["dimensions"]["hauteur"]
        self.largeur = donnees_carte["dimensions"]["largeur"]
        self.position_robot = list(donnees_carte["depart_robot"])

    def afficher(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        for ligne in range(self.hauteur):
            affichage_ligne = ""
            for colonne in range(self.largeur):
                if [ligne, colonne] == self.position_robot:
                    affichage_ligne += "R"
                else:
                    affichage_ligne += self.grille[ligne][colonne]
            
            print(affichage_ligne)
        
        time.sleep(0.5)


if __name__ == "__main__":
    # On charge la vraie carte depuis le fichier JSON chemin_fichier = "base_fournie/cartes/appartement_01.json" 
    vraie_carte= charger_carte("base_fournie/cartes/appartement_01.json")
    
    #On initialise le simulateur avec ces vraies données
    simu = Affichage(vraie_carte)
    
    # 3. On affiche la grille initiale !
    simu.afficher()