"""Le tapir en peluche de velours ras (2e dessin, d'après photos : un corps en POIRE, pas un blob) : l'avant et les
pattes d'un ardoise bleutée, la selle crème qui tombe d'un trait net derrière les épaules et couvre le dos jusqu'à la
croupe, le dos voûté, l'arrière-train large et haut, le cou court et épais, et une TÊTE en coin dont le museau se
prolonge en une courte trompe qui déborde la bouche (le profil de la tête et du nez ne font qu'une ligne) ; de petites
oreilles rondes bordées de blanc, de petits yeux, des pattes courtes à trois sabots, un moignon de queue. Il flaire,
la tête basse, tout le poids sur l'arrière.

    python tapir.py        fabrique la fiche art/apercus/animaux/tapir.png (velours ras, palier 3)
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


ARDOISE = np.array(M.hexa("#7189ad"))         # la dominante : ardoise bleutée moyenne (le poil la fonce)
CREME = np.array(M.hexa("#fbf4e4"))           # l'accent : la selle, le bord des oreilles
SOMBRE = np.array(M.hexa("#4e5d7c"))          # le museau, le dedans des oreilles
SABOT = M.hexa("#3a3a44")                     # les sabots, les narines
PAS = 0.010


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=72, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("tapir")
    a.taille = 2.00

    # ----- le corps, le cou, la tête et la trompe d'un seul tenant, couchés le long d'une courbe : la croupe haute et large,
    #       le dos voûté, les épaules plus étroites, le cou court, la tête en coin qui descend, le nez qui déborde -----
    chemin = [(0.0, y, z) for y, z in ((0.580, 0.620), (0.380, 0.710), (0.120, 0.740), (-0.140, 0.700), (-0.400, 0.600),
                                       (-0.650, 0.480), (-0.860, 0.390), (-1.040, 0.320))]
    fil = K.Fil(chemin, (1, 0, 0))
    L = fil.long
    pts = [(0.0, 0.0), (0.02, 0.150), (0.10, 0.240), (0.24, 0.282), (0.40, 0.268), (0.52, 0.222), (0.60, 0.170), (0.68, 0.152),
           (0.76, 0.130), (0.84, 0.108), (0.90, 0.086), (0.95, 0.074), (0.99, 0.062), (1.0, 0.0)]
    bloc = fuseau(pts, L, 80)
    x, y, z = bloc.v[:, 0], bloc.v[:, 1], bloc.v[:, 2]
    f = z / L
    th = np.abs(np.arctan2(x, y))
    bloc.v[:, 1] += 0.040 * np.exp(-((f - 0.36) / 0.12) ** 2) * (y > 0)                 # le dos voûté
    t = np.tile(ARDOISE, (len(z), 1))
    t[(f < 0.50) & (th < 2.45)] = CREME                                                   # la selle, d'un trait net
    t[(f > 0.86) & (y < -0.020)] = SOMBRE                                                 # le dessous du museau
    bloc.teinte = t
    a.piece("bloc", bloc.sculpte(fil.couche), None)
    centre, avant, nuque = fil.cadre(0.995 * L)
    a.tete = Vector(fil.cadre(0.90 * L)[0])

    # ----- la mâchoire du bas, plus courte que le nez ; les narines ; l'œil minuscule ; l'oreille ronde bordée de blanc -----
    c1, av1, nq1 = fil.cadre(0.90 * L)
    a.piece("machoire", A.boule(1.0, 24, 12).etire(0.044, 0.092, 0.030), tuple(SOMBRE),
            mat=A.cadre(Vector(c1) - Vector(nq1) * 0.052 - Vector(av1) * 0.030, Vector(av1), Vector(nq1)))
    flanc = np.array([1.0, 0.0, 0.0])
    for nom, c in (("G", 1), ("D", -1)):
        c2, av2, nq2 = fil.cadre(0.97 * L)
        a.piece("narine_" + nom, A.boule(1.0, 14, 8).etire(0.016, 0.022, 0.012), SABOT,
                pos=tuple(np.array(c2) - np.array(nq2) * 0.020 + np.array([c * 0.030, 0.0, 0.0])), poil=False)
        c3, av3, nq3 = fil.cadre(0.800 * L)
        p, n = a.surface("bloc", Vector(c3), Vector(flanc * c * 0.92 + np.array(nq3) * 0.30 - np.array(av3) * 0.10))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0185)
        c4, av4, nq4 = fil.cadre(0.700 * L)
        E = A.cadre(Vector(c4) + Vector(nq4) * 0.150 + Vector((c * 0.075, 0.0, 0.0)), Vector((c * 0.55, 0.15, 0.80)), Vector((c * 0.3, -0.9, 0.0)))
        po = A.profil([(0, 0), (0.044, 0.010), (0.054, 0.040), (0.044, 0.074), (0.020, 0.094), (0, 0.102)], 6)
        a.piece("oreille_" + nom, A.tour(po, 28).etire(1.0, 0.45, 1.0), tuple(ARDOISE), mat=E)
        a.piece("bord_" + nom, A.tour(po, 24).etire(0.62, 0.40, 0.70).pose((0, 0.010, 0.008)), tuple(CREME), mat=E, poil=False)

    # ----- les pattes : courtes, épaisses, trois sabots devant ; l'avant gauche avancée à tâtons ; un moignon de queue -----
    def pilier(haut, bas, r):
        fl = K.Fil([haut, ((haut[0] + bas[0]) / 2, (haut[1] + bas[1]) / 2, (haut[2] + bas[2]) / 2), bas], (1, 0, 0))
        m = fuseau([(0.0, r * 1.20), (0.40, r * 0.92), (0.86, r * 0.82), (1.0, r * 0.88)], fl.long, 40, 0.010)
        m.teinte = np.tile(ARDOISE, (len(m.v), 1))
        return m.sculpte(fl.couche)
    for nom, x_, y_, r, av in (("av_G", 0.150, -0.440, 0.092, -0.140), ("av_D", -0.150, -0.440, 0.092, 0.0),
                               ("ar_G", 0.175, 0.470, 0.108, 0.0), ("ar_D", -0.175, 0.470, 0.108, 0.0)):
        a.piece("patte_" + nom, pilier((x_, y_, 0.560), (x_ * 1.02, y_ + av, 0.040), r), None)
        for k in (-1, 0, 1):
            a.piece("sabot_%s%d" % (nom, k), A.boule(1.0, 12, 6).etire(0.028, 0.036, 0.024), SABOT,
                    pos=(x_ * 1.02 + k * 0.050, y_ + av - r * 0.95, 0.026), poil=False)
    a.piece("queue", A.boule(1.0, 20, 10).etire(0.040, 0.050, 0.044), tuple(CREME), pos=(0.0, 0.620, 0.600))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tapir", styles.style_de("tapir"), sys.modules[__name__]), "Tapir")
