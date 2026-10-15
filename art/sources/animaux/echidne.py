"""L'échidné en peluche de velours ras : un brun prune, tout le dos hérissé de piquants crème à pointe sombre, une
petite face ronde qui se prolonge en long bec fin et courbe, de minuscules yeux, des pattes courtes aux griffes
puissantes, et un ventre de poil. Le hérisson-fourmilier : trapu, bas, le museau au ras du sol qui renifle, une patte
avant creusant la terre, les piquants dressés en couronne, un œil en coin qui vérifie qu'on ne le suit pas.

    python echidne.py        fabrique la fiche art/apercus/animaux/echidne.png (velours ras, palier 3)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import garnitures as G
import matieres as M
import peluche as K

PRUNE = M.hexa("#8a6070")                     # la dominante : brun prune (le poil la fonce : on la prend claire)
CREME = M.hexa("#fff2d0")                     # l'accent : les piquants
POINTE = M.hexa("#5a4048")                    # le bout des piquants, le museau
CHARBON = M.hexa("#3a2c30")
CORPS = Vector((0.0, 0.050, 0.130))
TETE = Vector((0.0, -0.200, 0.115))
LACET = 22.0


def construire():
    a = K.Animal("echidne")
    a.taille = 0.50

    # ----- le corps : un dôme bas, large ; dessus, des rangs de piquants de feutrine (le geste des plumes du cygne) -----
    def dome(v):
        s = v * [0.150, 0.230, 0.118]
        s[:, 2] = np.where(s[:, 2] < 0, s[:, 2] * 0.55, s[:, 2])
        return s
    dos = A.boule(1.0, 48, 24).sculpte(dome)
    dos.teinte = np.tile(np.asarray(PRUNE, float), (len(dos.v), 1))
    a.piece("corps", dos, None, pos=CORPS)
    piquants = G.franges(dos, 0.080, 0.016, 0.022, 0.030,
                         lambda rang, t: tuple(np.asarray(CREME) * (0.88 + 0.12 * (rang % 2)) * (0.7 + 0.3 * t) + np.asarray(POINTE) * (0.25 * (1 - t))),
                         5, 1, 0.10, 0.98)
    a.piece("piquants", piquants, None, pos=CORPS, poil=False)

    # ----- la tête : une petite boule ronde sans cou, qui se prolonge en long bec fin, courbé vers le bas -----
    H = A.repere(TETE, (14, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.058, 0.060, 0.055), PRUNE, mat=H)

    def courbe_(v):
        s = v.copy()
        s[:, 1] -= 0.030 * np.clip(v[:, 2] / 0.200, 0, 1) ** 2
        return s
    bec = A.tour(A.profil([(0, 0), (0.030, 0.006), (0.024, 0.040), (0.014, 0.110), (0.008, 0.175), (0.004, 0.205), (0, 0.215)], 5), 24)
    a.piece("bec", bec.sculpte(courbe_), POINTE, mat=H @ A.repere((0, -0.040, -0.010), (90, 0, 0)))
    a.tete = H @ Vector((0, -0.150, -0.030))
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.82, -0.50, 0.22)))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0095)

    # ----- les pattes : quatre troncs courts, aux grandes griffes ; l'avant droite creuse -----
    for nom, x, y, creuse in (("av_G", 0.115, -0.090, False), ("av_D", -0.115, -0.090, True), ("ar_G", 0.115, 0.190, False), ("ar_D", -0.115, 0.190, False)):
        c = 1 if x > 0 else -1
        chemin = [(x * 0.8, y, 0.080), (x * 1.04, y - 0.010, 0.040), (x * 1.06, y - (0.050 if creuse else 0.020), 0.016)]
        a.piece("patte_" + nom, A.tube(A.courbe(chemin, 5), 0.030, 12), PRUNE)
        griffes = None
        for k in (-1, 0, 1):
            g = A.tour(A.profil([(0, 0), (0.008, 0.003), (0.006, 0.026), (0.003, 0.048), (0, 0.058)], 5), 10)
            g = g.pose((0, 0, 0), (-84, 0, 0)).pose((k * 0.018, -0.020, 0.0), (0, 0, k * 8))
            griffes = g if griffes is None else griffes + g
        a.piece("griffes_" + nom, griffes, CHARBON, pos=(x * 1.06, y - (0.050 if creuse else 0.020), 0.012), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("echidne", styles.style_de("echidne"), sys.modules[__name__]), "Échidné")
