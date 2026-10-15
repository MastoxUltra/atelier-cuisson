"""Le pélican en peluche : un nuage blanc rosé, saumon pâle, tout en bec. Le cou replié en S sur la poitrine, le bec
énorme posé sur le jabot, sous lequel pend la poche orange, gonflée comme une besace ; un petit œil de côté, sage et
tranquille, qui voit passer tous les poissons du monde. Les pattes courtes, orange, les ailes repliées en toit.

    python pelican.py        fabrique la fiche art/apercus/animaux/pelican.png (style du palier : C, velours ras)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K
import outils_a as O

SAUMON = np.array(M.hexa("#f2c5b8"))          # la dominante (registre : blanc rosé saumon pâle)
BLANC = np.array(M.hexa("#fbf4ee"))
AILE = np.array(M.hexa("#e6b3a6"))
BEC = np.array(M.hexa("#e8b58a"))             # le bec, rose chair
POCHE = M.hexa("#f08a2a")                     # l'accent : la poche orange
PATTE = M.hexa("#f08a2a")
SOMBRE = np.array(M.hexa("#5a4a44"))          # le bout des ailes
FIL = M.hexa("#8a4a28")


def construire():
    a = K.Animal("pelican")
    a.taille = 1.55

    # ----- le corps : un gros œuf, un peu penché, le dos saumon, le ventre blanc -----
    T = A.repere((0.0, 0.080, 0.300), (20, 0, 0))
    pc = A.profil([(0, 0.0), (0.150, 0.015), (0.250, 0.090), (0.285, 0.230), (0.250, 0.380), (0.170, 0.500), (0.080, 0.570), (0, 0.600)], 6)
    corps = A.tour(pc, 52)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(BLANC, (len(ang), 1))
    t[(ang < 1.3) & (corps.v[:, 2] > 0.05)] = SAUMON
    corps.teinte = t
    a.piece("corps", corps, None, mat=T)
    haut = Vector(T @ Vector((0, 0, 0.545)))

    # ----- le cou en S sur le jabot, la tête petite, le bec énorme posé sur la poitrine, la poche qui pend dessous -----
    cou = O.tube_r([haut + Vector((0, 0.02, 0.00)), haut + Vector((0, 0.04, 0.12)), haut + Vector((0, -0.04, 0.24)),
                    haut + Vector((0, -0.12, 0.26)), haut + Vector((0, -0.14, 0.18))], [0.115, 0.095, 0.082, 0.075, 0.070], 20)
    a.piece("cou", O.teinte(cou, BLANC), None)
    H = haut + Vector((0.0, -0.150, 0.150))
    tete = A.boule(1.0, 40, 20).etire(0.075, 0.095, 0.080)
    a.piece("tete", O.teinte(tete, BLANC), None, pos=tuple(H), rot=(20, 0, 0))
    a.tete = H + Vector((0.0, -0.20, -0.04))

    # le bec : un long fer plat, légèrement courbé vers le bas au bout, qui part du front en s'abaissant vers la poitrine
    bec = A.tour(A.profil([(0.058, 0), (0.060, 0.080), (0.054, 0.200), (0.040, 0.300), (0.026, 0.360), (0.010, 0.388), (0, 0.396)], 4), 28)
    bec = bec.etire(1.0, 0.46, 1.0).sculpte(lambda v: np.stack([v[:, 0], v[:, 1] - 0.14 * (v[:, 2] / 0.396) ** 3, v[:, 2]], axis=1))
    a.piece("bec", O.couche(O.teinte(bec, BEC), A.cadre(H + Vector((0.0, -0.075, -0.030)), (0.0, -0.55, -1.0), (0, 1.0, 0))), None, poil=False)
    poche = A.boule(1.0, 36, 18).etire(0.060, 0.045, 0.200)
    poche = poche.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] - 0.20 * (v[:, 2] > 0) * 0, v[:, 2]], axis=1))
    a.piece("poche", poche, POCHE, mat=A.cadre(H + Vector((0.0, -0.155, -0.200)), (0.0, -0.45, -1.0), (0, 1.0, 0)))
    O.paire_yeux(a, "tete", H, (0.88, -0.30, 0.30), 0.0175, decolle=0.002)

    # ----- les ailes repliées en toit, le bout sombre ; la queue courte ; les pattes courtes, orange -----
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 36, 18).etire(0.040, 0.110, 0.300)
        f = aile.v[:, 2] / 0.300
        t = np.tile(AILE, (len(f), 1))
        t[f < -0.62] = SOMBRE
        aile.teinte = t
        a.piece("aile_" + nom, aile, None, mat=T @ A.repere((c * 0.255, 0.050, 0.330), (0, 0, c * 6)))
        jambe = O.tube_r([(c * 0.110, 0.050, 0.130), (c * 0.120, 0.000, 0.065), (c * 0.120, -0.030, 0.012)], [0.032, 0.026, 0.022], 12)
        a.piece("jambe_" + nom, O.teinte(jambe, PATTE), None, poil=False)
        palme = A.boule(1.0, 20, 8).etire(0.068, 0.100, 0.010)
        a.piece("palme_" + nom, O.teinte(palme, PATTE), None, pos=(c * 0.124, -0.090, 0.011), rot=(0, 0, c * 6), poil=False)
    queue = A.boule(1.0, 24, 12).etire(0.065, 0.100, 0.020)
    a.piece("queue", O.teinte(queue, AILE), None, pos=(0.0, 0.440, 0.240), rot=(-26, 0, 0))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules[__name__], "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pelican", styles.style_de("pelican"), sys.modules[__name__]), "Pélican")
