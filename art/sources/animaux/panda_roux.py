"""Le panda roux en peluche : le petit prince cannelle des sapins. Debout sur ses pattes de derrière, les deux bras levés à
demi pour se faire plus grand (c'est ce qu'il fait quand il a peur, ça ne l'agrandit pas), le ventre et les pattes brun
sombre, la face blanche ornée de deux larmes rousses qui descendent de l'œil à la bouche, les oreilles triangulaires
ourlées de blanc, et la queue : un énorme panache annelé de huit bagues, enroulé dans son dos, plus haut que sa tête.
Il vous toise : il a décidé que vous étiez un chien.

    python panda_roux.py        fabrique la fiche art/apercus/animaux/panda_roux.png (style du palier : B, peluche de magasin)
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
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

CANNELLE = np.array(M.hexa("#c05c32"))        # la dominante (registre : cannelle rouge #b8512e) ; un cran plus clair (style B)
SOMBRE = np.array(M.hexa("#43302a"))          # le ventre, les pattes
BLANC = np.array(M.hexa("#f6f0e6"))           # la face, l'ourlet des oreilles
CREME = np.array(M.hexa("#e0b690"))           # les bagues claires de la queue
LARME = np.array(M.hexa("#a84c28"))           # les larmes
NEZ = M.hexa("#16110e")
FIL = M.hexa("#2a1a12")
TETE = Vector((0.0, -0.040, 0.660))


def construire():
    a = K.Animal("panda_roux")
    a.taille = 0.78

    # ----- le corps : une poire debout, cannelle sur le dos et les flancs, brun sombre sous le ventre -----
    pc = A.profil([(0, 0.0), (0.110, 0.012), (0.180, 0.075), (0.208, 0.190), (0.192, 0.310), (0.156, 0.410), (0.104, 0.472), (0.050, 0.500), (0, 0.514)], 6)
    corps = A.tour(pc, 52)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    z = corps.v[:, 2]
    t = np.tile(CANNELLE, (len(z), 1))
    t[(ang > 1.85) & (z < 0.44)] = SOMBRE
    corps.teinte = t

    def galbe(v):
        s = v.copy()
        s[:, 1] -= 0.028 * np.exp(-((v[:, 2] - 0.22) / 0.12) ** 2) * (v[:, 1] < 0)            # la panse
        s[:, 1] += 0.030 * np.exp(-((v[:, 2] - 0.38) / 0.10) ** 2) * (v[:, 1] > 0)            # le dos rond
        return s
    a.piece("corps", corps.sculpte(galbe), None, mat=A.repere((0.0, 0.040, 0.020), (6, 0, 0)))

    # ----- la tête : large et plate, les joues pleines ; face blanche, deux larmes rousses, la calotte cannelle -----
    tete = A.boule(1.0, 56, 28)
    for c in (1, -1):
        tete.sculpte(lambda v, c=c: K.bosse(v, (c * 0.9, -0.3, -0.20), 0.22, 0.30))
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(BLANC, (len(u), 1))
    t[(u[:, 2] > 0.42) | (u[:, 1] > 0.15) & (u[:, 2] > 0.0)] = CANNELLE                       # la calotte et la nuque
    larme = (u[:, 1] < -0.30) & (np.abs(np.abs(u[:, 0]) - 0.45 - 0.10 * (0.25 - u[:, 2])) < 0.10) & (u[:, 2] < 0.28) & (u[:, 2] > -0.50)
    t[larme] = LARME
    tete.teinte = t
    RT = A.repere(TETE, (4, 0, 14))
    a.piece("tete", tete.etire(0.150, 0.125, 0.112), None, mat=RT)
    museau = A.boule(1.0, 28, 14).etire(0.060, 0.054, 0.044)
    a.piece("museau", O.teinte(museau, BLANC), None, mat=RT @ A.repere((0.0, -0.100, -0.036)))
    a.piece("nez", A.boule(1.0, 16, 8).etire(0.022, 0.016, 0.014), NEZ, mat=RT @ A.repere((0.0, -0.148, -0.020)), poil=False)
    O.paire_yeux(a, "tete", TETE, (0.50, -0.82, 0.22), 0.0185, couleur_lourde=tuple(BLANC), coupe=0.05, decolle=0.003, R=RT)
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.tour(A.profil([(0.050, 0), (0.044, 0.030), (0.026, 0.070), (0.009, 0.095), (0, 0.104)], 4), 22).etire(1.0, 0.45, 1.0)
        a.piece("oreille_" + nom, O.couche(O.teinte(ore, CANNELLE), RT @ A.cadre(Vector((c * 0.100, 0.010, 0.082)), (c * 0.45, 0.10, 1.0), (0, 1, 0))), None)
        our = A.tour(A.profil([(0.036, 0), (0.030, 0.026), (0.016, 0.060), (0.005, 0.082), (0, 0.090)], 4), 20).etire(1.0, 0.40, 1.0)
        a.piece("ourlet_" + nom, O.couche(O.teinte(our, BLANC), RT @ A.cadre(Vector((c * 0.100, -0.006, 0.086)), (c * 0.45, 0.10, 1.0), (0, 1, 0))), None, poil=False)
    O.broder(a, "bouche", "museau", RT @ Vector((0, -0.100, -0.036)), [(0.46 * u_, -0.82, -0.50 + 0.08 * u_ * u_) for u_ in np.linspace(-1, 1, 7)], 0.0020, FIL, R=RT)
    a.tete = TETE + Vector((0.0, -0.17, 0.0))

    # ----- les bras : levés à demi, les coudes au dehors, de grosses pattes sombres aux trois griffes ; les jambes courtes -----
    for nom, c, pts in (("G", 1, [(0.185, 0.010, 0.470), (0.290, -0.050, 0.520), (0.300, -0.150, 0.620), (0.250, -0.215, 0.700)]),
                        ("D", -1, [(-0.185, 0.010, 0.470), (-0.300, -0.060, 0.490), (-0.350, -0.160, 0.550), (-0.330, -0.250, 0.630)])):
        bras = O.tube_r(pts, [0.074, 0.062, 0.054, 0.050], 18)
        bras.teinte = np.tile(SOMBRE, (len(bras.v), 1))
        fin = Vector(pts[-1])
        main = A.boule(1.0, 20, 10).etire(0.056, 0.050, 0.046).pose(tuple(fin))
        main.teinte = np.tile(SOMBRE * 0.9, (len(main.v), 1))
        ens = bras + main
        for k, dx in enumerate((-0.028, 0.0, 0.028)):
            g = O.griffe(0.034, 0.0072)
            g.teinte = np.tile(np.array([0.93, 0.88, 0.76]), (len(g.v), 1))
            ens = ens + O.couche(g, A.cadre(fin + Vector((dx, -0.044, 0.014)), (0.0, -1.0, 0.25), (0, 0, 1)))
        a.piece("bras_" + nom, ens, None)
        cuisse = O.tube_r([(c * 0.130, 0.080, 0.230), (c * 0.150, 0.010, 0.120), (c * 0.150, -0.040, 0.044)], [0.098, 0.080, 0.062], 18)
        a.piece("jambe_" + nom, O.teinte(cuisse, SOMBRE), None)
        pied = A.boule(1.0, 28, 12).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.066, 0.118, 0.032)
        a.piece("pied_" + nom, O.teinte(pied, SOMBRE * 0.9), None, pos=(c * 0.150, -0.110, 0.034), rot=(0, 0, c * -8), poil=False)

    # ----- la queue : un énorme panache annelé de huit bagues, qui s'élève dans son dos plus haut que la tête -----
    chemin = [(0.0, 0.230, 0.130), (0.0, 0.420, 0.112), (0.0, 0.560, 0.270), (0.0, 0.520, 0.520), (0.0, 0.380, 0.700)]
    paliers = [((k + 1) / 8, CANNELLE if k % 2 == 0 else CREME) for k in range(8)]
    queue = K.tube_peint(A.courbe(chemin, 6), lambda t_: (0.058 + 0.050 * math.sin(math.pi * min(t_ * 1.10, 1.0)) ** 0.8) * (1.0 - 0.62 * max(0.0, (t_ - 0.84) / 0.16) ** 1.6) + 0.006, paliers, 22)
    a.piece("queue", queue, None)
    bout = A.boule(1.0, 18, 9).etire(0.032, 0.032, 0.030)
    a.piece("queue_bout", O.teinte(bout, CREME), None, pos=(0.0, 0.380, 0.705))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("panda_roux", styles.style_de("panda_roux"), sys.modules[__name__]), "Panda roux")
