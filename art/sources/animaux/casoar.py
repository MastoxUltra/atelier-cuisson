"""Le casoar en peluche de magasin : un noir bleuté, le plumage en crin hirsute qui retombe comme une jupe de paille,
le cou nu d'un bleu cobalt éclatant strié de pourpre, deux caroncules écarlates qui pendent comme des mentons, et sur
le crâne un casque d'ivoire en proue. Le dinosaure de la forêt : debout, le cou tendu droit vers nous, le casque
en avant, la tête de profil, l'œil d'or rond et fixe, un pied levé avec ses trois énormes griffes.

    python casoar.py        fabrique la fiche art/apercus/animaux/casoar.png (peluche de magasin, palier 4)
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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
NOIR = M.hexa("#35405a")                      # la dominante : noir bleuté (le poil la fonce)
COBALT = M.hexa("#2f7cf0")                    # l'accent : le cou
ROUGE = M.hexa("#f02838")                     # les caroncules, la nuque
IVOIRE = M.hexa("#f4e8c0")                    # le casque
OR = M.hexa("#ffc83a")                        # les yeux
PATTE = M.hexa("#a89078")
CHARBON = M.hexa("#3a3030")
CORPS = Vector((0.0, 0.100, 0.680))


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
    a = K.Animal("casoar")
    a.taille = 1.70

    # ----- le corps : un gros œuf couché vers l'arrière, le dos arrondi ; une jupe de crins qui tombe des flancs -----
    def oeuf(v):
        s = v * [0.240, 0.300, 0.250]
        s[:, 1] += 0.040 * v[:, 2]
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(oeuf), NOIR, pos=CORPS, rot=(-8, 0, 0))
    rng = np.random.default_rng(13)
    jupe = None
    for i in range(34):
        t = 2 * math.pi * (i + rng.uniform(-0.3, 0.3)) / 34
        base = np.array([0.232 * math.cos(t), CORPS.y + 0.288 * math.sin(t)])
        radial = np.array([math.cos(t), math.sin(t) * 0.80])
        radial /= np.linalg.norm(radial)
        hz = CORPS.z + rng.uniform(0.00, 0.10)
        k = 0.8 + 0.7 * rng.random()
        chemin = [(base[0] * 0.92, CORPS.y + (base[1] - CORPS.y) * 0.92, hz + 0.05), (base[0], base[1], hz - 0.04),
                  (base[0] + radial[0] * 0.040, base[1] + radial[1] * 0.040, hz - 0.18 * k),
                  (base[0] + radial[0] * 0.060, base[1] + radial[1] * 0.060, hz - 0.34 * k)]
        m = meche(chemin, 0.042 + 0.012 * rng.random(), (radial[0], radial[1], 0.0))
        jupe = m if jupe is None else jupe + m
    a.piece("jupe", jupe, NOIR)

    # ----- le cou : long et nu, cobalt, en S qui monte vers la tête tendue vers nous ; la nuque rouge -----
    fil = K.Fil([(0.0, -0.180, 0.860), (0.0, -0.260, 1.000), (0.0, -0.250, 1.200), (0.0, -0.320, 1.380)], (1, 0, 0))
    L = fil.long
    pc = A.profil([(0, 0), (0.115, 0.03 * L), (0.085, 0.30 * L), (0.066, 0.70 * L), (0.058, 0.96 * L), (0, 1.02 * L)], 6)
    cou = A.tour(pc, 40)
    cou.teinte = np.where((cou.v[:, 1] > 0.02)[:, None] & (cou.v[:, 2] > 0.55 * L)[:, None], np.asarray(ROUGE), np.asarray(COBALT))
    a.piece("cou", cou.sculpte(fil.couche), None)
    bout = Vector(fil.cadre(L)[0])

    # ----- la tête : un petit crâne, le bec fort et droit, le casque d'ivoire en proue dessus ; de profil -----
    H = A.repere(bout + Vector((0.0, -0.030, 0.010)), (4, 0, 14))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.060, 0.080, 0.062), COBALT, mat=H)
    bec = A.tour(A.profil([(0, 0), (0.038, 0.006), (0.036, 0.040), (0.024, 0.090), (0.010, 0.125), (0, 0.140)], 6), 28)
    a.piece("bec", bec.etire(0.80, 0.70, 1.0), M.hexa("#d8c8a0"), mat=A.cadre(H @ Vector((0, -0.068, -0.014)), H3 @ Vector((0, -0.98, -0.10)), (0, 0, 1)), poil=False)
    casque = A.boule(1.0, 36, 18)
    a.piece("casque", casque.etire(0.034, 0.100, 0.070), IVOIRE, mat=H @ A.repere((0, -0.004, 0.060), (-18, 0, 0)), poil=False)
    a.tete = H @ Vector((0, -0.100, -0.010))
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.82, -0.40, 0.18)))
        a.rustine("iris_" + nom, "tete", H.to_translation(), H3 @ Vector((c * 0.82, -0.40, 0.18)), 0.30, OR, 0.003, 0)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0165)
    # les caroncules : deux gouttes écarlates qui pendent sous le menton
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("caroncule_" + nom, A.boule(1.0, 20, 10).etire(0.016, 0.014, 0.060), ROUGE, mat=H @ A.repere((c * 0.022, -0.020, -0.100)), poil=False)

    # ----- les pattes : deux piliers épais gris-beige, le pied à trois énormes doigts ; la droite levée -----
    plantee = [(0.110, 0.130, 0.480), (0.118, 0.150, 0.300), (0.118, 0.160, 0.130), (0.118, 0.150, 0.030)]
    levee = [(-0.110, 0.130, 0.480), (-0.118, 0.100, 0.330), (-0.118, 0.000, 0.300), (-0.118, -0.040, 0.180)]
    for nom, chemin, pied, rot in (("G", plantee, (0.118, 0.130, 0.012), (0, 0, 0)), ("D", levee, (-0.118, -0.080, 0.160), (-14, 0, 0))):
        a.piece("patte_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.060 - 0.020 * t, 14), PATTE, poil=False)
        doigts = None
        for ang in (-30, 0, 30):
            d = A.boule(1.0, 16, 8).etire(0.020, 0.090, 0.018).pose((0, -0.075, 0.0)).pose((0, 0, 0), (0, 0, ang))
            griffe = A.tour(A.profil([(0, 0), (0.014, 0.004), (0.010, 0.030), (0.004, 0.060), (0, 0.072)], 5), 12).pose((0, 0, 0), (-84, 0, 0)).pose((0, -0.150, 0.0), (0, 0, ang))
            doigts = (d + griffe) if doigts is None else doigts + d + griffe
        a.piece("doigts_" + nom, doigts, PATTE, pos=pied, rot=rot, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("casoar", styles.style_de("casoar"), sys.modules[__name__]), "Casoar")
