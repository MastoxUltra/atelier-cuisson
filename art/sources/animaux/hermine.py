"""L'hermine en peluche : la plus nerveuse des petites bêtes, brun chaud dessus, ventre crème, et le bout de la queue
noir comme une plume trempée dans l'encre. Elle bondit en arc : le long corps souple plié en cloche, les quatre pattes
rassemblées, le cou tendu, la tête haute et les yeux brillants. La robe d'été, bien sûr : l'hiver, c'est une autre robe.

    python hermine.py        fabrique la fiche art/apercus/animaux/hermine.png (style du palier : C, velours ras)
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

BRUN = np.array(M.hexa("#b27a46"))            # la dominante (registre : brun chaud l'été) ; le velours éclaircit
CREME = np.array(M.hexa("#f5ead2"))           # le ventre, le menton
NOIR = np.array(M.hexa("#1c1816"))            # le bout de la queue
NEZ = M.hexa("#2a1c18")
FIL = M.hexa("#4a3220")

# du bout de la queue au nez : une longue cloche, la croupe qui monte, le poitrail qui redescend, le cou qui se tend
CHEMIN = [(0.0, 0.58, 0.040), (0.0, 0.42, 0.070), (0.0, 0.26, 0.150), (0.0, 0.08, 0.230), (0.0, -0.10, 0.240), (0.0, -0.24, 0.190),
          (0.0, -0.32, 0.150), (0.0, -0.40, 0.200)]


def rayon(f):
    return O.interp([(0.0, 0.0), (0.03, 0.022), (0.20, 0.040), (0.42, 0.058), (0.62, 0.060), (0.80, 0.050), (0.93, 0.044), (1.0, 0.040)])(f)


def construire():
    a = K.Animal("hermine")
    a.taille = 0.52

    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        f = m.v[:, 2] / L
        t = np.tile(BRUN, (len(f), 1))
        t[(ang > 1.85) & (f > 0.10)] = CREME
        t[f < 0.16] = NOIR                                        # le bout de la queue
        t[(f >= 0.16) & (f < 0.22)] = NOIR * (1 - (f[(f >= 0.16) & (f < 0.22)][:, None] - 0.16) / 0.06) + BRUN * ((f[(f >= 0.16) & (f < 0.22)][:, None] - 0.16) / 0.06)
        return t
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=36, flanc=(1.0, 0.0, 0.0))

    # ----- la tête : petite, plate, le museau court ; de grands yeux noirs ; les oreilles rondes, crème dedans -----
    cb, ab, nb = (Vector(q) for q in fil.cadre(L))
    TETE = cb + Vector((0.0, -0.040, 0.020))
    tete = A.boule(1.0, 36, 18)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(BRUN, (len(u), 1))
    t[(u[:, 2] < -0.25) | ((u[:, 1] < -0.30) & (u[:, 2] < 0.1))] = CREME
    tete.teinte = t
    a.piece("tete", tete.etire(0.050, 0.060, 0.044), None, pos=tuple(TETE), rot=(-10, 0, 14))
    a.piece("nez", A.boule(1.0, 12, 6).etire(0.010, 0.008, 0.008), NEZ, pos=tuple(TETE + Vector((0.0, -0.062, 0.002))), poil=False)
    O.paire_yeux(a, "tete", TETE, (0.64, -0.74, 0.22), 0.0140, decolle=0.002, R=A.repere((0.0, 0.0, 0.0), (-10, 0, 14)))
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.boule(1.0, 16, 8).etire(0.022, 0.008, 0.024)
        a.piece("oreille_" + nom, O.teinte(ore, BRUN), None, pos=(c * 0.042, TETE.y + 0.018, TETE.z + 0.040), rot=(0, c * 14, 0))
    a.tete = TETE + Vector((0.0, -0.06, 0.0))

    # ----- les pattes : toutes rassemblées sous la cloche du corps, courtes, avec de petits pieds crème -----
    for nom, c, y, z in (("avant_G", 1, -0.250, 0.150), ("avant_D", -1, -0.250, 0.150), ("arriere_G", 1, 0.330, 0.140), ("arriere_D", -1, 0.330, 0.140)):
        patte = O.tube_r([(c * 0.032, y, z), (c * 0.040, y + 0.020 * (1 if y < 0 else -1), z - 0.060), (c * 0.042, y + 0.040 * (1 if y < 0 else -1), 0.012)],
                         [0.022, 0.018, 0.015], 10)
        a.piece("patte_" + nom, O.teinte(patte, BRUN), None)
        pied = A.boule(1.0, 14, 8).etire(0.016, 0.028, 0.009)
        a.piece("pied_" + nom, O.teinte(pied, CREME), None, pos=(c * 0.042, y + 0.040 * (1 if y < 0 else -1) - 0.010, 0.010), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad", souple=True)


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("hermine", styles.style_de("hermine"), sys.modules[__name__]), "Hermine")
