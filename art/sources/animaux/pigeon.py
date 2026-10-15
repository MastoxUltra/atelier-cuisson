"""Le pigeon en peluche : un gros ballon gris ardoise clair, le cou irisé de reflets violets, qui se promène en
dodelinant, le poitrail bombé en avant, la tête qui précède le corps. Les pattes roses, un petit œil orange rond,
deux bandes sombres sur les ailes : il a l'air de chercher des miettes, et il en trouve toujours.

    python pigeon.py        fabrique la fiche art/apercus/animaux/pigeon.png (style du palier : A, cousu main)
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

ARDOISE = np.array(M.hexa("#9aa5b4"))         # la dominante (registre : gris ardoise clair)
CLAIR = np.array(M.hexa("#bcc4cf"))           # le ventre
VIOLET = np.array(M.hexa("#8a5fb0"))          # les reflets du cou
VERT = np.array(M.hexa("#7a8fc2"))            # le reflet bleuté (jamais de vert franc)
SOMBRE = np.array(M.hexa("#5a6272"))          # les bandes des ailes
BEC = M.hexa("#6a6068")
CIRE = M.hexa("#e8e2da")
ROSE = M.hexa("#e58a98")                      # les pattes
OEIL = M.hexa("#f08a2a")


def construire():
    a = K.Animal("pigeon")
    a.taille = 0.44

    r = O.oiseau(a, dos=ARDOISE, ventre=CLAIR, tete=ARDOISE, aile=ARDOISE * 0.96, queue=SOMBRE, bec=BEC, patte=ROSE, long=0.36, ray=0.128,
                 incline=34.0, z0=0.120, tete_r=(0.066, 0.072, 0.064), tete_pos=(0.0, -0.100, 0.052), bec_long=0.046, bec_ray=0.0150, bec_suit=True,
                 aile_dim=(0.030, 0.100, 0.200), aile_pos=(0.0, 0.020, 0.0), queue_dim=(0.052, 0.100, 0.014), queue_haut=-18.0,
                 patte_long=0.090, patte_ray=0.0115, oeil_r=0.0150, oeil_dir=(0.76, -0.52, 0.18), coupe_dos=1.25)
    H, T, haut = r["H"], r["T"], r["haut"]

    # ----- le cou irisé : un collier de reflets violets et bleutés qui entoure la base de la tête -----
    for k, (c, h) in enumerate(((VIOLET, 0.0), (VERT, -0.022))):
        col = A.tore(0.052 - 0.006 * k, 0.020, 28, 8)
        a.piece("collier_%d" % k, O.teinte(col, c), None, pos=tuple(haut + Vector((0.0, -0.038, 0.024 + h))), rot=(60, 0, 0))
    # ----- la cire blanche à la base du bec, deux bandes sombres sur chaque aile -----
    cire = A.boule(1.0, 16, 8).etire(0.016, 0.014, 0.012)
    a.piece("cire", cire, CIRE, pos=tuple(H + Vector((0.0, -0.070, -0.002))), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        for k, dz in enumerate((0.040, -0.030)):
            band = A.boule(1.0, 16, 8).etire(0.012, 0.020, 0.054)
            a.piece("bande_%s%d" % (nom, k), O.teinte(band, SOMBRE), None, mat=T @ A.repere((c * 0.128, 0.030, 0.185 + dz), (0, 0, c * 5)), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pigeon", styles.style_de("pigeon"), sys.modules[__name__]), "Pigeon")
