"""La hyène en peluche de velours ras : un gris-brun froid taché de brun sombre (de grandes taches irrégulières nettes),
le dos en pente (les épaules hautes, la croupe basse), une crinière hérissée sur la nuque et l'échine, une grosse tête
carrée au museau noir, de grandes oreilles rondes et un cou de taureau. L'éclat de rire : la tête basse et lopsided,
la gueule entrouverte sur une rangée de dents, un œil oblique : elle a entendu la meilleure.

    python hyene.py        fabrique la fiche art/apercus/animaux/hyene.png (velours ras, palier 3)
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


GRIS = np.array(M.hexa("#c4b8a4"))            # la dominante : gris-brun froid (le poil le fonce : on le prend clair)
TACHE = np.array(M.hexa("#7a6a58"))           # l'accent : les taches
MUSEAU = np.array(M.hexa("#4a4040"))          # le museau, la crinière sombre
CLAIR = np.array(M.hexa("#e8dccb"))           # le ventre, le dedans des oreilles
DENT = M.hexa("#fff6e0")
OEIL = M.hexa("#c8962c")
CHARBON = M.hexa("#2e2828")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=72, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def tacheter(m, graine, n, rayon, couleur, base, ventre=None):
    rng = np.random.default_rng(graine)
    v = m.v
    t = np.tile(base, (len(v), 1))
    cibles = v[rng.choice(len(v), size=min(n, len(v)), replace=False)]
    r = rayon * (0.6 + 0.9 * rng.random(len(cibles)))
    d = np.linalg.norm(v[:, None, :] - cibles[None, :, :], axis=2)
    t[(d < r[None, :]).any(axis=1)] = couleur
    if ventre is not None:
        t[ventre(v)] = CLAIR
    m.teinte = t
    return m


def construire():
    a = K.Animal("hyene")
    a.taille = 1.60

    # ----- le corps : un tronc en pente (les épaules hautes, la croupe basse), le poitrail profond ; taches irrégulières -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.500, 0.520), (0.320, 0.570), (0.060, 0.650), (-0.180, 0.730), (-0.340, 0.760))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.110), (0.15, 0.170), (0.45, 0.190), (0.72, 0.215), (0.92, 0.205), (1.0, 0.0)], L, 72)
    tacheter(corps, 4, 70, 0.055, TACHE, GRIS, ventre=lambda v: (np.abs(np.arctan2(v[:, 0], v[:, 1])) > 2.6))
    a.piece("corps", corps.sculpte(fil.couche), None)
    # la crinière : une brosse hérissée le long de l'échine, de la nuque au milieu du dos
    crin = None
    for i, f in enumerate(np.linspace(0.30, 0.96, 20)):
        c_, av, nq = fil.cadre(f * L)
        r = float(np.interp(f, [0.0, 0.04, 0.15, 0.45, 0.72, 0.92, 1.0], [0.0, 0.110, 0.170, 0.190, 0.215, 0.205, 0.0]))
        e = A.boule(1.0, 10, 6).etire(0.012, 0.020, 0.052).pose(tuple(c_ + nq * (r * 0.98 + 0.020)))
        crin = e if crin is None else crin + e
    a.piece("criniere", crin, tuple(MUSEAU), poil=False)

    # ----- le cou de taureau et la tête : un bloc carré au front plat, le museau noir large ; baissée, penchée ; la gueule -----
    a.piece("cou", A.tube(A.courbe([(0.0, -0.240, 0.760), (0.0, -0.360, 0.740), (0.0, -0.440, 0.690)], 5), lambda t: 0.170 - 0.045 * t, 22), tuple(GRIS))
    H = A.cadre(Vector((0.0, -0.530, 0.640)), Vector((0.36, -1.0, -0.34)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.120), (0.22, 0.150), (0.42, 0.135), (0.62, 0.110), (0.86, 0.102), (0.97, 0.084), (1.0, 0.0)], 0.420, 56, 0.006)
    ang = np.arctan2(tete.v[:, 0], tete.v[:, 1])
    carre = 1.0 + 0.24 * np.abs(np.sin(2 * ang)) * K.lisse((tete.v[:, 2] / 0.420 - 0.40) / 0.2)
    tete.v[:, 0] *= carre
    tete.v[:, 1] *= carre
    tete.teinte = np.where((tete.v[:, 2] > 0.62 * 0.420)[:, None], MUSEAU, GRIS)
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0.030, -0.100)))
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.044, 0.030, 0.028), CHARBON, mat=H @ A.repere((0, 0.060, 0.320)), poil=False)
    a.tete = H @ Vector((0, 0.040, 0.220))
    # la gueule : la mâchoire du bas, entrouverte, la rangée de dents pâles entre les deux
    bas = A.boule(1.0, 36, 18).sculpte(lambda v: K.emousse(v, 0.82) * [0.098, 0.052, 0.170])
    a.piece("machoire", bas, tuple(MUSEAU), mat=H @ A.repere((0, -0.050, 0.180), (-14, 0, 0)))
    for k, dx in enumerate((-0.064, -0.032, 0.0, 0.032, 0.064)):
        a.piece("dent_%d" % k, A.boule(1.0, 8, 4).etire(0.010, 0.010, 0.020), DENT, mat=H @ A.repere((dx, 0.000, 0.250), (170, 0, 0)), poil=False)

    # ----- les yeux : obliques, d'ambre sombre, sous un sourcil rieur ; les oreilles : deux grandes rondes sur le côté -----
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.82, 0.40, 0.14))
        p, n = a.surface("tete", H @ Vector((0, 0.030, 0.080)), regard)
        a.rustine("iris_" + nom, "tete", H @ Vector((0, 0.030, 0.080)), regard, 0.16, OEIL, 0.003, 0)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0170)
        po = A.profil([(0, 0), (0.060, 0.012), (0.074, 0.050), (0.060, 0.092), (0.026, 0.120), (0, 0.130)], 6)
        E = A.cadre(H @ Vector((c * 0.130, 0.100, -0.030)), H3 @ Vector((c * 0.62, 0.20, 0.72)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, A.tour(po, 28).etire(1.0, 0.38, 1.0), tuple(GRIS), mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 20).etire(0.66, 0.30, 0.78).pose((0, 0.008, 0.012)), tuple(CLAIR), mat=E, poil=False)

    # ----- les pattes : les antérieures hautes et fortes, les postérieures courtes et repliées ; la queue : un court plumeau -----
    def patte(pts, r0, graine):
        f = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.45, r0 * 0.66), (0.60, r0 * 0.80), (0.92, r0 * 0.60), (1.0, 0.0)], f.long, 28, 0.009)
        tacheter(m, graine, 14, 0.030, TACHE, GRIS)
        m.teinte[m.v[:, 2] > 0.88 * f.long] = MUSEAU
        return m.sculpte(f.couche)
    for nom, pts, r0, g in (("av_G", [(0.110, -0.260, 0.680), (0.120, -0.270, 0.440), (0.118, -0.262, 0.040)], 0.075, 31),
                            ("av_D", [(-0.110, -0.260, 0.680), (-0.120, -0.270, 0.440), (-0.118, -0.262, 0.040)], 0.075, 32),
                            ("ar_G", [(0.130, 0.420, 0.520), (0.145, 0.360, 0.330), (0.140, 0.410, 0.040)], 0.085, 33),
                            ("ar_D", [(-0.130, 0.420, 0.520), (-0.145, 0.360, 0.330), (-0.140, 0.410, 0.040)], 0.085, 34)):
        a.piece("patte_" + nom, patte(pts, r0, g), None)
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.050, 0.080, 0.028), tuple(MUSEAU), pos=(pts[-1][0], pts[-1][1] - 0.040, 0.028))
    a.piece("queue", K.tube_peint(A.courbe([(0.0, 0.480, 0.540), (0.0, 0.560, 0.470), (0.020, 0.610, 0.340)], 5), lambda t: 0.036 + 0.012 * t, [(0.7, tuple(GRIS)), (1, tuple(MUSEAU))], 14), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("hyene", styles.style_de("hyene"), sys.modules[__name__]), "Hyène")
