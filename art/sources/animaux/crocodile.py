"""Le crocodile en peluche de magasin : un brun ocre boue, l'armure de grosses écailles en rangées sur le dos, le
ventre jaune pâle, un long museau plat à deux bosses de narines, deux yeux à fleur de tête, des mâchoires pleines de
dents d'ivoire inégales, quatre pattes écartées, une queue épaisse aussi longue que le corps. Le sourire de
l'embuscade : à plat sur le sol, la gueule entrouverte à demi, les dents qui dépassent, les yeux qui nous suivent.

    python crocodile.py        fabrique la fiche art/apercus/animaux/crocodile.png (peluche de magasin, palier 4)
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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
OCRE = M.hexa("#b89a58")                      # la dominante : brun ocre boue
SOMBRE = M.hexa("#7a6638")                    # l'accent : les écailles du dos, la queue
VENTRE = M.hexa("#f0e0a0")                    # le ventre, le dessous de la mâchoire
DENT = M.hexa("#fff6e0")
ROSE = M.hexa("#f08888")
OEIL = M.hexa("#f0c840")
CHARBON = M.hexa("#3a3028")
CORPS = Vector((0.0, 0.080, 0.150))


def construire():
    a = K.Animal("crocodile")
    a.taille = 5.00

    # ----- le corps + la queue : une seule pièce, un long fuseau aplati, couchée le long d'un fil en S ; le ventre clair -----
    fil = K.Fil([(0.0, -0.150, 0.250), (0.0, 0.250, 0.255), (0.0, 0.700, 0.235), (0.0, 1.100, 0.190), (0.0, 1.500, 0.160), (0.0, 1.900, 0.130)], (1, 0, 0))
    L = fil.long
    corps = A.tour(A.profil([(0, 0), (0.200, 0.02 * L), (0.230, 0.12 * L), (0.215, 0.28 * L), (0.170, 0.46 * L), (0.115, 0.64 * L),
                             (0.072, 0.82 * L), (0.036, 0.95 * L), (0, L)], 6), 48)
    corps.teinte = np.where((corps.v[:, 1] < -0.040)[:, None], np.asarray(VENTRE), np.asarray(OCRE))

    def aplati(v):
        s = v.copy()
        s[:, 0] *= 1.20
        s[:, 1] = np.where(v[:, 1] < 0, v[:, 1] * 0.70, v[:, 1])
        return s
    a.piece("corps", corps.sculpte(aplati).sculpte(fil.couche), None)
    # l'armure du dos : des rangées de languettes de feutrine, sombres, qui pointent vers l'arrière
    ecailles = G.franges(A.tour(A.profil([(0, 0), (0.210, 0.02 * L), (0.240, 0.12 * L), (0.225, 0.28 * L), (0.180, 0.46 * L), (0.125, 0.64 * L),
                                          (0.082, 0.82 * L), (0.046, 0.95 * L), (0, L)], 6), 40).sculpte(aplati).sculpte(fil.couche),
                         0.070, 0.050, 0.046, 0.016, lambda rang, t: tuple(np.asarray(SOMBRE) * (0.84 + 0.30 * (rang % 2))), 5, -1, 0.10, 0.96)
    a.piece("ecailles", ecailles, None, poil=False)

    # ----- la tête : un long museau plat à deux bosses de narines, deux yeux à fleur de tête ; la gueule entrouverte -----
    centre, avant, nuque = fil.cadre(0.0)
    H = A.cadre(Vector((0.0, -0.200, 0.290)), Vector((0.20, -1.0, 0.0)), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    haut = A.tour(A.profil([(0, 0), (0.150, 0.010), (0.210, 0.080), (0.190, 0.200), (0.150, 0.340), (0.118, 0.480), (0.096, 0.600), (0.108, 0.640),
                            (0.090, 0.680), (0, 0.700)], 6), 44)
    haut.teinte = np.tile(np.asarray(OCRE, float), (len(haut.v), 1))
    a.piece("tete", haut.sculpte(lambda v: v * [1.0, 0.52, 1.0]), None, mat=H)
    a.tete = H @ Vector((0, 0.100, 0.600))
    for c in (1, -1):
        n = "G" if c > 0 else "D"
        a.piece("globe_" + n, A.boule(1.0, 24, 12).etire(0.064, 0.060, 0.058), OCRE, mat=H @ A.repere((c * 0.110, 0.060, 0.130)))
        pos, nn = a.surface("globe_" + n, H @ Vector((c * 0.110, 0.060, 0.130)), H3 @ Vector((c * 0.50, 0.30, 0.70)))
        a.oeil("oeil_" + n, pos + nn * 0.004, nn, 0.0300)
        a.piece("narine_" + n, A.boule(1.0, 14, 8).etire(0.024, 0.026, 0.016), CHARBON, mat=H @ A.repere((c * 0.036, 0.012, 0.670)), poil=False)

    # ----- la mâchoire du bas : abaissée, le dessous clair ; la gueule rose ; les dents d'ivoire inégales -----
    bas = A.tour(A.profil([(0, 0), (0.140, 0.010), (0.190, 0.090), (0.150, 0.250), (0.110, 0.430), (0.084, 0.590), (0.064, 0.660), (0, 0.690)], 6), 40)
    bas.teinte = np.where((bas.v[:, 1] < 0.0)[:, None], np.asarray(VENTRE), np.asarray(OCRE))
    a.piece("machoire", bas.sculpte(lambda v: v * [1.0, 0.40, 1.0]), None, mat=H @ A.repere((0, -0.030, -0.020), (-14, 0, 0)) @ A.repere((0, 0, 0)), poil=False)
    a.piece("gueule", A.boule(1.0, 36, 18).etire(0.140, 0.026, 0.300).pose((0, 0, 0.340)), ROSE, mat=H @ A.repere((0, 0.030, 0.000)), poil=False)
    for k in range(10):
        c = 1 if k % 2 == 0 else -1
        z = 0.100 + 0.054 * (k // 2)
        r = 0.150 - 0.012 * (k // 2)
        a.piece("dent_%d" % k, A.tour(A.profil([(0, 0), (0.014, 0.004), (0.009, 0.026), (0.003, 0.044), (0, 0.050)], 5), 10),
                DENT, mat=H @ A.repere((c * r * 0.86, -0.010, z), (0, 0, 0)), poil=False)

    # ----- les pattes : quatre écartées, courtes, coudées ; les pieds aux griffes -----
    for nom, x, y in (("av_G", 0.300, 0.060), ("av_D", -0.300, 0.060), ("ar_G", 0.300, 0.820), ("ar_D", -0.300, 0.820)):
        c = 1 if x > 0 else -1
        chemin = [(x * 0.55, y, 0.240), (x * 1.00, y - 0.020, 0.200), (x * 1.18, y - 0.080, 0.036)]
        a.piece("patte_" + nom, A.tube(A.courbe(chemin, 6), 0.075, 16), OCRE)
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.100, 0.140, 0.026), SOMBRE, pos=(x * 1.22, y - 0.180, 0.026), rot=(0, 0, c * 18))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("crocodile", styles.style_de("crocodile"), sys.modules[__name__]), "Crocodile")
