"""La seiche en peluche : un coussin ovale taupe, zébré de crème, ourlé d'une jupe ondulante, posé sur le fond le nez
relevé. Devant, huit bras courts et deux longs tentacules raides, enroulés en crosse, qui se dressent comme des antennes ;
deux gros yeux sous une paupière en W, l'air de lire quelque chose de sombre. Elle change de couleur sous nos yeux,
paraît-il : pour l'instant, elle boude en zébré.

    python seiche.py        fabrique la fiche art/apercus/animaux/seiche.png (style du palier : C, velours ras)
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

TAUPE = np.array(M.hexa("#8c7a72"))           # la dominante (registre : taupe zébré de crème)
ZEBRE = np.array(M.hexa("#e9dccb"))           # les zébrures
OMBRE = np.array(M.hexa("#5d4b46"))           # le dessus de la tête, le bout des bras
FIL = M.hexa("#2a1f1c")


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def construire():
    a = K.Animal("seiche")
    a.taille = 0.70
    ROT = (-14, 0, 0)                              # le nez relevé

    # ----- le manteau : un coussin ovale couché, long (Y), zébré en travers ; la tête est dans son prolongement -----
    def coussin(v):
        s = v.copy()
        s[:, 2] = np.maximum(s[:, 2], -0.55 * 1.0)         # dessous presque plat
        return s
    manteau = A.boule(1.0, 56, 28).sculpte(coussin).etire(0.190, 0.340, 0.105)
    y = manteau.v[:, 1]
    zeb = (np.sin(y * 52.0 + 0.7 * manteau.v[:, 0] * 10) > 0.35) & (manteau.v[:, 2] > -0.01)
    t = np.tile(TAUPE, (len(y), 1))
    t[zeb] = ZEBRE * 0.92 + TAUPE * 0.08
    manteau.teinte = t
    a.piece("manteau", manteau, None, pos=(0.0, 0.12, 0.105), rot=ROT)

    # ----- la jupe : une nageoire ondulante qui court sur tout le tour, plus claire -----
    def ondule(v):
        s = v.copy()
        s[:, 2] += 0.014 * np.sin(v[:, 1] * 30)
        return s
    jupe = A.boule(1.0, 56, 12).sculpte(ondule).etire(0.240, 0.390, 0.014)
    jupe.teinte = np.tile(ZEBRE * 0.75 + TAUPE * 0.25, (len(jupe.v), 1))
    a.piece("jupe", jupe, None, pos=(0.0, 0.12, 0.070), rot=ROT, poil=False)

    # ----- la tête : une boule de l'autre côté du manteau, plus sombre dessus ; les yeux sur les côtés -----
    tete = A.boule(1.0, 40, 20).etire(0.140, 0.115, 0.105)
    tete.teinte = np.tile(OMBRE * 0.7 + TAUPE * 0.3, (len(tete.v), 1))
    a.piece("tete", tete, None, pos=(0.0, -0.250, 0.150), rot=ROT)
    centre = Vector((0.0, -0.250, 0.150))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, Vector((c * 0.95, -0.28, 0.12)))
        a.bouton("oeil_" + nom, pos + n * 0.002, n, 0.0360)
        haut_oeil = (Vector((0, 0.2, 1)) - n * n.dot(Vector((0, 0.2, 1)))).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.0360, 0.00), tuple(OMBRE * 0.7 + TAUPE * 0.3), mat=A.cadre(pos + n * 0.002, n, haut_oeil), poil=False)
    a.tete = centre + Vector((0.0, -0.10, 0.0))

    # ----- huit bras courts, écartés devant la tête ; le bout plus sombre -----
    for k in range(8):
        th = math.radians(-70 + 20 * k)
        pts = [(0.075 * math.sin(th), -0.320, 0.150 + 0.040 * math.cos(th) - 0.050),
               (0.110 * math.sin(th), -0.385, 0.110 + 0.016 * math.cos(th)),
               (0.130 * math.sin(th), -0.440, 0.080 + (0.020 if k % 2 else 0.0)),
               (0.140 * math.sin(th) * 1.1, -0.485, 0.052 + (0.040 if k % 2 else 0.006))]
        bras = K.tube_peint(A.courbe(pts, 5), lambda t: 0.040 - 0.028 * t, [(0.7, TAUPE), (1.0, OMBRE)], 12)
        a.piece("bras_%d" % k, bras, None)

    # ----- les deux longs tentacules : raides, dressés en antennes, chacun fini par une petite massue -----
    for nom, c in (("G", 1), ("D", -1)):
        pts = [(c * 0.040, -0.330, 0.190), (c * 0.085, -0.420, 0.215), (c * 0.115, -0.500, 0.255), (c * 0.100, -0.545, 0.310),
               (c * 0.070, -0.545, 0.345)]
        a.piece("tentacule_" + nom, K.tube_peint(A.courbe(pts, 5), lambda t: 0.017 - 0.006 * t, [(1.0, TAUPE)], 10), None)
        massue = A.boule(1.0, 18, 10).etire(0.028, 0.040, 0.026)
        massue.teinte = np.tile(ZEBRE * 0.8 + TAUPE * 0.2, (len(massue.v), 1))
        a.piece("massue_" + nom, massue, None, pos=(c * 0.066, -0.548, 0.352), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules[__name__], "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("seiche", styles.style_de("seiche"), sys.modules[__name__]), "Seiche")
