"""Le bernard-l'ermite en peluche : un petit corps abricot qui sort d'une coquille spiralée crème et lilas, trop
grande pour lui et qu'il porte comme une maison de vacances. Une grosse pince en avant, l'autre minuscule, deux yeux
sur de petites tiges, la bouche en trait ; il a déjà pensé à déménager, mais la vue d'ici est si bonne.

    python bernard_l_ermite.py        fabrique la fiche art/apercus/animaux/bernard_l_ermite.png (style du palier : A, cousu main)
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

ABRICOT = np.array(M.hexa("#f4a468"))         # la dominante (registre : corps abricot)
CREME = np.array(M.hexa("#f7ecd4"))           # la coquille
LILAS = np.array(M.hexa("#b69bd8"))
FONCE = np.array(M.hexa("#d9763a"))
FIL = M.hexa("#5a2e18")


def construire():
    a = K.Animal("bernard_l_ermite")
    a.taille = 0.36

    # ----- la coquille : une spirale conique qui s'élargit, rayée de crème et de lilas, posée sur le dos du bernard -----
    pts = []
    n = 40
    for i in range(n):
        t = i / (n - 1)
        th = math.radians(-60 + 760 * t)
        r = 0.020 + 0.115 * t                               # l'écart au centre croît
        pts.append((r * math.cos(th) * 0.9, 0.095 + r * math.sin(th) * 0.9, 0.050 + 0.230 * (1 - t) ** 0.8 + 0.10 * t))
    paliers = []
    for k in range(10):
        paliers.append(((k + 1) / 10, CREME if k % 2 == 0 else LILAS))
    coq = K.tube_peint(A.courbe(pts, 3), 0.001, paliers, 16)
    coq = A.tube(A.courbe(pts, 3), lambda t: 0.020 + 0.075 * t ** 0.9, 18)
    ts = np.linspace(0, 1, len(coq.v))
    idx = np.floor(np.linspace(0, 1, len(coq.v)) * 10).astype(int) % 2
    coq.teinte = np.where((idx % 2 == 0)[:, None], CREME, LILAS)
    a.piece("coquille", coq, None, poil=False)

    # ----- le corps : une grosse tête-thorax abricot qui sort de l'ouverture de la coquille, tournée vers nous -----
    thorax = A.boule(1.0, 36, 18).etire(0.075, 0.085, 0.070)
    a.piece("corps", O.teinte(thorax, ABRICOT), None, pos=(0.0, -0.055, 0.080))
    ventre = A.boule(1.0, 28, 14).etire(0.060, 0.070, 0.050)
    a.piece("abdomen", O.teinte(ventre, ABRICOT * 0.92), None, pos=(0.0, 0.030, 0.092))

    # ----- le visage : deux yeux sur de petites tiges, une bouche ; la grosse pince en avant, la petite de l'autre côté -----
    for nom, c in (("G", 1), ("D", -1)):
        tige = O.tube_r([(c * 0.030, -0.100, 0.130), (c * 0.036, -0.112, 0.178)], [0.0095, 0.009], 10)
        a.piece("tige_" + nom, O.teinte(tige, FONCE), None, poil=False)
        a.bouton("oeil_" + nom, Vector((c * 0.037, -0.116, 0.188)), Vector((c * 0.25, -0.92, 0.25)), 0.0200)
    O.broder(a, "bouche", "corps", Vector((0.0, -0.055, 0.080)), [(0.40 * u_, -0.94, -0.22 + 0.12 * u_ * u_) for u_ in np.linspace(-1, 1, 7)],
             0.0022, FIL, decolle=0.002)
    a.tete = Vector((0.0, -0.12, 0.130))

    grosse = O.tube_r([(0.070, -0.090, 0.060), (0.130, -0.135, 0.058), (0.150, -0.185, 0.062)], [0.024, 0.022, 0.020], 12)
    a.piece("bras_gros", O.teinte(grosse, FONCE), None, poil=False)
    pince = A.boule(1.0, 24, 12).etire(0.050, 0.070, 0.030)
    a.piece("pince_grosse", O.teinte(pince, ABRICOT), None, pos=(0.150, -0.235, 0.062), rot=(0, 0, 14))
    petit = O.tube_r([(-0.070, -0.090, 0.060), (-0.100, -0.125, 0.050), (-0.108, -0.150, 0.044)], [0.014, 0.013, 0.012], 10)
    a.piece("bras_petit", O.teinte(petit, FONCE), None, poil=False)
    a.piece("pince_petite", O.teinte(A.boule(1.0, 16, 8).etire(0.020, 0.030, 0.014), ABRICOT), None, pos=(-0.108, -0.172, 0.044), poil=False)

    # ----- quatre petites pattes, deux de chaque côté, à plat sur le sable -----
    for k in range(2):
        for nom, c in (("G", 1), ("D", -1)):
            y = -0.020 + 0.050 * k
            patte = O.tube_r([(c * 0.060, y, 0.050), (c * 0.115, y - 0.004, 0.040), (c * 0.150, y - 0.018, 0.008)], [0.012, 0.0105, 0.008], 8)
            a.piece("patte_%s%d" % (nom, k), O.teinte(patte, FONCE), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("bernard_l_ermite", styles.style_de("bernard_l_ermite"), sys.modules[__name__]), "Bernard-l'ermite")
