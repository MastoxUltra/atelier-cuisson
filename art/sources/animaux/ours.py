"""L'ours en peluche, deuxième dessin : l'ours brun adulte des sapins, debout sur ses pattes de derrière, noisette cendré,
les jambes et les bras plus sombres, une énorme bosse de muscle entre les épaules givrée de clair. La tête est large et
lourde, le front bas sous les sourcils, de petits yeux enfoncés sous la paupière, des oreilles basses sur les côtés, un
long museau carré au nez noir, la gueule entrouverte sur une langue rose et quatre crocs ; un bras levé, les griffes
longues en avant, l'autre abaissé devant lui. Il se dresse pour paraître plus grand, et il y parvient fort bien.

    python ours.py        fabrique la fiche art/apercus/animaux/ours.png (style du palier : B, peluche de magasin)
    (le premier dessin, jugé le 15/10 : « le nounours de supermarché »)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K
import outils_a as O

NOISETTE = np.array(M.hexa("#7a5c46"))        # la dominante (registre : brun noisette cendré #6e5846), un peu plus chaud (style B)
CLAIR = np.array(M.hexa("#a88c70"))           # le museau, le givre de la bosse
SOMBRE = np.array(M.hexa("#5a4435"))          # les bras, les jambes
GRIFFE = M.hexa("#e8dcc4")
DENT = M.hexa("#f2ead8")
NEZ = M.hexa("#16110e")
LANGUE = M.hexa("#c8606e")
FIL = M.hexa("#2a1c14")


def construire():
    a = K.Animal("ours")
    a.taille = 2.50

    # ----- le corps : une grosse poire debout, les épaules très larges, la bosse, le ventre rond ; le dos givré de clair -----
    pc = A.profil([(0, 0.0), (0.120, 0.012), (0.215, 0.080), (0.255, 0.200), (0.272, 0.340), (0.285, 0.480), (0.255, 0.600), (0.180, 0.680), (0.090, 0.720), (0, 0.740)], 6)
    corps = A.tour(pc, 56)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    z = corps.v[:, 2]
    t = np.tile(NOISETTE, (len(ang), 1))
    t[(ang > 2.2) & (z < 0.55)] = CLAIR * 0.92                                         # le ventre
    t[(ang < 1.10) & (z > 0.50)] = NOISETTE * 0.55 + CLAIR * 0.45                      # le dos givré
    t[z < 0.14] = SOMBRE
    corps.teinte = t

    def bosse(v):
        s = v.copy()
        s[:, 1] += 0.100 * np.exp(-((v[:, 2] - 0.60) / 0.11) ** 2) * (v[:, 1] > 0)        # la bosse entre les épaules
        s[:, 2] += 0.045 * np.exp(-((v[:, 2] - 0.60) / 0.14) ** 2) * (v[:, 1] > 0)
        s[:, 1] -= 0.050 * np.exp(-((v[:, 2] - 0.30) / 0.20) ** 2) * (v[:, 1] < 0)        # le ventre rond
        return s
    a.piece("corps", corps.sculpte(bosse), None, mat=A.repere((0.0, 0.050, 0.110), (-8, 0, 0)))

    # ----- la tête : large et lourde, le front bas sous les sourcils, les joues pleines ; un long museau carré, le nez noir -----
    H = Vector((0.0, -0.170, 0.880))
    RT = A.repere(H, (8, 0, -14))                                                      # le nez un peu baissé, de trois quarts
    crane = A.boule(1.0, 52, 26)
    for c in (1, -1):
        crane.sculpte(lambda v, c=c: K.bosse(v, (c * 0.9, -0.35, -0.30), 0.24, 0.34))   # les grosses joues
        crane.sculpte(lambda v, c=c: K.bosse(v, (c * 0.45, -0.70, 0.36), 0.14, 0.18))   # les arcades
    crane.teinte = np.tile(NOISETTE, (len(crane.v), 1))
    a.piece("tete", crane.etire(0.168, 0.150, 0.140), None, mat=RT)
    museau = A.boule(1.0, 36, 18).sculpte(lambda v: K.emousse(v, 0.55)).etire(0.082, 0.150, 0.070)
    a.piece("museau", O.teinte(museau, CLAIR), None, mat=RT @ A.repere((0.0, -0.188, -0.034), (-8, 0, 0)))
    a.piece("nez", A.boule(1.0, 18, 10).etire(0.044, 0.030, 0.032), NEZ, mat=RT @ A.repere((0.0, -0.328, -0.006)), poil=False)
    # la mâchoire du bas : abaissée, la langue, deux crocs dessous ; deux crocs dessus
    charn = RT @ A.repere((0.0, -0.090, -0.082))                                       # la charnière
    jaune = charn @ A.repere((0, 0, 0), (26, 0, 0))
    mach = A.boule(1.0, 32, 16).sculpte(lambda v: K.emousse(v, 0.6)).etire(0.062, 0.122, 0.034)
    a.piece("machoire", O.teinte(mach, CLAIR * 0.9), None, mat=jaune @ A.repere((0.0, -0.118, -0.010)))
    a.piece("langue", A.boule(1.0, 20, 8).etire(0.032, 0.080, 0.010), LANGUE, mat=jaune @ A.repere((0.0, -0.125, 0.014)), poil=False)
    # les crocs : chaque base est PLANTÉE dans la peau (le point de surface cherché au rayon), sans le moindre jour
    MUZ = RT @ A.repere((0.0, -0.188, -0.034), (-8, 0, 0))
    JAW = jaune @ A.repere((0.0, -0.118, -0.010))
    bas_m = (MUZ.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
    haut_j = (JAW.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
    for c in (1, -1):
        pu, nu = a.surface("museau", MUZ @ Vector((c * 0.046, -0.085, 0.0)), bas_m)
        dir_u = (bas_m + (RT.to_3x3() @ Vector((0.0, -0.10, 0.0)))).normalized()
        haut_ = O.pointe(0.046, 0.0105, 8)
        a.piece("croc_haut_%d" % c, O.couche(O.teinte(haut_, np.array(DENT)), A.cadre(pu - dir_u * 0.011, dir_u, (0, 1, 0))), None, poil=False)
        pb, nb = a.surface("machoire", JAW @ Vector((c * 0.034, -0.030, 0.0)), haut_j)
        dir_b = (haut_j + (RT.to_3x3() @ Vector((0.0, -0.10, 0.0)))).normalized()
        bas_ = O.pointe(0.038, 0.0095, 8)
        a.piece("croc_bas_%d" % c, O.couche(O.teinte(bas_, np.array(DENT)), A.cadre(pb - dir_b * 0.010, dir_b, (0, 1, 0))), None, poil=False)
    # de petits yeux enfoncés sous une lourde paupière : le regard noir
    O.paire_yeux(a, "tete", H, (0.62, -0.74, 0.20), 0.0160, couleur_lourde=tuple(NOISETTE * 0.9), coupe=0.18, decolle=0.001, R=RT)
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.boule(1.0, 24, 12).etire(0.040, 0.026, 0.040)
        a.piece("oreille_" + nom, O.teinte(ore, NOISETTE * 0.9), None, mat=RT @ A.repere((c * 0.150, 0.050, 0.092)))
    a.tete = H + Vector((0.0, -0.28, 0.0))

    # ----- les bras : épais, un levé, les griffes longues en avant ; l'autre abaissé devant lui -----
    haut = {"G": [(0.270, 0.010, 0.760), (0.420, -0.030, 0.860), (0.470, -0.150, 0.960), (0.430, -0.270, 1.040)],
            "D": [(-0.270, 0.010, 0.760), (-0.380, -0.050, 0.680), (-0.400, -0.190, 0.610), (-0.360, -0.320, 0.570)]}
    for nom, c in (("G", 1), ("D", -1)):
        pts = haut[nom]
        bras = O.tube_r(pts, [0.135, 0.112, 0.098, 0.088], 22)
        a.piece("bras_" + nom, O.teinte(bras, SOMBRE), None)
        fin = Vector(pts[-1])
        patte = A.boule(1.0, 28, 14).etire(0.082, 0.080, 0.064).pose(tuple(fin))
        a.piece("main_" + nom, O.teinte(patte, SOMBRE * 0.88), None)
        for k, dx in enumerate((-0.044, -0.015, 0.015, 0.044)):
            g = O.couche(O.teinte(O.griffe(0.072, 0.0125), np.array(GRIFFE)), A.cadre(fin + Vector((dx, -0.070, 0.004)), (0.0, -1.0, -0.25), (0, 0, 1)))
            a.piece("griffe_%s%d" % (nom, k), g, None, poil=False)
        # les jambes de derrière : fortes et courtes, les grands pieds plantés
        cuisse = O.tube_r([(c * 0.180, 0.080, 0.320), (c * 0.200, -0.010, 0.190), (c * 0.185, -0.060, 0.060)], [0.150, 0.120, 0.092], 22)
        a.piece("cuisse_" + nom, O.teinte(cuisse, SOMBRE), None)
        pied = A.boule(1.0, 32, 14).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.092, 0.170, 0.040)
        a.piece("pied_" + nom, O.teinte(pied, SOMBRE * 0.85), None, pos=(c * 0.190, -0.130, 0.040), rot=(0, 0, c * -10), poil=False)
        for k, dx in enumerate((-0.040, -0.013, 0.013, 0.040)):
            g = O.couche(O.teinte(O.griffe(0.052, 0.0105), np.array(GRIFFE)), A.cadre(Vector((c * 0.190 + dx, -0.292, 0.046)), (0.0, -1.0, -0.10), (0, 0, 1)))
            a.piece("griffe_pied_%s%d" % (nom, k), g, None, poil=False)

    # ----- la queue : un moignon rond, juste une boule derrière -----
    a.piece("queue", O.teinte(A.boule(1.0, 20, 10).etire(0.050, 0.050, 0.050), NOISETTE), None, pos=(0.0, 0.320, 0.260))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("ours", styles.style_de("ours"), sys.modules[__name__]), "Ours")
