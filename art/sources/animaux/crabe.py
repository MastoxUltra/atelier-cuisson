"""Le crabe en peluche : un galet rouge tomate large comme un coussin, aux yeux sur tiges, qui trotte de travers sur ses
six pattes en gardant les deux pinces levées. L'une est ouverte, prête à pincer, l'autre fermée en poing ; les bouts
de pinces sont noirs. Il avance toujours là où il ne regarde pas, et regarde toujours là où il ne va pas.

    python crabe.py        fabrique la fiche art/apercus/animaux/crabe.png (style du palier : A, cousu main)
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

TOMATE = np.array(M.hexa("#e24a30"))          # la dominante (registre : rouge tomate)
CLAIR = np.array(M.hexa("#f07a56"))           # le dessous, les bords
NOIR = M.hexa("#241818")
PATTE = np.array(M.hexa("#cf3a24"))
FIL = M.hexa("#5a1a10")


def construire():
    a = K.Animal("crabe")
    a.taille = 0.46

    # ----- la carapace : un galet très large, bombé, le front droit, les flancs pointus ; le dessous clair -----
    def galet(v):
        s = v.copy()
        s[:, 2] = np.maximum(s[:, 2], -0.35)
        s[:, 1] *= 1 - 0.18 * np.clip(v[:, 1], 0, None)
        s[:, 0] += np.sign(v[:, 0]) * 0.03 * np.exp(-((np.abs(v[:, 0]) - 0.95) / 0.12) ** 2)       # les pointes de côté
        return s
    carapace = A.boule(1.0, 56, 28).sculpte(galet).etire(0.215, 0.150, 0.085)
    u = carapace.v / np.maximum(np.abs(carapace.v).max(axis=0), 1e-9)
    t = np.tile(TOMATE, (len(u), 1))
    t[u[:, 2] < -0.30] = CLAIR
    t[(u[:, 2] > 0.35) & (np.abs(np.sin(u[:, 0] * 10 + 3 * u[:, 1])) > 0.93)] = CLAIR * 0.9
    carapace.teinte = t
    a.piece("carapace", carapace, None, pos=(0.0, 0.0, 0.095))

    # ----- le visage : deux yeux sur de courtes tiges, un sourire cousu sous le front -----
    for nom, c in (("G", 1), ("D", -1)):
        tige = O.tube_r([(c * 0.050, -0.105, 0.150), (c * 0.058, -0.125, 0.195)], [0.012, 0.011], 10)
        a.piece("tige_" + nom, O.teinte(tige, PATTE), None, poil=False)
        a.oeil("oeil_" + nom, Vector((c * 0.058, -0.134, 0.207)), Vector((c * 0.25, -0.9, 0.30)), 0.0240)
    O.broder(a, "sourire", "carapace", Vector((0.0, 0.0, 0.14)),
             [(0.62 * u_, -0.80, -0.06 + 0.22 * u_ * u_) for u_ in np.linspace(-1, 1, 9)], 0.0026, FIL, decolle=0.003)
    a.tete = Vector((0.0, -0.14, 0.17))

    # ----- les pinces : un bras à deux segments, une pince aux doigts noirs ; la gauche ouverte, la droite fermée en poing -----
    for nom, c, ouv in (("G", 1, 24.0), ("D", -1, 2.0)):
        bras = O.tube_r([(c * 0.170, -0.090, 0.120), (c * 0.250, -0.140, 0.160), (c * 0.270, -0.215, 0.230)], [0.030, 0.026, 0.024], 12)
        a.piece("bras_" + nom, O.teinte(bras, PATTE), None)
        p = O.pince(0.165, 0.125, 8.0 + ouv * 1.4, np.asarray(TOMATE, float), np.asarray(NOIR, float))
        a.piece("pince_" + nom, p, None, mat=A.cadre(Vector((c * 0.268, -0.245, 0.250)), (c * 0.12, -0.40, 1.0), (0, 1, 0)), poil=False)

    # ----- les six pattes : trois de chaque côté, repliées en genou vers le haut puis posées de travers -----
    for k in range(3):
        for nom, c in (("G", 1), ("D", -1)):
            y = -0.050 + 0.062 * k
            patte = O.tube_r([(c * 0.180, y, 0.080), (c * 0.270, y + 0.010 * k, 0.130 - 0.010 * k), (c * 0.330, y + 0.030, 0.008)],
                             [0.020, 0.017, 0.011], 10)
            a.piece("patte_%s%d" % (nom, k), O.teinte(patte, PATTE), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("crabe", styles.style_de("crabe"), sys.modules[__name__]), "Crabe")
