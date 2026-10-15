"""Le crocodile en peluche de magasin (2e dessin, d'après photos : plus de bec de canard) : un brun ocre boue, la tête
et le corps d'un seul jet, très bas, plats, le long museau étroit qui s'élargit en cuvette aux narines, les deux bosses
d'yeux à fleur du dessus du crâne, la rangée des dents inégales qui dépasse de la mâchoire fermée, le dos hérissé de
grosses écailles en crête, le ventre pâle, quatre pattes écartées aux griffes, et une queue épaisse et longue, baguée.
Il se laisse flotter sur la berge, la gueule fermée sur son sourire, un œil jaune qui ne cligne pas.

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


OCRE = np.array(M.hexa("#a89460"))            # la dominante : brun ocre boue
BOUE = np.array(M.hexa("#6a5a38"))            # les bandes du dos et de la queue
VENTRE = np.array(M.hexa("#f0e4b4"))          # le ventre, le dessous de la gorge
DENT = M.hexa("#fff8e0")
OEIL = M.hexa("#e8c030")
CHARBON = M.hexa("#2a2420")
PAS = 0.010


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=48, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 5)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("crocodile")
    a.taille = 5.00

    # ----- le corps entier d'une pièce, du bout du museau au bout de la queue : le museau long et étroit, le crâne, le cou
    #       court, le tronc large et plat, la queue épaisse qui s'effile ; couché le long d'une courbe ; plat dessus-dessous -----
    chemin = [(0.0, y, z) for y, z in ((-1.300, 0.100), (-1.000, 0.110), (-0.700, 0.120), (-0.420, 0.135), (-0.150, 0.150),
                                       (0.200, 0.150), (0.550, 0.140), (0.900, 0.115), (1.250, 0.085), (1.600, 0.055))]
    # la queue ondule : le dernier tiers dévie sur le côté
    chemin = [(0.0 if y < 0.9 else 0.02 + 0.30 * (y - 0.9) ** 1.5, y, z) for _x, y, z in chemin]
    fil = K.Fil(chemin, (1, 0, 0))
    L = fil.long
    pts = [(0.0, 0.0), (0.012, 0.040), (0.036, 0.100), (0.044, 0.200), (0.046, 0.260), (0.062, 0.330), (0.100, 0.380),
           (0.120, 0.420), (0.150, 0.500), (0.170, 0.600), (0.165, 0.680), (0.140, 0.760), (0.100, 0.850), (0.062, 0.930),
           (0.030, 0.985), (0.0, 1.0)]
    corps = fuseau(pts, L, 52)
    x, y, z = corps.v[:, 0], corps.v[:, 1], corps.v[:, 2]
    f = z / L
    corps.v[:, 1] *= 0.62                                                              # plat : bien moins haut que large
    th = np.abs(np.arctan2(x, corps.v[:, 1]))
    t = np.tile(OCRE, (len(z), 1))
    t[(f > 0.52) & (((f - 0.52) / 0.045) % 1.0 < 0.34) & (th < 2.0)] = BOUE            # les bandes du dos et de la queue
    t[th > 2.35] = VENTRE
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)
    a.tete = Vector(fil.cadre(0.16 * L)[0])

    # ----- les écailles du dos : une crête de grosses plaques en deux rangées, de la nuque à la queue -----
    ecailles = None
    for f_ in np.linspace(0.34, 0.90, 26):
        c_, av, nq = fil.cadre(f_ * L)
        r = float(np.interp(f_, [p[1] for p in pts], [p[0] for p in pts]))
        for dec in (-0.35, 0.35):
            lat = np.cross(np.array(av), np.array(nq))
            e = A.boule(1.0, 10, 6).etire(0.020, 0.026, 0.012).pose(tuple(np.array(c_) + np.array(nq) * (r * 0.62 + 0.004) + lat * dec * r * 0.9))
            ecailles = e if ecailles is None else ecailles + e
    a.piece("ecailles", ecailles, tuple(BOUE))

    # ----- les yeux : deux bosses à fleur du dessus du crâne, un œil jaune à fente ; les narines au bout du museau -----
    c1, av1, nq1 = fil.cadre(0.255 * L)
    lat1 = np.cross(np.array(av1), np.array(nq1))
    for nom, c in (("G", 1), ("D", -1)):
        pos = np.array(c1) + np.array(nq1) * 0.052 + lat1 * c * 0.052
        a.piece("bosse_" + nom, A.boule(1.0, 20, 10).etire(0.034, 0.040, 0.026), tuple(OCRE), pos=tuple(pos))
        a.oeil("oeil_" + nom, Vector(pos) + Vector(nq1) * 0.020 + Vector(av1) * -0.006, Vector((c * 0.55, -0.45, 0.70)).normalized(), 0.0150)
        c2, av2, nq2 = fil.cadre(0.040 * L)
        a.piece("narine_" + nom, A.boule(1.0, 14, 8).etire(0.010, 0.014, 0.008), CHARBON,
                pos=tuple(np.array(c2) + np.array(nq2) * 0.020 + np.array([c * 0.014, 0.0, 0.0])), poil=False)

    # ----- les dents : une rangée de petites dents blanches inégales qui dépassent le long de la mâchoire fermée -----
    dents = None
    for f_ in np.linspace(0.04, 0.34, 24):
        c_, av, nq = fil.cadre(f_ * L)
        r = float(np.interp(f_, [p[1] for p in pts], [p[0] for p in pts]))
        lat = np.cross(np.array(av), np.array(nq))
        for cote in (1, -1):
            h = 0.016 + 0.010 * ((int(f_ * 1000) % 3) / 2.0)
            d = A.tour(A.profil([(0, 0), (0.007, 0.002), (0.004, 0.012), (0, h)], 4), 8)
            d = d.pose((0, 0, 0), (180, 0, 0)).pose(tuple(np.array(c_) + lat * cote * r * 0.95 - np.array(nq) * r * 0.20 + np.array([0.0, 0.0, 0.0])))
            dents = d if dents is None else dents + d
    a.piece("dents", dents, DENT, poil=False)

    # ----- les pattes : quatre courtes pattes écartées, épaisses, aux orteils griffus ; le pied à plat -----
    for nom, x_, y_, av in (("av_G", 0.190, -0.150, -0.060), ("av_D", -0.190, -0.150, -0.060), ("ar_G", 0.190, 0.400, 0.060), ("ar_D", -0.190, 0.400, 0.060)):
        c = 1 if x_ > 0 else -1
        ch = [(x_ * 0.55, y_, 0.130), (x_ * 1.30, y_ + av * 0.4, 0.100), (x_ * 1.55, y_ + av, 0.030)]
        m = A.tube(A.courbe(propres(ch), 5), lambda t: 0.060 - 0.016 * t, 14)
        m.teinte = np.tile(OCRE, (len(m.v), 1))
        a.piece("patte_" + nom, m, None)
        orteils = None
        for k in (-1, 0, 1):
            o = A.boule(1.0, 12, 6).etire(0.014, 0.050, 0.012).pose((k * 0.030, -0.040, 0.0), (0, 0, k * 14))
            orteils = o if orteils is None else orteils + o
        a.piece("orteils_" + nom, orteils, tuple(BOUE), pos=(x_ * 1.55, y_ + av - 0.030, 0.014), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("crocodile", styles.style_de("crocodile"), sys.modules[__name__]), "Crocodile")
