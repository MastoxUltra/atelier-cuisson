"""L'émeu en peluche de velours ras (2e dessin, d'après photos : plus de jupe jusqu'au sol) : un grand oiseau debout, un
gros corps ovoïde recouvert d'un plumage hirsute en mèches courtes qui retombent sur le dos et les flancs (la poitrine
et le dessous plus lisses), un taupe lavande chiné de plus sombre ; un cou fort, long et nu, bleuté, qui porte une tête
moyenne au grand œil d'ambre sous de longs cils et au bec court et sombre ; et surtout de LONGUES jambes grises bien
visibles, aux gros pieds à trois doigts, plantées droites sous lui. Il se tient haut, le cou tendu vers nous.

    python emeu.py        fabrique la fiche art/apercus/animaux/emeu.png (velours ras, palier 3)
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


TAUPE = np.array(M.hexa("#bcaabc"))           # la dominante : taupe lavande (le poil la fonce : on la prend claire)
SOMBRE = np.array(M.hexa("#8a7888"))          # les mèches du dos, la croupe
COU = np.array(M.hexa("#9ec0d8"))             # le cou nu, bleuté
AMBRE = M.hexa("#e8a830")
CHARBON = M.hexa("#3a3036")
PATTE = np.array(M.hexa("#8a7a78"))
BEC = M.hexa("#6a5a5c")
CORPS = Vector((0.0, 0.080, 0.640))
LACET = 20.0


def construire():
    a = K.Animal("emeu")
    a.taille = 1.80

    # ----- le corps : un gros œuf bien posé sur les jambes, le dos arrondi ; le dessous lisse, plus clair -----
    def oeuf(v):
        s = v * [0.230, 0.320, 0.260]
        s[:, 1] += 0.020 * v[:, 2]
        return s
    corps = A.boule(1.0, 56, 28)
    corps.teinte = np.where((corps.v[:, 2] < -0.35)[:, None], tuple(TAUPE * 1.05), tuple(TAUPE))
    a.piece("corps", corps.sculpte(oeuf), None, pos=CORPS, rot=(-6, 0, 0))

    # ----- le plumage hirsute : des touffes de mèches courtes et épaisses, qui retombent du dos et des flancs, le plus
    #       long à la croupe ; elles couvrent le haut, pas le ventre, et s'arrêtent bien au-dessus des jambes -----
    rng = np.random.default_rng(9)
    touffes = None
    for i in range(46):
        z = rng.uniform(-0.15, 0.95)
        t = rng.uniform(0.0, 2 * math.pi)
        r = math.sqrt(max(0.0, 1 - z * z))
        d = np.array([r * math.cos(t), r * math.sin(t), z])
        if d[1] < -0.55 and z < 0.3:
            continue                                                              # pas sur la poitrine, plus lisse
        p = np.array(CORPS) + d * np.array([0.236, 0.326, 0.266])
        long_ = 0.080 + 0.060 * rng.random() + 0.040 * max(0.0, d[1])
        m = A.boule(1.0, 10, 6).etire(0.036, 0.030, long_).pose(tuple(p + np.array([d[0] * 0.01, d[1] * 0.01, -long_ * 0.70])),
                                                                 (12 * d[1], -14 * d[0], 0))
        touffes = m if touffes is None else touffes + m
    a.piece("plumage", touffes, tuple(SOMBRE))

    # ----- le cou : long, fort et nu, bleuté, qui part de la poitrine et se tend vers nous en S doux ; la tête moyenne -----
    fil = K.Fil([(0.0, -0.200, 0.780), (0.0, -0.310, 0.950), (0.0, -0.300, 1.150), (0.0, -0.360, 1.320)], (1, 0, 0))
    L = fil.long
    pc = A.profil([(0, 0), (0.095, 0.03 * L), (0.068, 0.30 * L), (0.056, 0.70 * L), (0.052, 0.95 * L), (0, 1.01 * L)], 6)
    cou = A.tour(pc, 28)
    cou.teinte = np.tile(COU, (len(cou.v), 1))
    a.piece("cou", cou.sculpte(fil.couche), None)
    bout = Vector(fil.cadre(L)[0])
    H = A.repere(bout + Vector((0.0, -0.030, 0.020)), (6, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 36, 18)
    tete.teinte = np.tile(TAUPE * 1.04, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.062, 0.082, 0.060), None, mat=H)
    a.tete = H @ Vector((0, -0.100, -0.010))
    bec = A.tour(A.profil([(0, 0), (0.034, 0.006), (0.030, 0.030), (0.018, 0.055), (0, 0.068)], 5), 24)
    a.piece("bec", bec.etire(1.0, 0.70, 1.0), BEC, mat=A.cadre(H @ Vector((0, -0.070, -0.014)), H3 @ Vector((0, -0.96, -0.20)), (0, 0, 1)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.82, -0.40, 0.18))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.30, AMBRE, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0190)
        a.piece("cils_" + nom, K.paupiere(0.0250, 0.24), CHARBON, mat=A.cadre(p + n * 0.004, n, H3 @ Vector((0, 0, 1))), poil=False)

    # ----- les pattes : très longues, grises, le genou marqué, les gros pieds à trois doigts, plantées droites ; bien visibles -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.100, 0.070, 0.470), (c * 0.108, 0.060, 0.300), (c * 0.108, 0.120, 0.140), (c * 0.108, 0.110, 0.030)]
        m = A.tube(A.courbe(propres(ch), 6), lambda t: 0.050 - 0.020 * t, 14)
        m.teinte = np.tile(PATTE, (len(m.v), 1))
        a.piece("patte_" + nom, m, None, poil=False)
        doigts = None
        for ang in (-28, 0, 28):
            d = A.boule(1.0, 14, 8).etire(0.016, 0.075, 0.014).pose((0, -0.060, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("doigts_" + nom, doigts, tuple(PATTE), pos=(c * 0.108, 0.090, 0.014), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("emeu", styles.style_de("emeu"), sys.modules[__name__]), "Émeu")
