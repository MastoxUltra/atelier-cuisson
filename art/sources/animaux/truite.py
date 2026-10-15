"""La truite en peluche : le bijou de la rivière, argent rosé, avec une large bande rose le long du flanc et des petits
points noirs et rouges semés sur le dos. Elle bondit : le corps en arc, la queue en fourche qui part en l'air, une
nageoire du dos dressée comme une voile, l'œil rond sous le nez retroussé. Une athlète, et elle le sait.

    python truite.py        fabrique la fiche art/apercus/animaux/truite.png (style du palier : A, cousu main)
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

DOS = np.array(M.hexa("#9aa09a"))             # le dos gris argent
ARGENT = np.array(M.hexa("#e6b9b1"))          # la dominante (registre : argent rosé)
BANDE = np.array(M.hexa("#ec7690"))           # la large bande rose du flanc
VENTRE = np.array(M.hexa("#fbf0e4"))
NOIR = np.array(M.hexa("#2a2224"))
ROUGE = np.array(M.hexa("#d8283a"))
NAGEOIRE = np.array(M.hexa("#c99a94"))
FIL = M.hexa("#5a2a30")

CHEMIN = [(0.0, -0.42, 0.30), (0.0, -0.30, 0.25), (0.0, -0.10, 0.20), (0.0, 0.14, 0.19), (0.0, 0.34, 0.22), (0.0, 0.47, 0.27),
          (0.0, 0.52, 0.31)]      # presque droit : plus de banane


def rayon(f):
    return O.interp([(0.0, 0.0), (0.03, 0.030), (0.10, 0.058), (0.30, 0.100), (0.50, 0.108), (0.70, 0.082), (0.88, 0.046),
                     (0.96, 0.040), (0.985, 0.030), (0.997, 0.015), (1.0, 0.0)])(f)


def construire():
    a = K.Animal("truite")
    a.taille = 0.60

    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))              # 0 : le dos ; pi : le ventre
        t = np.tile(ARGENT, (len(ang), 1))
        t[ang < 0.85] = DOS
        t[(ang > 1.20) & (ang < 1.85)] = BANDE
        t[ang > 2.30] = VENTRE
        rng = np.random.default_rng(3)
        u = (m.v - m.v.mean(axis=0))
        u /= np.maximum(np.linalg.norm(u, axis=1, keepdims=True), 1e-9)
        for couleur, n, graine in ((NOIR, 60, 1), (ROUGE, 24, 2)):
            g = rng.normal(size=(n, 3))
            g /= np.linalg.norm(g, axis=1, keepdims=True)
            proche = (u @ g.T > math.cos(0.085)).any(axis=1) & (ang < 1.9)
            t[proche] = couleur
        return t
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=36)

    # ----- les nageoires : la queue en fourche dressée au bout du fil, la voile du dos, deux pectorales, le ventre -----
    c1, av1, nq1 = (Vector(q) for q in fil.cadre(L))
    caudale = O.nageoire([(0, 0.016), (0.06, 0.08), (0.17, 0.17), (0.12, 0.0), (0.17, -0.17), (0.06, -0.08), (0, -0.016)], 0.030, NAGEOIRE)
    a.piece("caudale", O.couche(caudale, O.plan_vertical(c1 - av1 * 0.02, av1)), None, poil=False)
    dorsale = O.nageoire([(0, 0), (0.05, 0.13), (0.11, 0.16), (0.16, 0.05), (0.19, 0)], 0.030, NAGEOIRE * 0.93)
    cd, ad, nd = (Vector(q) for q in fil.cadre(0.42 * L))
    a.piece("dorsale", O.couche(dorsale, O.plan_dos(cd + nd * rayon(0.42) * 0.90 - Vector((0, 0.05, 0)), nd)), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        cp, ap, nq = (Vector(q) for q in fil.cadre(0.27 * L))
        p = A.boule(1.0, 20, 10).etire(0.010, 0.070, 0.030)
        p.teinte = np.tile(NAGEOIRE, (len(p.v), 1))
        a.piece("pectorale_" + nom, O.couche(p, A.cadre(cp + Vector((c * rayon(0.27) * 0.95, 0.03, -0.02)), (c * 0.7, 0.4, -0.5), (0, 0, 1))),
                None, poil=False)

    # ----- le visage : un gros bouton en haut du nez, la bouche en coin retroussée -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, direction = fil.vise(0.095 * L, 0.35, -c * 0.95, 0.18)
        pos, n = a.surface("corps", centre, direction)
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0270)
    pts = []
    for u_ in np.linspace(0.0, 1.0, 7):
        cc, dd = fil.vise((0.015 + 0.075 * u_) * L, 0.0, 1.0, -0.30 + 0.20 * u_)
        q = a.trace("corps", cc, [dd], 0.002)
        if q:
            pts.append(q[0])
    if len(pts) > 1:
        a.broderie("bouche", A.courbe(pts, 4), 0.0024, FIL)
    a.tete = Vector(fil.cadre(0.07 * L)[0]) + Vector((0.0, -0.05, 0.03))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("truite", styles.style_de("truite"), sys.modules[__name__]), "Truite")
