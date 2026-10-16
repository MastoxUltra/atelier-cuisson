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
VISAGE = np.array(M.hexa("#b8744a"))          # le visage, plus clair (la référence : un brun orangé)
AILE = np.array(M.hexa("#5a463c"))            # les ailes, brunes
AILE_BORD = np.array(M.hexa("#d9b48a"))       # leur bord, plus clair
PATTE = np.array(M.hexa("#5a4840"))
FIL = M.hexa("#241a16")


def construire():
    """(16/10, planche 27 : l'auteur veut la bête d'un vrai modèle) : d'après la référence (references_3d/luciole, CC-BY :
    mesurée, rien d'importé), en part de l'envergure : une grosse tête ronde aux gros yeux, un petit thorax, et derrière
    la LANTERNE, une boule aussi grosse que la tête et le thorax ensemble ; deux grandes ailes ouvertes en V au-dessus du
    dos ; six petites pattes sous le thorax ; deux longues antennes."""
    a = K.Animal("luciole")
    a.taille = 0.60                                # l'envergure

    E = 0.60                                       # les mesures de la référence, en part de l'envergure, mises à l'échelle
    def v(x, y, z):
        return Vector((x * E, y * E, z * E))

    # ----- la tête : une grosse boule ronde, le visage plus clair ; deux gros yeux en avant -----
    H = v(0.0, -0.175, 0.235)
    tete = A.boule(1.0, 36, 18).etire(0.135 * E, 0.105 * E, 0.115 * E)
    tete.teinte = np.tile(BRUN, (len(tete.v), 1))
    tete.teinte[(tete.v[:, 1] < -0.45 * 0.105 * E) & (tete.v[:, 2] < 0.35 * 0.115 * E)] = VISAGE      # le visage, devant et en bas
    a.piece("tete", tete, None, pos=tuple(H))
    O.paire_yeux(a, "tete", H, (0.42, -0.86, 0.12), 0.034 * E, decolle=0.003)
    for nom, c in (("G", 1), ("D", -1)):                          # les antennes : de longues tiges qui partent du front
        ant = O.tube_r([(c * 0.035 * E, -0.235 * E, 0.330 * E), (c * 0.075 * E, -0.300 * E, 0.400 * E), (c * 0.125 * E, -0.345 * E, 0.420 * E)],
                       [0.0075, 0.0060, 0.0050], 16)   # 16 côtés : à 8, elles étaient facettées (16/10)
        a.piece("antenne_" + nom, O.teinte(ant, BRUN * 0.8), None, poil=False)
        a.piece("bout_antenne_" + nom, A.boule(1.0, 12, 6).etire(0.009, 0.009, 0.009), tuple(BRUN * 0.8),
                pos=tuple(v(c * 0.125, -0.345, 0.420)), poil=False)
    a.tete = H + v(0.0, -0.10, 0.0)

    # ----- le thorax : court, sous les ailes, à liseré rouge -----
    T = v(0.0, -0.040, 0.215)
    thorax = A.boule(1.0, 32, 16).etire(0.115 * E, 0.085 * E, 0.100 * E)
    thorax.teinte = np.tile(BRUN, (len(thorax.v), 1))
    thorax.teinte[thorax.v[:, 2] > 0.55 * 0.100 * E] = LISERE                              # le bouclier rouge sur le dessus
    a.piece("thorax", thorax, None, pos=tuple(T))

    # ----- la lanterne : une grosse boule jaune lumineuse derrière, aussi grosse que la tête et le thorax ensemble -----
    B = v(0.0, 0.165, 0.185)
    boule = A.boule(1.0, 40, 20).etire(0.160 * E, 0.170 * E, 0.170 * E)
    boule.teinte = np.tile(np.array(LANTERNE), (len(boule.v), 1))
    boule.teinte[boule.v[:, 1] < -0.70 * 0.170 * E] = BRUN                                 # le premier anneau, brun, contre le thorax
    a.piece("lanterne", boule, None, pos=tuple(B))

    # ----- les ailes : deux grandes palettes ouvertes en V au-dessus du dos, vers l'arrière ; plates, en feutrine -----
    for nom, c in (("G", 1), ("D", -1)):
        depart = v(c * 0.040, 0.000, 0.300)
        vers = Vector((c * 0.80, 0.42, 0.42)).normalized()
        W = A.cadre(depart, vers, Vector((0.0, 0.0, 1.0)))
        aile = A.boule(1.0, 36, 12).etire(0.085 * E, 0.012 * E, 0.250 * E).pose((0, 0, 0.235 * E))
        aile.teinte = np.tile(AILE, (len(aile.v), 1))
        aile.teinte[np.hypot(aile.v[:, 0] / (0.085 * E), (aile.v[:, 2] - 0.235 * E) / (0.250 * E)) > 0.82] = AILE_BORD
        a.piece("aile_" + nom, aile, None, mat=W, poil=False)
    a.fusion_a_part = ("aile", "antenne", "bout_antenne")

    # ----- les six pattes : courtes, sous le thorax et la tête, posées au sol -----
    for k, y in enumerate((-0.120, -0.045, 0.030)):
        for nom, c in (("G", 1), ("D", -1)):
            patte = O.tube_r([tuple(v(c * 0.060, y, 0.150)), tuple(v(c * 0.130, y + 0.010, 0.095)), tuple(v(c * 0.160, y + 0.025, 0.012))],
                             [0.0090, 0.0080, 0.0070], 8)
            a.piece("patte_%s%d" % (nom, k), O.teinte(patte, PATTE), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("luciole", styles.style_de("luciole"), sys.modules[__name__]), "Luciole")
