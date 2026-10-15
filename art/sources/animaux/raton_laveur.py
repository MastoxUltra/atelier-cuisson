"""Le raton laveur en peluche, deuxième dessin : le bandit. Gris poivré, tout en rondeurs de voleur de poulailler, le masque
noir large comme un loup de carnaval qui lui barre la face de joue à joue, avec ses deux pointes en biais, un sourcil
blanc dessus et le museau clair dessous ; et une queue qu'on ne peut pas ne pas voir : un énorme panache annelé de sept
bagues, plus haut que lui, qui s'enroule dans son dos. Accroupi, les épaules remontées, il se frotte les mains avec un
air de n'avoir rien fait, et regarde par-dessus l'épaule, très lentement, pour voir qui regarde.

    python raton_laveur.py        fabrique la fiche art/apercus/animaux/raton_laveur.png (style du palier : A, cousu main)
    (le premier dessin, refusé le 15/10 : « une poire avec des bras en tuyau »)
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

POIVRE = np.array(M.hexa("#8f8e8a"))          # la dominante (registre : gris poivré)
CLAIR = np.array(M.hexa("#d6d2c8"))           # le museau, le sourcil, le ventre, l'ourlet des oreilles
CHARBON = np.array(M.hexa("#2a2828"))         # le masque, les bagues, les mains
NEZ = M.hexa("#171515")
FIL = M.hexa("#2a2424")
TETE = Vector((0.0, -0.095, 0.520))


def construire():
    a = K.Animal("raton_laveur")
    a.taille = 0.85

    # ----- le corps : accroupi, une grosse poire écrasée, le dos rond et les épaules hautes, la panse sur les cuisses -----
    pc = A.profil([(0, 0.0), (0.120, 0.012), (0.195, 0.070), (0.225, 0.160), (0.210, 0.260), (0.170, 0.350), (0.115, 0.415), (0.058, 0.450), (0, 0.465)], 6)
    corps = A.tour(pc, 56)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    z = corps.v[:, 2]
    t = np.tile(POIVRE, (len(z), 1))
    t[(ang > 2.15) & (z < 0.40)] = CLAIR * 0.80 + POIVRE * 0.20
    t[(np.sin(z * 44 + ang * 3) > 0.60) & (ang < 1.9)] = POIVRE * 0.80               # le grain sombre du poil
    corps.teinte = t

    def galbe(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 1] += 0.050 * np.exp(-((z - 0.34) / 0.10) ** 2) * (v[:, 1] > 0)         # les épaules remontées, le dos rond
        s[:, 1] -= 0.030 * np.exp(-((z - 0.18) / 0.10) ** 2) * (v[:, 1] < 0)         # la panse
        return s
    a.piece("corps", corps.sculpte(galbe), None, mat=A.repere((0.0, 0.050, 0.022), (16, 0, 0)))

    # ----- la tête : large aux joues, tournée par-dessus l'épaule ; le masque noir en loup, le sourcil blanc, le museau clair -----
    tete = A.boule(1.0, 56, 28)
    for c in (1, -1):
        tete.sculpte(lambda v, c=c: K.bosse(v, (c * 0.92, -0.25, -0.30), 0.26, 0.30))            # les joues pleines
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(POIVRE, (len(u), 1))
    x, y, zz = u[:, 0], u[:, 1], u[:, 2]
    front = y < 0.08
    masque = front & (np.abs(zz - 0.06 + 0.16 * np.abs(x)) < 0.22 + 0.10 * np.abs(x)) & (np.abs(x) > 0.10)       # le masque s'élargit et plonge vers les tempes
    t[front & (zz > 0.22) & (zz < 0.46) & (np.abs(x) > 0.08)] = CLAIR                                              # le sourcil blanc
    t[(y < -0.45) & (np.abs(x) < 0.34) & (zz < 0.28)] = CLAIR                                                      # le museau
    t[masque] = CHARBON
    t[(zz < -0.45) & front] = CLAIR
    tete.teinte = t
    RT = A.repere(TETE, (6, 0, 12))
    a.piece("tete", tete.etire(0.118, 0.106, 0.092), None, mat=RT)
    museau = A.tour(A.profil([(0.062, 0), (0.058, 0.024), (0.050, 0.052), (0.036, 0.078), (0.016, 0.094), (0, 0.098)], 5), 28).etire(1.0, 0.86, 1.0)
    a.piece("museau", O.couche(O.teinte(museau, CLAIR), RT @ A.cadre(Vector((0.0, -0.082, -0.024)), (0.0, -1.0, -0.14), (0, 1, 0))), None)
    a.piece("nez", A.boule(1.0, 14, 8).etire(0.016, 0.013, 0.012), NEZ, mat=RT @ A.repere((0.0, -0.182, -0.041)), poil=False)
    O.paire_yeux(a, "tete", TETE, (0.60, -0.76, 0.14), 0.0165, couleur_lourde=tuple(CHARBON), coupe=0.60, decolle=0.003, R=RT)
    # le masque creusé autour des yeux : une collerette noire en relief et, au-dessus, un fil crème qui souligne le sourcil
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", TETE, RT.to_3x3() @ Vector((c * 0.60, -0.76, 0.14)))
        a.piece("cerne_" + nom, A.tore(0.0250, 0.0075, 28, 8), tuple(CHARBON * 0.8), mat=A.cadre(pos + n * 0.001, n), poil=False)
        arc = [Vector((c * (0.34 + 0.34 * u_), -0.80 + 0.12 * u_, 0.40 + 0.06 * math.sin(math.pi * u_))) for u_ in np.linspace(0, 1, 8)]
        O.broder(a, "sourcil_" + nom, "tete", TETE, [tuple(d) for d in arc], 0.0030, tuple(CLAIR), decolle=0.004, R=RT)
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.tour(A.profil([(0.040, 0), (0.036, 0.020), (0.024, 0.048), (0.010, 0.068), (0, 0.076)], 4), 20).etire(1.0, 0.50, 1.0)
        a.piece("oreille_" + nom, O.couche(O.teinte(ore, POIVRE), RT @ A.cadre(Vector((c * 0.080, 0.010, 0.080)), Vector((c * 0.50, 0.10, 1.0)), (0, 1, 0))), None)
        our = A.tour(A.profil([(0.030, 0), (0.026, 0.016), (0.017, 0.040), (0.007, 0.057), (0, 0.064)], 4), 18).etire(1.0, 0.42, 1.0)
        a.piece("ourlet_" + nom, O.couche(O.teinte(our, CLAIR), RT @ A.cadre(Vector((c * 0.080, -0.002, 0.082)), Vector((c * 0.50, 0.10, 1.0)), (0, 1, 0))), None, poil=False)
    O.broder(a, "sourire", "tete", TETE, [(0.30 * u_ + 0.08, -0.97, -0.40 + 0.12 * u_ * u_) for u_ in np.linspace(-1, 1, 9)], 0.0022, FIL, decolle=0.003, R=RT)
    a.tete = TETE + Vector((0.12, -0.14, 0.0))

    # ----- les mains qui se frottent : deux avant-bras courts qui se rejoignent, des doigts en trait ; les cuisses, les pieds -----
    for nom, c, pts, pat in (("G", 1, [(0.200, -0.040, 0.380), (0.265, -0.115, 0.310), (0.160, -0.185, 0.270), (0.062, -0.200, 0.285)], (0.040, -0.206, 0.290)),
                             ("D", -1, [(-0.200, -0.040, 0.380), (-0.265, -0.120, 0.320), (-0.150, -0.200, 0.290), (-0.040, -0.215, 0.300)], (-0.020, -0.218, 0.296))):
        bras = O.tube_r(pts, [0.062, 0.054, 0.046, 0.042], 18)
        bras.teinte = np.tile(POIVRE, (len(bras.v), 1))
        main = A.boule(1.0, 20, 10).etire(0.044, 0.040, 0.034).pose(pat)
        main.teinte = np.tile(CHARBON, (len(main.v), 1))
        ens = bras + main
        for k, dx in enumerate((-0.020, 0.0, 0.020)):
            doigt = A.boule(1.0, 10, 6).etire(0.0075, 0.020, 0.0075)
            doigt.teinte = np.tile(CHARBON * 0.75, (len(doigt.v), 1))
            ens = ens + doigt.pose((pat[0] + dx, pat[1] - 0.036, pat[2] - 0.004))
        a.piece("bras_" + nom, ens, None)
        cuisse = A.boule(1.0, 36, 18).etire(0.100, 0.160, 0.120)
        a.piece("cuisse_" + nom, O.teinte(cuisse, POIVRE), None, pos=(c * 0.160, 0.060, 0.120), rot=(10, 0, c * 10))
        pied = A.boule(1.0, 28, 12).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.060, 0.115, 0.024)
        for k2, dx in enumerate((-0.036, -0.012, 0.012, 0.036)):
            pied = pied + A.boule(1.0, 12, 6).etire(0.012, 0.022, 0.012).pose((dx, -0.118, 0.0))
        pied.teinte = np.tile(CHARBON, (len(pied.v), 1))
        a.piece("pied_" + nom, pied, None, pos=(c * 0.140, -0.130, 0.028), rot=(0, 0, c * -12), poil=False)

    # ----- la queue : un énorme panache annelé, plus haut que lui, qui s'enroule dans son dos ; sept bagues et le bout noir -----
    chemin = [(0.0, 0.220, 0.130), (0.0, 0.440, 0.110), (0.0, 0.640, 0.190), (0.0, 0.640, 0.420), (0.0, 0.490, 0.610), (0.02, 0.330, 0.690)]
    paliers = []
    for k in range(8):
        paliers.append(((k + 1) / 8, POIVRE * 1.05 if k % 2 == 0 else CHARBON))
    paliers[-1] = (1.0, CHARBON)
    queue = K.tube_peint(A.courbe(chemin, 6), lambda t_: 0.052 + 0.050 * math.sin(math.pi * min(t_ * 1.12, 1.0)) ** 0.7, paliers, 24)
    a.piece("queue", queue, None)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
GONFLAGE = True      # gardée par l'auteur sur la base GONFLÉE (planche 11, 15/10) : toujours gonflée, même dans une liste de gardées
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("raton_laveur", styles.style_de("raton_laveur"), sys.modules[__name__]), "Raton laveur")
