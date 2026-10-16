"""Le poisson-vipère en peluche : le noir vert-de-gris des plateaux, un long fuseau mince à la tête énorme, la gueule ouverte
sur des crocs d'ivoire démesurés, courbes, plus longs que la tête n'est haute, qui ne ferment plus la bouche. Le premier rayon
de sa dorsale est un fouet qui passe au-dessus de sa tête et porte au bout une petite ampoule d'appât. Il avance la bouche
ouverte, parce qu'il ne peut pas faire autrement, avec l'air de quelqu'un qui s'excuse.

    python poisson_vipere.py        fabrique la fiche art/apercus/animaux/poisson_vipere.png (style du palier : voir styles.py)
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

VERT = np.array(M.hexa("#35463f"))            # la dominante (registre : vert-de-gris très sombre, presque noir, jamais vert franc)
VENTRE = np.array(M.hexa("#4a5e55"))          # le dessous
CROC = np.array(M.hexa("#f1e9d2"))            # l'accent : les crocs ivoire
LUEUR = np.array(M.hexa("#9fe8d4"))           # l'ampoule d'appât, les photophores
INTERIEUR = np.array(M.hexa("#7a3b3b"))       # le dedans de la bouche
FIL = M.hexa("#18201c")

CHEMIN = [(0.02, 0.62, 0.100), (0.00, 0.46, 0.110), (-0.03, 0.28, 0.116), (-0.02, 0.10, 0.120), (0.00, -0.06, 0.122), (0.00, -0.20, 0.124),
          (0.00, -0.30, 0.128)]
SX, SY = 0.90, 1.0


def rayon(f):
    return O.interp([(0.0, 0.0), (0.02, 0.008), (0.10, 0.014), (0.30, 0.030), (0.55, 0.046), (0.76, 0.052), (0.88, 0.074),
                     (0.96, 0.066), (0.99, 0.036), (1.0, 0.0)])(f)


TOURNE = 25                                   # la fiche tourne la bête vers la caméra (25° devant) : on compte les DEUX yeux ; 0 pour le jeu


def construire():
    a = K.Animal("poisson_vipere")
    a.taille = 1.00                                # plus gros : il se noyait dans l'herbe

    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(VERT, (len(ang), 1))
        t[ang > 2.2] = VENTRE
        return t

    def comprime(L):
        def g(v):
            s = v.copy()
            s[:, 0] *= SX
            return s
        return g
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=32, flanc=(1.0, 0.0, 0.0), deforme=comprime)

    # ----- la mâchoire du bas, entrouverte, un dedans sombre ; les crocs d'en haut et d'en bas, démesurés ; la lèvre brodée -----
    ch, avh, nqh = (Vector(q) for q in fil.cadre(0.93 * L))
    bas = A.tour(A.profil([(0.036, 0.0), (0.034, 0.030), (0.026, 0.070), (0.014, 0.104), (0.0, 0.118)], 4), 22).etire(1.0, 0.55, 1.0)
    bas.teinte = np.tile(VENTRE, (len(bas.v), 1))
    R = A.cadre(ch + Vector((0.0, -0.040, -0.058)), Vector((0.0, -1.0, -0.42)), (0, 0, 1))
    a.piece("machoire", O.couche(bas, R), None)
    dedans = A.boule(1.0, 20, 10).etire(0.030, 0.052, 0.012)
    a.piece("dedans", O.teinte(dedans, INTERIEUR), None, pos=tuple(ch + Vector((0.0, -0.090, -0.040))), rot=(-12, 0, 0), poil=False)
    for c in (1, -1):
        for k, (dy, hh, long) in enumerate(((0.000, 0.0, 0.110), (-0.030, 0.0, 0.135), (-0.058, 0.0, 0.095))):
            cr = O.couche(O.teinte(O.pointe(long, 0.0125, 8), CROC),
                          A.cadre(ch + Vector((c * 0.026, -0.040 + dy, -0.030)), Vector((c * 0.10, -0.30, -1.0)), (0, 1, 0)))
            a.piece("croc_haut_%s%d" % ("G" if c > 0 else "D", k), cr, None, poil=False)
        for k, (dy, long) in enumerate(((-0.004, 0.100), (-0.036, 0.125), (-0.066, 0.085))):
            cr = O.couche(O.teinte(O.pointe(long, 0.0115, 8), CROC),
                          A.cadre(ch + Vector((c * 0.024, -0.062 + dy, -0.078)), Vector((c * 0.10, -0.15, 1.0)), (0, 1, 0)))
            a.piece("croc_bas_%s%d" % ("G" if c > 0 else "D", k), cr, None, poil=False)

    # ----- le fouet de la dorsale et son ampoule ; les nageoires -----
    cd, ad, nd = (Vector(q) for q in fil.cadre(0.80 * L))
    fouet = O.tube_r([tuple(cd + nd * rayon(0.80) * 0.9), tuple(cd + nd * 0.10 + Vector((0.0, -0.04, 0.0))),
                      tuple(cd + nd * 0.17 + Vector((0.0, -0.16, 0.0))), tuple(cd + nd * 0.15 + Vector((0.0, -0.27, 0.0)))],
                     [0.006, 0.0045, 0.0035, 0.0030], 8)
    a.piece("fouet", O.teinte(fouet, VERT * 1.15), None, poil=False)
    ampoule = A.boule(1.0, 14, 8).etire(0.016, 0.016, 0.016)
    a.piece("ampoule", O.teinte(ampoule, LUEUR), None, pos=tuple(cd + nd * 0.15 + Vector((0.0, -0.285, 0.0))), poil=False)
    c0, av0, nq0 = (Vector(q) for q in fil.cadre(0.0))
    caudale = O.nageoire([(0, 0.012), (0.05, 0.055), (0.12, 0.100), (0.085, 0.0), (0.12, -0.100), (0.05, -0.055), (0, -0.012)], 0.014, VERT * 1.1)
    a.piece("caudale", O.couche(caudale, O.plan_vertical(c0 + Vector((0.0, -0.004, 0.0)), Vector((0.0, 1.0, 0.0)))), None, poil=False)
    cr_, ar_, nr_ = (Vector(q) for q in fil.cadre(0.30 * L))
    dors = O.nageoire([(0, 0), (0.030, 0.060), (0.080, 0.040), (0.110, 0.0)], 0.012, VERT * 1.1)
    a.piece("dorsale", O.couche(dors, O.plan_dos(cr_ + nr_ * rayon(0.30) * 0.9, nr_)), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        p, n = O.sur_corps(fil, L, rayon, 0.80, 100, c, SX, SY, -0.004)
        pec = A.boule(1.0, 16, 8).etire(0.007, 0.040, 0.018)
        pec.teinte = np.tile(VERT * 1.2, (len(pec.v), 1))
        a.piece("pectorale_" + nom, O.couche(pec, A.cadre(p, Vector((c * 0.8, 0.5, -0.1)), (0, 0, 1))), None, poil=False)

    # ----- l'œil énorme et pâle, un rang de photophores le long du ventre -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = O.sur_corps(fil, L, rayon, 0.925, 70, c, SX, SY, 0.002)
        a.oeil("oeil_" + nom, p, n, 0.046)
        h_ = Vector((0.0, 0.0, 1.0))
        a.piece("lourde_" + nom, K.paupiere(0.046, 0.60), tuple(VERT), mat=A.cadre(p + n * 0.003, n, (h_ - n * n.dot(h_)).normalized()), poil=False)
    pts = []
    for c in (1, -1):
        for k in range(14):
            pts.append(O.sur_corps(fil, L, rayon, 0.18 + 0.052 * k, 130, c, SX, SY, 0.0012))
    a.piece("photophores", O.points_lumineux(pts, 0.0070, LUEUR), None, poil=False)
    a.tete = Vector(fil.cadre(0.97 * L)[0]) + Vector((0.0, -0.10, 0.02))
    if TOURNE:
        O.tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("poisson_vipere", styles.style_de("poisson_vipere"), sys.modules[__name__]), "Poisson-vipère")
