"""Le pélican en peluche (3e dessin, 16/10, d'après les vues d'un vrai pélican blanc) : un nuage blanc rosé, saumon pâle, tout en
bec. Le cou replié en S, le long bec qui descend devant lui, sous lequel pend la poche orange, gonflée comme une besace ; un petit œil de côté, sage et
tranquille, qui voit passer tous les poissons du monde. Les pattes courtes, orange, les ailes repliées en toit.

    python pelican.py        fabrique la fiche art/apercus/animaux/pelican.png (style du palier : C, velours ras)
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

SAUMON = np.array(M.hexa("#f2c5b8"))          # la dominante (registre : blanc rosé saumon pâle)
BLANC = np.array(M.hexa("#fbf4ee"))
AILE = np.array(M.hexa("#e6b3a6"))
BEC = np.array(M.hexa("#e8b58a"))             # le bec, rose chair
POCHE = M.hexa("#f08a2a")                     # l'accent : la poche orange
PATTE = M.hexa("#f08a2a")
SOMBRE = np.array(M.hexa("#5a4a44"))          # le bout des ailes
FIL = M.hexa("#8a4a28")


def construire():
    a = K.Animal("pelican")
    a.taille = 1.55

    # 16/10, 3e dessin (« on dirait pas que c'est depuis un modèle ») : au plus près des vues d'un vrai pélican blanc (CC-BY,
    # rien d'importé). Le corps est un gros œuf COUCHÉ, penché vers l'avant (plus le manchot debout) ; le cou en S se replie,
    # la petite tête posée haut, la peau rose autour de l'œil ; le long bec étroit (un quart de la bête) descend devant le cou,
    # la poche orange pendue dessous ; les ailes repliées, gardées à part, aux rémiges noires ; les pattes courtes, les palmes.

    # ----- le corps : un œuf couché, l'avant relevé, le dos saumon pâle, le ventre blanc -----
    # (2e réglage : l'œuf rond faisait une boule ; le corps d'un pélican est bien plus long que haut)
    T = A.repere((0.0, 0.360, 0.240), (70, 0, 0))                   # l'axe : de la queue (derrière) au poitrail (devant, un peu en haut)
    pc = A.profil([(0, 0.0), (0.100, 0.020), (0.170, 0.120), (0.205, 0.300), (0.200, 0.480), (0.165, 0.640), (0.100, 0.760), (0, 0.820)], 6)
    corps = A.tour(pc, 52)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t_ = np.tile(BLANC, (len(ang), 1))
    t_[(ang < 1.25) & (corps.v[:, 2] > 0.05)] = SAUMON
    corps.teinte = t_
    a.piece("corps", corps, None, mat=T)
    haut = Vector(T @ Vector((0, 0, 0.760)))                        # le haut du poitrail, où part le cou

    # ----- le cou en S qui se replie, la petite tête posée haut au-dessus des épaules -----
    H = haut + Vector((0.0, -0.090, 0.330))                         # le cou en S doux, la tête en avant
    cou = O.tube_r([tuple(haut + Vector((0, 0.020, -0.010))), tuple(haut + Vector((0, -0.065, 0.120))), tuple(haut + Vector((0, -0.045, 0.230))),
                    tuple(H + Vector((0, 0.035, -0.035)))], [0.092, 0.078, 0.070, 0.064], 20)
    a.piece("cou", O.teinte(cou, BLANC), None)
    tete = A.boule(1.0, 40, 20)
    u = tete.v
    tt = np.tile(BLANC, (len(u), 1))
    tt[(u[:, 1] < -0.10) & (np.abs(u[:, 0]) > 0.45) & (u[:, 2] > -0.30) & (u[:, 2] < 0.45)] = np.array(M.hexa("#f2b0a8"))   # la peau rose de l'œil
    tete.teinte = tt
    a.piece("tete", tete.etire(0.068, 0.092, 0.074), None, pos=tuple(H), rot=(10, 0, 0))
    a.tete = H + Vector((0.0, -0.22, -0.08))

    # ----- le bec : long, étroit et plat, un peu crochu au bout ; il descend devant le cou ; la poche orange pendue dessous -----
    LB = 0.460
    sens_bec = Vector((0.0, -1.0, -0.32)).normalized()                 # vers l'avant, un peu vers le bas (il pendait à la verticale)
    B = A.cadre(H + Vector((0.0, -0.072, -0.016)), sens_bec, (0, 0, 1))
    e_ = 0.72
    prof_bec = [(0.046 * e_, 0.0), (0.045 * e_, 0.10 * LB), (0.042 * e_, 0.35 * LB), (0.037 * e_, 0.62 * LB), (0.031 * e_, 0.82 * LB),
                (0.024 * e_, 0.93 * LB), (0.013 * e_, 0.98 * LB), (0, LB)]
    bec = A.tour(A.profil(prof_bec, 4), 28)

    def fer(v):
        s = v.copy()
        t2 = np.clip(v[:, 2] / LB, 0.0, 1.0)
        s[:, 1] = v[:, 1] * 0.32 / e_ + 0.005 * np.sin(np.pi * t2)          # plat, le dessus à peine bombé
        s[:, 1] -= 0.030 * np.clip((t2 - 0.88) / 0.12, 0.0, 1.0) ** 2        # l'onglet : le bout crochu vers le bas
        return s
    bec.sculpte(fer)
    tb = np.tile(BEC, (len(bec.v), 1))
    tb[bec.v[:, 2] > 0.90 * LB] = BEC * 0.78 + np.asarray(POCHE, float) * 0.22
    bec.teinte = tb
    a.piece("bec", O.couche(bec, B), None, poil=False)
    prof_poche = [(0.034, 0.0), (0.050, 0.12 * LB), (0.054, 0.32 * LB), (0.046, 0.55 * LB), (0.030, 0.74 * LB), (0.013, 0.86 * LB), (0, 0.90 * LB)]
    poche = A.tour(A.profil(prof_poche, 5), 32)

    def pendre(v):
        s = v.copy()
        r = np.interp(v[:, 2], [q[1] for q in prof_poche], [q[0] for q in prof_poche])
        s[:, 0] = v[:, 0] * 0.80 * e_
        s[:, 1] = v[:, 1] - r - 0.008
        return s
    poche.sculpte(pendre)
    poche.teinte = np.tile(np.asarray(POCHE, float), (len(poche.v), 1))
    a.piece("poche", poche, None, mat=B)
    O.paire_yeux(a, "tete", H, (0.86, -0.36, 0.30), 0.0165, decolle=0.002)

    # ----- les ailes repliées le long des flancs, gardées à part (on les lit), le bout noir (les rémiges) ; la queue courte -----
    a.fusion_a_part = ("aile",)
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.tour(A.profil([(0, 0), (0.048, 0.030), (0.080, 0.100), (0.082, 0.220), (0.068, 0.360), (0.044, 0.480), (0.020, 0.570),
                                (0, 0.630)], 6), 36)
        zz = aile.v[:, 2]
        aile.teinte = np.where((zz > 0.40)[:, None], tuple(np.array(M.hexa("#26211f"))), tuple(AILE))
        depart = Vector((c * 0.170, -0.250, 0.470))
        vers = Vector((c * 0.030, 0.96, -0.26)).normalized()
        a.piece("aile_" + nom, aile.etire(0.38, 1.00, 1.12), None, mat=A.cadre(depart, vers, Vector((0, 0, 1))))   # de l'épaule à la queue
    queue = A.boule(1.0, 24, 12).etire(0.070, 0.090, 0.022)
    a.piece("queue", O.teinte(queue, BLANC), None, pos=(0.0, 0.420, 0.265), rot=(-20, 0, 0))

    # ----- les pattes courtes et fortes, rose orangé ; les grandes palmes -----
    for nom, c in (("G", 1), ("D", -1)):
        jambe = O.tube_r([(c * 0.095, 0.030, 0.210), (c * 0.100, 0.005, 0.100), (c * 0.103, -0.012, 0.016)], [0.028, 0.023, 0.020], 12)
        a.piece("jambe_" + nom, O.teinte(jambe, PATTE), None, poil=False)
        palme = A.boule(1.0, 20, 8).etire(0.074, 0.105, 0.012)
        a.piece("palme_" + nom, O.teinte(palme, PATTE), None, pos=(c * 0.106, -0.082, 0.012), rot=(0, 0, c * 8), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pelican", styles.style_de("pelican"), sys.modules[__name__]), "Pélican")
