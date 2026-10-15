"""La gerboise en peluche cousue main : un petit corps rond sable rosé, le ventre crème, une grosse tête aux yeux
immenses et aux oreilles hautes, un museau court au petit nez rose, des moustaches ; de minuscules mains serrées sur la
poitrine, des cuisses énormes et de longs pieds ; et une très longue queue, mince, qui se termine en plumet noir et
blanc. Le sauteur de minuit : debout sur ses pattes arrière, droit comme un point d'exclamation, sur le point de
bondir.

    python gerboise.py        fabrique la fiche art/apercus/animaux/gerboise.png (cousu main, palier 2)
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


def propres(points, eps=2e-4):
    """Les points d'un tracé sans doublons consécutifs (deux points identiques à la suite déforment un tube en NaN)."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie


SABLE = np.array(M.hexa("#f2c8a4"))           # la dominante : sable rosé (le poil le fonce)
CLAIR = np.array(M.hexa("#fff0e0"))           # le ventre, le dedans des pattes, le plumet blanc
DOS = np.array(M.hexa("#e0aa88"))             # le dos, le dessus de la tête
ROSE = M.hexa("#f0a8a0")                      # le dedans des oreilles, le nez
NOIR = np.array(M.hexa("#2e2826"))            # les yeux, le plumet noir
LACET = 22.0


def construire():
    a = K.Animal("gerboise")
    a.taille = 0.30

    # ----- le corps : un petit œuf debout, penché en arrière, le dos plus sombre, le ventre crème -----
    def oeuf(v):
        v = K.bosse(v, (0, -0.9, 0.1), 0.12, 0.40)
        return v * [0.074, 0.082, 0.108]
    corps = A.boule(1.0, 48, 24)
    corps.teinte = np.where((corps.v[:, 1] > 0.20)[:, None], DOS, np.where((corps.v[:, 1] < -0.45)[:, None], CLAIR, SABLE))
    a.piece("corps", corps.sculpte(oeuf), None, pos=(0.0, 0.030, 0.190), rot=(-14, 0, 0))

    # ----- la tête : grosse et ronde, le museau court, le petit nez rose ; les yeux IMMENSES ; les grandes oreilles -----
    TETE = Vector((0.0, -0.030, 0.318))
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.where((tete.v[:, 2] > 0.35)[:, None], DOS, SABLE)
    a.piece("tete", tete.etire(0.070, 0.066, 0.062), None, mat=H)
    a.piece("museau", A.boule(1.0, 28, 14).etire(0.032, 0.036, 0.030), tuple(CLAIR), mat=H @ A.repere((0.0, -0.058, -0.014)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.012, 0.010, 0.010), ROSE, mat=H @ A.repere((0.0, -0.092, -0.008)), poil=False)
    a.tete = H @ Vector((0.0, -0.080, -0.010))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.60, -0.62, 0.32))
        a.rustine("cerne_" + nom, "tete", H.to_translation(), regard, 0.26, tuple(NOIR), 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0195)
        # l'oreille : un grand ovale dressé, le dedans rose
        E = A.cadre(H @ Vector((c * 0.040, 0.014, 0.050)), H3 @ Vector((c * 0.26, 0.06, 0.96)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, A.boule(1.0, 28, 14).etire(0.030, 0.009, 0.086).pose((0, 0, 0.074)), tuple(SABLE), mat=E)
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).etire(0.019, 0.008, 0.068).pose((0, -0.005, 0.072)), ROSE, mat=E, poil=False)
        # trois moustaches de chaque côté : de longs fils clairs
        for k, (haut, ouvert) in enumerate(((0.012, 0.30), (0.0, 0.0), (-0.012, -0.30))):
            d = H3 @ Vector((c * 1.0, -0.40 + 0.30 * ouvert, 0.10 * ouvert * 2.0))
            dep = H @ Vector((c * 0.030, -0.078, -0.012 + haut))
            a.piece("moustache_%s%d" % (nom, k), A.tube([tuple(dep), tuple(dep + d.normalized() * 0.100)], 0.0022, 6), tuple(CLAIR), poil=False)

    # ----- les bras : minuscules, les mains serrées sur la poitrine ; les cuisses énormes, les longs pieds ; la queue -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.056, -0.016, 0.246), (c * 0.066, -0.060, 0.214), (c * 0.032, -0.082, 0.218)]
        a.piece("bras_" + nom, A.tube(A.courbe(propres(ch), 5), 0.014, 10), tuple(SABLE))
        a.piece("main_" + nom, A.boule(1.0, 14, 8).etire(0.014, 0.014, 0.012), tuple(CLAIR), pos=ch[-1])
        a.piece("cuisse_" + nom, A.boule(1.0, 28, 14).etire(0.046, 0.066, 0.084), tuple(SABLE), pos=(c * 0.062, 0.040, 0.120), rot=(-12, 0, c * 4))
        jam = [(c * 0.062, 0.020, 0.090), (c * 0.066, 0.056, 0.050), (c * 0.064, 0.050, 0.022)]
        a.piece("jambe_" + nom, A.tube(A.courbe(propres(jam), 5), lambda t: 0.026 - 0.012 * t, 10), tuple(SABLE))
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.020, 0.090, 0.016), tuple(CLAIR), pos=(c * 0.064, -0.010, 0.016), rot=(0, 0, c * 6))
    chemin = [(0.0, 0.100, 0.150), (0.0, 0.200, 0.100), (0.050, 0.310, 0.040), (0.150, 0.380, 0.030), (0.250, 0.360, 0.040), (0.290, 0.300, 0.070)]
    a.piece("queue", K.tube_peint(A.courbe(propres(chemin), 8), lambda t: 0.014 - 0.006 * t + 0.016 * max(0.0, (t - 0.80) / 0.20) ** 1.2,
                                  [(0.78, tuple(SABLE)), (0.90, tuple(NOIR)), (1.0, tuple(CLAIR))], 12), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("gerboise", styles.style_de("gerboise"), sys.modules[__name__]), "Gerboise")
