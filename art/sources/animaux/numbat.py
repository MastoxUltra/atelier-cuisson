"""Le numbat en peluche de velours ras (2e dessin) : un corps long et bas de marsupial, brun brique, un museau pointu
et fin, la poitrine claire, et sur l'ARRIÈRE du dos six à sept bandes crème en travers de la croupe, bien nettes ; une
queue en goupillon qui se dresse derrière lui. Le chasseur de termites au trot : tête basse, le museau au ras du sol,
une patte avant levée, le dos tendu en ligne, la queue dressée comme un point d'exclamation.

    python numbat.py        fabrique la fiche art/apercus/animaux/numbat.png (velours ras, palier 3)
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

BRIQUE = M.hexa("#cf7a4a")                    # la dominante : brun brique (le poil la fonce : on la prend claire)
CREME = M.hexa("#fff2d8")                     # l'accent : les bandes, la poitrine, le bout des pattes
CHARBON = M.hexa("#3a2c28")                   # le trait de l'œil, le nez
CORPS = Vector((0.0, 0.080, 0.150))
TETE = Vector((0.0, -0.330, 0.150))
LACET, PIQUE = 20.0, 22.0


def construire():
    a = K.Animal("numbat")
    a.taille = 0.60                           # queue comprise

    # ----- le corps : long, bas, étroit ; les bandes crème en travers de l'arrière du dos (de la mi-échine à la croupe) -----
    corps = A.boule(1.0, 64, 32)
    v = corps.v
    t = np.tile(np.asarray(BRIQUE, float), (len(v), 1))
    bande = (v[:, 1] > -0.10) & (v[:, 2] > 0.05) & (np.floor((v[:, 1] + 0.10) / 0.145) % 2 == 0)
    t[bande] = CREME
    t[(v[:, 1] < -0.30) & (v[:, 2] < 0.15)] = CREME
    t[(v[:, 2] < -0.45)] = CREME
    corps.teinte = t

    def long(v):
        v = K.bosse(v, (0, -0.85, 0.20), 0.08, 0.45)
        s = v * [0.068, 0.300, 0.080]
        s[:, 2] = np.where(s[:, 2] < 0, s[:, 2] * 0.80, s[:, 2])
        return s
    a.piece("corps", corps.sculpte(long), None, pos=CORPS)

    # ----- la tête : fine, le museau pointu et long ; basse, le trait charbon à travers l'œil ; les petites oreilles rondes -----
    H = A.repere(TETE, (PIQUE, 0, LACET))
    H3 = H.to_3x3()
    tete = A.tour(A.profil([(0, 0), (0.044, 0.008), (0.058, 0.044), (0.050, 0.090), (0.036, 0.130), (0.024, 0.162), (0.014, 0.182), (0, 0.192)], 6), 36)
    K.bandes(tete, [(0.170, BRIQUE), (9, CREME)])
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0.080, -0.010), (90, 0, 0)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.015, 0.011, 0.011), CHARBON, mat=H @ A.repere((0, -0.114, -0.010)), poil=False)
    a.tete = H @ Vector((0, -0.100, -0.010))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.74, -0.58, 0.14))
        p, n = a.surface("tete", H @ Vector((0, 0.020, -0.010)), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0125)
        trait = [H3 @ Vector((c * 0.50, -0.90, 0.46 - 0.30 * u)) for u in np.linspace(0, 1, 5)]
        a.broderie("trait_" + nom, propres(a.trace("tete", H @ Vector((0, 0.020, -0.010)), trait, 0.004)), 0.0040, CHARBON)
        po = A.profil([(0, 0), (0.024, 0.006), (0.030, 0.022), (0.022, 0.038), (0.008, 0.046), (0, 0.050)], 5)
        E = A.cadre(H @ Vector((c * 0.046, 0.060, 0.026)), H3 @ Vector((c * 0.40, 0.20, 0.90)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.45, 1.0), BRIQUE, mat=E)

    # ----- les pattes : quatre fines, au trot ; l'avant gauche levée, les bouts crème -----
    def patte(points, r0):
        return K.tube_peint(A.courbe(points, 6), lambda t: r0 - 0.008 * t, [(0.82, BRIQUE), (1, CREME)], 12)
    for nom, pts in (("av_D", [(-0.050, -0.130, 0.130), (-0.060, -0.140, 0.080), (-0.062, -0.140, 0.020)]),
                     ("ar_G", [(0.055, 0.260, 0.130), (0.065, 0.300, 0.070), (0.066, 0.280, 0.020)]),
                     ("ar_D", [(-0.055, 0.260, 0.130), (-0.065, 0.250, 0.070), (-0.066, 0.230, 0.020)])):
        a.piece("patte_" + nom, patte(pts, 0.026), None)
        x, y, _z = pts[-1]
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.022, 0.040, 0.014), CREME, pos=(x, y - 0.020, 0.014))
    levee = [(0.050, -0.130, 0.130), (0.062, -0.180, 0.110), (0.064, -0.230, 0.100)]
    a.piece("patte_av_G", patte(levee, 0.026), None)
    a.piece("pied_av_G", A.boule(1.0, 20, 10).etire(0.022, 0.040, 0.014), CREME, pos=(0.064, -0.258, 0.098), rot=(-30, 0, 0))

    # ----- la queue : un goupillon dressé, qui part de la croupe et monte presque droit, brique puis crème -----
    chemin = [(0.0, 0.330, 0.150), (0.0, 0.430, 0.220), (0.0, 0.470, 0.340), (0.0, 0.460, 0.480)]
    queue = K.tube_peint(A.courbe(chemin, 6), lambda t: 0.034 + 0.030 * math.sin(math.pi * min(t * 1.25, 1.0)) - 0.016 * t,
                         [(0.74, BRIQUE), (0.88, CREME), (1, BRIQUE)], 16)
    a.piece("queue", queue, None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("numbat", styles.style_de("numbat"), sys.modules[__name__]), "Numbat")
