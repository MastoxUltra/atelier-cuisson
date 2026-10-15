"""Le vautour en peluche de velours ras : un brun sombre en grandes plumes lisses, le cou nu et ridé d'un rose gris, la
collerette de duvet blanc à la base du cou, la petite tête chauve au bec crochu fort, les yeux enfoncés sous un front
bas, de grandes ailes repliées en cape, des serres. L'attente : perché sur un tronc invisible, le dos voûté, le cou
rentré dans la collerette puis étiré, la tête de profil tournée vers nous, le bec en crochet, un regard patient de
croque-mort qui prend son temps.

    python vautour.py        fabrique la fiche art/apercus/animaux/vautour.png (velours ras, palier 3)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
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


BRUN = np.array(M.hexa("#7a6250"))            # la dominante : brun sombre (le poil le fonce : on le prend plus clair)
PLUME = np.array(M.hexa("#9a8068"))           # les couvertures claires
PEAU = np.array(M.hexa("#e0a8a0"))            # le cou nu, la tête : rose gris
DUVET = np.array(M.hexa("#fff6e8"))           # la collerette
BEC = M.hexa("#c8b898")
OEIL = M.hexa("#c8903a")
CHARBON = M.hexa("#3a3230")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("vautour")
    a.taille = 1.10

    # ----- le corps : un œuf lourd, voûté, penché en avant ; les ailes en cape, de grandes plumes rangées -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.240, 0.250), (0.150, 0.420), (0.040, 0.570), (-0.060, 0.690))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.05, 0.150), (0.20, 0.230), (0.55, 0.240), (0.85, 0.180), (1.0, 0.0)], L, 64, 0.009)
    corps.teinte = np.where((np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1])) > 2.5)[:, None], PLUME, BRUN)
    a.piece("corps", corps.sculpte(fil.couche), None)
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 36, 18)
        aile.teinte = np.where((np.sin(16 * aile.v[:, 2]) > 0.7)[:, None], PLUME, BRUN)

        def galet(v):
            s = K.emousse(v, 0.88)
            s[:, 1] *= 1 - 0.42 * K.lisse((v[:, 2] + 0.2) / 1.2)
            return s
        a.piece("aile_" + nom, aile.sculpte(galet).etire(0.060, 0.120, 0.380), None, pos=(c * 0.205, 0.140, 0.430), rot=(-22, 0, c * 8))

    # ----- la collerette de duvet blanc ; le cou nu et ridé qui s'étire ; la petite tête chauve au bec crochu -----
    a.piece("collerette", A.boule(1.0, 36, 18).etire(0.150, 0.110, 0.090), tuple(DUVET), pos=(0.0, -0.040, 0.700))
    cou = K.tube_peint(A.courbe([(0.0, -0.020, 0.720), (0.0, -0.100, 0.800), (0.0, -0.160, 0.870)], 5), lambda t: 0.062 - 0.016 * t,
                       [(1, tuple(PEAU))], 18)
    a.piece("cou", cou, None)
    H = A.cadre(Vector((0.0, -0.200, 0.900)), Vector((0.62, -1.0, -0.12)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.056, 0.070, 0.058), tuple(PEAU), mat=H)
    bec = A.tour(A.profil([(0, 0), (0.040, 0.008), (0.040, 0.044), (0.030, 0.080), (0.016, 0.110), (0.004, 0.126), (0, 0.130)], 6), 28)
    bec.sculpte(lambda v: v + np.stack([np.zeros(len(v)), -0.030 * np.clip((v[:, 2] - 0.06) / 0.07, 0, 1) ** 1.6, np.zeros(len(v))], axis=1))
    a.piece("bec", bec, BEC, mat=A.cadre(H @ Vector((0, 0.0, 0.0)) + H3 @ Vector((0, -0.064, -0.006)), H3 @ Vector((0, -1.0, -0.10)), (0, 0, 1)), poil=False)
    a.tete = H @ Vector((0, -0.100, -0.010))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.84, -0.30, 0.30))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.20, OEIL, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0120)
        a.piece("lourde_" + nom, K.paupiere(0.0150, 0.18), tuple(PEAU), mat=A.cadre(p + n * 0.005, n, H3 @ Vector((0, 0, 1))), poil=False)

    # ----- la queue : un court éventail ; les serres : deux gros pieds gris à griffes noires, plantés sur le perchoir -----
    a.piece("queue", A.boule(1.0, 24, 12).etire(0.080, 0.180, 0.030), tuple(BRUN), pos=(0.0, 0.340, 0.180), rot=(-30, 0, 0))
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("jambe_" + nom, A.tube(A.courbe([(c * 0.080, 0.100, 0.300), (c * 0.086, 0.080, 0.160), (c * 0.088, 0.060, 0.050)], 5), 0.036, 12), tuple(PEAU), poil=False)
        doigts = None
        for ang in (-30, 0, 30):
            d = A.boule(1.0, 14, 8).etire(0.016, 0.076, 0.014).pose((0, -0.060, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("serres_" + nom, doigts, M.hexa("#8a7a74"), pos=(c * 0.088, 0.040, 0.018), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("vautour", styles.style_de("vautour"), sys.modules[__name__]), "Vautour")
