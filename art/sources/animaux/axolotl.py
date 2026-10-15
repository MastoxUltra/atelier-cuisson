"""L'axolotl en peluche : le rose franc des grottes, large tête plate au sourire éternel, trois panaches de branchies corail
de chaque côté, qui flottent comme des plumes, deux points noirs pour yeux, un long corps de salamandre aplati, une
queue-rame bordée d'un ourlet, quatre petites mains aux doigts écartés. Il ne grandira pas : il a décidé de rester
jeune pour toujours, et il en a l'air.

    python axolotl.py        fabrique la fiche art/apercus/animaux/axolotl.png (style du palier : C, velours ras)
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

ROSE = np.array(M.hexa("#f594ae"))            # la dominante (registre : rose franc #f08ca8), un cran plus clair (style C)
DESSOUS = np.array(M.hexa("#fbc2cf"))         # le ventre
CORAIL = np.array(M.hexa("#ff6e5c"))          # l'accent : les branchies
OURLET = np.array(M.hexa("#fdb0c2"))          # la crête de la queue
FIL = M.hexa("#7a2c40")

# du bout de la queue au bout du nez : la queue-rame qui s'enroule, le corps aplati, la tête large qui se relève
CHEMIN = [(0.20, 0.50, 0.026), (0.22, 0.40, 0.034), (0.15, 0.30, 0.046), (0.05, 0.20, 0.058), (-0.02, 0.08, 0.066), (-0.02, -0.04, 0.070),
          (0.02, -0.15, 0.072), (0.04, -0.25, 0.082), (0.01, -0.33, 0.108), (-0.04, -0.40, 0.136), (-0.09, -0.45, 0.150)]
CORPS = O.interp([(0.0, 0.0), (0.02, 0.010), (0.10, 0.024), (0.28, 0.046), (0.45, 0.066), (0.62, 0.074), (0.76, 0.072),
                  (0.84, 0.068), (0.90, 0.078), (0.96, 0.076), (0.99, 0.052), (1.0, 0.0)])


def construire():
    a = K.Animal("axolotl")
    a.taille = 0.42

    # ----- le corps : une pièce couchée sur son fil, aplatie ; la tête très large et plate ; le dessous plus pâle ; les points
    #       sombres des flancs -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(ROSE, (len(m.v), 1))
        t[ang > 2.0] = DESSOUS
        return O.moucheter(m, ROSE, ROSE * 0.82, graine=7, nombre=60, taille=0.045, depart=t)

    def aplati(L):
        def g(v):
            s = v.copy()
            fr = v[:, 2] / L
            h = np.clip((fr - 0.84) / 0.07, 0.0, 1.0)
            h = h * h * (3 - 2 * h)
            s[:, 1] *= 1.0 - 0.18 * np.clip(fr * 1.6, 0.0, 1.0) - 0.20 * h              # tout le corps aplati, la tête plus encore
            s[:, 0] *= 1.0 + 0.12 * np.clip((fr - 0.1) / 0.5, 0.0, 1.0) + 0.30 * h         # large
            return s
        return g
    fil, L = O.fil_corps(a, "corps", CHEMIN, CORPS, peint, None, cotes=36, flanc=(1.0, 0.0, 0.0), deforme=aplati)

    # ----- l'ourlet : une crête de nageoire qui court du dos jusqu'au bout de la queue -----
    pts = []
    for f in np.linspace(0.10, 0.80, 36):
        c, av, nq = (Vector(q) for q in fil.cadre(f * L))
        pts.append(tuple(c + nq * (CORPS(f) * 0.80 + 0.006)))
    ruban = A.tube(A.courbe(pts, 2), lambda t: 0.012 * (1 - 0.6 * t) + 0.003, 8)
    a.piece("crete", O.teinte(ruban, OURLET), None, poil=False)

    # ----- le visage : deux points noirs, le grand sourire qui remonte aux joues -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, direction = fil.vise(0.950 * L, 0.55, c * 0.50, 0.55)                   # sur le dessus du museau : deux yeux de face
        pos, n = a.surface("corps", centre, direction)
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0135)
        pts_b = []
        for u_ in np.linspace(0.0, 1.0, 9):
            cc, dd = fil.vise((0.992 - 0.074 * u_) * L, 0.0, c * 1.0, -0.20 + 0.40 * u_ ** 1.6)
            q = a.trace("corps", cc, [dd], 0.002)
            if q:
                pts_b.append(q[0])
        if len(pts_b) > 1:
            a.broderie("sourire_" + nom, A.courbe(pts_b, 3), 0.0026, FIL)

    # ----- les branchies : trois panaches corail de chaque côté, derrière la tête, qui flottent vers l'arrière ; quatre petites
    #       mains aux doigts écartés -----
    for c, nm in ((1, "G"), (-1, "D")):
        cen, av, nq = (Vector(q) for q in fil.cadre(0.875 * L))
        cote = nq.cross(av)
        base = cen + cote * (c * CORPS(0.875) * 0.95) + nq * 0.012
        axe = cote * (c * 0.85) + av * (-0.25) + nq * 0.55             # en éventail, relevées : les trois panaches se voient des deux côtés
        a.piece("branchies_" + nm, O.plumes(base, axe, av, n=3, long=0.150, ray=0.0140, couleur=tuple(CORAIL), filaments=8), None, poil=False)
        for pos_f, nom in ((0.765, "avant"), (0.360, "arriere")):
            cn, avn, nqn = (Vector(q) for q in fil.cadre(pos_f * L))
            cn2 = nqn.cross(avn)
            r = cn + cn2 * (c * 0.060) - nqn * 0.018
            coude = cn + cn2 * (c * 0.110)
            coude.z = 0.036
            main = Vector((cn.x + c * 0.130, cn.y - 0.030 if nom == "avant" else cn.y + 0.020, 0.010))
            pts_p = [tuple(r), tuple(coude), tuple(main + Vector((0, 0, 0.006)))]
            m = O.membre(pts_p, [0.030, 0.024, 0.020], [(1.0, tuple(ROSE))], 12)
            for dx in (-0.018, -0.006, 0.006, 0.018):
                m = m + O.tube_r([tuple(main), tuple(main + Vector((c * 0.020 + dx * c * 0.5, -0.040, -0.001)))], [0.0075, 0.0055], 8)
            m.teinte = np.tile(ROSE, (len(m.v), 1))
            a.piece("patte_%s_%s" % (nom, nm), m, None, poil=False)
    a.tete = Vector(fil.cadre(0.97 * L)[0]) + Vector((-0.04, -0.05, 0.02))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad", souple=True)


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("axolotl", styles.style_de("axolotl"), sys.modules[__name__]), "Axolotl")
