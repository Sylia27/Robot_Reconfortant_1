import unittest

from memoire import Memoire
from regles import liste_candidats
from decision import (direction, deplacer_vers, Demande, choisir_action,
                      ARMOIRE, RESIDENT, TERMINEE)

INDEX = {"seule": (4, 1)}      # un mini-dictionnaire écrit à la main


def creer_memoire():
    """Appartement 7x9, armoire en (3,4), dictionnaire en (5,1), R1 en (5,7)."""
    infos = {"hauteur": 7, "largeur": 9, "depart": (1, 1), "armoire": (3, 4),
             "dictionnaire": (5, 1), "residents": {"R1": (5, 7)},
             "casier_depart": (1, 0)}
    return Memoire(infos)


class TestDirection(unittest.TestCase):

    def test_les_quatre_directions(self):
        self.assertEqual(direction((6, 1), (6, 2)), "E")
        self.assertEqual(direction((6, 2), (6, 1)), "O")
        self.assertEqual(direction((5, 3), (6, 3)), "S")
        self.assertEqual(direction((6, 3), (5, 3)), "N")

    def test_cases_non_voisines(self):
        with self.assertRaises(ValueError):
            direction((6, 1), (6, 3))

    def test_diagonale_refusee(self):
        with self.assertRaises(ValueError):
            direction((6, 1), (5, 2))

    def test_meme_case_refusee(self):
        with self.assertRaises(ValueError):
            direction((6, 1), (6, 1))


class TestDeplacerVers(unittest.TestCase):

    def test_un_pas_vers_le_dictionnaire(self):
        m = creer_memoire()
        m.position = (3, 1)
        self.assertEqual(deplacer_vers(m, m.pos_dictionnaire), ("avancer", "S"))

    def test_deja_arrive(self):
        m = creer_memoire()
        m.position = (4, 1)                       # adjacent au dictionnaire (5,1)
        self.assertEqual(deplacer_vers(m, m.pos_dictionnaire), ("arrive", None))

    def test_replanification_apres_un_mur(self):
        m = creer_memoire()
        m.position = (3, 1)
        m.carte.murs.add((4, 1))                  # le robot découvre un mur
        self.assertEqual(deplacer_vers(m, m.pos_dictionnaire), ("avancer", "E"))

    def test_resident_inaccessible(self):
        m = creer_memoire()
        m.carte.murs.add((4, 7))                  # R1 est en (5,7) : ses autres
        m.carte.murs.add((5, 6))                  # voisines sont le bord
        self.assertEqual(deplacer_vers(m, m.residents["R1"]), ("inaccessible", None))


class TestChoisirAction(unittest.TestCase):

    def preparer_fouille(self, e, i):
        """Robot adjacent à l'armoire, phase ARMOIRE, candidats calculés."""
        m, d = creer_memoire(), Demande(1, "R1", [])
        m.position = (3, 3)
        d.phase = ARMOIRE
        d.candidats = liste_candidats(e, i)
        return m, d

    def test_dictionnaire_loin_avance(self):
        m, d = creer_memoire(), Demande(1, "R1", ["je", "suis", "seule"])
        self.assertEqual(choisir_action(m, d, INDEX), ("AVANCER", "S"))

    def test_dictionnaire_adjacent_consulte(self):
        m, d = creer_memoire(), Demande(1, "R1", ["seule"])
        m.position = (4, 1)
        self.assertEqual(choisir_action(m, d, INDEX), ("CONSULTER", None))
        self.assertTrue(d.consulte)

    def test_lecture_de_l_emotion_puis_phase_armoire(self):
        m, d = creer_memoire(), Demande(1, "R1", ["je", "suis", "seule"])
        m.position = (4, 1)
        choisir_action(m, d, INDEX)                       # CONSULTER
        action = choisir_action(m, d, INDEX)              # lecture, puis armoire
        self.assertEqual((d.emotion, d.intensite), (4, 1))
        self.assertEqual(d.phase, ARMOIRE)
        self.assertEqual(action[0], "AVANCER")

    def test_emotion_indeterminee(self):
        m, d = creer_memoire(), Demande(1, "R1", ["il", "fait", "beau"])
        m.position = (4, 1)
        choisir_action(m, d, INDEX)
        self.assertEqual(choisir_action(m, d, INDEX), ("ECHEC", "emotion indeterminee"))

    def test_fouille_casier_inconnu_donne_chercher(self):
        m, d = self.preparer_fouille(4, 1)                # tristesse/moyenne : (1,4)
        self.assertEqual(choisir_action(m, d, INDEX), ("CHERCHER", "E"))

    def test_fouille_casier_garni_donne_prendre(self):
        m, d = self.preparer_fouille(4, 1)
        m.armoire.selecteur = (1, 4)
        m.armoire.noter((1, 4), "couverture")
        self.assertEqual(choisir_action(m, d, INDEX), ("PRENDRE", "couverture"))
        self.assertEqual((d.casier_choisi, d.repli, d.phase), ((1, 4), "aucun", RESIDENT))

    def test_repli_sur_une_voisine_annexe_c5(self):
        m, d = self.preparer_fouille(3, 2)                # surprise/forte
        for casier in [(2, 3), (1, 3), (0, 3)]:
            m.armoire.noter(casier, None)                 # la colonne surprise est vide
        m.armoire.selecteur = (2, 4)
        m.armoire.noter((2, 4), "telephone")
        self.assertEqual(choisir_action(m, d, INDEX), ("PRENDRE", "telephone"))
        self.assertEqual((d.casier_choisi, d.repli), ((2, 4), "voisine_1"))

    def test_garni_moins_prioritaire_ne_passe_pas_devant(self):
        m, d = self.preparer_fouille(3, 2)
        for casier in [(2, 3), (1, 3)]:
            m.armoire.noter(casier, None)
        m.armoire.noter((2, 2), "bouton d appel")         # garni, mais rang 5
        action = choisir_action(m, d, INDEX)              # (0,3) est inconnu, rang 3
        self.assertEqual(action[0], "CHERCHER")

    def test_armoire_vide(self):
        m, d = self.preparer_fouille(3, 2)
        for candidat in d.candidats:
            m.armoire.noter(candidat["casier"], None)
        self.assertEqual(choisir_action(m, d, INDEX), ("ECHEC", "armoire vide"))

    def test_resident_deja_inaccessible_on_ne_prend_rien(self):
        m, d = self.preparer_fouille(4, 1)
        m.carte.murs.add((4, 7))
        m.carte.murs.add((5, 6))
        m.armoire.selecteur = (1, 4)
        m.armoire.noter((1, 4), "couverture")
        self.assertEqual(choisir_action(m, d, INDEX), ("ECHEC", "resident inaccessible"))
        self.assertEqual(d.phase, ARMOIRE)                # pas de passage à RESIDENT

    def test_donner_au_resident(self):
        m, d = creer_memoire(), Demande(1, "R1", [])
        d.phase, d.objet = RESIDENT, "couverture"
        m.position = (4, 7)                               # adjacent à R1 (5,7)
        self.assertEqual(choisir_action(m, d, INDEX), ("DONNER", "couverture"))
        self.assertEqual(d.phase, TERMINEE)

    def test_resident_inaccessible_apres_prendre(self):
        m, d = creer_memoire(), Demande(1, "R1", [])
        d.phase, d.objet = RESIDENT, "couverture"
        m.carte.murs.add((4, 7))
        m.carte.murs.add((5, 6))
        self.assertEqual(choisir_action(m, d, INDEX), ("ECHEC", "resident inaccessible"))


if __name__ == "__main__":
    unittest.main()