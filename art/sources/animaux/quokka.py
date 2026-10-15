"""Le quokka en peluche de velours ras (2e dessin) : un beige rosé, une petite poire (étroite en haut, lourde en bas)
sous une tête de rat à la face ronde, le museau court, de petites oreilles rondes, des mains fines levées devant la
poitrine, et une longue queue nue qui part de la croupe et sur laquelle il est assis, comme sur un trépied. Le plus
mignon des malins : assis, la tête penchée d'un côté, les mains jointes, un sourire en coin, un œil plus haut que
l'autre : il vient de décider que vous étiez de la famille.

    python quokka.py        fabrique la fiche art/apercus/animaux/quokka.png (velours ras, palier 3)
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

ROSE = M.hexa("#f0cdb0")                      # la dominante : beige rosé (le poil le fonce : on le prend clair)
CREME = M.hexa("#fff6e8")                     # le ventre, le tour du museau, le dedans des oreilles
NU = M.hexa("#d8b0a0")                        # la queue nue, les paumes
CHARBON = M.hexa("#3a3032")                   # l'accent : le nez, les yeux, le sourire
CORPS = Vector((0.0, 0.040, 0.160))
TETE = Vector((0.0, -0.070, 0.330))
LACET, PENCHE = 20.0, 14.0


def construire():
    a = K.Animal("quokka")
    a.taille = 0.55

    # ----- le corps : une poire assise (étroite aux épaules, lourde en bas), le ventre crème devant -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(ROSE, float), (len(v), 1))
    t[(v[:, 1] < -0.30) & (v[:, 2] < 0.50)] = CREME
    corps.teinte = t

    def poire(v):
        s = v * [0.110, 0.112, 0.160]
        s[:, 0] *= 0.70 + 0.55 * K.lisse((-v[:, 2] + 0.9) / 1.4)               # étroite en haut, large en bas
        s[:, 1] *= 0.75 + 0.45 * K.lisse((-v[:, 2] + 0.9) / 1.4)
        return s
    a.piece("corps", corps.sculpte(poire), None, pos=CORPS)

    # ----- la tête : une petite tête de rat, la face ronde, le museau court en cône, penchée d'un côté -----
    H = A.repere(TETE, (0, PENCHE, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 48, 24).etire(0.082, 0.082, 0.080), ROSE, mat=H)
    museau = A.tour(A.profil([(0, 0), (0.042, 0.006), (0.040, 0.030), (0.030, 0.056), (0.016, 0.070), (0, 0.076)], 6), 28)
    a.piece("museau", museau.etire(1.0, 0.82, 1.0), CREME, mat=H @ A.repere((0, -0.040, -0.016), (90, 0, 0)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.017, 0.012, 0.012), CHARBON, mat=H @ A.repere((0, -0.118, -0.016)), poil=False)
    a.tete = H @ Vector((0, -0.110, -0.012))
    # le sourire en coin : un seul trait, relevé du côté de nous
    sourire = [H3 @ Vector(d) for d in ((-0.10, -0.92, -0.42), (0.18, -0.92, -0.46), (0.42, -0.82, -0.40), (0.62, -0.68, -0.28))]
    a.broderie("sourire", A.courbe(propres(a.trace("tete", H.to_translation(), sourire, 0.003)), 4), 0.0026, CHARBON)

    # ----- les yeux : vivants, un peu hauts, l'un légèrement plus haut que l'autre ; les petites oreilles rondes -----
    for nom, c, hausse in (("G", 1, 0.22), ("D", -1, 0.14)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.46, -0.84, hausse)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0140)
        po = A.profil([(0, 0), (0.024, 0.008), (0.028, 0.026), (0.020, 0.042), (0.008, 0.050), (0, 0.054)], 5)
        E = A.cadre(H @ Vector((c * 0.060, 0.020, 0.062)), H3 @ Vector((c * 0.40, 0.20, 0.90)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.45, 1.0), ROSE, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 16).etire(0.62, 0.30, 0.66).pose((0, 0.006, 0.008)), CREME, mat=E, poil=False)

    # ----- les bras : fins, repliés, les mains jointes devant la poitrine ; les jambes : deux gros pieds à plat devant -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.082, -0.020, 0.250), (c * 0.108, -0.070, 0.210), (c * 0.060, -0.112, 0.205), (c * 0.020, -0.118, 0.215)]
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 5), lambda t: 0.020 - 0.006 * t, 12), ROSE)
        a.piece("main_" + nom, A.boule(1.0, 20, 10).etire(0.020, 0.024, 0.016), NU, pos=chemin[-1])
        a.piece("pied_" + nom, A.boule(1.0, 28, 14).etire(0.040, 0.090, 0.026), CREME, pos=(c * 0.075, -0.075, 0.026), rot=(0, 0, c * 10))

    # ----- la queue : longue et nue, qui part de la croupe, s'étale par terre derrière lui et se relève : son trépied -----
    chemin = [(0.0, 0.110, 0.095), (0.0, 0.260, 0.040), (0.050, 0.420, 0.030), (0.120, 0.520, 0.060), (0.140, 0.540, 0.140)]
    queue = K.tube_peint(A.courbe(chemin, 6), lambda t: 0.038 - 0.020 * t, [(0.55, ROSE), (1, NU)], 14)
    a.piece("queue", queue, None, poil=True)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("quokka", styles.style_de("quokka"), sys.modules[__name__]), "Quokka")
