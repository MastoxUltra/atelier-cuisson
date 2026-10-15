"""La crevette-mante en peluche : le boxeur du récif. Turquoise vif, cuirassée de six plaques qui s'emboîtent comme un
corset ; deux yeux énormes montés sur des tiges, qui regardent chacun de leur côté ; et deux poings orange hérissés de
piquants, repliés devant le visage en garde haute. Elle est accroupie, prête à cogner : elle frappe plus vite qu'une
balle, c'est elle qui le dit. La queue en éventail à piquants rase le sol derrière.

    python crevette_mante.py        fabrique la fiche art/apercus/animaux/crevette_mante.png (style du palier : C, velours ras)
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

TURQUOISE = np.array(M.hexa("#22b8b0"))       # la dominante (registre : turquoise)
SOMBRE = np.array(M.hexa("#157f86"))          # les arêtes des plaques, la queue
ORANGE = M.hexa("#f2862a")                    # l'accent : les poings, les pattes
CLAIR = np.array(M.hexa("#7fdcd2"))
NOIRC = M.hexa("#1a2e33")


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def construire():
    a = K.Animal("crevette_mante")
    a.taille = 0.52

    # ----- l'abdomen : six plaques qui s'emboîtent, de plus en plus petites vers l'arrière, légèrement incurvées -----
    plaques = None
    for k in range(6):
        y = 0.020 + 0.060 * k
        r = 0.125 - 0.011 * k
        m = A.boule(1.0, 36, 18).etire(r, 0.046, r * 0.78)
        m.teinte = np.tile(TURQUOISE * (1.0 if k % 2 == 0 else 0.86), (len(m.v), 1))
        m = m.pose((0.0, y, 0.075 + 0.006 * (k % 2) + 0.004 * k))
        plaques = m if plaques is None else plaques + m
    a.piece("abdomen", plaques, None)

    # ----- la carapace de devant : un bouclier large qui abrite la tête, avec une arête médiane -----
    bouclier = A.boule(1.0, 40, 20).etire(0.125, 0.135, 0.092)
    bouclier.teinte = np.tile(TURQUOISE * 1.04, (len(bouclier.v), 1))
    a.piece("bouclier", bouclier, None, pos=(0.0, -0.100, 0.100), rot=(-6, 0, 0))
    arete = A.tube(A.courbe([(0, -0.215, 0.082), (0, -0.120, 0.186), (0, -0.015, 0.164)], 5), lambda t: 0.012 + 0.004 * math.sin(math.pi * t), 12)
    arete.teinte = np.tile(SOMBRE, (len(arete.v), 1))
    a.piece("arete", arete, None, poil=False)

    # ----- les yeux sur tiges : un grand globe de chaque côté, la bille sombre bien en vue ; la bande médiane -----
    for nom, c in (("G", 1), ("D", -1)):
        tige = A.tube(A.courbe([(c * 0.055, -0.185, 0.150), (c * 0.092, -0.205, 0.215), (c * 0.108, -0.215, 0.290)], 5), 0.015, 12)
        tige.teinte = np.tile(SOMBRE, (len(tige.v), 1))
        a.piece("tige_" + nom, tige, None, poil=False)
        globe = A.boule(1.0, 36, 18).etire(0.056, 0.052, 0.056)
        globe.teinte = np.tile(CLAIR * 0.85, (len(globe.v), 1))
        a.piece("globe_" + nom, globe, None, pos=(c * 0.108, -0.222, 0.318))
        pos, n = a.surface("globe_" + nom, Vector((c * 0.108, -0.222, 0.318)), Vector((c * 0.35, -0.90, 0.10)))
        a.bouton("oeil_" + nom, pos + n * 0.002, n, 0.0300)
    a.tete = Vector((0.0, -0.250, 0.250))

    # ----- les deux poings : un bras qui plie en garde haute, un poing orange hérissé de trois piquants -----
    for nom, c in (("G", 1), ("D", -1)):
        bras = A.tube(A.courbe([(c * 0.090, -0.150, 0.055), (c * 0.155, -0.230, 0.090), (c * 0.150, -0.310, 0.150),
                                (c * 0.095, -0.330, 0.215)], 5), lambda t: 0.032 - 0.010 * t, 14)
        a.piece("bras_" + nom, bras, ORANGE)
        poing = A.boule(1.0, 28, 14).etire(0.050, 0.048, 0.062)
        a.piece("poing_" + nom, poing, ORANGE, pos=(c * 0.085, -0.338, 0.232))
        for k, ang in enumerate((-35, 0, 35)):
            r = math.radians(ang)
            d = Vector((c * math.sin(r) * 0.6, -0.5, math.cos(r)))
            pique = A.tour(A.profil([(0.010, 0), (0.007, 0.025), (0.0035, 0.045), (0, 0.058)], 3), 10)
            a.piece("pique_%s%d" % (nom, k), couche(pique, A.cadre(Vector((c * 0.085, -0.338, 0.232)) + d.normalized() * 0.052, d.normalized(), (0, 1, 0))),
                    NOIRC, poil=False)

    # ----- les pattes : petites, sous le ventre, orange ; la queue : un éventail à piquants -----
    for k in range(5):
        for nom, c in (("G", 1), ("D", -1)):
            y = -0.010 + 0.052 * k
            patte = A.tube(A.courbe([(c * 0.075, y, 0.050), (c * 0.115, y + 0.010, 0.030), (c * 0.135, y + 0.020, 0.008)], 4), 0.010, 8)
            a.piece("patte_%s%d" % (nom, k), patte, ORANGE, poil=False)
    queue = A.boule(1.0, 36, 12).etire(0.150, 0.100, 0.014)
    queue.teinte = np.tile(SOMBRE, (len(queue.v), 1))
    a.piece("queue", queue, None, pos=(0.0, 0.420, 0.040), rot=(8, 0, 0), poil=False)
    for k, x in enumerate(np.linspace(-0.12, 0.12, 5)):
        pique = A.tour(A.profil([(0.012, 0), (0.008, 0.030), (0.004, 0.060), (0, 0.080)], 3), 10)
        a.piece("epine_%d" % k, couche(pique, A.cadre(Vector((x, 0.500, 0.046)), (x * 1.5, 1.0, 0.25), (0, 0, 1))), NOIRC, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules[__name__], "fixe")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("crevette_mante", styles.style_de("crevette_mante"), sys.modules[__name__]), "Crevette-mante")
