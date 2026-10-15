"""Le kiwi en peluche de velours ras (2e dessin) : le seul oiseau qui a l'air d'un mammifère. Un corps en poire penché
en avant, tout en franges de poils hirsutes brun tabac, sans ailes ni queue, le cou qui coule du corps sans qu'on puisse
dire où commence la tête, de petits yeux, d'énormes cuisses de coq, de gros pieds à trois orteils, et ce long bec fin
d'ivoire qui fouille le sol, narines au bout, comme un nez de fourmilier. Il renifle : la pointe du bec dans la terre.

    python kiwi.py        fabrique la fiche art/apercus/animaux/kiwi.png (velours ras, palier 3)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import garnitures as G
import matieres as M
import peluche as K

TABAC = M.hexa("#c8a068")                     # la dominante : brun tabac (le poil le fonce : on le prend clair)
FONCE = M.hexa("#8a6a40")                     # les franges du dessus, le crâne
IVOIRE = M.hexa("#fff2d8")                    # l'accent : le bec
PATTE = M.hexa("#c89878")                     # les pattes
CHARBON = M.hexa("#3a2c28")
# le fil du corps, de la croupe au bout du cou (et de la tête) : en poire penchée, le cou qui plonge vers le sol
FIL = [(0.12, 0.340), (0.07, 0.365), (0.00, 0.360), (-0.06, 0.335), (-0.11, 0.300), (-0.14, 0.270)]
GALBE = [(0.0, 0.0), (0.035, 0.030), (0.090, 0.080), (0.140, 0.240), (0.150, 0.400), (0.120, 0.560), (0.080, 0.700), (0.055, 0.830),
         (0.050, 0.915), (0.052, 0.965), (0, 1.0)]


def construire():
    a = K.Animal("kiwi")
    a.taille = 0.60

    # ----- le corps, le cou et la tête : une seule pièce en poire penchée, les franges de poils hirsutes dessus -----
    fil = K.Fil([(0.0, y, z) for y, z in FIL], (1, 0, 0))
    L = fil.long
    corps = A.tour(A.profil([(r, f * L) for r, f in GALBE], 8), 48)
    corps.teinte = np.tile(np.asarray(TABAC, float), (len(corps.v), 1))
    corps = corps.sculpte(fil.couche)
    a.piece("corps", corps, None)
    franges = G.franges(corps, 0.070, 0.026, 0.026, 0.020,
                        lambda rang, t: tuple(np.asarray(TABAC) * (0.86 + 0.24 * (rang % 2)) * (0.78 + 0.30 * t) + np.asarray(FONCE) * 0.10),
                        3, 1, 0.04, 0.80)
    a.piece("franges", franges, None, poil=False)
    centre, avant, nuque = fil.cadre(0.93 * L)
    C = Vector(centre)

    # ----- le bec : long, fin, d'ivoire, légèrement recourbé, qui descend et fouille le sol ; les narines au bout -----
    dirige = Vector(avant * 0.78 + np.array([0.0, 0.0, -0.62]))
    dirige.normalize()
    B = A.cadre(C + dirige * 0.040, dirige, Vector((0, 0, 1)))

    def canne(v):
        s = v.copy()
        s[:, 1] += 0.040 * np.clip(v[:, 2] / 0.225, 0, 1) ** 2.0
        return s
    bec = A.tour(A.profil([(0, 0), (0.020, 0.006), (0.016, 0.040), (0.010, 0.140), (0.007, 0.245), (0.004, 0.220), (0, 0.230)], 5), 24)
    a.piece("bec", bec.sculpte(canne), IVOIRE, mat=B, poil=False)
    a.tete = C + dirige * 0.100
    for c in (1, -1):
        p, n = a.surface("corps", C + Vector((0, 0, 0.012)), Vector((c * 0.80, -0.30, 0.30)))
        a.oeil("oeil_" + ("G" if c > 0 else "D"), p + n * 0.003, n, 0.0098)

    # ----- les cuisses : d'énormes jambons, hauts sur la croupe ; les pattes : minces, les gros pieds à trois orteils -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.boule(1.0, 36, 18).etire(0.064, 0.094, 0.100), TABAC, pos=(c * 0.100, 0.120, 0.210), rot=(0, 0, c * 6))
        chemin = [(c * 0.100, 0.100, 0.200), (c * 0.108, 0.070, 0.120), (c * 0.108, 0.030, 0.026)]
        a.piece("patte_" + nom, A.tube(A.courbe(chemin, 5), 0.020, 12), PATTE, poil=False)
        doigts = None
        for ang in (-30, 0, 30):
            d = A.boule(1.0, 14, 8).etire(0.013, 0.060, 0.011).pose((0, -0.044, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("doigts_" + nom, doigts, PATTE, pos=(c * 0.108, 0.020, 0.012), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("kiwi", styles.style_de("kiwi"), sys.modules[__name__]), "Kiwi")
