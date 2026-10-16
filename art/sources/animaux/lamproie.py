"""La lamproie en peluche : un long ver gris plomb marbré, sans mâchoires, dressé à demi comme un cobra de rivière, qui
vous présente sa bouche : une ventouse ronde, ourlée de rose, tapissée de petites dents crème en cercles. Une rangée de
sept trous de chaque côté de la tête, un seul œil de chaque côté, et deux nageoires du dos en ondulation basse. Elle
s'accroche à ce qu'elle trouve, et elle vous trouve.

    python lamproie.py        fabrique la fiche art/apercus/animaux/lamproie.png (style du palier : C, velours ras)
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

PLOMB = np.array(M.hexa("#8a929c"))           # la dominante (registre : gris plomb marbré) ; le velours éclaircit un peu
MARBRE = np.array(M.hexa("#586068"))          # le marbrage
VENTRE = np.array(M.hexa("#cfd2d2"))
ROSE = M.hexa("#e68aa0")                      # le bord de la ventouse
DENT = M.hexa("#fbf3dc")
FOND = M.hexa("#7c3a4e")                      # le fond de la gorge
TROU = M.hexa("#2a2c33")

# de la queue à la bouche : couchée en S sur le sable, puis le cou se dresse et la ventouse regarde vers nous
CHEMIN = [(0.34, 0.58, 0.026), (0.20, 0.58, 0.032), (0.04, 0.48, 0.038), (-0.04, 0.32, 0.042), (0.06, 0.16, 0.046),
          (0.22, 0.08, 0.048), (0.28, -0.06, 0.050), (0.16, -0.18, 0.056), (0.10, -0.21, 0.110), (0.08, -0.22, 0.215),
          (0.08, -0.22, 0.320), (0.08, -0.22, 0.430)]            # le cou DROIT, la ventouse vers le haut : de n'importe où on voit les deux yeux sur les côtés


def rayon(f):
    r = O.interp([(0.0, 0.0), (0.02, 0.010), (0.12, 0.024), (0.40, 0.040), (0.80, 0.046), (0.93, 0.044), (0.975, 0.050),
                  (1.0, 0.052)])(f)
    return r * (0.74 + 0.26 * min(max((f - 0.86) / 0.10, 0.0), 1.0))     # plus fine et plus anguilliforme, comme le modèle de référence (vues de reference)


TOURNE = 34                                   # la fiche tourne la bête vers la caméra (34° devant) : on compte les DEUX yeux ; 0 pour le jeu


def construire():
    a = K.Animal("lamproie")
    a.taille = 0.85

    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(PLOMB, (len(ang), 1))
        t[ang > 2.2] = VENTRE
        rng = np.random.default_rng(6)
        u = m.v - m.v.mean(axis=0)
        u /= np.maximum(np.linalg.norm(u, axis=1, keepdims=True), 1e-9)
        g = rng.normal(size=(120, 3))
        g /= np.linalg.norm(g, axis=1, keepdims=True)
        proche = (u @ g.T > math.cos(0.075)).any(axis=1) & (ang < 2.0)
        t[proche] = MARBRE
        return t
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=36, flanc=(1.0, 0.0, 0.0))

    # ----- la ventouse : une couronne rose, le fond sombre, trois cercles de dents crème -----
    c0, av0, nq0 = (Vector(q) for q in fil.cadre(L))
    mat = A.cadre(c0 - av0 * 0.012, av0, nq0)
    a.piece("couronne", O.couche(A.tore(0.046, 0.0105, 30, 8), mat), ROSE, poil=False)
    fond = A.boule(1.0, 24, 12).etire(0.040, 0.040, 0.010)
    a.piece("gorge", O.couche(fond, A.cadre(c0 - av0 * 0.001, av0, nq0)), FOND, poil=False)
    for rang, (r, n, long) in enumerate(((0.040, 14, 0.014), (0.028, 10, 0.012), (0.014, 6, 0.010))):
        dents = None
        for k in range(n):
            th = math.tau * (k + 0.5 * rang) / n
            d = Vector((math.cos(th), math.sin(th), 0.0))
            m = O.couche(O.pointe(long, 0.0062, 8), A.cadre(Vector((r * math.cos(th), r * math.sin(th), 0.002)),
                                                            Vector((-math.cos(th) * 0.35, -math.sin(th) * 0.35, 1.0)), (0, 1, 0)))
            dents = m if dents is None else dents + m
        a.piece("dents_%d" % rang, O.couche(dents, A.cadre(c0 - av0 * 0.003, av0, nq0)), DENT, poil=False)

    # ----- l'œil de chaque côté, et la rangée de sept trous branchiaux -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, direction = Vector((0.08, -0.22, 0.385)), Vector((c * 0.78, -0.62, 0.18))        # sur l'AVANT du cou, côté caméra : les deux yeux se voient
        pos, n = a.surface("corps", centre, direction)
        a.oeil("oeil_" + nom, pos + n * 0.003, n, 0.0280)                  # un vrai œil, gros, sur le dessus de la tête
        trous = None
        for k in range(7):
            cc, dd = fil.vise((0.925 - 0.026 * k) * L, 0.0, -c * 1.0, 0.18)
            q = a.trace("corps", cc, [dd], 0.001)
            if q:
                m = A.boule(1.0, 12, 6).etire(0.007, 0.007, 0.0025)
                m = O.couche(m, A.cadre(q[0], dd))
                trous = m if trous is None else trous + m
        if trous is not None:
            a.piece("branchies_" + nom, trous, TROU, poil=False)

    # ----- les deux nageoires du dos : de basses ondulations sur le tiers arrière -----
    for k, (f0, f1) in enumerate(((0.52, 0.64), (0.67, 0.78))):
        pts = []
        for f in np.linspace(f0, f1, 14):
            c, av, nq = (Vector(q) for q in fil.cadre(f * L))
            pts.append(tuple(c + nq * (rayon(f) + 0.004)))
        rub = A.tube(A.courbe(pts, 2), lambda t: 0.014 * math.sin(math.pi * t) ** 0.7 + 0.003, 8)
        a.piece("dorsale_%d" % k, O.teinte(rub, MARBRE * 1.1), None, poil=False)
    a.tete = c0 + av0 * 0.03
    if TOURNE:
        O.tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "serpent")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lamproie", styles.style_de("lamproie"), sys.modules[__name__]), "Lamproie")
