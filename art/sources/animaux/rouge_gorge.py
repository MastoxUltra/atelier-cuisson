"""Le rouge-gorge en peluche : une boule de plumes brun gris, le plastron orange rouge vif qui lui monte du ventre
jusqu'aux joues comme un tablier, de grands yeux noirs bien ronds. Il se tient droit sur ses pattes grêles, le poitrail en
avant, la queue relevée, la tête un peu penchée : il est chez lui, ici, c'est son jardin, et il aime qu'on le sache.

    python rouge_gorge.py        fabrique la fiche art/apercus/animaux/rouge_gorge.png (style du palier : A, cousu main)
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

BRUN = np.array(M.hexa("#9a8670"))            # la dominante (registre : dos brun gris)
ORANGE = np.array(M.hexa("#f2561c"))          # l'accent : le plastron
CLAIR = np.array(M.hexa("#e8dccc"))           # le ventre bas
GRIS = np.array(M.hexa("#c6c0b6"))            # le lisere gris autour du plastron
BEC = M.hexa("#3a2f2a")
PATTE = M.hexa("#7a5a4a")


def construire():
    a = K.Animal("rouge_gorge")
    a.taille = 0.30

    r = O.oiseau(a, dos=BRUN, ventre=CLAIR, tete=BRUN, aile=BRUN * 0.92, queue=BRUN * 0.88, bec=BEC, patte=PATTE, long=0.27, ray=0.098,
                 incline=22.0, z0=0.095, tete_r=(0.062, 0.066, 0.060), tete_pos=(0.0, -0.075, 0.046), bec_long=0.034, bec_ray=0.0135,
                 aile_dim=(0.024, 0.070, 0.150), aile_pos=(0.0, 0.020, 0.0), queue_dim=(0.034, 0.070, 0.012), queue_haut=-36.0,
                 patte_long=0.075, patte_ray=0.0075, oeil_r=0.0170, oeil_dir=(0.74, -0.54, 0.18), coupe_dos=1.1)
    H, T, haut = r["H"], r["T"], r["haut"]

    # ----- le plastron : une grosse tache orange qui part du ventre, monte sur la gorge et déborde sur la face ;
    #       un lisere gris tout autour -----
    lisere = A.boule(1.0, 28, 14).etire(0.090, 0.064, 0.130)
    a.piece("lisere", O.teinte(lisere, GRIS), None, pos=tuple(T @ Vector((0.0, -0.062, 0.215))), rot=(14, 0, 0))
    plastron = A.boule(1.0, 28, 14).etire(0.082, 0.062, 0.120)
    a.piece("plastron", O.teinte(plastron, ORANGE), None, pos=tuple(T @ Vector((0.0, -0.070, 0.220))), rot=(14, 0, 0))
    face = A.boule(1.0, 28, 14).etire(0.050, 0.040, 0.048)
    a.piece("face", O.teinte(face, ORANGE), None, pos=tuple(H + Vector((0.0, -0.036, -0.020))))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("rouge_gorge", styles.style_de("rouge_gorge"), sys.modules[__name__]), "Rouge-gorge")
