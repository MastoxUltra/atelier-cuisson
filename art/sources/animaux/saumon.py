"""Le saumon en peluche : le pèlerin de la rivière, rouge carmin de frai, la tête ardoise, la mâchoire en crochet crème
(le bec du mâle en fin de remontée). Il grimpe le courant d'un bond tendu : le corps en arc très haut, la queue claquée
derrière lui, l'air d'avoir fait trois mille kilomètres pour rien, et d'être prêt à en refaire autant.

    python saumon.py        fabrique la fiche art/apercus/animaux/saumon.png (style du palier : A, cousu main)
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

CARMIN = np.array(M.hexa("#c42a42"))          # la dominante (registre : rouge carmin de frai)
ARDOISE = np.array(M.hexa("#5f6879"))         # la tête
DESSOUS = np.array(M.hexa("#e58a86"))         # le ventre, plus pâle
NAGEOIRE = np.array(M.hexa("#9d1f33"))
CREME = np.array(M.hexa("#f3e6cc"))
FIL = M.hexa("#3a1018")

CHEMIN = [(0.0, -0.46, 0.52), (0.0, -0.34, 0.40), (0.0, -0.14, 0.32), (0.0, 0.10, 0.23), (0.0, 0.36, 0.22), (0.0, 0.58, 0.32),
          (0.0, 0.72, 0.48), (0.0, 0.76, 0.62)]


def rayon(f):
    return O.interp([(0.0, 0.0), (0.03, 0.036), (0.10, 0.074), (0.30, 0.118), (0.52, 0.124), (0.72, 0.092), (0.84, 0.066),
                     (0.91, 0.056), (0.955, 0.044), (0.985, 0.028), (0.997, 0.012), (1.0, 0.0)])(f)      # la tête s'effile en museau, plus un tube coupé


TOURNE = 25                                   # la fiche tourne la bête vers la caméra (25° devant) : on compte les DEUX yeux ; 0 pour le jeu


def construire():
    a = K.Animal("saumon")
    a.taille = 0.95

    def peint(m, L):
        f = m.v[:, 2] / L
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(CARMIN, (len(f), 1))
        t[ang > 2.20] = DESSOUS
        t[f < 0.20] = ARDOISE                                       # la tête
        t[(f >= 0.20) & (f < 0.26)] = ARDOISE * (1 - (f[(f >= 0.20) & (f < 0.26)] - 0.20)[:, None] / 0.06) + CARMIN * ((f[(f >= 0.20) & (f < 0.26)] - 0.20)[:, None] / 0.06)
        return t
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=36)

    # ----- le crochet : une mâchoire inférieure qui se recourbe vers le haut, crème ; une petite bosse au front -----
    c0, av0, nq0 = (Vector(q) for q in fil.cadre(0.012 * L))
    kype = A.tour(A.profil([(0.030, 0), (0.022, 0.030), (0.012, 0.062), (0.004, 0.082), (0, 0.090)], 3), 14).sculpte(
        lambda v: np.stack([v[:, 0], v[:, 1] + 0.55 * v[:, 2] ** 1.4 * 3.0, v[:, 2]], axis=1))
    # (plus de crochet : de face il se lisait comme un anneau posé sur la tête)

    # ----- les nageoires -----
    c1, av1, nq1 = (Vector(q) for q in fil.cadre(L))
    caudale = O.nageoire([(0, 0.020), (0.07, 0.10), (0.20, 0.20), (0.15, 0.0), (0.20, -0.20), (0.07, -0.10), (0, -0.020)], 0.034, NAGEOIRE)
    a.piece("caudale", O.couche(caudale, O.plan_vertical(c1 - av1 * 0.02, av1)), None, poil=False)
    dorsale = O.nageoire([(0, 0), (0.05, 0.14), (0.12, 0.17), (0.18, 0.06), (0.21, 0)], 0.034, NAGEOIRE)
    cd, ad, nd = (Vector(q) for q in fil.cadre(0.42 * L))
    a.piece("dorsale", O.couche(dorsale, O.plan_dos(cd + nd * rayon(0.42) * 0.9 - Vector((0, 0.05, 0)), nd)), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        cp, ap, nq = (Vector(q) for q in fil.cadre(0.26 * L))
        p = A.boule(1.0, 20, 10).etire(0.011, 0.080, 0.034)
        p.teinte = np.tile(NAGEOIRE, (len(p.v), 1))
        a.piece("pectorale_" + nom, O.couche(p, A.cadre(cp + Vector((c * rayon(0.26) * 0.95, 0.03, -0.03)), (c * 0.7, 0.4, -0.5), (0, 0, 1))),
                None, poil=False)

    # ----- le visage : l'œil rond, la bouche tendue ; il serre les dents -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, direction = fil.vise(0.090 * L, 0.50, -c * 0.62, 0.72)
        pos, n = a.surface("corps", centre, direction)
        a.oeil("oeil_" + nom, pos + n * 0.003, n, 0.0380)
        # (plus de paupière lourde : l'anneau posé sur l'œil ; l'œil est nu, rond et ouvert)
    pts = []
    for u_ in np.linspace(0.0, 1.0, 7):
        cc, dd = fil.vise((0.012 + 0.085 * u_) * L, 0.0, 1.0, -0.34 + 0.12 * u_)
        q = a.trace("corps", cc, [dd], 0.002)
        if q:
            pts.append(q[0])
    if len(pts) > 1:
        a.broderie("bouche", A.courbe(pts, 4), 0.0026, FIL)
    a.tete = Vector(fil.cadre(0.07 * L)[0]) + Vector((0.0, -0.05, 0.03))
    if TOURNE:
        O.tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("saumon", styles.style_de("saumon"), sys.modules[__name__]), "Saumon")
