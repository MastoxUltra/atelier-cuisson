"""L'émeu en peluche de velours ras : un taupe lavande tout effiloché, le plumage en longues mèches pendantes comme un
manteau de laine, le cou nu bleuté, la petite tête au grand œil d'ambre sous de longs cils, de très longues pattes aux
gros pieds à trois doigts. Un professeur distrait qui fait les cent pas : en pleine marche, le cou tendu vers nous, un
pied levé, l'œil rond et vide, le manteau qui flotte d'un côté.

    python emeu.py        fabrique la fiche art/apercus/animaux/emeu.png (velours ras, palier 3)
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

TAUPE = M.hexa("#bcaabc")                     # la dominante : taupe lavande (le poil la fonce : on la prend claire)
SOMBRE = M.hexa("#8a7888")                    # les mèches du bas, la croupe
COU = M.hexa("#9ec0d8")                       # le cou nu, bleuté
AMBRE = M.hexa("#e8a830")
CHARBON = M.hexa("#3a3036")
PATTE = M.hexa("#8a7a78")
CORPS = Vector((0.0, 0.080, 0.600))
LACET = 20.0


def meche(chemin, large, face, plat=0.40, cotes=12):
    """Une mèche plate (le geste du cheval) couchée le long d'un chemin."""
    p = A.courbe(chemin, 8)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    n0 = np.asarray(face, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.linalg.norm(t, axis=1, keepdims=True)
        x = np.cross(n0, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.60 * large, 0.05 * L), (0.95 * large, 0.22 * L), (large, 0.42 * L), (0.72 * large, 0.70 * L),
                     (0.30 * large, 0.93 * L), (0.06 * large, 0.985 * L), (0, L)], 5)
    return A.tour(prof, cotes).etire(1.0, plat, 1.0).sculpte(couche)


def construire():
    a = K.Animal("emeu")
    a.taille = 1.80

    # ----- le corps : un gros œuf couché, le dos en voûte ; dessus, un manteau de mèches qui retombent des flancs -----
    def oeuf(v):
        s = v * [0.240, 0.330, 0.270]
        s[:, 1] += 0.020 * v[:, 2]
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(oeuf), TAUPE, pos=CORPS, rot=(-6, 0, 0))
    rng = np.random.default_rng(9)
    meches = None
    for i in range(30):
        t = 2 * math.pi * (i + rng.uniform(-0.3, 0.3)) / 30
        base = np.array([0.232 * math.cos(t), CORPS.y + 0.318 * math.sin(t)])
        radial = np.array([math.cos(t) * 1.0, math.sin(t) * 0.70])
        radial /= np.linalg.norm(radial)
        hz = CORPS.z + rng.uniform(0.02, 0.12)
        k = 0.8 + 0.7 * rng.random()
        chemin = [(base[0] * 0.92, CORPS.y + (base[1] - CORPS.y) * 0.92, hz + 0.05), (base[0], base[1], hz - 0.03),
                  (base[0] + radial[0] * 0.040, base[1] + radial[1] * 0.040, hz - 0.14 * k),
                  (base[0] + radial[0] * 0.070, base[1] + radial[1] * 0.070, hz - 0.26 * k)]
        m = meche(chemin, 0.044 + 0.012 * rng.random(), (radial[0], radial[1], 0.0))
        meches = m if meches is None else meches + m
    a.piece("meches", meches, SOMBRE)

    # ----- le cou : long et nu, bleuté, qui part de l'épaule et se tend vers nous en S ; la tête : petite -----
    fil = K.Fil([(0.0, -0.250, 0.700), (0.0, -0.350, 0.860), (0.0, -0.360, 1.050), (0.0, -0.420, 1.200)], (1, 0, 0))
    L = fil.long
    pc = A.profil([(0, 0), (0.085, 0.03 * L), (0.060, 0.30 * L), (0.048, 0.70 * L), (0.046, 0.95 * L), (0, 1.01 * L)], 6)
    a.piece("cou", A.tour(pc, 28).sculpte(fil.couche), COU)
    bout = Vector(fil.cadre(L)[0])
    H = A.repere(bout + Vector((0.0, -0.030, 0.020)), (6, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.062, 0.078, 0.060), TAUPE, mat=H)
    a.tete = H @ Vector((0, -0.100, -0.010))
    bec = A.tour(A.profil([(0, 0), (0.034, 0.006), (0.030, 0.030), (0.018, 0.055), (0, 0.068)], 5), 24)
    a.piece("bec", bec.etire(1.0, 0.70, 1.0), M.hexa("#c8b0a0"), mat=A.cadre(H @ Vector((0, -0.070, -0.014)), H3 @ Vector((0, -0.96, -0.20)), (0, 0, 1)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.82, -0.40, 0.18))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.30, AMBRE, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0185)

    # ----- les pattes : très longues, charbon grisé, le genou marqué ; un pied levé, les gros pieds à trois doigts -----
    plantee = [(0.100, 0.060, 0.480), (0.108, 0.080, 0.300), (0.108, 0.140, 0.140), (0.108, 0.130, 0.030)]
    levee = [(-0.100, 0.060, 0.480), (-0.108, 0.030, 0.320), (-0.108, -0.080, 0.300), (-0.108, -0.130, 0.190)]
    for nom, chemin, pied in (("G", plantee, (0.108, 0.100, 0.014)), ("D", levee, (-0.108, -0.170, 0.170))):
        a.piece("patte_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.050 - 0.020 * t, 14), PATTE, poil=False)
        doigts = None
        for ang in (-28, 0, 28):
            d = A.boule(1.0, 14, 8).etire(0.016, 0.075, 0.014).pose((0, -0.060, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("doigts_" + nom, doigts, PATTE, pos=pied, rot=(-10 if nom == "D" else 0, 0, 0), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("emeu", styles.style_de("emeu"), sys.modules[__name__]), "Émeu")
