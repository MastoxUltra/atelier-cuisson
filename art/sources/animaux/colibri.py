"""Le colibri en peluche, cousu main : un violet améthyste irisé, la gorge rubis, le ventre crème, un long bec-aiguille
charbon, des ailes en lames pointues levées en V et une queue en fourche. Le plus petit des gros bavards : posé en
pleine envolée, penché en avant, le bec pointé comme une épée, les ailes à demi dressées, une patte minuscule qui
touche à peine le sol : il s'arrête en route juste le temps de nous toiser.

    python colibri.py        fabrique la fiche art/apercus/animaux/colibri.png (cousu main, palier 2)
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

AMETHYSTE = M.hexa("#b080f0")                 # la dominante : améthyste irisé (le poil le fonce : on le prend clair)
INDIGO = M.hexa("#6a4fd0")                    # le bout des ailes et de la queue : un ton plus bas
RUBIS = M.hexa("#f0305f")                     # l'accent : la gorge
CREME = M.hexa("#fff2e4")                     # le ventre
CHARBON = M.hexa("#3a3236")                   # le bec, les pattes
CORPS = Vector((0.0, 0.050, 0.215))
TETE = Vector((0.0, -0.075, 0.345))
LACET = 26.0                                  # la tête tournée vers nous


def construire():
    a = K.Animal("colibri")
    a.taille = 0.42

    # ----- le corps : un œuf penché en avant ; le ventre crème devant, le dos améthyste ; une couture de dos -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(AMETHYSTE, float), (len(v), 1))
    t[(v[:, 1] < -0.30) & (v[:, 2] < 0.45)] = CREME
    corps.teinte = t

    def oeuf(v):
        s = v * [0.080, 0.088, 0.120]
        s[:, 1] -= 0.030 * K.lisse((v[:, 2] + 0.1) / 1.0)
        return s
    a.piece("corps", corps.sculpte(oeuf), None, pos=CORPS, rot=(-26, 0, 0))

    # ----- la tête : ronde, le front bombé ; la gorge rubis posée en bavoir dessous -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 40, 20).etire(0.062, 0.060, 0.060), AMETHYSTE, mat=H)
    a.rustine("gorge", "tete", TETE + Vector((0, 0.01, 0.0)), H3 @ Vector((0, -0.50, -0.86)), lambda th: 0.78 + 0.10 * math.cos(2 * th), RUBIS, 0.003, 0)
    a.tete = H @ Vector((0, -0.080, 0.0))

    # ----- le bec : une aiguille charbon, longue et fine, un tout petit peu courbée vers le bas -----
    B = A.cadre(H @ Vector((0, -0.052, -0.004)), H3 @ Vector((0, -0.97, -0.16)), H3 @ Vector((0, 0.2, 0.98)))

    def aiguille(v):
        s = v.copy()
        s[:, 1] -= 0.014 * np.clip(v[:, 2] / 0.20, 0, 1) ** 2
        return s
    a.piece("bec", A.tour(A.profil([(0, 0), (0.011, 0.004), (0.009, 0.060), (0.005, 0.150), (0.002, 0.195), (0, 0.205)], 5), 16).sculpte(aiguille),
            CHARBON, mat=B, poil=False)

    # ----- les yeux : un seul bouton de chaque côté, petit, brillant, sous un sourcil d'indigo -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, H3 @ Vector((c * 0.66, -0.66, 0.16)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0125)

    # ----- les ailes : deux lames pointues levées en V, le bout indigo ; la gauche (vers nous) plus haute -----
    for nom, c, vers in (("G", 1, (0.80, 0.30, 0.55)), ("D", -1, (-0.74, 0.34, 0.50))):
        aile = A.boule(1.0, 36, 18)
        aile.teinte = np.where((aile.v[:, 2] > 0.25)[:, None], np.asarray(INDIGO), np.asarray(AMETHYSTE))

        def lame(v):
            s = v.copy()
            s[:, 1] *= 1 - 0.55 * K.lisse((v[:, 2] + 0.1) / 1.1)
            s[:, 0] *= 1 - 0.35 * K.lisse((v[:, 2] + 0.2) / 1.2)
            return s
        a.piece("aile_" + nom, aile.sculpte(lame).etire(0.018, 0.050, 0.150).pose((0, 0, 0.130)), None,
                mat=A.cadre(Vector((c * 0.050, 0.070, 0.260)), Vector(vers), Vector((c * 0.2, -0.2, 0.9))))

    # ----- la queue : un petit éventail fourchu, indigo, qui retombe derrière -----
    for nom, c, cap in (("G", 1, 14), ("D", -1, -14)):
        lobe = A.boule(1.0, 20, 10).etire(0.018, 0.012, 0.085).pose((0, 0, 0.060), (0, 0, 0))
        a.piece("queue_" + nom, lobe, INDIGO, pos=(c * 0.012, 0.165, 0.195), rot=(150, 0, c * cap), poil=False)

    # ----- les pattes : deux brins de charbon, de minuscules doigts ; il touche à peine le sol -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("patte_" + nom, A.tube(A.courbe([(c * 0.026, 0.030, 0.130), (c * 0.030, 0.010, 0.060), (c * 0.032, -0.008, 0.014)], 4), 0.008, 10),
                CHARBON, poil=False)
        a.piece("doigts_" + nom, A.boule(1.0, 14, 8).etire(0.016, 0.026, 0.008), CHARBON, pos=(c * 0.032, -0.014, 0.008), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("colibri", styles.style_de("colibri"), sys.modules[__name__]), "Colibri")
