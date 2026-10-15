"""L'oryctérope en peluche de velours ras (2e dessin, d'après photos : plus de tube rose sur une armure) : le cochon de
terre, d'un gris sable rosé aux poils clairsemés ; le dos très arqué, l'arrière-train haut et lourd ; une tête longue qui
s'effile en un museau tubulaire à la truffe plate, de très longues oreilles dressées qui se rejoignent presque au sommet,
les yeux petits, une grosse queue épaisse à la base qui s'amincit, de fortes pattes aux griffes de pelle. Le museau au
ras du sol, le dos en arc, les oreilles tournées vers nous : il flaire la termitière.

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


SABLE = np.array(M.hexa("#e6cfc0"))           # la dominante : gris sable rosé (le poil le fonce)
ROSE = np.array(M.hexa("#f0c4bc"))            # le museau, le dedans des oreilles, le ventre
FONCE = np.array(M.hexa("#b09890"))           # le dessus de la queue, le bas des pattes
GRIFFE = M.hexa("#d8c8b8")
CHARBON = M.hexa("#3a3234")
PAS = 0.008
LACET = 24.0


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("orycterope")
    a.taille = 1.40

    # ----- le corps, le cou, la tête et le museau d'une pièce, couchés le long d'une courbe : l'arrière-train haut, le dos
    #       qui s'arque, les épaules plus basses, la tête qui descend en un long museau tubulaire -----
    chemin = [(0.0, y, z) for y, z in ((0.520, 0.560), (0.320, 0.640), (0.080, 0.640), (-0.160, 0.560), (-0.400, 0.450),
                                       (-0.620, 0.340), (-0.800, 0.250), (-0.950, 0.200))]
    fil = K.Fil(chemin, (1, 0, 0))
    L = fil.long
    pts = [(0.0, 0.0), (0.02, 0.140), (0.10, 0.210), (0.24, 0.236), (0.40, 0.215), (0.52, 0.170), (0.60, 0.130), (0.68, 0.110),
           (0.76, 0.088), (0.84, 0.070), (0.92, 0.056), (0.975, 0.050), (1.0, 0.0)]
    corps = fuseau(pts, L, 64)
    x, y, z = corps.v[:, 0], corps.v[:, 1], corps.v[:, 2]
    f = z / L
    th = np.abs(np.arctan2(x, y))
    t = np.tile(SABLE, (len(z), 1))
    t[(th > 2.3)] = ROSE
    t[f > 0.84] = ROSE                                                                 # le museau
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)
    a.tete = Vector(fil.cadre(0.84 * L)[0])

    # ----- la truffe plate, les narines ; les yeux petits ; les LONGUES oreilles dressées -----
    c1, av1, nq1 = fil.cadre(0.995 * L)
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.044, 0.020, 0.044), tuple(ROSE), pos=tuple(np.array(c1) + np.array(av1) * 0.006), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("narine_" + nom, A.boule(1.0, 12, 6).etire(0.010, 0.008, 0.010), CHARBON,
                pos=tuple(np.array(c1) + np.array(av1) * 0.026 + np.array([c * 0.016, 0.0, 0.0])), poil=False)
        c2, av2, nq2 = fil.cadre(0.700 * L)
        p, n = a.surface("corps", Vector(c2), Vector(np.array([c * 0.88, 0.0, 0.0]) + np.array(nq2) * 0.30 - np.array(av2) * 0.20))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0150)
        c3, av3, nq3 = fil.cadre(0.640 * L)
        po = A.profil([(0, 0), (0.036, 0.010), (0.044, 0.060), (0.040, 0.130), (0.030, 0.200), (0.014, 0.248), (0, 0.268)], 6)
        vers = (Vector(nq3) * 0.90 + Vector((c * 0.40, 0.0, 0.0)) - Vector(av3) * 0.10).normalized()
        E = A.cadre(Vector(c3) + Vector(nq3) * 0.100 + Vector((c * 0.040, 0.0, 0.0)), vers, Vector(av3))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 32).etire(1.0, 0.34, 1.0), [(0.100, tuple(SABLE)), (9, tuple(SABLE))]), None, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 24).etire(0.58, 0.28, 0.86).pose((0, 0.008, 0.010)), tuple(ROSE), mat=E, poil=False)

    # ----- les pattes : fortes, les arrière plus longues et coudées, les avant plus courtes aux grandes griffes de pelle -----
    def patte(pts_, r0):
        ft = K.Fil(pts_, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.35, r0 * 0.78), (0.70, r0 * 0.56), (0.94, r0 * 0.52), (1.0, 0.0)], ft.long, 32, 0.008)
        m.teinte = np.where((m.v[:, 2] > 0.60 * ft.long)[:, None], tuple(FONCE), tuple(SABLE))
        return m.sculpte(ft.couche)
    for nom, pts_, r0 in (("av_G", [(0.110, -0.300, 0.440), (0.120, -0.330, 0.250), (0.120, -0.360, 0.040)], 0.090),
                          ("av_D", [(-0.110, -0.300, 0.440), (-0.120, -0.330, 0.250), (-0.120, -0.360, 0.040)], 0.090),
                          ("ar_G", [(0.140, 0.420, 0.540), (0.170, 0.360, 0.330), (0.150, 0.440, 0.040)], 0.110),
                          ("ar_D", [(-0.140, 0.420, 0.540), (-0.170, 0.360, 0.330), (-0.150, 0.440, 0.040)], 0.110)):
        a.piece("patte_" + nom, patte(pts_, r0), None)
        x_, y_, _z = pts_[-1]
        griffes = None
        for k in (-1, 0, 1):
            g = A.tour(A.profil([(0, 0), (0.014, 0.004), (0.010, 0.030), (0.004, 0.056), (0, 0.070)], 5), 10)
            g = g.pose((0, 0, 0), (-84, 0, 0)).pose((k * 0.030, -0.040, 0.0), (0, 0, k * 10))
            griffes = g if griffes is None else griffes + g
        a.piece("griffes_" + nom, griffes, GRIFFE, pos=(x_, y_ - 0.030, 0.026), poil=False)
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(r0 * 0.70, r0 * 0.90, 0.030), tuple(FONCE), pos=(x_, y_ + 0.010, 0.030))

    # ----- la queue : très épaisse à la base, qui s'amincit en pointe -----
    qf = K.Fil([(0.0, 0.540, 0.540), (0.0, 0.700, 0.420), (0.0, 0.820, 0.250), (0.020, 0.860, 0.110)], (1, 0, 0))
    queue = fuseau([(0.0, 0.110), (0.30, 0.090), (0.70, 0.050), (0.96, 0.020), (1.0, 0.0)], qf.long, 36, 0.008)
    queue.teinte = np.where((queue.v[:, 1] > 0.0)[:, None], tuple(FONCE), tuple(SABLE))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("orycterope", styles.style_de("orycterope"), sys.modules[__name__]), "Oryctérope")
