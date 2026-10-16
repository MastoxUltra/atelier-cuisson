"""Le pélican en peluche : un nuage blanc rosé, saumon pâle, tout en bec. Le cou replié en S sur la poitrine, le bec
énorme posé sur le jabot, sous lequel pend la poche orange, gonflée comme une besace ; un petit œil de côté, sage et
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

    # ----- le corps : un gros œuf, un peu penché, le dos saumon, le ventre blanc -----
    T = A.repere((0.0, 0.080, 0.300), (20, 0, 0))
    pc = A.profil([(0, 0.0), (0.150, 0.015), (0.250, 0.090), (0.285, 0.230), (0.250, 0.380), (0.170, 0.500), (0.080, 0.570), (0, 0.600)], 6)
    corps = A.tour(pc, 52)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(BLANC, (len(ang), 1))
    t[(ang < 1.3) & (corps.v[:, 2] > 0.05)] = SAUMON
    corps.teinte = t
    a.piece("corps", corps, None, mat=T)
    haut = Vector(T @ Vector((0, 0, 0.545)))

    # ----- le cou en S sur le jabot, la tête petite, le bec énorme posé sur la poitrine, la poche qui pend dessous -----
    cou = O.tube_r([haut + Vector((0, 0.02, 0.00)), haut + Vector((0, 0.04, 0.12)), haut + Vector((0, -0.06, 0.26)),
                    haut + Vector((0, -0.20, 0.32)), haut + Vector((0, -0.30, 0.30))], [0.115, 0.095, 0.082, 0.075, 0.070], 20)
    a.piece("cou", O.teinte(cou, BLANC), None)
    H = haut + Vector((0.0, -0.320, 0.280))      # la tête loin devant la poitrine : le bec et la poche pendent dans le vide
    tete = A.boule(1.0, 40, 20).etire(0.075, 0.095, 0.080)
    a.piece("tete", O.teinte(tete, BLANC), None, pos=tuple(H), rot=(20, 0, 0))
    a.tete = H + Vector((0.0, -0.20, -0.04))

    # le bec (refait le 16/10, planche 21 : « le bec bizarre ») : un long fer PLAT et droit, un peu bombé sur le dessus,
    # qui finit par un petit crochet vers le BAS (l'onglet) ; l'ancien remontait en spatule (son repère avait l'axe y vers
    # le bas). Le repère a maintenant y vers le haut : z le long du bec, x sur le côté.
    LB = 0.460                                                               # 2e essai : plus long et plus à plat (il plongeait
    sens_bec = Vector((0.0, -1.0, -0.24)).normalized()                       # contre la poitrine et se lisait mal)
    k_ = LB / 0.400
    B = A.cadre(H + Vector((0.0, -0.068, -0.024)), sens_bec, (0, 0, 1))
    prof_bec = [(0.050, 0.0), (0.049, 0.060 * k_), (0.045, 0.160 * k_), (0.040, 0.260 * k_), (0.035, 0.335 * k_), (0.029, 0.372 * k_),
                (0.017, 0.392 * k_), (0, LB)]
    bec = A.tour(A.profil(prof_bec, 4), 28)

    def fer(v):
        s = v.copy()
        t = np.clip(v[:, 2] / LB, 0.0, 1.0)
        s[:, 1] = v[:, 1] * 0.32 + 0.006 * np.sin(np.pi * t)                 # plat, le dessus à peine bombé
        s[:, 1] -= 0.034 * np.clip((t - 0.86) / 0.14, 0.0, 1.0) ** 2          # l'onglet : le bout crochu vers le bas
        return s
    bec.sculpte(fer)
    tb = np.tile(BEC, (len(bec.v), 1))
    tb[bec.v[:, 2] > 0.90 * LB] = BEC * 0.80 + np.asarray(POCHE, float) * 0.20                # l'onglet plus soutenu
    bec.teinte = tb
    a.piece("bec", O.couche(bec, B), None, poil=False)
    # la poche : la peau orange sous la mandibule, qui l'épouse sur presque toute sa longueur (sa ligne du haut colle au
    # dessous du bec), la plus profonde au premier tiers, et qui rejoint la gorge (fondue avec elle par la base gonflée)
    prof_poche = [(0.040, 0.0), (0.056, 0.070 * k_), (0.060, 0.140 * k_), (0.050, 0.220 * k_), (0.033, 0.290 * k_), (0.015, 0.334 * k_),
                  (0, 0.350 * k_)]
    poche = A.tour(A.profil(prof_poche, 5), 32)

    def pendre(v):
        s = v.copy()
        r = np.interp(v[:, 2], [p[1] for p in prof_poche], [p[0] for p in prof_poche])
        s[:, 0] = v[:, 0] * 0.80                                             # un peu moins large que le bec
        s[:, 1] = v[:, 1] - r - 0.010                                        # pendue : le haut sous la mandibule
        return s
    poche.sculpte(pendre)
    poche.teinte = np.tile(np.asarray(POCHE, float), (len(poche.v), 1))
    a.piece("poche", poche, None, mat=B)
    O.paire_yeux(a, "tete", H, (0.88, -0.30, 0.30), 0.0175, decolle=0.002)

    # ----- les ailes repliées en toit, le bout sombre ; la queue courte ; les pattes courtes, orange -----
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 36, 18).etire(0.040, 0.110, 0.300)
        f = aile.v[:, 2] / 0.300
        t = np.tile(AILE, (len(f), 1))
        t[f < -0.62] = SOMBRE
        aile.teinte = t
        a.piece("aile_" + nom, aile, None, mat=T @ A.repere((c * 0.255, 0.050, 0.330), (0, 0, c * 6)))
        jambe = O.tube_r([(c * 0.110, 0.050, 0.130), (c * 0.120, 0.000, 0.065), (c * 0.120, -0.030, 0.012)], [0.032, 0.026, 0.022], 12)
        a.piece("jambe_" + nom, O.teinte(jambe, PATTE), None, poil=False)
        palme = A.boule(1.0, 20, 8).etire(0.068, 0.100, 0.010)
        a.piece("palme_" + nom, O.teinte(palme, PATTE), None, pos=(c * 0.124, -0.090, 0.011), rot=(0, 0, c * 6), poil=False)
    queue = A.boule(1.0, 24, 12).etire(0.065, 0.100, 0.020)
    a.piece("queue", O.teinte(queue, AILE), None, pos=(0.0, 0.440, 0.240), rot=(-26, 0, 0))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pelican", styles.style_de("pelican"), sys.modules[__name__]), "Pélican")
