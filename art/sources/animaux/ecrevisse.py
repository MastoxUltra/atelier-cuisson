"""L'écrevisse en peluche : une petite armure brun-rouge laqué, six plaques en queue qui se terminent en éventail, deux
pinces orange levées bien haut (elle est prête à pincer, et ça se voit), deux longues antennes qui fouettent l'eau, des
yeux perlés sur de courtes tiges. Plantée sur ses huit petites pattes, elle recule vers les cailloux sans lâcher du regard
ceux qui la regardent.

    python ecrevisse.py        fabrique la fiche art/apercus/animaux/ecrevisse.png (style du palier : A, cousu main)
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

LAQUE = np.array(M.hexa("#9a4230"))           # la dominante (registre : brun-rouge laqué #8a3a2a) ; le poil fonce
CLAIR = np.array(M.hexa("#b85a42"))           # les plaques plus claires
ORANGE = M.hexa("#f08a2c")                    # l'accent : les pinces
PIEDS = M.hexa("#c26a4a")
FIL = M.hexa("#3a1710")


def construire():
    a = K.Animal("ecrevisse")
    a.taille = 0.60                                # plus gros : il se noyait dans l'herbe (« flou »)

    # ----- le thorax : un bouclier allongé, pointu devant (le rostre), bombé derrière -----
    def bouclier(v):
        s = v.copy()
        avant = np.clip(-v[:, 1], 0, 1)
        s[:, 0] *= 1 - 0.55 * avant ** 1.5
        s[:, 2] *= 1 - 0.30 * avant
        return s
    thorax = A.boule(1.0, 48, 24).sculpte(bouclier).etire(0.105, 0.160, 0.095)
    thorax.teinte = np.tile(LAQUE, (len(thorax.v), 1))
    a.piece("thorax", thorax, None, pos=(0.0, -0.10, 0.115))
    rostre = O.pointe(0.075, 0.020, 12)
    a.piece("rostre", O.couche(O.teinte(rostre, CLAIR), A.cadre(Vector((0.0, -0.250, 0.135)), (0.0, -1.0, 0.12), (0, 0, 1))), None)

    # ----- l'abdomen : six plaques qui s'emboîtent et se recourbent vers le bas, le dernier un éventail -----
    plaques = None
    for k in range(6):
        t = k / 5
        y = 0.075 + 0.058 * k
        z = 0.108 - 0.050 * t ** 1.5
        r = 0.098 - 0.010 * k
        m = A.boule(1.0, 28, 14).etire(r, 0.040, r * 0.80)
        m.teinte = np.tile(CLAIR if k % 2 else LAQUE, (len(m.v), 1))
        m = m.pose((0.0, y, z), (-14 * t, 0, 0))
        plaques = m if plaques is None else plaques + m
    a.piece("abdomen", plaques, None)
    eventail = A.boule(1.0, 28, 10).etire(0.130, 0.080, 0.014)
    a.piece("queue", O.teinte(eventail, CLAIR), None, pos=(0.0, 0.440, 0.040), rot=(-10, 0, 0), poil=False)

    # ----- les pinces : un bras levé, deux doigts qui s'ouvrent, orange -----
    for nom, c in (("G", 1), ("D", -1)):
        bras = O.tube_r([(c * 0.075, -0.180, 0.100), (c * 0.150, -0.260, 0.130), (c * 0.170, -0.340, 0.190), (c * 0.120, -0.380, 0.270)],
                        [0.030, 0.027, 0.024, 0.022], 14)
        a.piece("bras_" + nom, bras, tuple(LAQUE), poil=True)
        p = O.pince(0.190, 0.100, 30.0, np.asarray(ORANGE, float), np.array([0.12, 0.08, 0.07]))
        a.piece("pince_" + nom, p, None, mat=A.cadre(Vector((c * 0.116, -0.395, 0.290)), (c * 0.14, -0.55, 0.85), (0, 1, 0)), poil=False)

    # ----- les antennes : deux longs fouets qui partent du front ; les yeux perlés sur deux tiges -----
    for nom, c in (("G", 1), ("D", -1)):
        antenne = O.tube_r([(c * 0.040, -0.240, 0.150), (c * 0.110, -0.360, 0.200), (c * 0.220, -0.470, 0.215), (c * 0.340, -0.560, 0.185)],
                           [0.010, 0.0085, 0.0065, 0.0035], 8)
        a.piece("antenne_" + nom, O.teinte(antenne, PIEDS), None, poil=False)
        tige = O.tube_r([(c * 0.040, -0.205, 0.180), (c * 0.058, -0.235, 0.215)], [0.0085, 0.0085], 8)
        a.piece("tige_" + nom, O.teinte(tige, PIEDS), None, poil=False)
        a.oeil("oeil_" + nom, Vector((c * 0.060, -0.243, 0.222)), Vector((c * 0.45, -0.85, 0.30)), 0.0155)
    a.tete = Vector((0.0, -0.26, 0.15))

    # ----- les petites pattes : quatre de chaque côté, sous le thorax -----
    for k in range(4):
        for nom, c in (("G", 1), ("D", -1)):
            y = -0.150 + 0.050 * k
            patte = O.tube_r([(c * 0.075, y, 0.085), (c * 0.125, y - 0.015, 0.060), (c * 0.150, y - 0.030, 0.008)], [0.0115, 0.010, 0.0075], 8)
            a.piece("patte_%s%d" % (nom, k), O.teinte(patte, PIEDS), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("ecrevisse", styles.style_de("ecrevisse"), sys.modules[__name__]), "Écrevisse")
