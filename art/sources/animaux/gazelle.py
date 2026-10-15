"""La gazelle en peluche cousue main : un caramel clair, le ventre blanc, la bande sombre qui sépare le dos et le
flanc, deux lignes brunes sur le visage de l'œil au museau, de longues oreilles étroites, de grands yeux noirs aux
longs cils, deux cornes annelées en lyre, de très longues jambes fines, une courte queue noire. La nerveuse :
l'arrêt net : un antérieur levé, la tête haute et tournée vers nous, les oreilles dressées, les narines frémissantes :
elle va bondir.

    python gazelle.py        fabrique la fiche art/apercus/animaux/gazelle.png (cousu main, palier 2)
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


CARAMEL = np.array(M.hexa("#f2c88a"))         # la dominante : caramel clair (le poil le fonce)
BLANC = np.array(M.hexa("#fffaf0"))           # le ventre, la croupe, le museau
BANDE = np.array(M.hexa("#8a5a38"))           # la bande du flanc, les lignes du visage
NOIR = np.array(M.hexa("#2e2824"))            # la queue, les sabots, les cornes
PAS = 0.007


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("gazelle")
    a.taille = 1.20

    # ----- le corps : un fuseau élancé ; le dos caramel, la bande brune du flanc, le ventre et la croupe blancs -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.380, 0.560), (0.200, 0.600), (0.000, 0.610), (-0.200, 0.640), (-0.320, 0.660))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.080), (0.14, 0.125), (0.45, 0.135), (0.78, 0.140), (0.94, 0.100), (1.0, 0.0)], L, 64)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    f = corps.v[:, 2] / L
    t = np.tile(CARAMEL, (len(f), 1))
    t[(th > 1.50) & (th < 1.95)] = BANDE                                          # la bande sombre du flanc
    t[th >= 1.95] = BLANC
    t[f < 0.10] = BLANC                                                           # la croupe
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou et la tête fine ; les deux lignes brunes de l'œil au museau ; les longues oreilles ; les cornes en lyre -----
    a.piece("cou", A.tube(A.courbe([(0.0, -0.250, 0.680), (0.0, -0.340, 0.790), (0.0, -0.390, 0.890)], 5), lambda t: 0.082 - 0.030 * t, 20), tuple(CARAMEL))
    H = A.cadre(Vector((0.0, -0.400, 0.900)), Vector((0.40, -1.0, -0.30)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.060), (0.24, 0.074), (0.50, 0.060), (0.78, 0.046), (0.96, 0.040), (1.0, 0.0)], 0.300, 48, 0.006)
    tete.teinte = np.where(((tete.v[:, 2] > 0.80 * 0.300) | (np.abs(np.arctan2(tete.v[:, 0], tete.v[:, 1])) > 2.3))[:, None], BLANC, CARAMEL)
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0, -0.050)))
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.028, 0.020, 0.016), M.hexa("#2e2824"), mat=H @ A.repere((0, 0.012, 0.246)), poil=False)
    a.tete = H @ Vector((0, 0.010, 0.140))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.84, 0.26, 0.14))
        p, n = a.surface("tete", H @ Vector((0, 0.0, 0.030)), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0200)
        ligne = [H3 @ Vector((c * (0.82 - 0.30 * t), 0.30 - 0.34 * t, 0.10 + 0.34 * t)) for t in np.linspace(0, 1, 6)]
        a.broderie("ligne_" + nom, A.courbe(propres(a.trace("tete", H @ Vector((0, 0.0, 0.030)), ligne, 0.003)), 4), 0.0030, tuple(BANDE))
        po = A.profil([(0, 0), (0.026, 0.010), (0.034, 0.050), (0.026, 0.100), (0.010, 0.140), (0, 0.152)], 6)
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.36, 1.0), tuple(CARAMEL),
                mat=A.cadre(H @ Vector((c * 0.052, 0.070, -0.010)), H3 @ Vector((c * 0.62, 0.10, 0.70)), H3 @ Vector((c * 0.3, -0.9, 0.0))))
        # les cornes en lyre : deux courbes annelées qui montent en S
        ch = [H @ Vector(q) for q in ((c * 0.034, 0.060, 0.040), (c * 0.060, 0.100, 0.140), (c * 0.076, 0.150, 0.250), (c * 0.050, 0.170, 0.340))]
        a.piece("corne_" + nom, K.tube_peint(A.courbe(propres(ch), 6), lambda t: 0.020 - 0.014 * t,
                                             [(0.15, tuple(NOIR)), (0.28, tuple(CARAMEL * 0.7)), (0.42, tuple(NOIR)), (0.58, tuple(CARAMEL * 0.7)),
                                              (0.74, tuple(NOIR)), (1, tuple(NOIR))], 12), None)

    # ----- les pattes : très longues, fines, le genou marqué, les sabots noirs ; un antérieur levé -----
    def patte(pts, r0):
        f_ = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.40, r0 * 0.54), (0.50, r0 * 0.66), (0.60, r0 * 0.44), (0.94, r0 * 0.40), (1.0, 0.0)], f_.long, 24, 0.008)
        m.teinte = np.where((m.v[:, 2] > 0.55 * f_.long)[:, None], CARAMEL * 0.96, CARAMEL)
        return m.sculpte(f_.couche)
    for nom, pts, r0 in (("av_D", [(-0.075, -0.220, 0.640), (-0.080, -0.230, 0.440), (-0.080, -0.220, 0.250), (-0.080, -0.230, 0.040)], 0.044),
                         ("ar_G", [(0.085, 0.300, 0.540), (0.095, 0.250, 0.380), (0.095, 0.320, 0.210), (0.095, 0.310, 0.040)], 0.052),
                         ("ar_D", [(-0.085, 0.300, 0.540), (-0.095, 0.250, 0.380), (-0.095, 0.320, 0.210), (-0.095, 0.310, 0.040)], 0.052),
                         ("av_G", [(0.075, -0.220, 0.640), (0.082, -0.240, 0.480), (0.084, -0.330, 0.450), (0.084, -0.360, 0.330)], 0.044)):
        a.piece("patte_" + nom, patte(pts, r0), None)
        a.piece("sabot_" + nom, A.boule(1.0, 20, 10).etire(0.030, 0.042, 0.026), tuple(NOIR), pos=(pts[-1][0], pts[-1][1] - 0.010, max(pts[-1][2] - 0.012, 0.026)), poil=False)
    a.piece("queue", A.tube(A.courbe([(0.0, 0.390, 0.560), (0.0, 0.430, 0.500), (0.0, 0.440, 0.430)], 5), 0.020, 10), tuple(NOIR))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("gazelle", styles.style_de("gazelle"), sys.modules[__name__]), "Gazelle")
