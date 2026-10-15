"""Le tatou en peluche cousue main : un rose gris cuir, la carapace en larges bandes articulées (le bouclier de
l'épaule, les bandes du milieu, le bouclier de la croupe), le dessous nu, un museau pointu, de petites oreilles en
tuyau, des pattes courtes aux griffes de pelle, une queue en cône cuirassé. Le blindé timide : le museau au ras du sol
qui renifle, le dos en dôme, une patte avant levée ; il est à un souffle de se rouler en boule.

    python tatou.py        fabrique la fiche art/apercus/animaux/tatou.png (cousu main, palier 2)
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


CUIR = np.array(M.hexa("#e0b0a0"))            # la dominante : rose gris cuir (le poil le fonce)
PLAQUE = np.array(M.hexa("#c8968a"))          # les bandes de la carapace, un ton plus bas
JOINT = np.array(M.hexa("#8a6258"))           # les joints entre les bandes
VENTRE = np.array(M.hexa("#f4d8c8"))
GRIFFE = M.hexa("#f2e4cc")
NOIR = M.hexa("#3a3030")
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 5)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("tatou")
    a.taille = 0.75

    # ----- le corps : un dôme long et bas ; la carapace : bouclier, bandes articulées (des joints sombres nets), bouclier ;
    #       le dessous nu -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.250, 0.130), (0.130, 0.170), (0.000, 0.180), (-0.130, 0.165), (-0.220, 0.130))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.090), (0.14, 0.140), (0.45, 0.160), (0.78, 0.150), (0.94, 0.100), (1.0, 0.0)], L, 72)
    z = corps.v[:, 2]
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    f = z / L
    t = np.tile(PLAQUE, (len(z), 1))
    bande = (f > 0.30) & (f < 0.74)
    t[bande & (((f - 0.30) / 0.044) % 1.0 < 0.14)] = JOINT                              # les joints des bandes
    t[(f < 0.26) | (f > 0.78)] = CUIR * 0.96                                           # les deux boucliers
    t[th > 2.05] = VENTRE                                                              # le ventre nu
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- la tête : un coin pointu, le museau long ; les oreilles en tuyau ; les yeux petits ; penchée, le museau au sol -----
    H = A.cadre(Vector((0.0, -0.320, 0.140)), Vector((0.30, -1.0, -0.34)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.070), (0.22, 0.090), (0.46, 0.074), (0.74, 0.054), (0.95, 0.040), (1.0, 0.0)], 0.300, 48, 0.006)
    tete.teinte = np.tile(CUIR, (len(tete.v), 1))
    tete.teinte[(tete.v[:, 2] > 0.10) & (tete.v[:, 2] < 0.16)] = JOINT
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0, -0.050)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.022, 0.016, 0.016), tuple(JOINT), mat=H @ A.repere((0, 0.006, 0.250)), poil=False)
    a.tete = H @ Vector((0, 0.0, 0.140))
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H @ Vector((0, 0.0, 0.020)), H3 @ Vector((c * 0.84, 0.30, 0.0)))
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0120)
        po = A.profil([(0, 0), (0.020, 0.008), (0.028, 0.034), (0.022, 0.060), (0.008, 0.074), (0, 0.080)], 5)
        a.piece("oreille_" + nom, A.tour(po, 20).etire(1.0, 0.45, 1.0), tuple(CUIR),
                mat=A.cadre(H @ Vector((c * 0.060, 0.050, -0.040)), H3 @ Vector((c * 0.50, 0.30, 0.80)), H3 @ Vector((c * 0.3, -0.9, 0.0))))

    # ----- les pattes : courtes, aux griffes de pelle ; une patte avant levée ; la queue : un cône cuirassé à joints -----
    for nom, x_, y_, levee in (("av_G", 0.100, -0.160, True), ("av_D", -0.100, -0.160, False), ("ar_G", 0.105, 0.150, False), ("ar_D", -0.105, 0.150, False)):
        c = 1 if x_ > 0 else -1
        bas = (x_ * 1.05, y_ - (0.090 if levee else 0.020), 0.090 if levee else 0.030)
        a.piece("patte_" + nom, A.tube(A.courbe(propres([(x_, y_, 0.130), (x_ * 1.03, y_ - 0.030, 0.080), bas]), 5), 0.036, 12), tuple(CUIR))
        g = None
        for k in (-1, 0, 1):
            gr = A.tour(A.profil([(0, 0), (0.010, 0.003), (0.008, 0.028), (0.003, 0.052), (0, 0.062)], 5), 10)
            gr = gr.pose((0, 0, 0), (-78, 0, 0)).pose((k * 0.020, -0.020, 0.0), (0, 0, k * 8))
            g = gr if g is None else g + gr
        a.piece("griffes_" + nom, g, GRIFFE, pos=(bas[0], bas[1] - 0.016, bas[2] - 0.006), poil=False)
    queue = fuseau([(0.0, 0.070), (0.40, 0.050), (0.80, 0.026), (1.0, 0.0)], 0.300, 32, 0.006)
    queue.teinte = np.where(((queue.v[:, 2] / 0.040) % 1.0 < 0.16)[:, None], JOINT, PLAQUE)
    qf = K.Fil([(0.0, 0.240, 0.110), (0.0, 0.380, 0.070), (0.0, 0.500, 0.040)], (1, 0, 0))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tatou", styles.style_de("tatou"), sys.modules[__name__]), "Tatou")
