"""Le fourmilier en peluche de velours ras : un gris brun, la grande bande noire bordée de blanc qui part de la
poitrine et file en diagonale vers le dos, un long museau tubulaire en baguette à la bouche minuscule, de tout petits
yeux et une queue énorme en panache de plumes pendantes. Il marche sur les articulations, les griffes énormes des
antérieurs repliées : l'aspirateur de termitières : le museau au ras du sol qui renifle, le dos voûté, le panache qui
traîne et se soulève.

    python fourmilier.py        fabrique la fiche art/apercus/animaux/fourmilier.png (velours ras, palier 3)
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


GRIS = np.array(M.hexa("#b4a498"))            # la dominante : gris brun (le poil le fonce : on le prend clair)
NOIR = np.array(M.hexa("#3a3434"))            # l'accent : la bande
BLANC = np.array(M.hexa("#fff6e8"))           # le liseré de la bande
CLAIR = np.array(M.hexa("#d8cabc"))
GRIFFE = M.hexa("#f2e4c8")
CHARBON = M.hexa("#2e2828")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("fourmilier")
    a.taille = 1.80                           # queue comprise

    # ----- le corps : un long œuf voûté ; la grande bande noire bordée de blanc, en diagonale du cou à l'épaule opposée -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.420, 0.380), (0.250, 0.440), (0.000, 0.470), (-0.250, 0.430), (-0.400, 0.340))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.090), (0.14, 0.150), (0.45, 0.185), (0.78, 0.170), (0.94, 0.120), (1.0, 0.0)], L, 80, 0.007)
    x, y, z = corps.v[:, 0], corps.v[:, 1], corps.v[:, 2]
    th = np.arctan2(x, y)
    f = z / L
    diag = f - 0.34 - 0.15 * (th / math.pi)                                            # la diagonale descend du dos vers le ventre
    t = np.tile(GRIS, (len(z), 1))
    t[(f > 0.20) & (np.abs(th) < 2.6)] = GRIS
    t[(np.abs(diag - 0.22) < 0.16) & (f > 0.55) & (np.abs(th) < 2.4)] = BLANC
    t[(np.abs(diag - 0.22) < 0.12) & (f > 0.55) & (np.abs(th) < 2.4)] = NOIR
    t[np.abs(th) > 2.7] = CLAIR
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le museau : un long tube mince qui descend de la tête vers le sol, la bouche minuscule au bout ; la petite tête -----
    H = Vector((0.0, -0.470, 0.340))
    chemin = [H + Vector((0.0, 0.0, 0.030)), H + Vector((0.0, -0.150, -0.020)), H + Vector((0.0, -0.320, -0.100)), H + Vector((0.0, -0.470, -0.200)),
              H + Vector((0.0, -0.560, -0.270))]
    a.piece("museau", K.tube_peint(A.courbe(propres(chemin), 6), lambda t: 0.082 - 0.056 * t, [(0.60, tuple(GRIS)), (1, tuple(NOIR))], 20), None)
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.090, 0.110, 0.095), tuple(GRIS), pos=tuple(H + Vector((0.0, 0.040, 0.030))))
    a.tete = H + Vector((0.0, -0.220, -0.060))
    for nom, c in (("G", 1), ("D", -1)):
        a.oeil("oeil_" + nom, tuple(H + Vector((c * 0.078, -0.020, 0.060))), (c * 0.90, -0.30, 0.30), 0.0125)
        po = A.profil([(0, 0), (0.026, 0.008), (0.032, 0.030), (0.024, 0.050), (0.008, 0.060), (0, 0.064)], 5)
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.42, 1.0), tuple(NOIR),
                mat=A.cadre(H + Vector((c * 0.070, 0.090, 0.090)), Vector((c * 0.40, 0.10, 0.90)), Vector((c * 0.3, -0.9, 0.0))))

    # ----- la queue : un énorme panache de longues mèches plates, qui traîne et se soulève ; les pattes : courtes, les antérieures
    #       aux énormes griffes repliées (il marche sur les articulations) -----
    racine = np.array([0.0, 0.400, 0.360])
    plume = None
    for k in range(9):
        u = k / 8.0 - 0.5
        ch = [tuple(racine), tuple(racine + np.array([u * 0.10, 0.150, 0.000])), tuple(racine + np.array([u * 0.26, 0.340, -0.060])),
              tuple(racine + np.array([u * 0.40, 0.560, -0.130 + 0.050 * math.cos(u * 3)]))]
        m = A.tube(A.courbe(ch, 6), lambda t: 0.060 + 0.070 * math.sin(math.pi * min(t * 1.15, 1.0)) - 0.030 * t, 12)
        plume = m if plume is None else plume + m
    a.piece("queue", plume, tuple(GRIS))
    for nom, x_, y_ in (("av_G", 0.110, -0.230), ("av_D", -0.110, -0.230), ("ar_G", 0.115, 0.300), ("ar_D", -0.115, 0.300)):
        a.piece("patte_" + nom, A.tube(A.courbe([(x_, y_, 0.310), (x_ * 1.05, y_ - 0.010, 0.170), (x_ * 1.05, y_ - 0.030, 0.050)], 5), 0.048, 14), tuple(GRIS))
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.050, 0.080, 0.030), tuple(NOIR), pos=(x_ * 1.05, y_ - 0.060, 0.030))
        if nom.startswith("av"):
            c = 1 if x_ > 0 else -1
            g = None
            for k in (-1, 0, 1):
                gr = A.tour(A.profil([(0, 0), (0.016, 0.004), (0.012, 0.050), (0.005, 0.100), (0, 0.130)], 5), 12)
                gr = gr.pose((0, 0, 0), (-74, 0, 0)).pose((k * 0.030, -0.040, 0.0), (0, 0, k * 8))
                g = gr if g is None else g + gr
            a.piece("griffes_" + nom, g, GRIFFE, pos=(x_ * 1.05, y_ - 0.090, 0.050), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("fourmilier", styles.style_de("fourmilier"), sys.modules[__name__]), "Fourmilier")
