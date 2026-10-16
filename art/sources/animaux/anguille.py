"""L'anguille en peluche : un très long boudin ambre brun, le ventre jaune pâle, qui s'est lové en deux grandes
boucles à plat et lève la tête hors des anneaux, l'œil doré fixé sur vous, le menton avancé. Une nageoire à ourlet
court tout le long du dos et jusqu'au bout de la queue, comme une bordure de rideau. Elle a l'air d'écouter.

    python anguille.py        fabrique la fiche art/apercus/animaux/anguille.png (style du palier : A, cousu main)
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

AMBRE = np.array(M.hexa("#b87a36"))           # la dominante (registre : ambre brun)
DESSOUS = np.array(M.hexa("#f1dd9a"))         # le ventre jaune pâle
OURLET = np.array(M.hexa("#7a4d22"))          # la nageoire
OR = M.hexa("#f2b92a")                        # l'œil doré
FIL = M.hexa("#4a2a12")

# du bout de la queue à la tête : deux grandes boucles à plat, puis le cou qui se redresse en col de cygne
CHEMIN = [(0.30, 0.52, 0.040), (0.10, 0.60, 0.050), (-0.12, 0.50, 0.054), (-0.20, 0.30, 0.056), (-0.02, 0.16, 0.058),
          (0.22, 0.20, 0.058), (0.36, 0.02, 0.058), (0.22, -0.16, 0.058), (-0.02, -0.14, 0.058), (-0.18, -0.26, 0.064),
          (-0.14, -0.42, 0.110), (-0.02, -0.48, 0.200), (0.04, -0.54, 0.285), (0.00, -0.64, 0.318)]


def rayon(f):
    return O.interp([(0.0, 0.0), (0.02, 0.012), (0.10, 0.030), (0.30, 0.046), (0.70, 0.050), (0.90, 0.044), (0.965, 0.040),
                     (0.985, 0.036), (1.0, 0.0)])(f)


def construire():
    a = K.Animal("anguille")
    a.taille = 1.30

    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(AMBRE, (len(ang), 1))
        t[ang > 2.0] = DESSOUS
        f = m.v[:, 2] / L
        t[f > 0.965] = AMBRE * 0.82                                  # le dessus du museau, un peu plus sombre
        return t
    # un seul fuseau lisse ; haut : le dos toujours en haut le long des boucles (16/10, planche 21 « bizarre » : avec le flanc
    # fixe, le corps s'écrasait en ruban tordu là où la boucle passait par le flanc, le ventre jaune tournant autour)
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=40, pas=24, flanc=(1.0, 0.0, 0.0), haut=(0.0, 0.0, 1.0))

    # ----- la nageoire en ourlet : un mince ruban le long du dos, de la nuque jusqu'au bout de la queue -----
    pts = []
    for f in np.linspace(0.05, 0.93, 60):
        c, av, nq = (Vector(q) for q in fil.cadre(f * L))
        pts.append(tuple(c + nq * (rayon(f) + 0.004)))
    ruban = A.tube(A.courbe(pts, 2), lambda t: 0.0095 * (1 - 0.5 * abs(2 * t - 1)), 8)
    a.piece("ourlet", O.teinte(ruban, OURLET), None, poil=False)

    # ----- le visage : un petit œil doré de chaque côté de la tête, la bouche fendue en un trait, deux narines -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, direction = fil.vise(0.965 * L, 0.60, c * 0.55, 0.30)
        pos, n = a.surface("corps", centre, direction)
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0175)                       # un vrai œil vivant, plus de pièce de monnaie
    pts = []
    for u_ in np.linspace(0.0, 1.0, 7):
        cc, dd = fil.vise((0.998 - 0.040 * u_) * L, 0.0, 1.0, -0.40 + 0.10 * u_)
        q = a.trace("corps", cc, [dd], 0.002)
        if q:
            pts.append(q[0])
    if len(pts) > 1:
        a.broderie("bouche", A.courbe(pts, 4), 0.0022, FIL)
    # une nageoire pectorale minuscule de chaque côté, juste derrière la tête
    for nom, c in (("G", 1), ("D", -1)):
        cp, ap, nq = (Vector(q) for q in fil.cadre(0.925 * L))
        p = A.boule(1.0, 16, 8).etire(0.006, 0.030, 0.014)
        p.teinte = np.tile(OURLET, (len(p.v), 1))
        a.piece("pectorale_" + nom, O.couche(p, A.cadre(cp + Vector((-c * 0.040, 0.0, 0.0)), (-c * 0.9, 0.4, 0.0), (0, 0, 1))), None, poil=False)
    a.tete = Vector(fil.cadre(0.985 * L)[0]) + Vector((0.0, -0.03, 0.0))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "serpent")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("anguille", styles.style_de("anguille"), sys.modules[__name__]), "Anguille")
