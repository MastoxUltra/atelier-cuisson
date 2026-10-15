"""Le macareux en peluche : le clown des falaises, noir et blanc, la face blanche comme un masque, et le bec : un grand
triangle de feutrine rayé d'orange, de bleu ardoise et de jaune, trop gros pour sa tête, qu'il porte avec fierté.
Debout comme un petit monsieur sur ses pattes orange, les ailes noires un peu écartées, le poitrail blanc bombé, l'œil
cerné de rouge sous un triangle gris : il a l'air d'un contrôleur qui a perdu son carnet.

    python macareux.py        fabrique la fiche art/apercus/animaux/macareux.png (style du palier : C, velours ras)
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

NOIR = np.array(M.hexa("#26262e"))            # la dominante (registre : noir et blanc)
BLANC = np.array(M.hexa("#fbf9f2"))
ORANGE = np.array(M.hexa("#f2762a"))          # l'accent : le bec, les pattes
BLEU = np.array(M.hexa("#5f7ca0"))            # la bande bleu ardoise du bec
JAUNE = np.array(M.hexa("#f5c63a"))
GRIS = M.hexa("#7c7f88")
ROUGE = M.hexa("#e0382a")
FIL = M.hexa("#1d1a1d")


def construire():
    a = K.Animal("macareux")
    a.taille = 0.40

    # ----- le corps : un œuf droit, noir dans le dos, blanc devant, légèrement penché en avant -----
    T = A.repere((0.0, 0.020, 0.058), (8, 0, 0))
    pc = A.profil([(0, 0.0), (0.060, 0.008), (0.098, 0.060), (0.112, 0.150), (0.100, 0.240), (0.074, 0.305), (0.040, 0.340), (0, 0.352)], 6)
    corps = A.tour(pc, 44)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(NOIR, (len(ang), 1))
    t[(ang > 1.25) & (corps.v[:, 2] > 0.02)] = BLANC
    corps.teinte = t
    a.piece("corps", corps, None, mat=T)

    # ----- la tête : ronde, la face blanche en masque, la calotte et la nuque noires ; l'œil cerné de rouge, un triangle gris -----
    H = Vector((0.0, -0.020, 0.405))
    tete = A.boule(1.0, 44, 22)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(NOIR, (len(u), 1))
    t[(u[:, 1] < 0.10) & (u[:, 2] < 0.62) & (np.abs(u[:, 0]) > 0.0)] = BLANC          # la face
    t[(u[:, 2] < -0.35)] = BLANC
    tete.teinte = t
    a.piece("tete", tete.etire(0.100, 0.095, 0.092), None, pos=tuple(H))
    a.tete = H + Vector((0.0, -0.10, 0.0))
    O.paire_yeux(a, "tete", H, (0.62, -0.70, 0.22), 0.0150, decolle=0.002)
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", H, Vector((c * 0.62, -0.70, 0.22)))
        a.piece("cerne_" + nom, A.tore(0.0215, 0.0045, 24, 6), ROUGE, mat=A.cadre(pos + n * 0.001, n), poil=False)

    # ----- le bec : un grand triangle aplati sur les côtés, trois bandes (jaune, orange, bleu) ; une rainure -----
    bec = A.tour(A.profil([(0.062, 0), (0.060, 0.030), (0.048, 0.070), (0.026, 0.108), (0.008, 0.126), (0, 0.132)], 4), 28)
    bec = bec.etire(0.50, 1.0, 1.0)
    f = bec.v[:, 2] / 0.132
    t = np.tile(ORANGE, (len(f), 1))
    t[f < 0.20] = BLEU
    t[(f >= 0.20) & (f < 0.34)] = JAUNE
    bec.teinte = t
    a.piece("bec", O.couche(bec, A.cadre(H + Vector((0.0, -0.080, -0.012)), (0.0, -1.0, -0.06), (0, 1.0, 0))), None, poil=False)

    # ----- les ailes noires, un peu écartées ; la queue ; les pattes orange, à plat -----
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 28, 14).etire(0.020, 0.058, 0.148)
        a.piece("aile_" + nom, O.teinte(aile, NOIR), None, mat=T @ A.repere((c * 0.108, 0.020, 0.185), (0, 0, c * 10)))
        jambe = O.tube_r([(c * 0.040, -0.005, 0.070), (c * 0.045, -0.020, 0.035), (c * 0.046, -0.030, 0.008)], [0.012, 0.011, 0.010], 8)
        a.piece("jambe_" + nom, O.teinte(jambe, ORANGE), None, poil=False)
        pied = A.boule(1.0, 16, 8).etire(0.032, 0.056, 0.007)
        a.piece("pied_" + nom, O.teinte(pied, ORANGE), None, pos=(c * 0.048, -0.056, 0.008), rot=(0, 0, c * 8), poil=False)
    queue = A.boule(1.0, 18, 8).etire(0.030, 0.045, 0.010)
    a.piece("queue", O.teinte(queue, NOIR), None, pos=(0.0, 0.130, 0.060), rot=(20, 0, 0))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("macareux", styles.style_de("macareux"), sys.modules[__name__]), "Macareux")
