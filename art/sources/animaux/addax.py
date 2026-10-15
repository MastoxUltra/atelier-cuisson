"""L'addax en peluche de velours ras : une antilope du grand erg, blanc pur, trapue, le cou épais barré d'un collier
brun, une touffe brune sur le front, le nez et les joues blancs ; deux longues cornes en SPIRALE, annelées, qui montent
en vrille vers l'arrière ; de larges sabots plats qui ne s'enfoncent pas dans le sable. Le blanc sous le soleil :
debout, la tête un peu basse et tournée vers nous, les cornes dressées comme deux tire-bouchons.

    python addax.py        fabrique la fiche art/apercus/animaux/addax.png (velours ras, palier 3)
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


BLANC = np.array(M.hexa("#fffcf4"))           # la dominante : blanc pur
OMBRE = np.array(M.hexa("#f0e6d0"))           # le dos, le dessus du cou : à peine plus bas
BRUN = np.array(M.hexa("#8a6a48"))            # l'accent : le collier, le front, la touffe de la queue
CORNE = M.hexa("#e0d0a8")                     # les cornes
CORNE_FONCE = M.hexa("#b8a070")
NOIR = np.array(M.hexa("#3a3030"))
PAS = 0.007


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=60, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("addax")
    a.taille = 1.90

    # ----- le corps : un tonneau trapu d'antilope, le garrot un peu haut, tout blanc, le dos à peine plus sombre -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.420, 0.760), (0.230, 0.810), (0.000, 0.850), (-0.200, 0.890), (-0.340, 0.900))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.115), (0.15, 0.180), (0.45, 0.200), (0.75, 0.212), (0.92, 0.190), (0.98, 0.130), (1.0, 0.0)], L, 72)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.teinte = np.where((th < 0.8)[:, None], OMBRE, BLANC)
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou épais, le collier brun et la barbe ; la tête large, baissée et tournée vers nous -----
    a.piece("cou", A.tube(A.courbe([(0.0, -0.250, 0.920), (0.0, -0.390, 0.900), (0.0, -0.490, 0.830)], 5), lambda t: 0.150 - 0.052 * t, 24), tuple(BLANC))
    a.piece("collier", A.boule(1.0, 40, 20).etire(0.152, 0.152, 0.075), tuple(BRUN), mat=A.cadre(Vector((0.0, -0.345, 0.865)), Vector((0.0, -1.0, -0.20)), Vector((0, 0, 1))))
    a.piece("barbe", A.boule(1.0, 24, 12).etire(0.060, 0.040, 0.110), tuple(BRUN), pos=(0.0, -0.470, 0.700), rot=(-18, 0, 0))
    T = A.cadre(Vector((0.0, -0.600, 0.790)), Vector((0.42, -1.0, -0.34)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.07, 0.078), (0.26, 0.096), (0.52, 0.084), (0.78, 0.072), (0.95, 0.060), (1.0, 0.0)], 0.320, 52, 0.006)
    tt = np.tile(BLANC, (len(tete.v), 1))
    fr = (tete.v[:, 1] > 0.020) & (tete.v[:, 2] > 0.03) & (tete.v[:, 2] < 0.15)
    tt[fr] = BRUN                                                                 # le front brun
    tete.teinte = tt
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.090)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.034, 0.024, 0.024), tuple(NOIR), mat=T @ A.repere((0, 0.004, 0.232)), poil=False)
    a.tete = T @ Vector((0, 0.0, 0.150))
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.82, 0.38, 0.02))
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0170)
        a.piece("lourde_" + nom, K.paupiere(0.0215, 0.22), tuple(BLANC), mat=A.cadre(p + n * 0.005, n, T3 @ Vector((0, 1, 0))), poil=False)
        # la corne en vrille : un axe qui monte vers l'arrière, la tige qui tourne autour, deux tours et demi
        pts = []
        for i in range(0, 41):
            u = i / 40.0
            axe = np.array([c * (0.045 + 0.110 * u), 0.060 + 0.500 * u ** 0.9, -0.020 - 0.200 * u])
            ang = 2 * math.pi * 2.5 * u + (0.0 if c > 0 else math.pi)
            r = 0.028 * (1.0 - 0.45 * u)
            pts.append(tuple(T @ Vector(tuple(axe + np.array([r * math.cos(ang), 0.0, r * math.sin(ang)])))))
        bandes = [((k + 1) / 10.0, tuple(CORNE) if k % 2 == 0 else tuple(CORNE_FONCE)) for k in range(10)]
        a.piece("corne_" + nom, K.tube_peint(A.courbe(propres(pts), 3), lambda t: 0.023 - 0.016 * t, bandes, 12), None)
        po = A.profil([(0, 0), (0.030, 0.008), (0.040, 0.036), (0.032, 0.070), (0.012, 0.100), (0, 0.112)], 5)
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.38, 1.0), tuple(BLANC),
                mat=A.cadre(T @ Vector((c * 0.070, 0.040, -0.030)), T3 @ Vector((c * 0.90, 0.20, -0.30)), T3 @ Vector((c * 0.3, 0.0, 1.0))))

    # ----- les pattes : épaisses, le genou net, les grands sabots plats et sombres ; l'antérieur gauche avancé -----
    def patte(pts, r0):
        ft = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.30, r0 * 0.62), (0.46, r0 * 0.50), (0.52, r0 * 0.62), (0.60, r0 * 0.44), (0.92, r0 * 0.42), (0.97, r0 * 0.54), (1.0, 0.0)],
                   ft.long, 28, 0.007)
        m.teinte = np.tile(BLANC, (len(m.v), 1))
        return m.sculpte(ft.couche)
    for nom, pts, r0 in (("av_D", [(-0.110, -0.220, 0.800), (-0.116, -0.225, 0.520), (-0.116, -0.215, 0.280), (-0.116, -0.225, 0.040)], 0.082),
                         ("ar_G", [(0.120, 0.360, 0.700), (0.130, 0.310, 0.460), (0.130, 0.380, 0.260), (0.130, 0.370, 0.040)], 0.092),
                         ("ar_D", [(-0.120, 0.360, 0.700), (-0.130, 0.310, 0.460), (-0.130, 0.380, 0.260), (-0.130, 0.370, 0.040)], 0.092),
                         ("av_G", [(0.110, -0.220, 0.800), (0.116, -0.255, 0.540), (0.116, -0.350, 0.330), (0.116, -0.385, 0.040)], 0.082)):
        a.piece("patte_" + nom, patte(pts, r0), None)
        a.piece("sabot_" + nom, A.boule(1.0, 24, 12).etire(0.052, 0.068, 0.032), tuple(NOIR), pos=(pts[-1][0], pts[-1][1] - 0.012, 0.030), poil=False)
    a.piece("queue", A.tube(A.courbe(propres([(0.0, 0.440, 0.760), (0.0, 0.500, 0.690), (0.0, 0.510, 0.560)]), 5), lambda t: 0.022 - 0.006 * t, 12), tuple(BLANC))
    a.piece("touffe", A.boule(1.0, 20, 10).etire(0.030, 0.030, 0.062), tuple(BRUN), pos=(0.0, 0.512, 0.520))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("addax", styles.style_de("addax"), sys.modules[__name__]), "Addax")
