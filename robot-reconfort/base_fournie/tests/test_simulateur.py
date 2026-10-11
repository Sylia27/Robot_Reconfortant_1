import unittest
from pathlib import Path

import reconfort_io as rio
from environnement import Environnement, ActionIllegale

DOSSIER = Path(__file__).parent.parent      


def creer_env():
    
    carte = rio.charger_carte(DOSSIER / "cartes" / "appartement_01.json")
    armoire = rio.charger_armoire(DOSSIER / "donnees" / "armoire_standard.json")
    return Environnement(carte, armoire)


class TestEnvironnement(unittest.TestCase):

    def test_perception_au_depart(self):
        env = creer_env()
        attendu = {"N": "libre", "S": "libre", "E": "libre", "O": "mur"}
        self.assertEqual(env.percevoir(), attendu)

    def test_avancer_change_la_position(self):
        env = creer_env()
        env.appliquer("AVANCER", "E")
        self.assertEqual(env.position, (6, 2))

    def test_avancer_dans_un_mur_est_refuse(self):
        env = creer_env()
        with self.assertRaises(ActionIllegale):
            env.appliquer("AVANCER", "O")         
        self.assertEqual(env.position, (6, 1))     

    def test_contenu_invisible_loin_de_l_armoire(self):
        env = creer_env()
        self.assertIsNone(env.contenu_casier())

    def test_contenu_visible_pres_de_l_armoire(self):
        env = creer_env()
        env.position = (6, 3)                     
        self.assertEqual(env.contenu_casier(), "photo de famille")  

    def test_chercher_deplace_le_selecteur(self):
        env = creer_env()
        env.position = (6, 3)
        env.appliquer("CHERCHER", "E")
        self.assertEqual(env.selecteur, (1, 1))
        self.assertEqual(env.contenu_casier(), "plaid")

    def test_chercher_loin_de_l_armoire_est_refuse(self):
        env = creer_env()
        with self.assertRaises(ActionIllegale):
            env.appliquer("CHERCHER", "E")

    def test_prendre_puis_deuxieme_prendre_refuse(self):
        env = creer_env()
        env.position = (6, 3)
        env.appliquer("CHERCHER", "E")
        env.appliquer("CHERCHER", "E")            
        env.appliquer("PRENDRE", "lampe torche")
        self.assertEqual(env.porte, "lampe torche")
        with self.assertRaises(ActionIllegale):
            env.appliquer("PRENDRE", "lampe torche")  

    def test_prendre_casier_vide_refuse(self):
        env = creer_env()
        env.position = (6, 3)
        for _ in range(3):
            env.appliquer("CHERCHER", "E")        
        with self.assertRaises(ActionIllegale):
            env.appliquer("PRENDRE", "couverture")

    def test_donner_au_bon_resident(self):
        env = creer_env()
        env.nouvelle_demande("R1")
        env.porte = "couverture"
        env.position = (6, 10)                    
        env.appliquer("DONNER", "couverture")
        self.assertIsNone(env.porte)

    def test_donner_trop_loin_refuse(self):
        env = creer_env()
        env.nouvelle_demande("R1")
        env.porte = "couverture"
        with self.assertRaises(ActionIllegale):
            env.appliquer("DONNER", "couverture")  

if __name__ == "__main__":
    unittest.main()