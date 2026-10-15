"""L'otarie en peluche : le gros bébé de la côte, caramel sombre luisant, long cou, longues moustaches crème qui
fouettent l'air. Dressée sur ses deux nageoires avant bien plantées, le torse relevé, le museau au ciel et les
yeux mi-clos : elle applaudit toute seule, ou elle attend la sardine, on ne sait pas. Les nageoires arrière traînent
derrière elle comme deux gants de caoutchouc.

    python otarie.py        fabrique la fiche art/apercus/animaux/otarie.png (style du palier : C, velours ras)
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

CARAMEL = np.array(M.hexa("#8a5a30"))         # la dominante (registre : caramel sombre luisant) ; le velours éclaircit
CLAIR = np.array(M.hexa("#b58558"))           # le ventre, le cou
CREME = M.hexa("#f3e6c4")                     # les moustaches
NEZ = M.hexa("#1d1512")
NAGEOIRE = np.array(M.hexa("#5c3a1e"))
FIL = M.hexa("#2a1a10")

# de la queue (les nageoires arrière) à la nuque : un grand arc, le torse qui se redresse
CHEMIN = [(0.0, 0.62, 0.050), (0.0, 0.46, 0.100), (0.0, 0.26, 0.180), (0.0, 0.04, 0.330), (0.0, -0.12, 0.520),
          (0.0, -0.20, 0.690), (0.0, -0.23, 0.800)]


def rayon(f):
    return O.interp([(0.0, 0.0), (0.02, 0.030), (0.14, 0.080), (0.34, 0.150), (0.52, 0.185), (0.70, 0.165), (0.86, 0.110),
                     (0.96, 0.092), (1.0, 0.090)])(f)


def construire():
    a = K.Animal("otarie")
    a.taille = 1.80

    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        f = m.v[:, 2] / L
        t = np.tile(CARAMEL, (len(f), 1))
        t[(ang > 1.9) & (f > 0.2)] = CLAIR
        t[f > 0.80] = CLAIR * 0.5 + CARAMEL * 0.5
        return t
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=44, flanc=(-1.0, 0.0, 0.0))

    # ----- la tête : un museau qui pointe en l'air, le front bombé, les yeux ronds ; la truffe noire -----
    cb, ab, nb = (Vector(q) for q in fil.cadre(L))
    H = cb + Vector((0.0, -0.040, 0.100))
    tete = A.boule(1.0, 44, 22)
    tete.teinte = np.tile(CARAMEL * 0.75 + CLAIR * 0.25, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.092, 0.118, 0.086), None, pos=tuple(H), rot=(-26, 0, 0))
    museau = A.boule(1.0, 28, 14).etire(0.058, 0.070, 0.050)
    a.piece("museau", O.teinte(museau, CLAIR), None, pos=tuple(H + Vector((0.0, -0.105, 0.045))))
    a.piece("nez", A.boule(1.0, 16, 8).etire(0.024, 0.018, 0.016), NEZ, pos=tuple(H + Vector((0.0, -0.165, 0.085))), poil=False)
    O.paire_yeux(a, "tete", H, (0.74, -0.58, 0.20), 0.0240, couleur_lourde=tuple(CARAMEL), coupe=0.60, decolle=0.003, haut=(0, 0.3, 1))
    for nom, c in (("G", 1), ("D", -1)):
        for k, dz in enumerate((0.020, 0.0, -0.020)):
            a.broderie("moustache_%s%d" % (nom, k), [H + Vector((c * 0.020, -0.150, 0.060 + dz * 0.4)), H + Vector((c * 0.090, -0.180, 0.070 + dz)),
                                                      H + Vector((c * 0.175, -0.170, 0.080 + 2.2 * dz))], 0.0017, CREME)
        oreille = A.boule(1.0, 14, 8).etire(0.008, 0.026, 0.020)
        a.piece("oreille_" + nom, O.teinte(oreille, NAGEOIRE), None, pos=(c * 0.088, H.y + 0.040, H.z + 0.020), poil=False)
    a.tete = H + Vector((0.0, -0.14, 0.04))

    # ----- les nageoires avant : deux bras épais plantés, la nageoire à plat devant ; les arrière, deux gants traînants -----
    for nom, c in (("G", 1), ("D", -1)):
        bras = O.tube_r([(c * 0.150, -0.060, 0.420), (c * 0.185, -0.150, 0.250), (c * 0.170, -0.230, 0.080), (c * 0.165, -0.260, 0.030)],
                        [0.074, 0.062, 0.052, 0.046], 18)
        a.piece("bras_" + nom, O.teinte(bras, CARAMEL), None)
        nag = A.boule(1.0, 28, 12).etire(0.050, 0.120, 0.016)
        a.piece("nageoire_" + nom, O.teinte(nag, NAGEOIRE), None, pos=(c * 0.170, -0.335, 0.020), rot=(0, 0, c * -12), poil=False)
        ar = A.boule(1.0, 28, 12).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.060, 0.190, 0.018)
        a.piece("arriere_" + nom, O.teinte(ar, NAGEOIRE), None, pos=(c * 0.075, 0.710, 0.020), rot=(0, 0, c * 18), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("otarie", styles.style_de("otarie"), sys.modules[__name__]), "Otarie")
