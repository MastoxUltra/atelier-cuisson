"""Le loir en peluche : un petit dormeur gris perle argenté, le masque noir autour de grands yeux ronds qui prennent
toute la face, les oreilles rondes, une queue touffue qui monte dans son dos comme un panache. Assis sur son derrière,
les deux petites mains jointes sous le menton, la tête penchée : il vient de se réveiller pour la nuit, et il est déjà
fatigué de ce qu'il va lui falloir faire.

    python loir.py        fabrique la fiche art/apercus/animaux/loir.png (style du palier : A, cousu main)
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

PERLE = np.array(M.hexa("#b3b8c0"))           # la dominante (registre : gris perle argenté)
VENTRE = np.array(M.hexa("#f1ece2"))
MASQUE = np.array(M.hexa("#22201f"))          # le masque noir autour des yeux
ROSE = M.hexa("#e8a6a0")
FIL = M.hexa("#3a3030")
TETE = Vector((0.0, -0.035, 0.205))


def construire():
    a = K.Animal("loir")
    a.taille = 0.32

    # ----- le corps : une poire assise, gris perle dessus, clair devant -----
    pc = A.profil([(0, 0.0), (0.060, 0.008), (0.092, 0.050), (0.100, 0.110), (0.082, 0.170), (0.056, 0.205), (0.026, 0.222), (0, 0.230)], 6)
    corps = A.tour(pc, 40)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(PERLE, (len(ang), 1))
    t[(ang > 1.9) & (corps.v[:, 2] > 0.01)] = VENTRE
    corps.teinte = t
    a.piece("corps", corps.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] + 0.30 * v[:, 2] * 0, v[:, 2]], axis=1)), None, pos=(0.0, 0.015, 0.0))

    # ----- la tête : ronde, penchée ; le masque noir : un bandeau qui passe sur les yeux ; la truffe rose -----
    tete = A.boule(1.0, 44, 22)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(PERLE, (len(u), 1))
    t[(np.abs(u[:, 2] - 0.05) < 0.30) & (u[:, 1] < 0.05)] = MASQUE
    t[(u[:, 2] < -0.40) & (u[:, 1] < 0.0)] = VENTRE
    tete.teinte = t
    a.piece("tete", tete.etire(0.082, 0.078, 0.074), None, pos=tuple(TETE), rot=(8, 0, 12))
    museau = A.boule(1.0, 20, 10).etire(0.028, 0.034, 0.024)
    a.piece("museau", O.teinte(museau, VENTRE), None, pos=(0.0, -0.100, 0.188))
    a.piece("nez", A.boule(1.0, 14, 8).etire(0.0105, 0.009, 0.0085), ROSE, pos=(0.0, -0.131, 0.194), poil=False)
    O.paire_yeux(a, "tete", TETE, (0.54, -0.78, 0.18), 0.0270, decolle=0.003, R=A.repere((0.0, 0.0, 0.0), (8, 0, 12)))
    for nom, c in (("G", 1), ("D", -1)):
        oreille = A.boule(1.0, 20, 10).etire(0.030, 0.010, 0.032)
        a.piece("oreille_" + nom, O.teinte(oreille, MASQUE * 1.4), None, pos=(c * 0.066, 0.000, 0.268), rot=(0, c * 16, 0))
        for k, dz in enumerate((0.010, -0.006)):
            a.broderie("moustache_%s%d" % (nom, k), [Vector((c * 0.014, -0.128, 0.186)), Vector((c * 0.050, -0.138, 0.190 + dz * 0.6)),
                                                      Vector((c * 0.090, -0.140, 0.194 + dz * 2.0))], 0.0011, tuple(VENTRE))
    O.broder(a, "bouche", "tete", TETE, [(0.28 * u_, -0.97, -0.38 + 0.08 * u_ * u_) for u_ in np.linspace(-1, 1, 7)], 0.0017, FIL, decolle=0.002)
    a.tete = TETE + Vector((0.0, -0.10, 0.0))

    # ----- les bras : deux petites mains jointes sous le menton ; les cuisses rondes, les grands pieds devant -----
    for nom, c in (("G", 1), ("D", -1)):
        bras = O.tube_r([(c * 0.075, -0.030, 0.150), (c * 0.085, -0.080, 0.120), (c * 0.040, -0.100, 0.130), (c * 0.014, -0.102, 0.150)],
                        [0.020, 0.018, 0.016, 0.015], 12)
        a.piece("bras_" + nom, O.teinte(bras, PERLE), None)
        cuisse = A.boule(1.0, 24, 12).etire(0.036, 0.060, 0.050)
        a.piece("cuisse_" + nom, O.teinte(cuisse, PERLE), None, pos=(c * 0.080, 0.020, 0.052), rot=(10, 0, c * 8))
        pied = A.boule(1.0, 20, 8).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.022, 0.050, 0.010)
        a.piece("pied_" + nom, O.teinte(pied, VENTRE), None, pos=(c * 0.060, -0.070, 0.010), rot=(0, 0, c * 14), poil=False)

    # ----- la queue touffue : un panache qui monte dans le dos, plus sombre au bout -----
    queue = O.tube_r([(0.0, 0.090, 0.040), (0.0, 0.160, 0.090), (0.0, 0.170, 0.180), (0.0, 0.120, 0.250), (0.0, 0.080, 0.285)],
                     [0.030, 0.050, 0.056, 0.048, 0.030], 16)
    a.piece("queue", K.tube_peint(A.courbe([(0.0, 0.090, 0.040), (0.0, 0.160, 0.090), (0.0, 0.170, 0.180), (0.0, 0.120, 0.250), (0.0, 0.080, 0.285)], 6),
                                  lambda t_: 0.030 + 0.030 * math.sin(math.pi * t_) ** 0.7, [(0.6, PERLE), (1.0, MASQUE * 2.2)], 16), None)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("loir", styles.style_de("loir"), sys.modules[__name__]), "Loir")
