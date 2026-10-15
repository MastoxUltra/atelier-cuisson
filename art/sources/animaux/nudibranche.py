"""La nudibranche en peluche : la limace de mer la plus flamboyante du récif. Un long corps bleu cobalt, bordé d'une
jupe ondulante plus claire, hérissé sur le dos de petits doigts orange (les cérates) qui lui font une crête comme une
coiffure de fête ; deux cornes annelées sur la tête (les rhinophores), le panache de branchies qui s'ouvre derrière.
Elle est entièrement convaincue d'être la plus belle de la mer, et elle n'a pas tort.

    python nudibranche.py        fabrique la fiche art/apercus/animaux/nudibranche.png (style du palier : A, cousu main)
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

COBALT = M.hexa("#2f55d6")                    # la dominante (registre : bleu cobalt) ; le poil fonce : un cran plus clair
JUPE = np.array(M.hexa("#6f8df0"))            # la jupe du pied
ORANGE = np.array(M.hexa("#ff7a1a"))          # l'accent : les cérates, les cornes, le panache
FIL = M.hexa("#1d2c6b")


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def construire():
    a = K.Animal("nudibranche")
    a.taille = 0.42

    # ----- le corps : un long fuseau en S, couché ; la tête à l'avant (-Y), la queue qui se redresse un peu ; sa jupe autour -----
    prof = A.profil([(0, 0), (0.060, 0.030), (0.095, 0.120), (0.108, 0.240), (0.100, 0.380), (0.070, 0.500), (0.038, 0.580), (0, 0.620)], 5)
    corps = A.tour(prof, 44)

    def serpente(v):                                    # le long corps ondule : le fuseau est tourné sur Z, on le couche sur Y
        s = np.stack([v[:, 0] * 1.05 + 0.040 * np.sin(v[:, 2] * 7.0), v[:, 2] - 0.31, v[:, 1] * 0.62 + 0.078], axis=1)
        return s
    a.piece("corps", corps.sculpte(serpente), COBALT)

    def jupe_(v):
        s = v.copy()
        s[:, 2] = 0.018 * np.sin(v[:, 1] * 38) + 0.5 * v[:, 2]
        return s
    j = A.boule(1.0, 56, 14).etire(0.175, 0.315, 0.026)
    j.teinte = np.tile(JUPE, (len(j.v), 1))
    j = j.sculpte(lambda v: np.stack([v[:, 0] + 0.040 * np.sin(v[:, 1] * 7.0 / 0.315 * 0.31 * 3.2), v[:, 1] + 0.0, v[:, 2] + 0.018 * np.sin(v[:, 1] * 32)], axis=1))
    a.piece("jupe", j, None, pos=(0.0, 0.0, 0.030), poil=False)

    # ----- les cérates : de petits doigts orange en deux rangs sur le dos, de plus en plus courts vers la queue -----
    doigts = None
    for rang in (-1, 1):
        for k in range(8):
            y = -0.18 + 0.075 * k
            x = rang * (0.045 + 0.010 * math.sin(k))
            long = 0.090 - 0.0045 * k
            m = A.tour(A.profil([(0.016, 0), (0.019, 0.25 * long), (0.014, 0.65 * long), (0.006, 0.92 * long), (0, long)], 4), 12)
            t = np.clip(m.v[:, 2] / long, 0, 1)[:, None]
            m.teinte = np.array(COBALT) * 0.0 + ORANGE * (0.55 + 0.45 * t) + JUPE * (0.45 - 0.45 * t) * 0.0
            d = Vector((rang * 0.55, -0.20, 1.0)).normalized()
            m = couche(m, A.cadre(Vector((x, y + 0.002, 0.146 - 0.010 * abs(k - 3))), d, (0, 1, 0)))
            doigts = m if doigts is None else doigts + m
    a.piece("cerates", doigts, None, poil=False)

    # ----- les rhinophores : deux cornes annelées, orange, plantées devant ; le panache de branchies, derrière -----
    for nom, c in (("G", 1), ("D", -1)):
        corne = A.tube(A.courbe([(c * 0.034, -0.275, 0.120), (c * 0.050, -0.292, 0.176), (c * 0.048, -0.296, 0.232)], 5),
                       lambda t: 0.017 - 0.008 * t, 12)
        corne.teinte = np.tile(ORANGE, (len(corne.v), 1))
        a.piece("corne_" + nom, corne, None, poil=False)
        for k, tt in enumerate((0.25, 0.45, 0.65, 0.85)):
            p = Vector((c * (0.034 + 0.016 * tt), -0.275 - 0.021 * tt, 0.120 + 0.112 * tt))
            ring = A.tore(0.0145 - 0.006 * tt, 0.0045, 20, 6)
            ring.teinte = np.tile(ORANGE * 0.8, (len(ring.v), 1))
            a.piece("anneau_%s%d" % (nom, k), ring, None, pos=tuple(p), poil=False)
    for k in range(7):
        ang = math.tau * k / 7
        base = Vector((0.0, 0.215, 0.098))
        d = Vector((0.55 * math.cos(ang), 0.20 + 0.15 * math.sin(ang), 1.0)).normalized()
        plume = A.tour(A.profil([(0.014, 0), (0.017, 0.030), (0.010, 0.065), (0.003, 0.088), (0, 0.098)], 4), 10)
        plume.teinte = np.tile(ORANGE * (0.92 + 0.08 * math.cos(ang)), (len(plume.v), 1))
        a.piece("branchie_%d" % k, couche(plume, A.cadre(base + Vector((0.030 * math.cos(ang), 0.030 * math.sin(ang), 0)), d, (0, 1, 0))), None, poil=False)

    # ----- le visage : deux petits boutons sur la tête, un sourire fier -----
    centre = Vector((0.0, -0.20, 0.084))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("corps", centre, Vector((c * 0.40, -0.80, 0.36)))
        a.bouton("oeil_" + nom, pos + n * 0.001, n, 0.0185)
    sourire = [Vector((0.34 * u_, -0.82, -0.05 + 0.12 * u_ * u_)) for u_ in np.linspace(-1, 1, 9)]
    a.broderie("sourire", A.courbe(a.trace("corps", centre, sourire, 0.002), 4), 0.0022, FIL)
    a.tete = Vector((0.0, -0.30, 0.100))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "mou")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("nudibranche", styles.style_de("nudibranche"), sys.modules[__name__]), "Nudibranche")
