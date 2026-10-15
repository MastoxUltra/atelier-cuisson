"""Le suricate en peluche cousue main : un fauve sable, des rayures sombres en travers du dos, des taches noires
autour des yeux, le ventre clair et nu, un museau pointu, de petites oreilles rondes et noires, une queue fine à bout
noir. La sentinelle : debout sur ses pattes arrière et sa queue (un trépied), le torse droit, les petites mains sur le
ventre, la tête haute et tournée vers nous, deux yeux grands ouverts qui surveillent le ciel.

    python suricate.py        fabrique la fiche art/apercus/animaux/suricate.png (cousu main, palier 2)
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


FAUVE = np.array(M.hexa("#f0cc90"))           # la dominante : fauve sable (le poil le fonce)
CLAIR = np.array(M.hexa("#fff0d4"))           # le ventre, la gorge
RAYURE = np.array(M.hexa("#8a6040"))          # l'accent : les rayures du dos
NOIR = np.array(M.hexa("#2e2826"))            # les taches des yeux, les oreilles, le bout de la queue
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
    a = K.Animal("suricate")
    a.taille = 0.55

    # ----- le corps : un long tronc debout, un peu penché en arrière ; les rayures sombres en travers du dos ; le ventre clair -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.060, 0.080), (0.040, 0.220), (0.010, 0.360), (-0.020, 0.470))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.05, 0.085), (0.22, 0.115), (0.60, 0.100), (0.90, 0.078), (1.0, 0.0)], L, 56)
    z = corps.v[:, 2]
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(FAUVE, (len(z), 1))
    t[(((z - 0.20 * L) / 0.060) % 1.0 < 0.34) & (th < 1.6) & (z > 0.18 * L) & (z < 0.85 * L)] = RAYURE
    t[th > 2.3] = CLAIR
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- la tête : petite et pointue, le museau fin ; les taches noires autour des yeux ; les petites oreilles rondes -----
    H = A.cadre(Vector((0.0, -0.040, 0.560)), Vector((0.34, -1.0, 0.04)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.10, 0.060), (0.34, 0.068), (0.62, 0.050), (0.88, 0.034), (0.97, 0.026), (1.0, 0.0)], 0.200, 40, 0.005)
    tete.teinte = np.where((tete.v[:, 2] > 0.70 * 0.200)[:, None], CLAIR, FAUVE)
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0, -0.040)))
    a.piece("nez", A.boule(1.0, 16, 8).etire(0.014, 0.010, 0.010), tuple(NOIR), mat=H @ A.repere((0, 0.006, 0.152)), poil=False)
    a.tete = H @ Vector((0, 0.0, 0.100))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.60, 0.24, 0.30))
        a.rustine("tache_" + nom, "tete", H @ Vector((0, 0.0, 0.020)), regard, 0.30, tuple(NOIR), 0.003, 0)
        p, n = a.surface("tete", H @ Vector((0, 0.0, 0.020)), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0165)
        po = A.profil([(0, 0), (0.020, 0.006), (0.026, 0.022), (0.020, 0.036), (0.008, 0.042), (0, 0.046)], 5)
        a.piece("oreille_" + nom, A.tour(po, 20).etire(1.0, 0.45, 1.0), tuple(NOIR),
                mat=A.cadre(H @ Vector((c * 0.050, 0.050, -0.040)), H3 @ Vector((c * 0.50, 0.20, 0.84)), H3 @ Vector((c * 0.3, -0.9, 0.0))))

    # ----- les petits bras : les mains jointes sur le ventre ; les pattes : deux gros pieds, la queue : le troisième pied -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.085, 0.000, 0.400), (c * 0.110, -0.040, 0.330), (c * 0.060, -0.080, 0.300), (c * 0.026, -0.082, 0.310)]
        a.piece("bras_" + nom, A.tube(A.courbe(propres(ch), 5), lambda t: 0.020 - 0.006 * t, 12), tuple(FAUVE))
        a.piece("main_" + nom, A.boule(1.0, 16, 8).etire(0.018, 0.022, 0.016), tuple(NOIR), pos=ch[-1])
        a.piece("cuisse_" + nom, A.boule(1.0, 24, 12).etire(0.044, 0.070, 0.056), tuple(FAUVE), pos=(c * 0.070, 0.040, 0.070))
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.036, 0.088, 0.022), tuple(NOIR), pos=(c * 0.074, -0.040, 0.022), rot=(0, 0, c * 8))
    chemin = [(0.0, 0.100, 0.100), (0.0, 0.180, 0.050), (0.0, 0.250, 0.030), (0.030, 0.320, 0.026)]
    a.piece("queue", K.tube_peint(A.courbe(chemin, 6), lambda t: 0.032 - 0.016 * t, [(0.80, tuple(FAUVE)), (1, tuple(NOIR))], 12), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("suricate", styles.style_de("suricate"), sys.modules[__name__]), "Suricate")
