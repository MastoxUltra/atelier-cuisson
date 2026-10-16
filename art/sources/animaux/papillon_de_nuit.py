"""Le papillon de nuit en peluche : un gros corps duveteux gris mauve poudré, quatre ailes en feutrine bien ouvertes, chacune
avec un grand œil en cercles crème et sombre, et deux antennes plumeuses roux, qui se déploient comme des peignes. Il
est posé à plat, une aile levée, à peine sorti de son sommeil, la poussière des ailes encore sur les doigts.

    python papillon_de_nuit.py        fabrique la fiche art/apercus/animaux/papillon_de_nuit.png (style du palier : A, cousu main)
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

MAUVE = M.hexa("#a8a0b8")                     # la dominante (registre : gris mauve poudré)
FONCE = np.array(M.hexa("#7a6e8a"))           # le bord des ailes, les bandes
CREME = np.array(M.hexa("#f3e8d2"))           # les cercles des ocelles
OEIL = np.array(M.hexa("#2c2530"))            # le centre des ocelles
ROUX = M.hexa("#b5602d")                      # l'accent : les antennes
FIL = M.hexa("#3a3040")


def aile(contour, miroir):
    m = A.decoupe(A.courbe(np.array(contour) * [miroir, 1], 5, fermee=True), 0.018, 0.007)
    return m.sculpte(lambda v: np.stack([v[:, 0], v[:, 1], v[:, 2] + 3.20 * v[:, 0] ** 2 + 0.90 * v[:, 1] ** 2], axis=1))      # bombée, pas une assiette plate


def construire():
    a = K.Animal("papillon_de_nuit")
    a.taille = 0.40

    # ----- le corps : un gros fuseau duveteux, une tête ronde ; les antennes plumeuses -----
    corps = A.boule(1.0, 36, 18).etire(0.050, 0.130, 0.048)
    a.piece("corps", corps, MAUVE, pos=(0.0, 0.040, 0.060))
    tete = A.boule(1.0, 28, 14).etire(0.044, 0.040, 0.040)
    a.piece("tete", tete, MAUVE, pos=(0.0, -0.112, 0.066))
    H = Vector((0.0, -0.112, 0.066))
    O.paire_yeux(a, "tete", H, (0.62, -0.76, 0.18), 0.0160, decolle=0.002)
    for nom, c in (("G", 1), ("D", -1)):
        base = Vector((c * 0.020, -0.140, 0.088))
        pts = [base, base + Vector((c * 0.050, -0.070, 0.050)), base + Vector((c * 0.110, -0.095, 0.080))]
        a.piece("antenne_" + nom, O.tube_r([tuple(p) for p in pts], [0.0065, 0.0055, 0.0040], 8), ROUX, poil=False)
        for k in range(7):
            t = 0.12 + 0.12 * k
            p = base + (pts[1] - base) * min(t / 0.5, 1.0) + (pts[2] - pts[1]) * max(0.0, (t - 0.5) / 0.5) * 0.9
            for s in (-1, 1):
                barbule = O.tube_r([tuple(p), tuple(p + Vector((c * 0.012 * s, -0.010, 0.020 * s * 0 + 0.010 * s)))], [0.0035, 0.0025], 6)
                a.piece("barbule_%s%d%s" % (nom, k, "a" if s > 0 else "b"), barbule, ROUX, poil=False)
    a.tete = H + Vector((0.0, -0.08, 0.0))

    # ----- les ailes : deux grandes devant (la gauche levée), deux plus petites derrière ; chacune avec son ocelle -----
    devant = [(0.00, 0.00), (0.07, -0.05), (0.19, -0.04), (0.29, 0.00), (0.31, 0.08), (0.24, 0.15), (0.12, 0.13), (0.04, 0.08)]
    derriere = [(0.00, 0.00), (0.08, 0.04), (0.20, 0.10), (0.24, 0.18), (0.17, 0.24), (0.07, 0.19), (0.02, 0.10)]
    for nom, c in (("G", 1), ("D", -1)):
        for j, (contour, y0, taille_oc) in enumerate(((devant, 0.020, 0.040), (derriere, 0.070, 0.028))):
            leve = 28.0 if (c == 1 and j == 0) else 4.0
            m = aile(contour, c)
            xs = m.v[:, 0] * c
            t = np.tile(np.array(MAUVE), (len(m.v), 1))
            t[xs > 0.18] = FONCE
            m.teinte = t
            rep = A.repere((c * 0.040, y0 - 0.020 * j, 0.062), (0, c * -leve, c * (-8 + 16 * j)))
            a.piece("aile_%d_%s" % (j, nom), m, None, mat=rep, poil=False)
            # l'ocelle : un disque crème, un disque sombre, un point crème
            for r, col, dz in ((taille_oc, CREME, 0.0070), (taille_oc * 0.62, OEIL, 0.0085), (taille_oc * 0.24, CREME, 0.0100)):
                d = A.boule(1.0, 20, 8).etire(r, r, 0.004)
                px, py = (0.195, 0.045) if j == 0 else (0.150, 0.130)
                a.piece("ocelle_%d%s%d" % (j, nom, int(r * 1000)), O.teinte(d, col), None,
                        mat=rep @ A.repere((c * px, py, dz + 3.2 * px ** 2 + 0.9 * py ** 2)), poil=False)      # l'ocelle suit la cambrure de l'aile (elle traînait au sol)
    # ----- les pattes : deux de chaque côté, sous le thorax -----
    for nom, c in (("G", 1), ("D", -1)):
        for k, y in enumerate((-0.040, 0.020)):
            p = O.tube_r([(c * 0.030, y, 0.050), (c * 0.075, y - 0.012, 0.035), (c * 0.100, y - 0.020, 0.008)], [0.0080, 0.0070, 0.0055], 8)
            a.piece("patte_%s%d" % (nom, k), O.teinte(p, np.array(MAUVE) * 0.8), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("papillon_de_nuit", styles.style_de("papillon_de_nuit"), sys.modules[__name__]), "Papillon de nuit")
