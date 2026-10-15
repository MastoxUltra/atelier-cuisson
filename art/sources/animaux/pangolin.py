"""Le pangolin en peluche de magasin : une armure d'écailles terre cuite posées en rangs serrés comme des tuiles, du cou
jusqu'au bout d'une longue queue, le ventre et les pattes en peau crème, une petite tête en cône au museau pointu, des
yeux minuscules et de grandes griffes de fouisseur. Un chevalier au repos : dressé sur ses pattes arrière, appuyé sur
sa queue, les mains repliées sur le ventre, la tête levée de trois quarts, l'air de réfléchir à ce qu'il va creuser.

    python pangolin.py        fabrique la fiche art/apercus/animaux/pangolin.png (peluche de magasin, palier 4)
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
TUILE = M.hexa("#e88a5a")                     # la dominante : terre cuite
TUILE_BRUN = M.hexa("#b0603c")                # le dessous des écailles, un ton plus bas
DORE = M.hexa("#ffc872")                      # l'accent : le bout des écailles
CREME = M.hexa("#fff0d8")                     # le ventre, le museau, les pattes
CHARBON = M.hexa("#4a3a38")                   # les griffes
CORPS = [(0.0, -0.040, 0.640), (0.0, 0.020, 0.560), (0.0, 0.110, 0.400), (0.0, 0.230, 0.200), (0.0, 0.430, 0.075), (0.0, 0.650, 0.035)]


def construire():
    a = K.Animal("pangolin")
    a.taille = 1.10

    # ----- le corps et la queue : une seule pièce, du cou au bout de la queue, couchée le long d'un fil (le dos en pente) ;
    #       dessus, des rangs de languettes de feutrine : les écailles, qui retombent vers la queue -----
    fil = K.Fil(CORPS, (1, 0, 0))
    L = fil.long
    base = A.tour(A.profil([(0, 0), (0.092, 0.020 * L), (0.150, 0.100 * L), (0.178, 0.260 * L), (0.168, 0.420 * L), (0.130, 0.580 * L),
                            (0.090, 0.730 * L), (0.050, 0.860 * L), (0.022, 0.950 * L), (0, L)], 6), 40)
    base.teinte = np.tile(np.asarray(TUILE_BRUN, float), (len(base.v), 1))
    base = base.sculpte(fil.couche)
    a.piece("corps", base, None, poil=False)
    ecailles = G.franges(base, 0.115, 0.058, 0.050, 0.020,
                         lambda rang, t: tuple(np.asarray(TUILE) * (0.78 + 0.32 * (rang % 2) + 0.18 * t) + np.asarray(DORE) * 0.10 * t), 4, 1, 0.0, 0.97)
    a.piece("ecailles", ecailles, None, poil=False)

    # ----- le ventre : un grand plastron crème, en peau, sur le devant du corps (le dos reste en armure) -----
    centre, avant, nuque = fil.cadre(0.30 * L)
    V = A.cadre(Vector(centre) - Vector(nuque) * 0.040, Vector(avant), Vector(-nuque))
    a.piece("ventre", A.boule(1.0, 36, 18).etire(0.100, 0.060, 0.230), CREME, mat=V, poil=True)

    # ----- la tête : un cône lisse, le museau pointu et rosé, de minuscules yeux ; levée de trois quarts -----
    top = Vector(CORPS[0])
    H = A.cadre(top + Vector((0.0, -0.080, 0.045)), Vector((0.40, -0.90, 0.10)), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = A.tour(A.profil([(0, 0), (0.074, 0.010), (0.082, 0.050), (0.066, 0.110), (0.046, 0.175), (0.030, 0.235), (0.018, 0.285), (0, 0.300)], 6), 40)
    K.bandes(tete, [(0.240, TUILE), (9, CREME)])
    a.piece("tete", tete, None, mat=H, poil=False)
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.020, 0.018, 0.016), M.hexa("#9a5a5a"), mat=H @ A.repere((0, 0, 0.296)), poil=False)
    a.tete = H @ Vector((0, 0, 0.250))
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H @ Vector((0, 0, 0.100)), H3 @ Vector((c * 0.95, 0.15, 0.20)))
        a.bouton("oeil_" + nom, p + n * 0.002, n, 0.018)

    # ----- les bras : épais, repliés sur le ventre ; deux énormes griffes de fouisseur sur chaque main -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.140, 0.000, 0.560), (c * 0.185, -0.075, 0.470), (c * 0.150, -0.150, 0.400)]
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.052 - 0.012 * t, 14), TUILE_BRUN, poil=False)
        a.piece("main_" + nom, A.boule(1.0, 24, 12).etire(0.045, 0.050, 0.040), CREME, pos=(chemin[-1][0], chemin[-1][1] - 0.012, chemin[-1][2] - 0.004))
        griffes = None
        for k in (-1, 0, 1):
            g = A.tour(A.profil([(0, 0), (0.016, 0.004), (0.012, 0.034), (0.005, 0.066), (0, 0.082)], 5), 14)
            g = g.etire(1.0, 1.0, 1.0).pose((0, 0, 0), (-70, 0, 0)).pose((k * 0.032, -0.030, 0.0), (0, 0, -k * 12))
            griffes = g if griffes is None else griffes + g
        a.piece("griffes_" + nom, griffes, CHARBON, pos=(chemin[-1][0], chemin[-1][1] - 0.030, chemin[-1][2] - 0.020), poil=False)

    # ----- les pattes arrière : deux gros pieds plats crème, qui tiennent avec la queue le trépied ; les orteils cousus -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("pied_" + nom, A.boule(1.0, 28, 14).etire(0.064, 0.110, 0.034), CREME, pos=(c * 0.120, -0.020, 0.034), rot=(0, 0, c * 12))
        a.piece("cuisse_" + nom, A.boule(1.0, 28, 14).etire(0.085, 0.120, 0.110), TUILE_BRUN, pos=(c * 0.120, 0.150, 0.150), poil=False)
        a.piece("jambe_" + nom, A.tube(A.courbe([(c * 0.120, 0.110, 0.180), (c * 0.122, 0.040, 0.100), (c * 0.120, 0.000, 0.040)], 5), 0.052, 14), TUILE_BRUN, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pangolin", styles.style_de("pangolin"), sys.modules[__name__]), "Pangolin")
