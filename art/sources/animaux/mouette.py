"""La mouette en peluche : la tête et le ventre blancs, le dos gris perle, les bouts d'ailes noirs, un bec jaune à point
rouge grand ouvert : elle crie à la mer, le cou tendu, la poitrine en avant, les ailes à demi décollées du corps comme si
elle allait partir d'un coup. Les pattes roses, palmées, plantées sur le sable ; un œil rond, un peu jaloux.

    python mouette.py        fabrique la fiche art/apercus/animaux/mouette.png (style du palier : A, cousu main)
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

BLANC = np.array(M.hexa("#fbfaf6"))
PERLE = np.array(M.hexa("#aeb7c3"))           # le dos gris perle (la sépare de l'oie blanche)
NOIR = np.array(M.hexa("#2a2a30"))            # le bout des ailes et de la queue
JAUNE = M.hexa("#f7c830")                     # le bec
ROUGE = M.hexa("#e0342a")                     # le point rouge du bec
ROSE = M.hexa("#e89a8a")                      # les pattes
FIL = M.hexa("#4a3a30")


def construire():
    a = K.Animal("mouette")
    a.taille = 0.58

    # ----- le corps : un œuf penché en avant, blanc devant, gris perle sur le dos ; un jabot rond -----
    T = A.repere((0.0, 0.050, 0.120), (30, 0, 0))
    pc = A.profil([(0, 0.0), (0.058, 0.010), (0.100, 0.070), (0.120, 0.160), (0.108, 0.250), (0.076, 0.320), (0.040, 0.360), (0, 0.375)], 6)
    corps = A.tour(pc, 44)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(BLANC, (len(ang), 1))
    t[(ang < 1.25) & (corps.v[:, 2] > 0.04)] = PERLE
    corps.teinte = t
    a.piece("corps", corps, None, mat=T)
    haut = T @ Vector((0, 0, 0.345))

    # ----- le cou et la tête : tendus vers l'avant, le menton levé ; blancs -----
    cou = O.tube_r([haut + Vector((0, 0.01, -0.03)), haut + Vector((0, -0.045, 0.010)), haut + Vector((0, -0.085, 0.040))], [0.056, 0.050, 0.046], 14)
    a.piece("cou", O.teinte(cou, BLANC), None)
    H = haut + Vector((0.0, -0.115, 0.058))
    tete = A.boule(1.0, 40, 20).etire(0.062, 0.078, 0.060)
    a.piece("tete", O.teinte(tete, BLANC), None, pos=tuple(H), rot=(-8, 0, 0))
    a.tete = H + Vector((0.0, -0.10, 0.0))

    # ----- le bec grand ouvert : deux becs jaunes, un point rouge au bout du bec du haut, le gosier sombre -----
    haut_bec = A.tour(A.profil([(0.026, 0), (0.023, 0.040), (0.015, 0.082), (0.007, 0.112), (0, 0.126)], 4), 20).etire(0.80, 0.55, 1.0)
    bas_bec = A.tour(A.profil([(0.022, 0), (0.019, 0.040), (0.012, 0.080), (0.005, 0.106), (0, 0.118)], 4), 20).etire(0.78, 0.50, 1.0)
    a.piece("bec_haut", O.couche(haut_bec, A.cadre(H + Vector((0.0, -0.062, -0.008)), (0.0, -1.0, -0.12), (0, 1, 0))), JAUNE, poil=False)
    a.piece("bec_bas", O.couche(bas_bec, A.cadre(H + Vector((0.0, -0.058, -0.022)), (0.0, -1.0, -0.14), (0, 1, 0))), JAUNE, poil=False)
    a.piece("point", A.boule(1.0, 14, 8).etire(0.012, 0.012, 0.008), ROUGE, mat=A.cadre(H + Vector((0.0, -0.120, -0.034)), (0.0, -1.0, -0.62), (0, 1, 0)),
            poil=False)
    O.paire_yeux(a, "tete", H, (0.78, -0.50, 0.26), 0.0165, decolle=0.002)

    # ----- les ailes : deux grandes lames gris perle, un peu décollées, le bout noir ; la queue blanche -----
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 36, 18).etire(0.030, 0.085, 0.200)
        f = aile.v[:, 2] / 0.200
        t = np.tile(PERLE, (len(f), 1))
        t[f < -0.55] = NOIR
        aile.teinte = t
        a.piece("aile_" + nom, aile, None, mat=T @ A.repere((c * 0.108, 0.034, 0.165), (0, 0, c * 5)))
    queue = A.boule(1.0, 24, 12).etire(0.050, 0.075, 0.014)
    t = np.tile(BLANC, (len(queue.v), 1))
    t[queue.v[:, 1] > 0.060] = NOIR * 0.0 + PERLE
    queue.teinte = t
    a.piece("queue", queue, None, pos=(0.0, 0.205, 0.158), rot=(-22, 0, 0))

    # ----- les pattes roses, palmées, plantées sur le sable -----
    for nom, c in (("G", 1), ("D", -1)):
        jambe = O.tube_r([(c * 0.045, 0.040, 0.130), (c * 0.050, 0.005, 0.070), (c * 0.050, -0.020, 0.014)], [0.014, 0.012, 0.010], 10)
        a.piece("jambe_" + nom, O.teinte(jambe, M.hexa("#e89a8a")), None, poil=False)
        palme = A.boule(1.0, 18, 8).etire(0.036, 0.060, 0.007)
        a.piece("palme_" + nom, O.teinte(palme, M.hexa("#e89a8a")), None, pos=(c * 0.052, -0.050, 0.008), rot=(0, 0, c * 8), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("mouette", styles.style_de("mouette"), sys.modules[__name__]), "Mouette")
