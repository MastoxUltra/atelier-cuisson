"""La pie en peluche, troisième dessin : un fuseau noir et blanc, tendu du bec au bout de la queue. La poitrine en avant à
trente degrés, la tête fondue dans les épaules, un bec fort, noir, un peu crochu ; le dos et la poitrine noirs, le ventre
et l'épaulette en lame blancs, les ailes à reflets bleu-vert. Et la traîne : trois plumes étagées, bleu nuit virant au
turquoise, plus longues que le corps, qui se relèvent à vingt degrés derrière elle pour claquer en silhouette. Elle
marche : une patte levée, le bec haut, l'œil rond qui a déjà repéré ce qui brille chez vous.

    python pie.py        fabrique la fiche art/apercus/animaux/pie.png (style du palier : A, cousu main)
    (les deux premiers dessins, refusés le 15/10 : « une boule à tête ronde », « le corps toujours une boule »)
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

NOIR = np.array(M.hexa("#25252c"))            # la dominante (registre : noir et blanc tranchés)
BLANC = np.array(M.hexa("#fbfaf4"))
BLEU = np.array(M.hexa("#26468f"))            # la traîne : bleu nuit
TURQ = np.array(M.hexa("#2f8a98"))            # son bout, turquoise (jamais un vert franc)
VIOLET = np.array(M.hexa("#5a3a7a"))
REFLET = np.array(M.hexa("#2e5a86"))          # le reflet bleu-vert des ailes
BEC = M.hexa("#1a181c")
PATTE = np.array(M.hexa("#2a282e"))
LONG = 0.58                                   # la longueur du fuseau du corps
T = A.repere((0.0, 0.080, 0.140), (30, 0, 0)) # la poitrine en avant à 30°


def construire():
    a = K.Animal("pie")
    a.taille = 1.00                            # la traîne dépasse le corps : c'est ce qui fait la taille

    # ----- le corps : un fuseau long, plus gros vers l'avant (les épaules), la poitrine noire, les flancs et le ventre blancs -----
    pc = A.profil([(0, 0.0), (0.050, 0.012), (0.098, 0.090), (0.126, 0.200), (0.138, 0.320), (0.128, 0.420), (0.100, 0.500), (0.060, 0.550), (0, 0.575)], 6)
    corps = A.tour(pc, 52)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    z = corps.v[:, 2]
    t = np.tile(BLANC, (len(z), 1))
    t[(ang < 1.10) & (z > 0.03)] = NOIR                       # le dos
    t[(z > 0.40) & (ang > 1.10)] = NOIR                       # le bavoir : la poitrine, jusqu'au cou
    corps.teinte = t

    def forme(v):
        s = v.copy()
        s[:, 1] -= 0.030 * np.exp(-((v[:, 2] - 0.40) / 0.10) ** 2) * (v[:, 1] < 0)        # la poitrine en proue
        s[:, 1] += 0.025 * np.exp(-((v[:, 2] - 0.46) / 0.10) ** 2) * (v[:, 1] > 0)        # le dos monte aux épaules
        return s
    a.piece("corps", corps.sculpte(forme), None, mat=T)

    # ----- la tête fondue dans les épaules : une boule noire posée contre le haut du fuseau ; un bec fort et noir -----
    H = Vector(T @ Vector((0.0, -0.075, 0.590)))
    tete = A.boule(1.0, 44, 22)
    tete.teinte = np.tile(NOIR, (len(tete.v), 1))
    RT = A.repere(H, (-4, 0, 20))
    a.piece("tete", tete.etire(0.082, 0.092, 0.078), None, mat=RT)
    bec = A.tour(A.profil([(0.040, 0), (0.037, 0.036), (0.027, 0.080), (0.013, 0.115), (0, 0.136)], 4), 24).etire(0.92, 0.82, 1.0)
    bec = bec.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] - 0.014 * (v[:, 2] / 0.136) ** 2.4, v[:, 2]], axis=1))
    a.piece("bec", bec, BEC, mat=RT @ A.cadre(Vector((0.0, -0.075, -0.006)), (0.0, -1.0, -0.05), (0, 1, 0)), poil=False)
    O.paire_yeux(a, "tete", H, (0.82, -0.52, 0.22), 0.0155, couleur_lourde=tuple(NOIR), coupe=0.15, decolle=0.002)
    a.tete = H + Vector((0.0, -0.13, 0.0))

    # ----- les ailes repliées le long du corps, noires à reflets, l'épaulette blanche en lame sur le haut ; les bouts croisés -----
    for nom, c in (("G", 1), ("D", -1)):
        al = A.boule(1.0, 36, 18).etire(0.046, 0.105, 0.300)
        zf = al.v[:, 2] / 0.300
        t = np.tile(NOIR, (len(zf), 1))
        t[zf < -0.15] = REFLET * 0.9 + NOIR * 0.1
        t[zf < -0.75] = NOIR
        al.teinte = t
        a.piece("aile_" + nom, al, None, mat=T @ A.repere((c * 0.122, 0.060, 0.300), (0, 0, c * 5)))
        ep = A.boule(1.0, 24, 12).etire(0.015, 0.034, 0.130)
        a.piece("epaule_" + nom, O.teinte(ep, BLANC), None, mat=T @ A.repere((c * 0.160, 0.085, 0.380), (0, 0, c * 5)), poil=False)

    # ----- la traîne : trois plumes étagées qui sortent du croupion, rasent un peu, puis se relèvent à 20° derrière elle -----
    base = Vector(T @ Vector((0.0, 0.030, 0.030)))
    for k, (dx, long_) in enumerate(((0.0, 1.00), (-0.050, 0.80), (0.050, 0.80))):
        pts = [base, base + Vector((dx * 0.3, 0.20 * long_, -0.045)), base + Vector((dx * 0.7, 0.45 * long_, -0.040)),
               base + Vector((dx * 1.2, 0.75 * long_, 0.030)), base + Vector((dx * 1.6, 1.02 * long_, 0.165))]
        ray = lambda t_: 0.044 * math.sin(math.pi * min(t_ * 1.02 + 0.05, 1.0)) ** 0.55 + 0.007
        paliers = [(0.34, BLEU), (0.64, TURQ * 0.55 + BLEU * 0.45), (0.90, TURQ), (1.0, VIOLET)]
        plume = K.tube_peint(A.courbe([tuple(p) for p in pts], 6), ray, paliers, 14)
        a.piece("traine_%d" % k, plume, None, poil=False)

    # ----- les pattes : sortent du ventre à la verticale du centre de gravité ; la gauche levée en plein pas -----
    for nom, c, plantee in (("D", -1, True), ("G", 1, False)):
        if plantee:
            pts = [(c * 0.060, -0.030, 0.290), (c * 0.064, -0.020, 0.170), (c * 0.066, -0.060, 0.016)]
            fin = Vector((c * 0.066, -0.060, 0.0))
        else:
            pts = [(c * 0.060, -0.020, 0.290), (c * 0.070, -0.090, 0.215), (c * 0.068, -0.150, 0.165)]
            fin = Vector((c * 0.068, -0.150, 0.150))
        a.piece("patte_" + nom, O.teinte(O.tube_r(pts, [0.024, 0.017, 0.013], 10), PATTE), None, poil=False)
        doigts = None
        for ang_ in (-34, 0, 34):
            r_ = math.radians(ang_)
            d = Vector((math.sin(r_), -math.cos(r_), 0.0))
            tub = O.tube_r([(0.0, 0.0, 0.012), tuple(d * 0.040 + Vector((0, 0, 0.008))), tuple(d * 0.072 + Vector((0, 0, 0.004)))],
                           [0.0095, 0.0085, 0.0065], 8).pose(fin + Vector((0.0, 0.0, 0.004)))
            doigts = tub if doigts is None else doigts + tub
        a.piece("doigts_" + nom, O.teinte(doigts, PATTE), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules[__name__], "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pie", styles.style_de("pie"), sys.modules[__name__]), "Pie")
