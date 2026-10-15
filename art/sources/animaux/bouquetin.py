"""Le bouquetin en peluche, deuxième dessin : le roi de la crête. Gris lavande de pierre bleutée, massif : le garrot en bosse,
le poitrail en proue, les cuisses lourdes, les jambes courtes aux genoux marqués et aux chaussettes chocolat. Il est
perché sur un à-pic qu'on ne voit pas, trois pattes plantées et une avant posée plus haut, la tête de profil, le nez
busqué en l'air, une barbiche chocolat, et sur le crâne les deux cornes qui font tout : deux sabres d'ivoire, noueux, qui
montent et se couchent en grand arc jusqu'au milieu du dos. Il regarde l'horizon : le reste n'est pas à sa hauteur.

    python bouquetin.py        fabrique la fiche art/apercus/animaux/bouquetin.png (style du palier : C, velours ras)
    (le premier dessin, refusé le 15/10 : « maigre, sur des pattes en bâtons, raide, presque face à nous »)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import matieres as M
import peluche as K
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

PIERRE = np.array(M.hexa("#9b8ba9"))          # la dominante (registre : gris lavande, pierre bleutée), un peu soutenue (velours)
PALE = np.array(M.hexa("#e2dbe6"))            # le ventre, l'arrière des cuisses
CHOCO = np.array(M.hexa("#3f2f30"))           # le plastron, les chaussettes, la barbiche, les sabots
IVOIRE = np.array(M.hexa("#f1e6c8"))          # l'accent : les cornes
SABOT = M.hexa("#2a2324")
FIL = M.hexa("#2a1f20")

CROUPE = Vector((0.0, 0.300, 0.500))          # le centre arrière du corps
LONG = 0.62
H = Vector((0.110, -0.480, 1.030))            # le centre de la tête


def gauss(x):
    return np.exp(-np.asarray(x) ** 2)


def corne(RT, cote):
    """Un sabre d'ivoire : il part du front, monte et se couche en grand arc vers l'arrière ; des nœuds tout du long."""
    chemin = [(cote * 0.030, 0.040, 0.060), (cote * 0.040, 0.110, 0.130), (cote * 0.052, 0.220, 0.160), (cote * 0.066, 0.350, 0.130),
              (cote * 0.080, 0.480, 0.050), (cote * 0.092, 0.580, -0.060), (cote * 0.098, 0.640, -0.190)]
    chemin = [(x * 1.0, y * 1.45, z * 1.35) for x, y, z in chemin]                      # immenses : elles font l'arc de la silhouette
    pts = [tuple(RT @ Vector(p)) for p in A.courbe(chemin, 8)]

    def rayon(t):
        noeud = 1 + 0.16 * max(0.0, math.sin(math.tau * 9.5 * t)) ** 3 * (1 - 0.6 * t)
        return (0.0400 - 0.0290 * t ** 1.05) * noeud
    return A.tube(pts, rayon, 16)


def construire():
    a = K.Animal("bouquetin")
    a.taille = 1.55

    # ----- le corps : un tonneau massif, le garrot en bosse, le poitrail en proue, les cuisses lourdes, le ventre rentré -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        f = m.v[:, 2] / L
        t = np.tile(PIERRE, (len(f), 1))
        t[(ang > 2.20) & (f < 0.72)] = PALE
        t[(f > 0.80) & (ang > 1.75)] = CHOCO                    # le plastron : le bas de la poitrine sombre
        return t

    def galbe(L):
        def f(v):
            s = v.copy()
            fr = v[:, 2] / L
            s[:, 0] *= 1 + 0.12 * gauss((fr - 0.10) / 0.10) - 0.10 * gauss((fr - 0.42) / 0.14) + 0.14 * gauss((fr - 0.80) / 0.12)
            dev = v[:, 1] < 0
            s[dev, 1] *= (1 - 0.20 * gauss((fr - 0.42) / 0.14) + 0.22 * gauss((fr - 0.80) / 0.10))[dev]
            s[~dev, 1] *= (1 + 0.20 * gauss((fr - 0.82) / 0.10) + 0.06 * gauss((fr - 0.10) / 0.10))[~dev]    # le garrot en bosse, la croupe
            return s
        return f
    rayon = O.interp([(0.0, 0.0), (0.04, 0.100), (0.16, 0.158), (0.40, 0.160), (0.70, 0.185), (0.90, 0.176), (1.0, 0.135)])
    O.corps_h(a, "corps", CROUPE, LONG, rayon, peint, None, cotes=52, deforme=galbe, pitch=10.0)

    # ----- l'encolure : courte et épaisse ; puis la tête de profil -----
    cou = O.tube_r([(0.0, -0.250, 0.800), (0.060, -0.340, 0.900), (0.140, -0.420, 0.980)], [0.150, 0.125, 0.100], 22)
    cou.teinte = np.tile(PIERRE, (len(cou.v), 1))
    a.piece("cou", cou, None)

    RT = A.repere(H, (-14, 0, 30))               # la tête de trois quarts, le nez levé : les cornes filent sur le cou
    tete = A.boule(1.0, 56, 28)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(PIERRE, (len(u), 1))
    t[(u[:, 1] < -0.55) & (u[:, 2] < 0.25)] = PALE * 0.85 + PIERRE * 0.15
    tete.teinte = t
    a.piece("tete", tete.sculpte(lambda v: K.bosse(v, (0.0, -0.6, 0.8), 0.18, 0.30)).etire(0.102, 0.132, 0.110), None, mat=RT)
    museau = A.boule(1.0, 36, 18).etire(0.064, 0.100, 0.066)
    a.piece("museau", O.teinte(museau, PALE * 0.9 + PIERRE * 0.1), None, mat=RT @ A.repere((0.0, -0.140, -0.040)))   # le nez busqué
    a.piece("nez", A.boule(1.0, 18, 8).etire(0.036, 0.024, 0.026), tuple(CHOCO), mat=RT @ A.repere((0.0, -0.236, -0.026)), poil=False)
    barbe = K.tube_peint(A.courbe([tuple(RT @ Vector(p)) for p in ((0, -0.085, -0.100), (0, -0.098, -0.145), (0, -0.092, -0.190))], 4),
                         lambda t_: 0.020 * (1 - t_) ** 0.8 + 0.005, [(1.0, tuple(M.hexa("#5c3f30")))], 12)         # une mèche, courte, chocolat
    a.piece("barbiche", barbe, None)
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("corne_" + nom, O.teinte(corne(RT, c), IVOIRE), None, poil=False)
        ore = A.tour(A.profil([(0.030, 0), (0.026, 0.030), (0.014, 0.060), (0.004, 0.080), (0, 0.086)], 4), 18).etire(1.0, 0.42, 1.0)
        a.piece("oreille_" + nom, O.couche(O.teinte(ore, PIERRE), RT @ A.cadre(Vector((c * 0.086, 0.040, 0.030)), (c * 0.9, 0.05, -0.20), (0, 0, 1))), None)
    O.paire_yeux(a, "tete", H, (0.84, -0.50, 0.22), 0.0170, couleur_lourde=tuple(PIERRE), coupe=0.60, decolle=0.003, R=RT)
    O.broder(a, "bouche", "museau", RT @ Vector((0, -0.140, -0.040)), [(0.52 * u_, -0.80, -0.40 + 0.10 * u_ * u_) for u_ in np.linspace(-1, 1, 7)], 0.0022, FIL, R=RT)
    a.tete = H + Vector((0.10, -0.20, 0.0))

    # ----- les jambes : courtes, fortes, le genou et le jarret marqués, la chaussette chocolat, le sabot en deux ; l'antérieur
    #       gauche posé plus haut, sur le rocher -----
    avant_D = [(-0.100, -0.250, 0.560), (-0.108, -0.262, 0.440), (-0.100, -0.268, 0.330), (-0.092, -0.274, 0.210), (-0.090, -0.276, 0.100),
               (-0.090, -0.278, 0.050), (-0.090, -0.280, 0.034)]
    avant_G = [(0.100, -0.250, 0.560), (0.114, -0.300, 0.450), (0.116, -0.380, 0.400), (0.114, -0.410, 0.300), (0.112, -0.428, 0.200),
               (0.112, -0.432, 0.165), (0.112, -0.436, 0.150)]
    arriere_D = [(-0.100, 0.260, 0.540), (-0.126, 0.210, 0.420), (-0.116, 0.300, 0.300), (-0.104, 0.260, 0.200), (-0.098, 0.250, 0.100),
                 (-0.098, 0.244, 0.050), (-0.098, 0.240, 0.034)]
    arriere_G = [(0.100, 0.260, 0.540), (0.126, 0.200, 0.420), (0.122, 0.280, 0.290), (0.108, 0.220, 0.200), (0.102, 0.210, 0.100),
                 (0.102, 0.204, 0.050), (0.102, 0.200, 0.034)]
    rayons_av = [0.110, 0.080, 0.062, 0.042, 0.036, 0.034, 0.031]          # l'épaule, le genou gonflé (3e), le boulet (5e)
    rayons_ar = [0.130, 0.092, 0.066, 0.042, 0.036, 0.034, 0.031]
    for nom, pts, ray in (("avant_D", avant_D, rayons_av), ("avant_G", avant_G, rayons_av), ("arriere_D", arriere_D, rayons_ar), ("arriere_G", arriere_G, rayons_ar)):
        a.piece("patte_" + nom, O.membre(pts, ray, [(0.52, tuple(PIERRE)), (1.0, tuple(CHOCO))], 20), None)
        fin = pts[-1]
        onglons = None
        for c2 in (1, -1):
            o = A.tour(A.profil([(0, 0), (0.0200, 0.003), (0.0215, 0.018), (0.0165, 0.036), (0, 0.044)], 4), 20).etire(0.84, 1.20, 1.0)
            o = o.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] - 0.012 * np.clip((0.034 - v[:, 2]) / 0.034, 0, 1), v[:, 2]], axis=1)).pose((c2 * 0.0185, -0.006, 0.0))
            onglons = o if onglons is None else onglons + o
        a.piece("sabot_" + nom, O.couche(onglons, A.repere((fin[0], fin[1], fin[2] - 0.034))), SABOT, poil=False)

    # ----- la queue : un court moignon sombre, relevé -----
    queue = O.tube_r([(0.0, 0.300, 0.560), (0.0, 0.360, 0.580), (0.0, 0.390, 0.560)], [0.034, 0.030, 0.026], 14)
    a.piece("queue", O.teinte(queue, CHOCO), None)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("bouquetin", styles.style_de("bouquetin"), sys.modules[__name__]), "Bouquetin")
