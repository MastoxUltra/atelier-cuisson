"""Le bison en peluche de magasin (2e dessin, d'après photos) : un brun tabac roux ; tout le poids à l'AVANT : la bosse
haute et laineuse des épaules, la grosse tête basse sous une crinière sombre qui lui tombe sur les yeux, la barbe, de
courtes cornes noires qui se relèvent, des jambes avant en culottes de laine ; et l'arrière-train mince, plus clair, qui
s'effile en une queue au bout touffu. Un chef de troupeau : la tête baissée à hauteur de genou, le regard par en dessous.

    python bison.py        fabrique la fiche art/apercus/animaux/bison.png (peluche de magasin, palier 4)
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


# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
TABAC = np.array(M.hexa("#9a6a48"))           # la dominante : brun tabac roux (l'arrière-train, plus clair)
LAINE = np.array(M.hexa("#5a3e30"))           # la masse sombre de l'avant : bosse, cou, poitrail, culottes
NOIR = np.array(M.hexa("#2a2220"))            # la tête, la barbe, les sabots
CORNE = M.hexa("#2a2624")
PAS = 0.010


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=72, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("bison")
    a.taille = 3.00

    # ----- le corps, le cou et la tête d'un seul tenant : la croupe mince et haute, le dos qui monte à la bosse des épaules,
    #       le cou énorme, la grosse tête basse ; la masse sombre devant, l'arrière-train clair derrière -----
    chemin = [(0.0, y, z) for y, z in ((0.980, 0.800), (0.700, 0.880), (0.350, 0.950), (0.000, 1.020), (-0.350, 1.060), (-0.680, 0.950),
                                       (-0.960, 0.720), (-1.150, 0.520), (-1.230, 0.400))]
    fil = K.Fil(chemin, (1, 0, 0))
    L = fil.long
    pts = [(0.0, 0.0), (0.02, 0.150), (0.08, 0.205), (0.20, 0.232), (0.34, 0.225), (0.46, 0.250), (0.56, 0.330), (0.66, 0.345),
           (0.74, 0.300), (0.82, 0.230), (0.88, 0.190), (0.94, 0.140), (0.985, 0.100), (1.0, 0.0)]
    corps = fuseau(pts, L, 80)
    x, y, z = corps.v[:, 0], corps.v[:, 1], corps.v[:, 2]
    f = z / L
    corps.v[:, 1] += 0.150 * np.exp(-((f - 0.60) / 0.10) ** 2) * (y > 0)                  # la bosse
    th = np.abs(np.arctan2(x, y))
    t = np.tile(TABAC, (len(z), 1))
    t[f > 0.46] = LAINE
    t[f > 0.80] = NOIR
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)
    a.tete = Vector(fil.cadre(0.90 * L)[0])

    # ----- la crinière du front, la barbe ; les cornes courtes ; les petits yeux sous la crinière ; les narines -----
    c1, av1, nq1 = fil.cadre(0.86 * L)
    lat1 = np.cross(np.array(av1), np.array(nq1))
    a.piece("criniere", A.boule(1.0, 28, 14).etire(0.170, 0.130, 0.150), tuple(LAINE),
            pos=tuple(np.array(c1) + np.array(nq1) * 0.170 + np.array(av1) * 0.020))
    c2, av2, nq2 = fil.cadre(0.95 * L)
    a.piece("barbe", A.boule(1.0, 24, 12).etire(0.060, 0.070, 0.160), tuple(NOIR),
            pos=tuple(np.array(c2) - np.array(nq2) * 0.130 + np.array(av2) * 0.020), rot=(-10, 0, 0))
    for nom, c in (("G", 1), ("D", -1)):
        base = np.array(c1) + np.array(nq1) * 0.150 + lat1 * c * 0.150
        ch = [tuple(base), tuple(base + lat1 * c * 0.100 + np.array(nq1) * 0.020), tuple(base + lat1 * c * 0.160 + np.array(nq1) * 0.130)]
        a.piece("corne_" + nom, A.tube(A.courbe(propres(ch), 5), lambda t: 0.036 - 0.024 * t, 12), CORNE, poil=False)
        c3, av3, nq3 = fil.cadre(0.90 * L)
        p, n = a.surface("corps", Vector(c3), Vector(np.array([c * 0.90, 0.0, 0.0]) + np.array(nq3) * 0.10 - np.array(av3) * 0.30))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0200)
        c4, av4, nq4 = fil.cadre(0.985 * L)
        a.piece("narine_" + nom, A.boule(1.0, 14, 8).etire(0.016, 0.022, 0.012), CORNE,
                pos=tuple(np.array(c4) - np.array(nq4) * 0.020 + lat1 * c * 0.032), poil=False)

    # ----- les pattes : les avant épaisses, en culottes de laine sombres ; les arrière minces et claires ; sabots noirs -----
    def pilier(haut, bas, r, laine):
        fl = K.Fil([haut, ((haut[0] + bas[0]) / 2, (haut[1] + bas[1]) / 2, (haut[2] + bas[2]) / 2), bas], (1, 0, 0))
        m = fuseau([(0.0, r * 1.25), (0.35, r * 1.00), (0.70, r * 0.62), (0.92, r * 0.58), (1.0, r * 0.60)], fl.long, 36, 0.010)
        zz = m.v[:, 2] / fl.long
        m.teinte = np.where((zz < 0.45)[:, None], tuple(LAINE if laine else TABAC), tuple(TABAC))
        return m.sculpte(fl.couche)
    for nom, x_, y_, r, laine in (("av_G", 0.220, -0.560, 0.120, True), ("av_D", -0.220, -0.560, 0.120, True),
                                  ("ar_G", 0.210, 0.760, 0.100, False), ("ar_D", -0.210, 0.760, 0.100, False)):
        a.piece("patte_" + nom, pilier((x_, y_, 0.760), (x_ * 1.02, y_ + 0.020, 0.050), r, laine), None)
        a.piece("sabot_" + nom, A.boule(1.0, 20, 10).etire(r * 0.70, r * 0.95, 0.040), CORNE, pos=(x_ * 1.02, y_ + 0.010, 0.040), poil=False)
    queue = A.tube(A.courbe(propres([(0.0, 0.990, 0.800), (0.0, 1.060, 0.620), (0.0, 1.070, 0.420)]), 5), lambda t: 0.030 - 0.010 * t, 12)
    queue.teinte = np.tile(TABAC, (len(queue.v), 1))
    a.piece("queue", queue, None)
    a.piece("pinceau", A.boule(1.0, 20, 10).etire(0.050, 0.050, 0.120), tuple(NOIR), pos=(0.0, 1.072, 0.350))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("bison", styles.style_de("bison"), sys.modules[__name__]), "Bison")
