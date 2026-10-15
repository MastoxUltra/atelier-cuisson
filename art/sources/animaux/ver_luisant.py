"""Le ver luisant en peluche : la petite larve ivoire des voûtes, un long boudin à dix anneaux doux, six pattes minuscules
sous la tête, deux perles noires pour yeux, et au bout de la queue, relevée comme une lanterne, une ampoule jaune citron
qui rayonne. Il attend, immobile, accroché au rien, que le noir de la grotte lui amène quelqu'un. C'est de la patience,
avec une lampe.

    python ver_luisant.py        fabrique la fiche art/apercus/animaux/ver_luisant.png (style du palier : A, cousu main)
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

IVOIRE = np.array(M.hexa("#f3ecd8"))          # la dominante (registre : ivoire)
ANNEAU = np.array(M.hexa("#ddd2b4"))          # les plis entre les anneaux
TETE = np.array(M.hexa("#cdb990"))            # la tête, les pattes
CITRON = np.array(M.hexa("#fff04c"))          # l'accent : la lanterne jaune citron
FIL = M.hexa("#8a7a58")

# du bout de la queue (relevé) à la tête, posée au sol
CHEMIN = [(0.00, 0.30, 0.290), (0.00, 0.35, 0.190), (0.00, 0.31, 0.100), (0.00, 0.21, 0.058), (0.00, 0.07, 0.050), (0.00, -0.07, 0.050),
          (0.00, -0.19, 0.078), (0.00, -0.28, 0.130), (0.00, -0.34, 0.190)]


def rayon(f):
    base = O.interp([(0.0, 0.0), (0.015, 0.030), (0.05, 0.052), (0.11, 0.040), (0.25, 0.044), (0.55, 0.050), (0.80, 0.048),
                     (0.90, 0.042), (0.96, 0.036), (0.99, 0.022), (1.0, 0.0)])(f)
    return base * (1.0 + 0.075 * math.cos(2.0 * math.pi * 10.0 * f) * min(1.0, max(0.0, (f - 0.10) / 0.10)))


def construire():
    a = K.Animal("ver_luisant")
    a.taille = 0.32

    # ----- le corps : un boudin à anneaux, ivoire ; plus sombre dans les plis ; la queue jaune citron qui s'allume sur le dernier
    #       dixième ; la tête plus sombre -----
    def peint(m, L):
        f = m.v[:, 2] / L
        t = np.tile(IVOIRE, (len(f), 1))
        t[np.cos(2.0 * math.pi * 10.0 * f) < -0.80] = ANNEAU
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t[ang > 2.4] = IVOIRE * 0.96
        t[f < 0.075] = CITRON
        t[(f >= 0.075) & (f < 0.115)] = CITRON * 0.55 + IVOIRE * 0.45
        t[f > 0.945] = TETE
        return t
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=32, flanc=(1.0, 0.0, 0.0))

    # ----- le visage : deux perles noires sur le front, une bouche d'un seul point brodé -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, direction = fil.vise(0.968 * L, 0.55, c * 0.50, 0.55)          # devant : les deux yeux se comptent de face
        pos, n = a.surface("corps", centre, direction)
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0205)
    cc, dd = fil.vise(0.995 * L, 0.0, 0.0, -0.12)
    q = a.trace("corps", cc, [dd], 0.002)
    if q:
        pts = [q[0]]
        for u_ in (-1, 1):
            c2, d2 = fil.vise(0.990 * L, 0.0, u_ * 0.55, -0.20)
            q2 = a.trace("corps", c2, [d2], 0.002)
            if q2:
                pts.append(q2[0])
        if len(pts) > 1:
            a.broderie("bouche", A.courbe(sorted(pts, key=lambda p: p[0]), 2), 0.0020, FIL)

    # ----- les six pattes : trois paires de petits crochets sous les premiers anneaux ; la lanterne : une ampoule en plus -----
    for c in (1, -1):
        for k, f in enumerate((0.800, 0.848, 0.896)):
            cen, av, nq = (Vector(q_) for q_ in fil.cadre(f * L))
            cote = nq.cross(av)
            p0 = cen + cote * (c * rayon(f) * 0.70) - nq * rayon(f) * 0.55
            p1 = p0 + cote * (c * 0.020) - nq * 0.014 + av * (-0.006)
            p2 = Vector((p1.x + c * 0.008, p1.y - 0.008, 0.009))
            pat = O.tube_r([tuple(p0), tuple(p1), tuple(p2)], [0.0075, 0.0060, 0.0045], 8)
            a.piece("patte_%s%d" % ("G" if c > 0 else "D", k), O.teinte(pat, TETE), None, poil=False)
    c0, a0, n0 = (Vector(q_) for q_ in fil.cadre(0.012 * L))
    ampoule = A.boule(1.0, 24, 12).etire(0.058, 0.058, 0.060)
    a.piece("lanterne", O.teinte(ampoule, CITRON), None, pos=tuple(c0 + Vector((0.0, 0.0, 0.020))), poil=False)
    a.tete = Vector(fil.cadre(0.97 * L)[0]) + Vector((0.0, -0.05, 0.02))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "mou")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("ver_luisant", styles.style_de("ver_luisant"), sys.modules[__name__]), "Ver luisant")
