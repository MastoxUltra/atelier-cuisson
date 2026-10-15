"""Le grillon des cavernes en peluche : le bossu pâle des voûtes, brun clair de sable mouillé, le dos en voûte comme un petit
dôme, de grandes pattes arrière repliées en Z, hautes au-dessus du dos, et deux antennes plus longues que lui, qui
balaient le noir en grand. Pas d'ailes, pas d'yeux qui comptent : il goûte le monde du bout des antennes, et le monde
n'a pas encore su lui faire peur.

    python grillon_des_cavernes.py        fabrique la fiche art/apercus/animaux/grillon_des_cavernes.png (style du palier : A, cousu main)
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

BRUN = np.array(M.hexa("#cfb593"))            # la dominante (registre : brun pâle #c9b08f), un cran plus clair (cousu main)
SOMBRE = np.array(M.hexa("#9a7a56"))          # les bandes des pattes, les antennes
CLAIR = np.array(M.hexa("#e6d6bb"))           # le ventre, les articles des pattes
FIL = M.hexa("#5a432a")


def construire():
    a = K.Animal("grillon_des_cavernes")
    a.taille = 0.34

    # ----- le corps : le thorax en dôme, l'abdomen qui s'effile derrière, les deux courtes queues ; le dessous plus clair -----
    pc = A.profil([(0, 0.0), (0.045, 0.006), (0.075, 0.050), (0.085, 0.130), (0.078, 0.210), (0.055, 0.270), (0.026, 0.300), (0, 0.312)], 6)
    corps = A.tour(pc, 36)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(BRUN, (len(ang), 1))
    t[(ang > 2.1)] = CLAIR
    t[(np.sin(corps.v[:, 2] * 52.0) > 0.78) & (ang < 2.0)] = BRUN * 0.88                 # les bandes de l'abdomen
    corps.teinte = t
    a.piece("corps", corps, None, mat=A.repere((0.0, -0.070, 0.176), (-78, 0, 0)))       # couché : l'avant devant, le dos en voûte
    dome = A.boule(1.0, 28, 14).etire(0.070, 0.100, 0.070)
    a.piece("dome", O.teinte(dome, BRUN * 1.02), None, pos=(0.0, 0.020, 0.215))
    tete = A.boule(1.0, 28, 14).etire(0.046, 0.056, 0.048)
    a.piece("tete", O.teinte(tete, BRUN * 0.98), None, pos=(0.0, -0.170, 0.150), rot=(-12, 0, 0))
    for c in (1, -1):
        cerque = O.tube_r([(c * 0.014, 0.300, 0.115), (c * 0.034, 0.350, 0.108), (c * 0.050, 0.395, 0.100)], [0.0085, 0.0065, 0.0040], 8)
        a.piece("cerque_%d" % c, O.teinte(cerque, SOMBRE), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        a.oeil("oeil_" + nom, Vector((c * 0.030, -0.212, 0.176)), Vector((c * 0.55, -0.80, 0.30)).normalized(), 0.0270)
        # les antennes : plus longues que le corps, balayant en arc vers le haut et le dehors
        ant = O.tube_r([(c * 0.014, -0.208, 0.168), (c * 0.110, -0.360, 0.300), (c * 0.300, -0.450, 0.440), (c * 0.520, -0.420, 0.470),
                        (c * 0.690, -0.320, 0.400)], [0.0070, 0.0058, 0.0046, 0.0036, 0.0026], 8)
        a.piece("antenne_" + nom, O.teinte(ant, SOMBRE), None, poil=False)
        # les pattes avant et du milieu : fines, le genou levé
        for k, (y0, yk, yp) in enumerate(((-0.090, -0.160, -0.215), (0.000, -0.020, -0.040))):
            pt = O.tube_r([(c * 0.050, y0, 0.150), (c * 0.150, yk, 0.150 + 0.030 * k), (c * 0.190, yp, 0.012)], [0.0125, 0.0095, 0.0060], 10)
            pt = pt + A.boule(1.0, 12, 6).etire(0.011, 0.011, 0.008).pose((c * 0.190, yp, 0.010))
            a.piece("patte_%s%d" % (nom, k), O.teinte(pt, CLAIR * 0.95 + BRUN * 0.05), None, poil=False)
        # la grande patte arrière : la cuisse géante qui monte au-dessus du dos, le tibia qui revient, trois éperons
        cuisse = O.tube_r([(c * 0.060, 0.070, 0.150), (c * 0.120, 0.180, 0.300), (c * 0.150, 0.310, 0.330)], [0.034, 0.030, 0.016], 14)
        cuisse.teinte = np.tile(BRUN, (len(cuisse.v), 1))
        tibia = O.tube_r([(c * 0.150, 0.310, 0.330), (c * 0.215, 0.250, 0.170), (c * 0.250, 0.150, 0.014)], [0.014, 0.011, 0.0075], 10)
        tibia.teinte = np.tile(SOMBRE, (len(tibia.v), 1))
        a.piece("cuisse_" + nom, cuisse, None, poil=False)
        a.piece("tibia_" + nom, tibia, None, poil=False)
        for s_, t_ in enumerate((0.28, 0.52, 0.76)):
            px = c * (0.150 + 0.100 * t_ if t_ > 0 else 0.150)
            py = 0.310 - 0.160 * t_
            pz = 0.330 - 0.316 * t_
            ep = O.couche(O.teinte(O.pointe(0.026, 0.0060, 6), SOMBRE * 0.8), A.cadre(Vector((px, py, pz)), Vector((c * 0.55, -0.20, -0.45)), (0, 0, 1)))
            a.piece("eperon_%s%d" % (nom, s_), ep, None, poil=False)
    a.tete = Vector((0.0, -0.200, 0.170))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("grillon_des_cavernes", styles.style_de("grillon_des_cavernes"), sys.modules[__name__]), "Grillon des cavernes")
