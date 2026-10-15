"""Le caméléon en peluche, cousu main : un rose vif zébré de bandes turquoise, un corps haut et aplati comme une feuille,
la crête du dos en dents de scie, la queue enroulée en escargot, et surtout ses yeux : deux tourelles coniques qui
tournent chacune de leur côté. Il avance au ralenti, une patte levée au-dessus du vide, un œil rivé sur nous et l'autre
qui regarde très haut, derrière lui, quelque chose que nous ne verrons jamais.

    python cameleon.py        fabrique la fiche art/apercus/animaux/cameleon.png (cousu main, palier 2)
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
    """Les points d'un tracé sans doublons consécutifs (un tube dont deux points se suivent à l'identique se déforme en NaN) ;
    au moins deux points, écartés d'un millimètre au pire."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie

ROSE = M.hexa("#ff8db4")                      # la dominante : rose vif (le poil la fonce un peu)
TURQUOISE = M.hexa("#3fdcd0")                 # l'accent : les bandes, l'iris
CITRON = M.hexa("#fff27a")                    # la crête, le dessous
CHARBON = M.hexa("#3a3236")                   # les griffes, le bout de la queue
CORPS = Vector((0.0, 0.020, 0.190))


def construire():
    a = K.Animal("cameleon")
    a.taille = 0.55

    # ----- le corps : haut, aplati de côté, le dos voûté ; peint de bandes turquoise en travers (avant d'être sculpté) -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(ROSE, float), (len(v), 1))
    bande = (np.floor((v[:, 1] + 1.0) / 0.28) % 2 == 1)
    t[bande] = TURQUOISE
    t[(v[:, 2] < -0.55)] = CITRON                                                  # le ventre
    corps.teinte = t

    def feuille(v):
        s = v * [0.062, 0.175, 0.125]
        s[:, 2] += 0.030 * np.cos(v[:, 1] * 1.4)                                    # le dos voûté
        return s
    G.sillons(corps, [14], 0.004, 1.1)
    a.piece("corps", corps.sculpte(feuille), None, pos=CORPS, rot=(-6, 0, 0))

    # ----- la crête : de petites dents de scie citron le long de l'échine -----
    dents = None
    for i, y in enumerate(np.linspace(-0.130, 0.140, 8)):
        d = A.tour(A.profil([(0, 0), (0.016, 0.004), (0.012, 0.022), (0, 0.040)], 4), 14).etire(0.55, 1.0, 1.0)
        d = d.pose((0, CORPS.y + y, CORPS.z + 0.120 + 0.025 * math.cos(y * 1.4 * 1.0)), (-4, 0, 0))
        dents = d if dents is None else dents + d
    a.piece("crete", dents, CITRON, poil=False)

    # ----- la tête : un coin, le casque pointu vers l'arrière, le menton fin ; tournée vers nous -----
    T = A.repere(Vector((0.0, -0.200, 0.250)), (8, 0, 20))
    T3 = T.to_3x3()

    def casque(v):
        s = v.copy()
        s[:, 2] += 0.060 * K.lisse((v[:, 1] - 0.2) / 0.8) * (1 - v[:, 0] ** 2)       # le casque se relève derrière
        s[:, 0] *= 0.60 + 0.30 * K.lisse((v[:, 1] + 0.3) / 1.0)
        return s * [0.064, 0.100, 0.060]
    a.piece("tete", K.bandes(A.boule(1.0, 40, 20), [(-0.55, CITRON), (9, ROSE)], axe=1).sculpte(casque), None, mat=T)
    a.tete = T @ Vector((0, -0.100, 0.0))
    a.piece("nez", A.boule(1.0, 16, 8).etire(0.012, 0.012, 0.010), CHARBON, mat=T @ A.repere((0, -0.098, 0.004)), poil=False)
    bouche = [T3 @ Vector(d) for d in ((-0.30, -0.78, -0.30), (0.0, -0.98, -0.34), (0.32, -0.76, -0.30))]
    a.broderie("sourire", A.courbe(propres(a.trace("tete", T.to_translation(), bouche, 0.004)), 4), 0.0022, CHARBON)

    # ----- les yeux en tourelle : deux petits cônes de la couleur de la peau, un iris turquoise, une pupille : celui qui
    #       nous regarde droit, l'autre tourné très haut -----
    for nom, c, regard in (("G", 1, (0.40, -0.90, 0.12)), ("D", -1, (-0.80, 0.30, 0.50))):
        place = T @ Vector((c * 0.060, -0.018, 0.034))
        cone = A.boule(1.0, 28, 14).etire(0.040, 0.040, 0.036)
        a.piece("tourelle_" + nom, cone, ROSE, mat=A.repere(place))
        vers = T3 @ Vector(regard)
        vers.normalize()
        p, n = a.surface("tourelle_" + nom, place, vers)
        a.rustine("iris_" + nom, "tourelle_" + nom, place, vers, 0.62, TURQUOISE, 0.003, 14)
        a.oeil("oeil_" + nom, p + n * 0.006, n, 0.0135)

    # ----- les pattes : quatre pattes fines, coudées, aux doigts en pince ; l'avant gauche levée dans le vide -----
    def patte(points, r=0.019):
        return A.tube(A.courbe(points, 6), lambda t: r - 0.006 * t, 12)
    pattes = (("av_D", [(-0.040, -0.110, 0.230), (-0.085, -0.120, 0.130), (-0.060, -0.135, 0.030)]),
              ("ar_G", [(0.040, 0.130, 0.220), (0.085, 0.145, 0.120), (0.060, 0.130, 0.030)]),
              ("ar_D", [(-0.040, 0.130, 0.220), (-0.085, 0.145, 0.120), (-0.060, 0.130, 0.030)]),
              ("av_G", [(0.040, -0.110, 0.230), (0.090, -0.150, 0.190), (0.075, -0.210, 0.175)]))
    for nom, pts in pattes:
        a.piece("patte_" + nom, patte(pts), ROSE)
        x, y, z = pts[-1]
        a.piece("pince_" + nom, A.boule(1.0, 20, 10).etire(0.026, 0.032, 0.015), CHARBON, pos=(x, y - 0.010, z - 0.004 if z < 0.1 else z), poil=False)

    # ----- la queue : un long fouet qui s'enroule en escargot dans son dos, le bout charbon -----
    chemin = [(0.0, 0.160, 0.170)]
    for k in range(1, 15):
        ang = 0.55 * k
        r = 0.150 - 0.0075 * k
        chemin.append((0.0, 0.330 + r * math.sin(ang - 1.0), 0.190 + r * math.cos(ang - 1.0)))
    queue = K.tube_peint(A.courbe(chemin, 4), lambda t: 0.034 - 0.024 * t, [(0.55, ROSE), (0.70, TURQUOISE), (0.88, ROSE), (1.0, CHARBON)], 14)
    a.piece("queue", queue, None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("cameleon", styles.style_de("cameleon"), sys.modules[__name__]), "Caméléon")
