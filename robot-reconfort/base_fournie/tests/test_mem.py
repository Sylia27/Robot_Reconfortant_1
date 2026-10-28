import unittest

from memoire import CarteMentale, ArmoireMentale, Memoire
from regles import liste_candidats


def creer_memoire():
    """Appartement 7x9, armoire en (3,4), dictionnaire en (5,1), R1 en (5,7)."""
    infos = {"hauteur": 7, "largeur": 9, "depart": (1, 1), "armoire": (3, 4),
             "dictionnaire": (5, 1), "residents": {"R1": (5, 7)},
             "casier_depart": (1, 0)}
    return Memoire(infos)


class TestCarteMentale(unittest.TestCase):

    def test_inconnu_est_traversable(self):
        m = creer_memoire()
        self.assertTrue(m.carte.est_traversable((2, 3)))

    def test_le_bord_n_est_pas_traversable(self):
        m = creer_memoire()
        self.assertFalse(m.carte.est_traversable((0, 3)))
        self.assertFalse(m.carte.est_traversable((3, 0)))
        self.assertFalse(m.carte.est_traversable((-1, 3)))    # hors grille

    def test_obstacles_connus_d_avance(self):
        m = creer_memoire()
        self.assertFalse(m.carte.est_traversable((3, 4)))     # armoire
        self.assertFalse(m.carte.est_traversable((5, 1)))     # dictionnaire
        self.assertFalse(m.carte.est_traversable((5, 7)))     # résident R1

    def test_un_mur_decouvert_devient_intraversable(self):
        m = creer_memoire()
        m.position = (3, 3)
        self.assertTrue(m.carte.est_traversable((4, 3)))      # avant la perception
        m.integrer({"N": "libre", "S": "mur", "E": "armoire", "O": "libre"}, "plaid")
        self.assertFalse(m.carte.est_traversable((4, 3)))     # après

    def test_arrivees_autour_de_l_armoire(self):
        carte = CarteMentale(7, 9, {(3, 4)})
        self.assertEqual(carte.arrivees_autour((3, 4)),
                         {(2, 4), (4, 4), (3, 5), (3, 3)})

    def test_arrivees_excluent_le_bord(self):
        carte = CarteMentale(7, 9, {(1, 1)})
        self.assertEqual(carte.arrivees_autour((1, 1)), {(2, 1), (1, 2)})

    def test_arrivees_se_recalculent_apres_un_mur(self):
        carte = CarteMentale(7, 9, {(3, 4)})
        carte.sauvegarde((4, 3), {"N": "libre", "S": "libre", "E": "mur", "O": "libre"})
        # le mur en (4,4) retire cette case des arrivées possibles
        self.assertEqual(carte.arrivees_autour((3, 4)),
                         {(2, 4), (3, 5), (3, 3)})


class TestArmoireMentale(unittest.TestCase):

    def test_les_trois_etats_d_un_casier(self):
        armoire = ArmoireMentale((1, 0))
        armoire.noter((1, 3), None)               # vu vide
        armoire.noter((1, 4), "couverture")       # vu garni
        self.assertTrue(armoire.est_vu_vide((1, 3)))
        self.assertFalse(armoire.est_vu_vide((1, 4)))
        self.assertFalse(armoire.est_vu_vide((2, 4)))   # jamais vu

    def test_premier_candidat_utile_saute_les_casiers_vides(self):
        armoire = ArmoireMentale((1, 0))
        armoire.noter((2, 3), None)
        armoire.noter((1, 3), None)
        res = armoire.premier_candidat_utile(liste_candidats(3, 2))
        self.assertEqual(res, {"casier": (0, 3), "repli": "intensite"})

    def test_casier_garni_moins_prioritaire_ne_passe_pas_devant(self):
        # tristesse/forte (2,4) et peur/forte (2,2) sont garnis,
        # mais le candidat inconnu (0,3) est plus prioritaire que les deux
        armoire = ArmoireMentale((1, 0))
        armoire.noter((2, 3), None)
        armoire.noter((1, 3), None)
        armoire.noter((2, 2), "bouton d appel")
        res = armoire.premier_candidat_utile(liste_candidats(3, 2))
        self.assertEqual(res["casier"], (0, 3))

    def test_tous_les_candidats_vides(self):
        armoire = ArmoireMentale((1, 0))
        for candidat in liste_candidats(3, 2):
            armoire.noter(candidat["casier"], None)
        self.assertIsNone(armoire.premier_candidat_utile(liste_candidats(3, 2)))

    def test_deplacer_suit_le_bouclage(self):
        armoire = ArmoireMentale((2, 7))
        armoire.deplacer("E")
        self.assertEqual(armoire.selecteur, (2, 0))


class TestMemoire(unittest.TestCase):

    def test_integrer_note_le_casier_pres_de_l_armoire(self):
        m = creer_memoire()
        m.position = (3, 3)
        m.integrer({"N": "libre", "S": "mur", "E": "armoire", "O": "libre"}, "plaid")
        self.assertEqual(m.armoire.vus, {(1, 0): "plaid"})

    def test_integrer_ne_note_rien_loin_de_l_armoire(self):
        m = creer_memoire()
        m.integrer({"N": "mur", "S": "libre", "E": "libre", "O": "mur"}, None)
        self.assertEqual(m.armoire.vus, {})

    def test_avancer_met_a_jour_la_position(self):
        m = creer_memoire()
        m.position = (3, 3)
        m.avancer("N")
        self.assertEqual(m.position, (2, 3))

    def test_le_selecteur_garde_sa_position(self):
        m = creer_memoire()
        m.armoire.deplacer("E")
        self.assertEqual(m.armoire.selecteur, (1, 1))


if __name__ == "__main__":
    unittest.main()