"""Le tamarin en peluche de velours ras (2e dessin, d'après photos : un petit singe, plus un fauve) : un or flamme
lumineux, un corps mince et nerveux, assis droit comme un écureuil ; la crinière n'est qu'une collerette de longs poils
dorés autour du cou et derrière les oreilles, qui laisse voir la petite FACE noire et nue aux grands yeux d'ambre ; des
bras et des jambes fins, de minuscules mains, et une très longue queue fine qui s'enroule. Le seigneur des branches :
assis, le torse droit, la tête de trois quarts, les mains sur le ventre, un regard de curieux.

    python tamarin.py        fabrique la fiche art/apercus/animaux/tamarin.png (velours ras, palier 3)
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


OR = np.array(M.hexa("#ffb030"))              # la dominante : or flamme lumineux
CLAIR = np.array(M.hexa("#ffd070"))           # la collerette, le dessous
FACE = np.array(M.hexa("#5a4044"))            # la face nue, les mains
AMBRE = M.hexa("#f0b030")
CHARBON = M.hexa("#2e2428")
CORPS = Vector((0.0, 0.050, 0.200))
TETE = Vector((0.0, -0.030, 0.390))
LACET = 28.0
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=36, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 5)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("tamarin")
    a.taille = 0.55                           # queue comprise

    # ----- le corps : un œuf mince, assis droit, la poitrine un peu plus claire -----
    corps = A.boule(1.0, 48, 24)
    corps.teinte = np.where((corps.v[:, 1] < -0.55)[:, None], tuple(CLAIR), tuple(OR))
    a.piece("corps", corps.etire(0.074, 0.070, 0.115), None, pos=tuple(CORPS), rot=(-6, 0, 0))

    # ----- la tête : petite et ronde ; la FACE nue et noire en avant, le museau court, de grands yeux d'ambre ; la collerette
    #       de longs poils dorés autour du cou et derrière la tête (pas autour de la face) ; de petites oreilles rondes -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.where(((tete.v[:, 1] < -0.30) & (np.abs(tete.v[:, 0]) < 0.78))[:, None], tuple(FACE), tuple(OR))
    a.piece("tete", tete.etire(0.050, 0.052, 0.048), None, mat=H)
    a.piece("museau", A.boule(1.0, 24, 12).etire(0.024, 0.026, 0.020), tuple(FACE), mat=H @ A.repere((0, -0.046, -0.014)))
    a.tete = H @ Vector((0, -0.060, 0.0))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.46, -0.84, 0.20))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.30, AMBRE, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0145)
        a.piece("oreille_" + nom, A.boule(1.0, 20, 10).etire(0.024, 0.010, 0.026), tuple(FACE), mat=A.cadre(H @ Vector((c * 0.046, 0.016, 0.034)), H3 @ Vector((c * 0.7, 0.2, 0.6)), (0, 0, 1)), poil=False)
    # la collerette : un anneau de longs poils qui retombent sur les épaules et la nuque
    rng = np.random.default_rng(5)
    poils = None
    for i in range(22):
        ang = 2 * math.pi * i / 22
        if math.sin(ang) < -0.35:
            continue                                                                 # rien devant : la face reste dégagée
        base = np.array(TETE) + np.array([0.060 * math.cos(ang), 0.050 * math.sin(ang) + 0.004, -0.030])
        l = 0.060 + 0.030 * rng.random()
        m = A.boule(1.0, 8, 6).etire(0.018, 0.014, l).pose(tuple(base + np.array([0.0, 0.0, -l * 0.7])), (10 * math.sin(ang), -12 * math.cos(ang), 0))
        poils = m if poils is None else poils + m
    a.piece("collerette", poils, tuple(CLAIR))

    # ----- les bras : fins, les mains sur le ventre ; les jambes : repliées, fines, les pieds à plat ; la queue : très longue -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.070, -0.010, 0.290), (c * 0.092, -0.050, 0.210), (c * 0.040, -0.098, 0.190)]
        a.piece("bras_" + nom, A.tube(A.courbe(propres(ch), 5), lambda t: 0.019 - 0.005 * t, 12), tuple(OR))
        a.piece("main_" + nom, A.boule(1.0, 16, 8).etire(0.018, 0.022, 0.014), tuple(FACE), pos=ch[-1], poil=False)
        a.piece("cuisse_" + nom, A.boule(1.0, 24, 12).etire(0.036, 0.074, 0.040), tuple(OR), pos=(c * 0.078, 0.010, 0.060))
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.026, 0.060, 0.014), tuple(FACE), pos=(c * 0.084, -0.060, 0.016), rot=(0, 0, c * 6), poil=False)
    qf = K.Fil([(0.0, 0.130, 0.100), (0.0, 0.230, 0.060), (0.060, 0.320, 0.100), (0.100, 0.310, 0.230), (0.060, 0.230, 0.300),
                (0.0, 0.200, 0.250)], (1, 0, 0))
    queue = fuseau([(0.0, 0.022), (0.50, 0.024), (0.94, 0.018), (1.0, 0.0)], qf.long, 20, 0.006)
    queue.teinte = np.where((queue.v[:, 2] > 0.88 * qf.long)[:, None], tuple(FACE), tuple(OR))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tamarin", styles.style_de("tamarin"), sys.modules[__name__]), "Tamarin")
