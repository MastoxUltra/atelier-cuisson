"""Le martin-pêcheur en peluche : le joyau de la rivière, le dos et la calotte d'un bleu cobalt lumineux, le poitrail
orange roux, une tache blanche à la gorge, les pattes rouges, un bec long comme un poignard. Tout en avant : le corps
penché à quarante-cinq degrés, la tête enfoncée dans les épaules, le bec pointé vers le bas : il a vu un poisson et il
compte jusqu'à trois. Une queue ridiculement courte.

    python martin_pecheur.py        fabrique la fiche art/apercus/animaux/martin_pecheur.png (style du palier : C, velours ras)
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

COBALT = np.array(M.hexa("#2650c8"))          # la dominante (registre : bleu cobalt lumineux)
CIEL = np.array(M.hexa("#58b6e0"))            # la bande du dos, les rayures de la calotte
ORANGE = np.array(M.hexa("#e8782a"))          # le poitrail
BLANC = np.array(M.hexa("#f8f2e4"))
ROUGE = M.hexa("#dc3a2a")                     # les pattes
BEC = M.hexa("#1d1a1c")
FIL = M.hexa("#1d1a1c")


def construire():
    a = K.Animal("martin_pecheur")
    a.taille = 0.30

    # ----- le corps : un œuf court, penché en avant de 40° ; cobalt dessus, orange roux dessous, un trait ciel sur le dos -----
    pc = A.profil([(0, 0.0), (0.060, 0.008), (0.098, 0.050), (0.108, 0.120), (0.092, 0.200), (0.062, 0.265), (0.030, 0.300), (0, 0.312)], 6)
    corps = A.tour(pc, 44)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    z = corps.v[:, 2]
    t = np.tile(COBALT, (len(z), 1))
    t[(ang > 1.65)] = ORANGE
    t[(ang < 0.28) & (z > 0.06) & (z < 0.26)] = CIEL
    t[(ang > 1.60) & (z > 0.215) & (np.abs(corps.v[:, 0]) < 0.040)] = BLANC          # la gorge
    corps.teinte = t
    T = A.repere((0.0, 0.020, 0.115), (46, 0, 0))
    a.piece("corps", corps, None, mat=T)
    haut = Vector(T @ Vector((0, 0.0, 0.250)))

    # ----- la tête : grosse, écrasée dans les épaules ; la calotte cobalt à rayures ciel, la joue orange, la tache blanche -----
    H = Vector((0.0, -0.100, 0.275))
    tete = A.boule(1.0, 48, 24)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(COBALT, (len(u), 1))
    t[(u[:, 2] < 0.10) & (np.abs(u[:, 0]) > 0.35)] = ORANGE
    t[(np.abs(u[:, 0]) > 0.70) & (u[:, 1] < -0.25) & (u[:, 2] < 0.45)] = BLANC * 0.0 + ORANGE
    t[(u[:, 2] > 0.55) & (np.sin(u[:, 0] * 14) > 0.6)] = CIEL                # les rayures de la calotte
    t[(u[:, 1] > 0.30) & (u[:, 2] < 0.25) & (np.abs(u[:, 0]) > 0.55)] = BLANC     # la tache blanche, sur le côté du cou
    tete.teinte = t
    a.piece("tete", tete.etire(0.088, 0.092, 0.080), None, pos=tuple(H), rot=(20, 0, 0))
    a.tete = H + Vector((0.0, -0.08, 0.0))

    # ----- le bec : long comme un poignard, noir, légèrement baissé -----
    bec = A.tour(A.profil([(0.026, 0.0), (0.022, 0.040), (0.015, 0.085), (0.008, 0.125), (0, 0.150)], 4), 20)
    a.piece("bec", bec.etire(1.0, 0.82, 1.0), BEC, mat=A.cadre(H + Vector((0.0, -0.085, -0.010)), (0.0, -1.0, -0.55), (0, 0.5, 1)), poil=False)

    # ----- les yeux : petits et perçants, un trait noir au bec ; la queue courte ; les pattes rouges, minuscules -----
    O.paire_yeux(a, "tete", H, (0.70, -0.62, 0.20), 0.0145, couleur_lourde=tuple(COBALT), coupe=0.60, decolle=0.002)
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 28, 14).etire(0.020, 0.040, 0.110)
        aile.teinte = np.tile(COBALT * 0.88, (len(aile.v), 1))
        a.piece("aile_" + nom, aile, None, mat=T @ A.repere((c * 0.098, 0.012, 0.150)))
        patte = O.tube_r([(c * 0.030, -0.030, 0.060), (c * 0.032, -0.040, 0.030), (c * 0.036, -0.058, 0.004)], [0.009, 0.0085, 0.0075], 8)
        a.piece("patte_" + nom, O.teinte(patte, M.hexa("#dc3a2a")), None, poil=False)
        pied = A.boule(1.0, 14, 8).etire(0.018, 0.034, 0.006)
        a.piece("pied_" + nom, O.teinte(pied, M.hexa("#dc3a2a")), None, pos=(c * 0.036, -0.066, 0.006), poil=False)
    queue = A.boule(1.0, 20, 10).etire(0.030, 0.050, 0.012)
    a.piece("queue", O.teinte(queue, COBALT * 0.85), None, pos=(0.0, 0.200, 0.160), rot=(-34, 0, 0))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("martin_pecheur", styles.style_de("martin_pecheur"), sys.modules[__name__]), "Martin-pêcheur")
