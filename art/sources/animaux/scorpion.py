"""Le scorpion en peluche : l'ambré des pierres chaudes, large carapace plate aux deux petits yeux sur le dessus, deux
grosses pinces sombres brandies devant, huit pattes minces en éventail, et la queue : cinq anneaux qui montent en arc
par-dessus le dos et s'achèvent sur un dard noir, la pointe pendue vers l'avant. Il ne menace personne. Il se tient
simplement prêt, depuis très longtemps.

    python scorpion.py        fabrique la fiche art/apercus/animaux/scorpion.png (style du palier : A, cousu main)
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

AMBRE = np.array(M.hexa("#e8ac40"))           # la dominante (registre : ambre #e0a63a), un cran plus clair (cousu main)
MIEL = np.array(M.hexa("#f1c872"))            # le dessous, les articulations
SOMBRE = np.array(M.hexa("#5a3a24"))          # l'accent : les pinces, le dard
FIL = M.hexa("#3a2412")


def construire():
    a = K.Animal("scorpion")
    a.taille = 0.34

    # ----- la carapace plate (le prosoma) et l'abdomen en anneaux qui s'allonge derrière ; le dessous plus clair -----
    car = A.boule(1.0, 36, 18).sculpte(lambda v: K.emousse(v, 0.7)).etire(0.092, 0.100, 0.034)
    car.teinte = np.tile(AMBRE, (len(car.v), 1))
    a.piece("carapace", car, None, pos=(0.0, -0.040, 0.060))
    abd = None
    for k in range(5):
        r = 0.076 - 0.007 * k
        seg = A.boule(1.0, 24, 12).sculpte(lambda v: K.emousse(v, 0.75)).etire(r, 0.040, 0.030 - 0.002 * k)
        seg.teinte = np.tile(AMBRE * (1.0 - 0.03 * (k % 2)), (len(seg.v), 1))
        seg = O.couche(seg, A.repere((0.0, 0.082 + 0.058 * k, 0.056 - 0.002 * k)))
        abd = seg if abd is None else abd + seg
    a.piece("abdomen", abd, None)

    # ----- la queue : cinq anneaux qui montent en arc par-dessus le dos, puis la boule du dard et l'aiguille -----
    base = Vector((0.0, 0.350, 0.050))
    chemin = [tuple(base), (0.0, 0.420, 0.070), (0.0, 0.470, 0.130), (0.0, 0.480, 0.215), (0.0, 0.440, 0.300), (0.0, 0.370, 0.356),
              (0.0, 0.285, 0.372), (0.0, 0.200, 0.352), (0.0, 0.140, 0.300)]
    queue = A.tube(A.courbe(chemin, 6), lambda t: 0.034 * (1.0 - 0.34 * t) * (1.0 + 0.16 * math.cos(2 * math.pi * 5.0 * t)), 16)
    queue.teinte = np.tile(AMBRE, (len(queue.v), 1))
    a.piece("queue", queue, None)
    ampoule = A.boule(1.0, 20, 10).etire(0.030, 0.034, 0.034)
    a.piece("ampoule", O.teinte(ampoule, AMBRE * 0.92), None, pos=(0.0, 0.130, 0.280))
    dard = O.couche(O.teinte(O.pointe(0.065, 0.018, 10), SOMBRE), A.cadre(Vector((0.0, 0.118, 0.255)), Vector((0.0, -0.45, -0.90)), (1, 0, 0)))
    a.piece("dard", dard, None, poil=False)

    # ----- les pinces : un bras court, une main renflée, deux doigts qui se rejoignent par la pointe -----
    for nom, c in (("G", 1), ("D", -1)):
        bras = O.tube_r([(c * 0.070, -0.090, 0.060), (c * 0.150, -0.150, 0.066), (c * 0.170, -0.235, 0.068)], [0.026, 0.026, 0.030], 14)
        a.piece("bras_" + nom, O.teinte(bras, AMBRE), None)
        main = A.boule(1.0, 24, 12).etire(0.046, 0.058, 0.032)
        main.teinte = np.tile(SOMBRE, (len(main.v), 1))
        a.piece("main_" + nom, main, None, pos=(c * 0.172, -0.282, 0.070), rot=(0, 0, c * -8))
        fixe = O.couche(O.teinte(O.pointe(0.100, 0.026, 12), SOMBRE),
                        A.cadre(Vector((c * 0.148, -0.318, 0.072)), Vector((-c * 0.02, -1.0, 0.0)), (0, 0, 1)))
        mobile = O.couche(O.teinte(O.pointe(0.092, 0.020, 12), SOMBRE * 0.9),
                          A.cadre(Vector((c * 0.214, -0.312, 0.070)), Vector((-c * 0.60, -1.0, 0.0)), (0, 0, 1)))
        a.piece("doigt_fixe_" + nom, fixe, None)
        a.piece("doigt_mobile_" + nom, mobile, None)

    # ----- huit pattes minces, quatre de chaque côté, le genou levé, le bout posé ; deux petits yeux sur le dessus -----
    for nom, c in (("G", 1), ("D", -1)):
        for k in range(4):
            y0 = 0.020 - 0.052 * (k - 1.5) * -1.0
            depart = (c * 0.070, -0.075 + 0.045 * k, 0.050)
            genou = (c * (0.160 + 0.012 * k), -0.100 + 0.052 * k, 0.108 - 0.006 * k)
            pied = (c * (0.250 + 0.014 * k), -0.150 + 0.080 * k, 0.010)
            patte = O.tube_r([depart, genou, pied], [0.0105, 0.0090, 0.0060], 10)
            a.piece("patte_%s%d" % (nom, k), O.teinte(patte, MIEL * 0.92 + AMBRE * 0.08), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        a.bouton("oeil_" + nom, Vector((c * 0.028, -0.092, 0.092)), Vector((c * 0.25, -0.35, 0.90)).normalized(), 0.0105)
    a.tete = Vector((0.0, -0.140, 0.090))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("scorpion", styles.style_de("scorpion"), sys.modules[__name__]), "Scorpion")
