"""Le kangourou en peluche de velours ras : un roux miel chaud, le ventre et le poitrail plus clairs, les oreilles en
longues feuilles, de petits bras courts et repliés, d'énormes pattes arrière aux grands pieds bruns et une queue épaisse
comme un troisième pied. Le boxeur du bush : assis en triangle sur sa queue et ses pieds, le torse haut, les poings
levés à hauteur du menton, la tête de trois quarts, une oreille tournée vers nous : il attend qu'on s'approche.

    python kangourou.py        fabrique la fiche art/apercus/animaux/kangourou.png (velours ras, palier 3)
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

ROUX = M.hexa("#f2a560")                      # la dominante : roux miel (le poil la fonce : on la prend claire)
CLAIR = M.hexa("#ffe2b4")                     # le ventre, le museau, le dedans des oreilles
BRUN = M.hexa("#6a4630")                      # l'accent : le bout des pattes, les poings, le bout des oreilles
CORPS = Vector((0.0, 0.080, 0.520))
TETE = Vector((0.0, -0.100, 1.040))
LACET = 28.0


def construire():
    a = K.Animal("kangourou")
    a.taille = 1.80

    # ----- le corps : une poire dressée, étroite aux épaules et large aux hanches ; le ventre clair devant -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(ROUX, float), (len(v), 1))
    t[(v[:, 1] < -0.35) & (v[:, 2] < 0.65)] = CLAIR
    corps.teinte = t

    def poire(v):
        v = K.bosse(v, (0, -0.9, -0.1), 0.12, 0.45)
        s = v * [0.220, 0.200, 0.440]
        s[:, 0] *= 1 + 0.28 * K.lisse((-v[:, 2] + 0.3) / 1.2)
        s[:, 1] *= 1 + 0.18 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s
    a.piece("corps", corps.sculpte(poire), None, pos=CORPS, rot=(-12, 0, 0))

    # ----- la tête : un long museau doux, le front bombé, les oreilles immenses ; tournée de trois quarts -----
    H = A.repere(TETE, (-8, 0, LACET))
    H3 = H.to_3x3()
    tete = A.tour(A.profil([(0, 0), (0.060, 0.010), (0.102, 0.060), (0.104, 0.130), (0.080, 0.210), (0.056, 0.275), (0.044, 0.315), (0, 0.340)], 6), 48)
    K.bandes(tete, [(0.250, ROUX), (9, CLAIR)])
    a.piece("tete", tete.etire(1.12, 1.18, 1.12), None, mat=H @ A.repere((0, 0.120, -0.090), (90, 0, 0)))
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.028, 0.020, 0.018), M.hexa("#3a2a28"), mat=H @ A.repere((0, -0.300, -0.102)), poil=False)
    a.tete = H @ Vector((0, -0.220, -0.070))
    bouche = [H3 @ Vector(d) for d in ((-0.35, -0.80, -0.55), (0.0, -0.96, -0.60), (0.35, -0.80, -0.55))]
    a.broderie("bouche", A.courbe(propres(a.trace("tete", H @ Vector((0, -0.120, -0.090)), bouche, 0.004)), 4), 0.0026, M.hexa("#3a2a28"))

    # ----- les yeux : grands et doux, sous un long cil ; les oreilles : de grandes feuilles dressées, le bout brun -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.74, -0.52, 0.34)))
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0215)
        po = A.profil([(0, 0), (0.036, 0.012), (0.056, 0.070), (0.054, 0.140), (0.036, 0.205), (0.014, 0.248), (0, 0.262)], 6)
        vers = (H3 @ Vector((c * 0.42, 0.18, 0.88))).normalized()
        E = A.cadre(H @ Vector((c * 0.075, 0.070, 0.080)) - vers * 0.015, vers, H3 @ Vector((c * 0.3, 0.9, -0.1)))
        oreille = K.bandes(A.tour(po, 36).etire(1.0, 0.30, 1.0), [(0.200, ROUX), (9, BRUN)])
        a.piece("oreille_" + nom, oreille, None, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 28).etire(0.60, 0.30, 0.70).pose((0, 0.008, 0.012)), CLAIR, mat=E, poil=False)

    # ----- les bras : courts et repliés, les poings bruns levés à hauteur du menton (le boxeur) -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.150, -0.060, 0.820), (c * 0.210, -0.140, 0.740), (c * 0.150, -0.230, 0.800), (c * 0.085, -0.240, 0.880)]
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.050 - 0.012 * t, 14), ROUX)
        a.piece("poing_" + nom, A.boule(1.0, 24, 12).etire(0.052, 0.058, 0.046), BRUN, pos=chemin[-1])

    # ----- les pattes arrière : deux énormes jambons, les grands pieds bruns posés à plat devant ; la queue : un tronc épais -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.boule(1.0, 36, 18).etire(0.130, 0.250, 0.190), ROUX, pos=(c * 0.210, 0.090, 0.240), rot=(0, 0, c * 6))
        a.piece("pied_" + nom, A.boule(1.0, 28, 14).etire(0.072, 0.260, 0.042), BRUN, pos=(c * 0.220, -0.190, 0.042), rot=(0, 0, c * 4))
    queue = K.tube_peint(A.courbe([(0.0, 0.250, 0.220), (0.0, 0.560, 0.090), (0.0, 0.900, 0.045)], 6), lambda t: 0.210 - 0.150 * t, [(0.85, ROUX), (1, BRUN)], 20)
    a.piece("queue", queue, None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("kangourou", styles.style_de("kangourou"), sys.modules[__name__]), "Kangourou")
