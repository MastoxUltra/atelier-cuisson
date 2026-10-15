"""La loutre en peluche, deuxième dessin : la funambule de la rivière, tout en souplesse. Café sombre luisant, la gorge
et le menton crème, une face large et plate de chat qui a pris des coups de moustaches blanches, longues comme des
baguettes. Debout en périscope, le long corps en S, appuyée sur sa queue épaisse qui part en faucille sur le côté ; une
patte contre la poitrine, l'autre au menton : elle réfléchit, à ce qu'elle va faire du poisson qu'elle n'a pas encore pris.
Les pieds palmés, grands comme des palmes, posés en V.

    python loutre.py        fabrique la fiche art/apercus/animaux/loutre.png (style du palier : C, velours ras)
    (le premier dessin, refusé le 15/10 : « des boules et des tubes lisses »)
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

CAFE = np.array(M.hexa("#5c4130"))            # la dominante (registre : café sombre luisant) ; le velours éclaircit un peu
CLAIR = np.array(M.hexa("#b89a74"))           # le ventre, le dessous du cou
GORGE = np.array(M.hexa("#ecdcbe"))           # la gorge et le menton, crème
BLANC = M.hexa("#fbf8f0")                     # les moustaches
NEZ = M.hexa("#1a1311")
FIL = M.hexa("#241812")

# de la pointe de la queue à la nuque : la queue en faucille sur le sol, les hanches, le ventre, le torse qui se dresse en S
CHEMIN = [(0.36, 0.56, 0.044), (0.22, 0.52, 0.056), (0.09, 0.42, 0.090), (0.01, 0.28, 0.150), (-0.03, 0.15, 0.270), (-0.01, 0.06, 0.420),
          (0.02, 0.00, 0.560), (0.04, -0.045, 0.680), (0.04, -0.085, 0.730)]
T_TETE = Vector((0.04, -0.110, 0.800))


def rayon(f):
    return O.interp([(0.0, 0.0), (0.02, 0.016), (0.12, 0.046), (0.26, 0.074), (0.36, 0.098), (0.50, 0.112), (0.68, 0.098), (0.84, 0.078),
                     (0.94, 0.066), (1.0, 0.062)])(f)


def construire():
    a = K.Animal("loutre")
    a.taille = 1.10

    # ----- le corps : une seule pièce du bout de la queue à la nuque, hanches larges, panse pleine, poitrail, cou long -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        f = m.v[:, 2] / L
        t = np.tile(CAFE, (len(f), 1))
        t[(ang > 2.0) & (f > 0.40)] = CLAIR * 0.55 + CAFE * 0.45
        t[(ang > 2.35) & (f > 0.78)] = GORGE
        return t

    def galbe(L):
        def f(v):
            s = v.copy()
            fr = v[:, 2] / L
            dev = v[:, 1] < 0
            s[dev, 1] *= (1 + 0.20 * np.exp(-((fr - 0.55) / 0.10) ** 2))[dev]                  # la panse
            s[~dev, 1] *= (1 + 0.10 * np.exp(-((fr - 0.40) / 0.08) ** 2))[~dev]                # la croupe
            return s
        return f
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=48, flanc=(1.0, 0.0, 0.0), deforme=galbe)

    # ----- la tête : large, plate, les coussinets à moustaches gonflés ; le museau court, le nez en poire ; petites oreilles basses -----
    tete = A.boule(1.0, 56, 28)
    for c in (1, -1):
        tete.sculpte(lambda v, c=c: K.bosse(v, (c * 0.55, -0.90, -0.30), 0.30, 0.22))            # les coussinets à moustaches
        tete.sculpte(lambda v, c=c: K.bosse(v, (c * 0.55, -0.65, 0.65), 0.12, 0.20))             # les arcades
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(CAFE, (len(u), 1))
    t[(u[:, 1] < -0.25) & (u[:, 2] < 0.05)] = GORGE * 0.85 + CAFE * 0.15
    t[(u[:, 2] < -0.45)] = GORGE
    tete.teinte = t
    RT = A.repere(T_TETE, (-8, 0, 24))
    a.piece("tete", tete.etire(0.100, 0.105, 0.082), None, mat=RT)
    museau = A.boule(1.0, 28, 14).etire(0.062, 0.050, 0.040)
    a.piece("museau", O.teinte(museau, GORGE * 0.90), None, mat=RT @ A.repere((0.0, -0.085, -0.030)))
    a.piece("nez", A.boule(1.0, 18, 10).etire(0.030, 0.020, 0.018), NEZ, mat=RT @ A.repere((0.0, -0.126, -0.018)), poil=False)
    O.paire_yeux(a, "tete", T_TETE, (0.60, -0.78, 0.26), 0.0150, couleur_lourde=tuple(CAFE), coupe=0.60, decolle=0.002, R=RT)
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.boule(1.0, 16, 8).etire(0.020, 0.012, 0.022)
        a.piece("oreille_" + nom, O.teinte(ore, CAFE * 0.9), None, mat=RT @ A.repere((c * 0.088, 0.020, 0.058)), poil=False)
        for k, dz in enumerate((0.022, 0.006, -0.010, -0.026)):
            a.broderie("moustache_%s%d" % (nom, k), [RT @ Vector((c * 0.030, -0.120, -0.020 + dz * 0.3)), RT @ Vector((c * 0.090, -0.150, -0.016 + dz * 1.0)),
                                                      RT @ Vector((c * 0.165, -0.150, -0.012 + dz * 2.1))], 0.0014, BLANC)
    a.tete = T_TETE + Vector((0.0, -0.13, 0.0))

    # ----- les bras : l'un contre la poitrine, l'autre posé plus bas sur la panse (Principal, 15/10 : levé au menton, il faisait
    # une palette sombre collée à la joue) ; trois petits doigts -----
    for nom, c, pts, pat in (("G", 1, [(0.110, -0.010, 0.660), (0.175, -0.080, 0.600), (0.105, -0.150, 0.560), (0.050, -0.165, 0.570)], (0.036, -0.168, 0.574)),
                             ("D", -1, [(-0.110, -0.010, 0.660), (-0.168, -0.080, 0.580), (-0.110, -0.140, 0.520), (-0.055, -0.148, 0.518)], (-0.040, -0.150, 0.515))):
        bras = O.tube_r(pts, [0.046, 0.040, 0.034, 0.030], 18)
        bras.teinte = np.tile(CAFE, (len(bras.v), 1))
        main = A.boule(1.0, 18, 10).etire(0.038, 0.032, 0.028).pose(pat)
        main.teinte = np.tile(CAFE * 0.8, (len(main.v), 1))
        a.piece("bras_" + nom, bras + main, None)
        # les cuisses : épaisses, qui plongent vers les pieds palmés
        cuisse = O.tube_r([(c * 0.085, 0.230, 0.230), (c * 0.135, 0.150, 0.135), (c * 0.145, 0.030, 0.050)], [0.092, 0.074, 0.050], 20)
        a.piece("cuisse_" + nom, O.teinte(cuisse, CAFE), None)
        pied = A.boule(1.0, 32, 12).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.052, 0.120, 0.016)
        for dx in (-0.034, -0.012, 0.012, 0.034):
            pied = pied + A.boule(1.0, 12, 6).etire(0.011, 0.026, 0.011).pose((dx, -0.128, 0.0))
        pied.teinte = np.tile(CAFE * 0.78, (len(pied.v), 1))
        a.piece("pied_" + nom, pied, None, pos=(c * 0.138, -0.040, 0.021), rot=(0, 0, c * -16), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
GONFLAGE = True      # gardée par l'auteur sur la base GONFLÉE (planche 11, 15/10) : toujours gonflée, même dans une liste de gardées
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad", souple=True)


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("loutre", styles.style_de("loutre"), sys.modules[__name__]), "Loutre")
