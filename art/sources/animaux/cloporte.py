"""Le cloporte en peluche : la petite armure grise bleutée des caves, sept plaques qui se chevauchent comme des tuiles, un
anneau plus sombre à chaque jointure, deux antennes courtes, deux yeux noirs au coin de la tête, sept paires de pattes
minuscules sous le bord, et à l'arrière deux piques en queue. Il avance sans se presser : quand on lui fait peur, il se
roule en boule, et personne ne l'attend plus.

    python cloporte.py        fabrique la fiche art/apercus/animaux/cloporte.png (style du palier : A, cousu main)
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

BLEUTE = np.array(M.hexa("#b3bfcd"))          # la dominante (registre : gris bleuté clair), un cran plus clair (cousu main)
ANNEAU = np.array(M.hexa("#76869a"))          # l'accent : les anneaux plus sombres
VENTRE = np.array(M.hexa("#d6dde6"))          # le dessous, les pattes
FIL = M.hexa("#4a5668")


def construire():
    a = K.Animal("cloporte")
    a.taille = 0.20

    # ----- le corps : sept plaques qui se chevauchent, chacune un peu plus large vers le milieu, un anneau sombre au bord ;
    #       la tête arrondie devant, le dernier segment pointu -----
    larg = (0.060, 0.082, 0.098, 0.106, 0.104, 0.092, 0.074)
    corps = None
    for k, w in enumerate(larg):
        y = -0.020 + 0.058 * k
        seg = A.boule(1.0, 28, 14).sculpte(lambda v: K.emousse(v, 0.78)).etire(w, 0.044, 0.056 - 0.002 * abs(k - 3))
        ang = np.abs(np.arctan2(seg.v[:, 0], seg.v[:, 1]))
        zz = seg.v[:, 2]
        t = np.tile(BLEUTE * (1.0 - 0.025 * (k % 2)), (len(seg.v), 1))
        t[(seg.v[:, 1] > 0.036 * 0.9)] = BLEUTE * 0.97                                       # le dessus plus lisse
        t[(np.abs(seg.v[:, 1]) < 0.012) & (np.abs(seg.v[:, 0]) > w * 0.55)] = ANNEAU         # le bord sombre sur le côté
        seg.teinte = t
        seg = O.couche(seg, A.repere((0.0, y, 0.040 + 0.002 * abs(k - 3) * 0.0)))
        corps = seg if corps is None else corps + seg
    a.piece("plaques", corps, None)
    tete = A.boule(1.0, 28, 14).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.060, 0.044, 0.044)
    a.piece("tete", O.teinte(tete, BLEUTE * 0.94), None, pos=(0.0, -0.100, 0.040))
    queue = None
    for c in (1, -1):
        p = O.couche(O.teinte(O.pointe(0.060, 0.0145, 8), ANNEAU), A.cadre(Vector((c * 0.020, 0.398, 0.036)), Vector((c * 0.18, 1.0, 0.05)), (0, 0, 1)))
        queue = p if queue is None else queue + p
    a.piece("piques", queue, None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        ant = O.tube_r([(c * 0.026, -0.138, 0.050), (c * 0.050, -0.185, 0.066), (c * 0.080, -0.222, 0.060)], [0.0070, 0.0058, 0.0042], 8)
        a.piece("antenne_" + nom, O.teinte(ant, ANNEAU), None, poil=False)
        a.bouton("oeil_" + nom, Vector((c * 0.046, -0.120, 0.058)), Vector((c * 0.80, -0.50, 0.32)).normalized(), 0.0100)
        # sept paires de pattes : de petits crochets sous le bord
        for k in range(7):
            y = -0.015 + 0.058 * k
            w = larg[k]
            pat = O.tube_r([(c * w * 0.80, y, 0.026), (c * (w * 0.95 + 0.012), y - 0.004, 0.016), (c * (w * 0.95 + 0.020), y - 0.010, 0.006)],
                           [0.0075, 0.0060, 0.0045], 8)
            a.piece("patte_%s%d" % (nom, k), O.teinte(pat, VENTRE), None, poil=False)
    a.tete = Vector((0.0, -0.140, 0.050))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("cloporte", styles.style_de("cloporte"), sys.modules[__name__]), "Cloporte")
