"""Les poses : de quoi écrire une animation comme une fonction du temps. Voir usine.py et GUIDE.md."""
import math

TAU = math.tau


def cloche(t, centre, large, boucle=True):
    """Une bosse douce autour de « centre », de demi-largeur « large » (en fraction de l'animation)."""
    d = ((t - centre + 0.5) % 1.0) - 0.5 if boucle else t - centre
    x = max(0.0, 1.0 - abs(d) / large)
    return x * x * (3 - 2 * x)


def onde(t, tours, phase=0.0):
    return math.sin(TAU * (t * tours + phase))


def borne(x):
    return min(max(x, 0.0), 1.0)


class Pose:
    def __init__(self):
        self.os = {}
        self.ouvert = 1.0          # les yeux : 1 ouverts, 0 fermés

    def add(self, nom, rot=(0, 0, 0), pos=(0, 0, 0), ech=(1, 1, 1)):
        o = self.os.setdefault(nom, {"rot": [0.0, 0.0, 0.0], "pos": [0.0, 0.0, 0.0], "ech": [1.0, 1.0, 1.0]})
        for i in range(3):
            o["rot"][i] += rot[i]
            o["pos"][i] += pos[i]
            o["ech"][i] *= ech[i]
        return self

    def paire(self, nom, rot=(0, 0, 0), pos=(0, 0, 0), ech=(1, 1, 1)):
        """Le même geste des deux côtés, en miroir."""
        self.add(nom + "_G", rot, pos, ech)
        self.add(nom + "_D", (rot[0], -rot[1], -rot[2]), (-pos[0], pos[1], pos[2]), ech)
        return self
