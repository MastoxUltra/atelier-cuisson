"""La luciole en peluche : un petit scarabée brun noir, deux élytres lisses, un thorax à liseré rouge, de longues antennes,
et surtout le derrière : un ventre-lanterne jaune lumineux qu'elle lève fièrement vers le ciel, comme une lampe de poche
qu'on a allumée trop tôt. Posée sur ses six pattes grêles, la tête baissée, elle a l'air d'avoir oublié ce qu'elle
cherchait, et de s'en moquer, puisque tout le monde la voit.

    python luciole.py        fabrique la fiche art/apercus/animaux/luciole.png (style du palier : A, cousu main)
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

BRUN = np.array(M.hexa("#4a3a34"))            # la dominante (registre : brun noir) ; le poil fonce un peu : un cran plus clair
LISERE = np.array(M.hexa("#c8452e"))          # le liseré rouge du thorax
LANTERNE = M.hexa("#fff25a")                  # l'accent : le ventre-lanterne
HALO = M.hexa("#fffbc0")
PATTE = np.array(M.hexa("#5a4840"))
FIL = M.hexa("#241a16")


def construire():
    a = K.Animal("luciole")
    a.taille = 0.30

    # ----- le thorax : un bouclier bombé à liseré rouge, la tête cachée dessous ; les élytres : deux lames brunes écartées -----
    thorax = A.boule(1.0, 36, 18).etire(0.070, 0.062, 0.050)
    thorax.teinte = np.tile(BRUN, (len(thorax.v), 1))
    a.piece("thorax", thorax, None, pos=(0.0, -0.050, 0.125))
    lisere = A.tore(0.055, 0.0085, 32, 8).etire(1.0, 0.9, 1.0)
    a.piece("lisere", O.teinte(lisere, LISERE), None, pos=(0.0, -0.050, 0.118), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        elytre = A.boule(1.0, 32, 14).etire(0.036, 0.140, 0.034)
        elytre.teinte = np.tile(BRUN * 0.88, (len(elytre.v), 1))
        a.piece("elytre_" + nom, elytre, None, pos=(c * 0.040, 0.085, 0.132), rot=(-8, 0, c * 4))

    # ----- le ventre-lanterne : un gros bout jaune lumineux qui dépasse des élytres et se lève ; un halo plus pâle -----
    ventre = A.tour(A.profil([(0, 0), (0.040, 0.012), (0.062, 0.060), (0.066, 0.130), (0.052, 0.200), (0.026, 0.250), (0, 0.272)], 5), 32)  # un abdomen effilé, pas une balle
    ventre = ventre.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] * 0.88, v[:, 2]], axis=1))
    a.piece("lanterne", ventre, LANTERNE, pos=(0.0, 0.170, 0.150), rot=(-100, 0, 0))
    halo = A.boule(1.0, 28, 14).etire(0.040, 0.050, 0.032)
    a.piece("halo", halo, HALO, pos=(0.0, 0.292, 0.165), rot=(-18, 0, 0), poil=False)

    # ----- la tête : une petite boule noire sous le thorax, deux gros boutons, les longues antennes -----
    H = Vector((0.0, -0.120, 0.100))
    tete = A.boule(1.0, 28, 14).etire(0.044, 0.040, 0.038)
    a.piece("tete", O.teinte(tete, BRUN * 0.8), None, pos=tuple(H))
    O.paire_yeux(a, "tete", H, (0.62, -0.75, 0.20), 0.0240, decolle=0.003)
    for nom, c in (("G", 1), ("D", -1)):
        ant = O.tube_r([(c * 0.020, -0.150, 0.115), (c * 0.050, -0.215, 0.160), (c * 0.075, -0.265, 0.150)], [0.0058, 0.0050, 0.0040], 8)
        a.piece("antenne_" + nom, O.teinte(ant, BRUN * 0.8), None, poil=False)
    a.tete = H + Vector((0.0, -0.06, 0.0))

    # ----- les six pattes : fines, repliées en genou, posées de chaque côté -----
    for k, y in enumerate((-0.040, 0.010, 0.060)):
        for nom, c in (("G", 1), ("D", -1)):
            genou = (c * (0.115 + 0.012 * k), y - 0.020 + 0.010 * k, 0.095)
            patte = O.tube_r([(c * 0.050, y, 0.108), genou, (c * (0.150 + 0.010 * k), y + 0.040, 0.007)], [0.0085, 0.0075, 0.0060], 8)
            a.piece("patte_%s%d" % (nom, k), O.teinte(patte, PATTE), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("luciole", styles.style_de("luciole"), sys.modules[__name__]), "Luciole")
