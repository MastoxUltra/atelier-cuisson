"""L'étoile de mer en peluche : une belle étoile corail à pois crème, couchée sur le sable, qui lève un bras pour nous
saluer. Cinq bras bien ronds et un peu aplatis, le centre bombé ; deux petits boutons et un sourire cousu en travers
du centre. Un bras est dressé, plié au coude comme une main qui fait coucou ; les autres tiennent le sable.

    python etoile_de_mer.py        fabrique la fiche art/apercus/animaux/etoile_de_mer.png (style du palier : A, cousu main)
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

CORAIL = M.hexa("#ee6a55")                    # la dominante (registre du 14/10 : corail) ; tissu imprimé, sans poil
POIS = M.hexa("#ffe9cf")                      # les pois crème
FIL = M.hexa("#4b2a24")                       # le sourire
LONG = 0.185                                  # la longueur d'un bras, du centre au bout


def couche(m, mat):
    """Pose une maille par une matrice 4×4 (A.cadre) : le repère de la pièce devient celui de la matrice."""
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def bras(angle, leve=0.0):
    """Un bras : un fuseau tourné, aplati sur la verticale, de plus en plus fin ; il se dresse en crochet si leve > 0.
    angle : sa direction dans le plan du sol, en degrés (0 : vers la gauche de l'étoile, +X)."""
    prof = A.profil([(0, 0), (0.064, 0.004), (0.062, 0.030), (0.050, 0.085), (0.034, 0.135), (0.018, 0.170), (0, LONG)], 4)
    m = A.tour(prof, 28).etire(1.0, 0.66, 1.0)

    def plie(v):
        s = v.copy()
        u = np.clip((v[:, 2] - 0.06) / (LONG - 0.06), 0.0, 1.0)
        s[:, 1] += leve * u ** 1.8                                   # Y est le haut, une fois le bras posé par cadre()
        return s
    m = m.sculpte(plie)
    r = math.radians(angle)
    return couche(m, A.cadre((0, 0, 0.040), (math.cos(r), math.sin(r), 0.0), (0, 0, 1)))


def construire():
    a = K.Animal("etoile_de_mer")
    a.taille = 0.36

    # ----- cinq bras à 72°, le gauche-avant dressé ; un centre bombé -----
    etoile = A.boule(1.0, 40, 20).etire(0.088, 0.088, 0.058).pose((0, 0, 0.046))
    for k in range(5):
        etoile = etoile + bras(90 + 72 * k + 36, leve=0.075 if k == 4 else 0.0)
    a.piece("etoile", etoile, CORAIL, motif=("pois", POIS))

    # ----- le visage cousu sur le centre : deux boutons et un sourire. Les points sont calculés sur le dôme (une ellipsoïde)
    #       au lieu d'un lancer de rayons : le vrai Blender donnait ici des points confondus et une fiche vide -----
    def dome(d):
        """Le point du dôme et sa normale, dans la direction d (de l'étoile vers le haut), depuis le centre (0, 0, 0.040)."""
        d = Vector(d).normalized()
        o = Vector((0.0, 0.0, 0.040 - 0.046))
        rx, ry, rz = 0.088, 0.088, 0.058
        qa = (d.x / rx) ** 2 + (d.y / ry) ** 2 + (d.z / rz) ** 2
        qb = 2.0 * (o.x * d.x / rx ** 2 + o.y * d.y / ry ** 2 + o.z * d.z / rz ** 2)
        qc = (o.x / rx) ** 2 + (o.y / ry) ** 2 + (o.z / rz) ** 2 - 1.0
        s_ = (-qb + math.sqrt(max(qb * qb - 4.0 * qa * qc, 0.0))) / (2.0 * qa)
        q = o + d * s_
        n = Vector((q.x / rx ** 2, q.y / ry ** 2, q.z / rz ** 2)).normalized()
        return Vector((q.x, q.y, q.z + 0.046)), n
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = dome((c * 0.34, -0.40, 0.85))
        a.bouton("oeil_" + nom, pos + n * 0.001, n, 0.020)
    pts = []
    for u in np.linspace(-1, 1, 9):
        p_, n_ = dome((0.46 * u, -0.78, 0.50 + 0.22 * u * u))
        pts.append(tuple(p_ + n_ * 0.002))
    a.broderie("sourire", A.courbe(pts, 4), 0.0022, FIL)

    a.tete = Vector((0.0, -0.040, 0.100))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "etoile", angles_deg=[126, 198, 270, 342, 54])


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("etoile_de_mer", styles.style_de("etoile_de_mer"), sys.modules[__name__]), "Étoile de mer")
