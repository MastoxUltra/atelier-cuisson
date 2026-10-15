"""L'oryctérope en peluche de velours ras : un rose chair pâle grisé de poils clairsemés, le dos très arqué, un long
museau de cochon à la truffe plate, de longues oreilles en oreilles de lapin à pointe repliée, une grosse queue épaisse
à la base, des pattes courtes aux griffes de pelle. Le cochon de terre : le dos en arc, le museau au ras de la termitière
qu'il renifle, les oreilles dressées, une patte avant grattant le sol, une expression d'extrême sérieux.

    python orycterope.py        fabrique la fiche art/apercus/animaux/orycterope.png (velours ras, palier 3)
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


ROSE = np.array(M.hexa("#f2c8b8"))            # la dominante : rose chair pâle
GRIS = np.array(M.hexa("#d8c8c0"))            # le dos grisé, les poils clairsemés
OREILLE = np.array(M.hexa("#e8a8a0"))         # le dedans des oreilles
GRIFFE = M.hexa("#e8dcc8")
CHARBON = M.hexa("#3a3030")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=60, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("orycterope")
    a.taille = 1.70                           # queue comprise

    # ----- le corps : un dos très arqué, la croupe haute, le poitrail bas ; le dos grisé, le ventre rose -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.420, 0.420), (0.250, 0.560), (0.000, 0.610), (-0.250, 0.540), (-0.400, 0.420))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.120), (0.14, 0.190), (0.45, 0.210), (0.78, 0.190), (0.94, 0.130), (1.0, 0.0)], L, 64)
    corps.teinte = np.where((np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1])) < 1.9)[:, None], GRIS, ROSE)
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou, la tête et le long museau de cochon à truffe plate ; baissé, au ras du sol -----
    H = Vector((0.0, -0.560, 0.330))
    chemin = [H + Vector((0.0, 0.060, 0.080)), H + Vector((0.0, -0.040, 0.030)), H + Vector((0.0, -0.170, -0.040)), H + Vector((0.0, -0.290, -0.100)), H + Vector((0.0, -0.360, -0.130))]
    a.piece("museau", K.tube_peint(A.courbe(propres(chemin), 6), lambda t: 0.118 - 0.054 * t, [(0.84, tuple(ROSE)), (1, tuple(OREILLE))], 20), None)
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.060, 0.034, 0.060), tuple(OREILLE), pos=tuple(H + Vector((0.0, -0.380, -0.136))), rot=(-24, 0, 0), poil=False)
    a.piece("crane", A.boule(1.0, 36, 18).etire(0.120, 0.140, 0.120), tuple(GRIS), pos=tuple(H + Vector((0.0, 0.090, 0.120))))
    a.tete = H + Vector((0.0, -0.150, -0.030))
    for nom, c in (("G", 1), ("D", -1)):
        a.oeil("oeil_" + nom, tuple(H + Vector((c * 0.100, -0.030, 0.100))), (c * 0.90, -0.30, 0.30), 0.0125)
        # les grandes oreilles de lapin, longues et dressées, la pointe repliée
        po = A.profil([(0, 0), (0.046, 0.012), (0.058, 0.070), (0.050, 0.150), (0.034, 0.220), (0.012, 0.268), (0, 0.285)], 6)
        E = A.cadre(H + Vector((c * 0.080, 0.130, 0.200)), Vector((c * 0.34, 0.16, 0.92)), Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 28).etire(1.0, 0.34, 1.0), [(0.250, tuple(GRIS)), (9, tuple(OREILLE))]), None, mat=E)

    # ----- la queue : épaisse à la base, longue et conique ; les pattes : courtes, aux griffes de pelle ; l'une gratte -----
    a.piece("queue", K.tube_peint(A.courbe([(0.0, 0.440, 0.400), (0.0, 0.620, 0.300), (0.0, 0.800, 0.170), (0.0, 0.880, 0.070)], 6),
                                  lambda t: 0.120 - 0.100 * t, [(1, tuple(GRIS))], 18), None)
    for nom, x_, y_, gratte in (("av_G", 0.130, -0.240, True), ("av_D", -0.130, -0.240, False), ("ar_G", 0.140, 0.320, False), ("ar_D", -0.140, 0.320, False)):
        c = 1 if x_ > 0 else -1
        bas = (x_ * 1.05, y_ - (0.150 if gratte else 0.030), 0.130 if gratte else 0.040)
        a.piece("patte_" + nom, A.tube(A.courbe(propres([(x_, y_, 0.400), (x_ * 1.03, y_ - 0.040, 0.250), bas]), 5), 0.060, 14), tuple(ROSE))
        g = None
        for k in (-1, 0, 1):
            gr = A.tour(A.profil([(0, 0), (0.018, 0.004), (0.014, 0.044), (0.006, 0.088), (0, 0.108)], 5), 12)
            gr = gr.pose((0, 0, 0), (-80, 0, 0)).pose((k * 0.034, -0.030, 0.0), (0, 0, k * 6))
            g = gr if g is None else g + gr
        a.piece("griffes_" + nom, g, GRIFFE, pos=(bas[0], bas[1] - 0.030, bas[2] - 0.010), poil=False)
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.050, 0.064, 0.032), tuple(ROSE), pos=(bas[0], bas[1] - 0.012, bas[2] + 0.004))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("orycterope", styles.style_de("orycterope"), sys.modules[__name__]), "Oryctérope")
