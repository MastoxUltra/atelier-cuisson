"""Le harfang en peluche de velours ras : tout blanc, moucheté de barres charbon qui s'épaississent sur le dos et les
ailes, la tête ronde sans aigrettes, deux grands yeux soufre sous des sourcils de plumes lourds, un petit bec noir
presque noyé dans la bavette. Une statue de givre sur sa souche : droit comme un i, les pieds en pantoufles de plumes,
la tête tournée de trois quarts et un peu baissée, qui nous toise.

    python harfang.py        fabrique la fiche art/apercus/animaux/harfang.png (velours ras, palier 3)
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

NEIGE = M.hexa("#fdfcf8")                     # la dominante : blanc moucheté (le poil le grise à peine)
CHARBON = M.hexa("#3a3638")                   # les barres
SOUFRE = M.hexa("#ffd21e")                    # l'accent : les yeux
BEC = M.hexa("#26222a")                       # le bec et les griffes
CORPS = Vector((0.0, 0.03, 0.262))
TETE = Vector((0.0, -0.040, 0.545))
LACET, PENCHE, PIQUE = 34.0, 9.0, -8.0        # la tête tournée vers nous, un peu de travers, le nez baissé


def barrer(m, dos=0.50, face=0.16, graine=1, une_sur=2):
    """Peint la boule encore unité en blanc et la mouchette de barres charbon : sur un anneau sur « une_sur », des
    tirets au hasard, plus drus vers le dos (+Y) que sur la face (-Y)."""
    rng = np.random.default_rng(graine)
    t = np.tile(np.asarray(NEIGE, float), (len(m.v), 1))
    for i, anneau in enumerate(m.anneaux):
        if len(anneau) < 2 or i % une_sur:
            continue
        for k in anneau:
            densite = face + (dos - face) * float(K.lisse(m.v[k, 1] * 0.8 + 0.5))
            if rng.random() < densite:
                t[k] = CHARBON
    m.teinte = t
    return m


def construire():
    a = K.Animal("harfang")
    a.taille = 0.85

    # ----- le corps : un œuf droit, le poitrail un peu rond, qui s'effile en bas vers les pieds ; barré -----
    def oeuf(v):
        v = K.bosse(v, (0, -0.9, 0.25), 0.10, 0.5)
        s = v * [0.150, 0.150, 0.215]
        s[:, 0] *= 1 - 0.18 * K.lisse((-v[:, 2] + 0.1) / 1.0)
        s[:, 1] *= 1 - 0.14 * K.lisse((-v[:, 2] + 0.1) / 1.0)
        return s
    a.piece("corps", barrer(A.boule(1.0, 56, 28), 0.40, 0.12, 1).sculpte(oeuf), None, pos=CORPS, rot=(-4, 0, 0))

    # ----- la tête : ronde, sans aigrettes, le front bombé ; blanche, quelques points charbon sur le crâne -----
    H = A.repere(TETE, (PIQUE, PENCHE, LACET))
    H3 = H.to_3x3()

    def crane(v):
        v = K.bosse(v, (0, -0.8, 0.3), 0.08, 0.5)
        return v * [0.118, 0.108, 0.108]
    a.piece("tete", barrer(A.boule(1.0, 48, 24), 0.22, 0.04, 3, 3).sculpte(crane), None, mat=H)
    a.tete = H @ Vector((0, -0.100, -0.005))

    # ----- les yeux : un disque soufre cerné de blanc, la pupille noire et son reflet ; sous un sourcil lourd, en biais -----
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.50, -0.82, 0.12))
        a.rustine("iris_" + nom, "tete", TETE, regard, 0.34, SOUFRE, 0.003, 0)
        p, n = a.surface("tete", TETE, regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0200)
        P = A.cadre(p + n * 0.006, n, H3 @ Vector((c * -0.45, 0.20, 1.0)))
        a.piece("lourde_" + nom, K.paupiere(0.0235, 0.55), NEIGE, mat=P, poil=False)

    # ----- le bec : un petit crochet noir entre les yeux, à demi noyé dans les plumes de la bavette -----
    B = A.cadre(H @ Vector((0, -0.100, -0.030)), H3 @ Vector((0, -0.86, -0.50)), H3 @ Vector((0, 0.5, 0.86)))
    bec = A.tour(A.profil([(0, 0), (0.020, 0.006), (0.019, 0.022), (0.012, 0.040), (0.004, 0.052), (0, 0.056)], 5), 28)
    bec.sculpte(lambda v: v + np.stack([np.zeros(len(v)), -0.014 * (v[:, 2] / 0.056) ** 2, np.zeros(len(v))], axis=1))
    a.piece("bec", bec, BEC, mat=B, poil=False)
    a.piece("bavette", A.boule(1.0, 28, 14).etire(0.034, 0.024, 0.030), NEIGE, mat=H @ A.repere((0, -0.088, -0.042)))

    # ----- les ailes : deux galets plaqués sur les flancs, plus drus en barres, la pointe qui croise sous la queue -----
    def galet(v):
        s = K.emousse(v, 0.85)
        s[:, 2] *= 1 - 0.40 * K.lisse((v[:, 1] + 0.2) / 1.2)
        return s
    for nom, c in (("G", 1), ("D", -1)):
        aile = barrer(A.boule(1.0, 40, 20), 0.42, 0.26, 5 + (c > 0), 2)
        a.piece("aile_" + nom, aile.sculpte(galet).etire(0.032, 0.180, 0.135), None, pos=(c * 0.125, 0.055, 0.250), rot=(-8, 0, c * 4))

    # ----- la queue : un court éventail barré qui descend derrière -----
    queue = barrer(A.tour(A.profil([(0, 0), (0.060, 0.010), (0.056, 0.070), (0.040, 0.130), (0.020, 0.170), (0, 0.185)], 6), 36), 0.62, 0.50, 7, 1)
    a.piece("queue", queue.etire(1.0, 0.34, 1.0), None, pos=(0, 0.150, 0.215), rot=(168, 0, 0))

    # ----- les pieds : deux grosses pantoufles de plumes blanches, les griffes noires qui dépassent -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("pied_" + nom, A.boule(1.0, 28, 14).etire(0.054, 0.082, 0.046), NEIGE, pos=(c * 0.060, -0.030, 0.042))
        for k in (-1, 0, 1):
            griffe = A.tour(A.profil([(0, 0), (0.007, 0.004), (0.005, 0.022), (0, 0.034)], 4), 14)
            a.piece("griffe_%s%d" % (nom, k), griffe, BEC, mat=A.cadre(Vector((c * 0.060 + k * 0.022, -0.108, 0.026)), Vector((k * 0.15, -0.9, -0.45)), (0, 0, 1)), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("harfang", styles.style_de("harfang"), sys.modules[__name__]), "Harfang")
