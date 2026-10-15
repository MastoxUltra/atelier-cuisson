"""L'autruche en peluche de velours ras (2e dessin, d'après photos) : un gros corps ovoïde d'un noir velouté, les ailes et
la queue en panaches de plumes BLANCHES bouclées, un très long cou rosé presque nu en S qui porte une toute petite tête
au grand œil à longs cils et au bec plat et large, et deux très longues jambes roses et épaisses, à deux gros orteils,
plantées bien droites sous le corps. Elle se tient haut, droite, le cou dressé, la tête tournée vers nous : la plus
grande des oiseaux, et la plus perplexe.

    python autruche.py        fabrique la fiche art/apercus/animaux/autruche.png (velours ras, palier 3)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K


def propres(points, eps=2e-4):
    """Les points d'un tracé sans doublons consécutifs (deux points identiques à la suite déforment un tube en NaN)."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie


ENCRE = np.array(M.hexa("#4a4650"))           # la dominante : noir d'encre velouté (le poil le fonce : on le prend plus clair)
BLANC = np.array(M.hexa("#fffaf2"))           # les plumes des ailes et de la queue
ROSE = np.array(M.hexa("#e8a8a0"))            # le cou, les jambes
BEC = M.hexa("#e8c8b8")
OEIL = M.hexa("#7a4a30")
CHARBON = M.hexa("#3a3236")
LACET = 30.0


def construire():
    a = K.Animal("autruche")
    a.taille = 2.30

    # ----- le corps : un gros œuf noir, le dos un peu plus haut derrière, posé haut sur les jambes -----
    def oeuf(v):
        v = K.bosse(v, (0, -0.75, 0.30), 0.14, 0.40)
        return v * [0.230, 0.320, 0.250]
    corps = A.boule(1.0, 56, 28)
    corps.teinte = np.tile(ENCRE, (len(corps.v), 1))
    a.piece("corps", corps.sculpte(oeuf), None, pos=(0.0, 0.060, 0.740), rot=(8, 0, 0))

    # ----- les plumes : deux grandes ailes blanches en éventail sur les flancs, qui retombent ; la queue en panache dressé -----
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 36, 18)
        aile.teinte = np.tile(BLANC, (len(aile.v), 1))
        a.piece("aile_" + nom, aile.etire(0.080, 0.230, 0.190), None, pos=(c * 0.230, 0.090, 0.780), rot=(10, 0, c * 14))
        a.piece("aile_bas_" + nom, A.boule(1.0, 28, 14).etire(0.060, 0.180, 0.110), tuple(BLANC), pos=(c * 0.250, 0.140, 0.640), rot=(18, 0, c * 18))
    for k, (dx, dy, dz, rx) in enumerate(((0.0, 0.350, 0.880, -34), (0.090, 0.340, 0.840, -22), (-0.090, 0.340, 0.840, -22))):
        a.piece("queue_%d" % k, A.boule(1.0, 28, 14).etire(0.070, 0.050, 0.180), tuple(BLANC), pos=(dx, dy, dz), rot=(rx, 0, dx * 90))

    # ----- le cou : très long, rosé, en S doux, mince ; la tête minuscule, le bec plat et large, le grand œil à cils -----
    cou = A.tube(A.courbe(propres([(0.0, -0.180, 0.900), (0.0, -0.290, 1.120), (0.0, -0.200, 1.360), (0.0, -0.250, 1.600)]), 6),
                 lambda t: 0.060 - 0.026 * t, 20)
    cou.teinte = np.tile(ROSE, (len(cou.v), 1))
    a.piece("cou", cou, None, poil=False)
    H = A.repere(Vector((0.0, -0.290, 1.655)), (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 36, 18)
    tete.teinte = np.tile(ROSE, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.038, 0.062, 0.038), None, mat=H, poil=False)
    a.tete = H @ Vector((0, -0.090, 0.0))
    a.piece("bec", A.boule(1.0, 28, 14).etire(0.036, 0.062, 0.016), BEC, mat=H @ A.repere((0, -0.088, -0.006)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.86, -0.30, 0.30))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.30, OEIL, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0165)
        a.piece("cils_" + nom, K.paupiere(0.022, 0.26), tuple(CHARBON), mat=A.cadre(p + n * 0.004, n, H3 @ Vector((0, 0, 1))), poil=False)

    # ----- les jambes : très longues, épaisses, roses, le genou en arrière ; deux gros orteils ; bien droites sous le corps -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.100, 0.060, 0.600), (c * 0.108, 0.040, 0.420), (c * 0.108, 0.075, 0.220), (c * 0.108, 0.060, 0.040)]
        m = A.tube(A.courbe(propres(ch), 6), lambda t: 0.050 - 0.020 * t, 16)
        m.teinte = np.tile(ROSE, (len(m.v), 1))
        a.piece("jambe_" + nom, m, None, poil=False)
        a.piece("orteil_" + nom, A.boule(1.0, 20, 10).etire(0.034, 0.090, 0.028), tuple(ROSE), pos=(c * 0.112, -0.010, 0.030))
        a.piece("petit_orteil_" + nom, A.boule(1.0, 16, 8).etire(0.022, 0.050, 0.022), tuple(ROSE), pos=(c * 0.160, 0.020, 0.024), rot=(0, 0, c * -18))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("autruche", styles.style_de("autruche"), sys.modules[__name__]), "Autruche")
