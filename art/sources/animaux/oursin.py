"""L'oursin en peluche : une boule prune foncé hérissée de piquants plus clairs, plantée sur ses petits pieds. Il a l'air
de mauvais poil : les yeux à moitié clos sous une lourde paupière, la bouche tirée vers le bas, les piquants dressés en
tous sens, quelques-uns couchés d'un côté comme après une nuit agitée. Personne ne le touche, et c'est très bien comme ça.

    python oursin.py        fabrique la fiche art/apercus/animaux/oursin.png (style du palier : A, cousu main)
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

PRUNE = M.hexa("#70385d")                     # la dominante (registre du 14/10 : prune foncé) ; le poil fonce un peu
PIQUANT = np.array(M.hexa("#c68fb2"))         # l'accent : les piquants, plus clairs
POINTE = np.array(M.hexa("#f0d6e4"))          # leur bout, presque rose pâle
FIL = M.hexa("#241216")                       # la bouche
R = 0.098                                     # le rayon du corps
CENTRE = Vector((0.0, 0.0, 0.100))


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def piquant(long, base=0.0092):
    """Un piquant : un cône de feutrine un peu rond, clair au bout."""
    m = A.tour(A.profil([(base, 0), (0.78 * base, 0.30 * long), (0.46 * base, 0.64 * long), (0.18 * base, 0.90 * long), (0, long)], 4), 10)
    t = np.clip(m.v[:, 2] / long, 0.0, 1.0)[:, None] ** 1.4
    m.teinte = PIQUANT * (1 - t) + POINTE * t
    return m


def construire():
    a = K.Animal("oursin")
    a.taille = 0.40

    # ----- le corps : une boule un peu écrasée, pleine -----
    a.piece("corps", A.boule(1.0, 48, 24).etire(R, R, 0.90 * R).pose(CENTRE), PRUNE)

    # ----- les piquants : une trentaine d'une spirale, repoussés du visage, jamais sous le ventre -----
    avant = Vector((0.0, -1.0, 0.10)).normalized()
    herisson = None
    n = 62
    for k in range(n):
        z = 1 - 2 * (k + 0.5) / n
        ang = math.pi * (3 - math.sqrt(5)) * k
        r = math.sqrt(1 - z * z)
        d = Vector((r * math.cos(ang), r * math.sin(ang), z))
        if d.z < -0.30 or d.dot(avant) > 0.74:
            continue
        long = 0.060 + 0.030 * math.sin(2.7 * k) ** 2
        d_ = (d + Vector((0.20, 0.0, 0.0)) * (1 if d.x > 0 and d.z > 0 else 0)).normalized()      # le côté gauche est couché
        haut = (0, 0, 1) if abs(d_.z) < 0.9 else (0, 1, 0)
        m = couche(piquant(long), A.cadre(CENTRE + d * (0.90 * R), d_, haut))
        herisson = m if herisson is None else herisson + m
    a.piece("piquants", herisson, None, poil=False)

    # ----- le visage : les yeux sous une lourde paupière, la bouche tirée vers le bas, les sourcils froncés -----
    centre = CENTRE
    for nom, c in (("G", 1), ("D", -1)):
        pos, n_ = a.surface("corps", centre, Vector((c * 0.34, -0.90, 0.16)))
        a.bouton("oeil_" + nom, pos + n_ * 0.002, n_, 0.0210)
        haut_oeil = (Vector((0, 0, 1)) - n_ * n_.z).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.0210, 0.02), PRUNE, mat=A.cadre(pos + n_ * 0.002, n_, haut_oeil), poil=False)
    bouche = [Vector((0.38 * u, -0.92, -0.20 - 0.14 * u * u)) for u in np.linspace(-1, 1, 9)]
    a.broderie("bouche", A.courbe(a.trace("corps", centre, bouche, 0.003), 4), 0.0024, FIL)

    a.tete = CENTRE + Vector((0.0, -0.090, 0.0))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "fixe")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("oursin", styles.style_de("oursin"), sys.modules[__name__]), "Oursin")
