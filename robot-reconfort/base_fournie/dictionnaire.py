
import reconfort_io as rio
from regles import construire_index


class Dictionnaire:
    """Le dictionnaire du robot. Le fichier n'est lu qu'à la première consultation """

    def __init__(self, chemin):
        self.chemin = chemin
        self.index_formes = None       
        self.emotions = None
        self.intensites = None

    def consulter(self):
        """
        Lit le fichier la première fois, puis garde son contenu en mémoire"""
        if self.index_formes is None:
            contenu= rio.charger_dictionnaire(self.chemin)
            self.index_formes= construire_index(contenu)
            self.emotions=contenu["emotions"]
            self.intensites=contenu["intensites"]