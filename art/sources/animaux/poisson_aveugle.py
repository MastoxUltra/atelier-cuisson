"""Le poisson aveugle des grottes en peluche : le fuseau nacré, d'un blanc bleuté froid, sans œil, juste deux creux lisses
là où il y en avait, les ouïes d'un rose vif seul reste de couleur, une ligne de petits points brodés tout le long du
flanc : c'est avec elle qu'il voit. Couché sur le ventre, les nageoires pâles étalées, il sent venir le monde à travers l'eau
comme d'autres à travers la porte.

    python poisson_aveugle.py        fabrique la fiche art/apercus/animaux/poisson_aveugle.png (style du palier : C, velours ras)
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
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

NACRE = np.array(M.hexa("#d8e2ee"))           # la dominante (registre : nacre froide bleutée), un cran plus clair (style C)
DOS = np.array(M.hexa("#bccadb"))             # le dos, un peu plus sombre
VENTRE = np.array(M.hexa("#f1f5fa"))          # le ventre
OUIE = np.array(M.hexa("#f2a9b8"))            # l'accent : les ouïes rosées
NAGEOIRE = np.array(M.hexa("#e4ebf4"))        # les nageoires pâles
CREUX = np.array(M.hexa("#b3c1d4"))           # les creux des yeux absents
FIL = M.hexa("#7a8aa0")

# de la tête à la queue, couché sur le ventre, un peu courbé
CHEMIN = [(0.02, -0.40, 0.090), (0.00, -0.28, 0.102), (-0.03, -0.12, 0.100), (-0.02, 0.06, 0.100), (0.03, 0.22, 0.102), (0.09, 0.36, 0.090),
          (0.14, 0.46, 0.084)]


def rayon(f):
    return O.interp([(0.0, 0.0), (0.03, 0.034), (0.10, 0.062), (0.28, 0.084), (0.48, 0.080), (0.70, 0.056), (0.88, 0.034),
                     (0.97, 0.024), (1.0, 0.020)])(f)


def construire():
    a = K.Animal("poisson_aveugle")
    a.taille = 0.70                                # plus gros : il se noyait dans l'herbe (« flou »)

    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        f = m.v[:, 2] / L
        t = np.tile(NACRE, (len(ang), 1))
        t[ang < 0.9] = DOS
        t[ang > 2.3] = VENTRE
        pass                                                                             # (plus de bande rose)
        return t

    def comprime(L):
        def g(v):
            s = v.copy()
            s[:, 0] *= 0.82                                                              # un fuseau un peu plus haut que large
            return s
        return g
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=36, deforme=comprime)

    # ----- les nageoires : la queue en fourche, le dos, le ventre, les pectorales, étalées et pâles -----
    c1, av1, nq1 = (Vector(q) for q in fil.cadre(L))
    caudale = O.nageoire([(0, 0.014), (0.05, 0.055), (0.13, 0.115), (0.09, 0.0), (0.13, -0.115), (0.05, -0.055), (0, -0.014)], 0.020, NAGEOIRE)
    a.piece("caudale", O.couche(caudale, O.plan_vertical(c1 - av1 * 0.02, av1)), None, poil=False)
    dorsale = O.nageoire([(0, 0), (0.04, 0.075), (0.09, 0.090), (0.13, 0.03), (0.15, 0)], 0.020, NAGEOIRE * 0.97)
    cd, ad, nd = (Vector(q) for q in fil.cadre(0.46 * L))
    a.piece("dorsale", O.couche(dorsale, O.plan_dos(cd + nd * rayon(0.46) * 0.90 - Vector((0, 0.05, 0)), nd)), None, poil=False)
    anale = O.nageoire([(0, 0), (0.03, -0.05), (0.08, -0.065), (0.11, -0.015), (0.13, 0)], 0.020, NAGEOIRE * 0.97)
    ca, aa, na = (Vector(q) for q in fil.cadre(0.64 * L))
    a.piece("anale", O.couche(anale, O.plan_dos(ca - na * rayon(0.64) * 0.55 - Vector((0, 0.04, 0)), na)), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        cp, ap, nq = (Vector(q) for q in fil.cadre(0.27 * L))
        p = A.boule(1.0, 20, 10).etire(0.010, 0.074, 0.032)
        p.teinte = np.tile(NAGEOIRE, (len(p.v), 1))
        a.piece("pectorale_" + nom, O.couche(p, A.cadre(cp + Vector((c * rayon(0.27) * 0.78, 0.03, -0.03)), (c * 0.85, 0.50, -0.10), (0, 0, 1))),
                None, poil=False)

    # ----- le visage : pas d'œil, deux creux lisses ; la bouche ; la ligne latérale brodée de chaque côté du flanc -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, direction = fil.vise(0.100 * L, 0.45, c * 0.60, 0.35)
        pos, n = a.surface("corps", centre, direction)
        a.oeil("oeil_" + nom, pos + n * 0.003, n, 0.0280)               # deux yeux ronds et ouverts, même pour un poisson aveugle (règle d'l'auteur)
        pts = []
        for u_ in np.linspace(0.0, 1.0, 14):
            cc, dd = fil.vise((0.27 + 0.58 * u_) * L, 0.0, c * 1.0, 0.18 - 0.10 * u_)
            q = a.trace("corps", cc, [dd], 0.002)
            if q:
                pts.append(q[0])
        if len(pts) > 1:
            a.broderie("ligne_" + nom, A.courbe(pts, 3), 0.0020, tuple(FIL))
    pts = []
    for u_ in np.linspace(0.0, 1.0, 7):
        cc, dd = fil.vise((0.012 + 0.070 * u_) * L, 0.0, 1.0, -0.34 + 0.16 * u_)
        q = a.trace("corps", cc, [dd], 0.002)
        if q:
            pts.append(q[0])
    if len(pts) > 1:
        a.broderie("bouche", A.courbe(pts, 4), 0.0023, FIL)
    a.tete = Vector(fil.cadre(0.07 * L)[0]) + Vector((0.0, -0.05, 0.02))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("poisson_aveugle", styles.style_de("poisson_aveugle"), sys.modules[__name__]), "Poisson aveugle")
