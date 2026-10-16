"""Le poisson-lanterne en peluche : le petit noir bleuté des plateaux de l'abîme, un fuseau de velours sombre aux gros yeux
ronds, la queue en fourche, une rangée de points lumineux bleu ciel le long du ventre et une autre sur le flanc, et un gros
phare sous l'œil. Il vit par bancs de millions et ne sait pas, tout seul, qu'il est la chose la plus lumineuse à
cinq cents mètres à la ronde.

    python poisson_lanterne.py        fabrique la fiche art/apercus/animaux/poisson_lanterne.png (style du palier : voir styles.py)
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

VELOURS = np.array(M.hexa("#2a3552"))         # la dominante (registre : noir velours bleuté), un cran plus clair pour qu'il se lise
VENTRE = np.array(M.hexa("#3d4d74"))          # le dessous
LUEUR = np.array(M.hexa("#9fd8ff"))           # l'accent : les points lumineux bleu ciel
NAGEOIRE = np.array(M.hexa("#34426a"))
FIL = M.hexa("#9fb4d8")

# de la queue à la tête, couché sur le ventre, un peu courbé
CHEMIN = [(0.02, 0.34, 0.052), (0.00, 0.22, 0.060), (-0.02, 0.08, 0.066), (-0.02, -0.06, 0.068), (0.00, -0.18, 0.066), (0.00, -0.28, 0.062)]
SX, SY = 0.84, 1.0


def rayon(f):
    return O.interp([(0.0, 0.0), (0.02, 0.010), (0.12, 0.016), (0.30, 0.034), (0.55, 0.054), (0.75, 0.060), (0.90, 0.054),
                     (0.97, 0.038), (1.0, 0.0)])(f)


TOURNE = 25                                   # la fiche tourne la bête vers la caméra (25° devant) : on compte les DEUX yeux ; 0 pour le jeu


def construire():
    a = K.Animal("poisson_lanterne")
    a.taille = 0.85                                # plus gros : il se noyait dans l'herbe

    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(VELOURS, (len(ang), 1))
        t[ang > 2.2] = VENTRE
        return t

    def comprime(L):
        def g(v):
            s = v.copy()
            s[:, 0] *= SX
            return s
        return g
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=32, flanc=(1.0, 0.0, 0.0), deforme=comprime)

    # ----- les nageoires : la queue en fourche, une petite dorsale, deux pectorales -----
    c0, av0, nq0 = (Vector(q) for q in fil.cadre(0.0))
    caudale = O.nageoire([(0, 0.014), (0.05, 0.060), (0.13, 0.115), (0.09, 0.0), (0.13, -0.115), (0.05, -0.060), (0, -0.014)], 0.018, NAGEOIRE)
    a.piece("caudale", O.couche(caudale, O.plan_vertical(c0 + Vector((0.0, -0.006, 0.0)), Vector((0.0, 1.0, 0.0)))), None, poil=False)
    cd, ad, nd = (Vector(q) for q in fil.cadre(0.46 * L))
    dorsale = O.nageoire([(0, 0), (0.035, 0.055), (0.075, 0.065), (0.105, 0.0)], 0.014, NAGEOIRE * 1.1)
    a.piece("dorsale", O.couche(dorsale, O.plan_dos(cd + nd * rayon(0.46) * 0.92, nd)), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        p, n = O.sur_corps(fil, L, rayon, 0.78, 100, c, SX, SY, -0.004)
        pec = A.boule(1.0, 16, 8).etire(0.008, 0.050, 0.020)
        pec.teinte = np.tile(NAGEOIRE, (len(pec.v), 1))
        a.piece("pectorale_" + nom, O.couche(pec, A.cadre(p, Vector((c * 0.8, 0.5, -0.1)), (0, 0, 1))), None, poil=False)

    # ----- le visage : un gros œil rond, le phare sous l'œil, une bouche large -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = O.sur_corps(fil, L, rayon, 0.915, 78, c, SX, SY, 0.002)
        a.oeil("oeil_" + nom, p, n, 0.040)
        h_ = Vector((0.0, 0.0, 1.0))
        a.piece("lourde_" + nom, K.paupiere(0.040, 0.60), tuple(VELOURS), mat=A.cadre(p + n * 0.003, n, (h_ - n * n.dot(h_)).normalized()), poil=False)
        pp, nn = O.sur_corps(fil, L, rayon, 0.950, 112, c, SX, SY, 0.0015)
        ph = O.couche(O.teinte(A.boule(1.0, 14, 8).etire(0.013, 0.013, 0.006), LUEUR), A.cadre(pp, nn, (0, 0, 1)))
        a.piece("phare_" + nom, ph, None, poil=False)
        pts = []
        for u in np.linspace(0.0, 1.0, 8):
            q, _n = O.sur_corps(fil, L, rayon, 0.995 - 0.085 * u, 125 - 10 * u, c, SX, SY, 0.002)
            pts.append(tuple(q))
        a.broderie("bouche_" + nom, A.courbe(pts, 3), 0.0022, FIL)

    # ----- les photophores : une rangée le long du ventre, une autre sur le flanc, de chaque côté -----
    dots = []
    for c in (1, -1):
        for k in range(10):
            dots.append(O.sur_corps(fil, L, rayon, 0.22 + 0.065 * k, 128, c, SX, SY, 0.0012))
        for k in range(6):
            dots.append(O.sur_corps(fil, L, rayon, 0.36 + 0.09 * k, 92, c, SX, SY, 0.0012))
    a.piece("photophores", O.points_lumineux(dots, 0.0085, LUEUR), None, poil=False)
    a.tete = Vector(fil.cadre(0.95 * L)[0]) + Vector((0.0, -0.05, 0.02))
    if TOURNE:
        O.tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("poisson_lanterne", styles.style_de("poisson_lanterne"), sys.modules[__name__]), "Poisson-lanterne")
