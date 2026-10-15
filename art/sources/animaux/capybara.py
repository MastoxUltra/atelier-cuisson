"""Le capybara en peluche : le grand calme des sources chaudes, brun sable chaud, un long tonneau sur quatre pattes courtes, la
grosse tête carrée au museau émoussé et sombre, les petits yeux hauts, les petites oreilles rondes, les narines tout au
bout du nez. Debout, la tête un peu tournée, il regarde passer le monde avec la patience de celui qui a déjà vu un
crocodile et n'en a pas fait toute une histoire.

    python capybara.py        fabrique la fiche art/apercus/animaux/capybara.png (style du palier : C, velours ras)
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

SABLE = np.array(M.hexa("#b58a64"))           # la dominante (registre : brun sable chaud #a88060), un cran plus clair (style C)
CLAIR = np.array(M.hexa("#d0ab88"))           # le ventre, le menton, les joues
MUFLE = np.array(M.hexa("#6a4a38"))           # l'accent : le museau sombre
PIED = np.array(M.hexa("#7a5a46"))            # les pieds palmés
NEZ = M.hexa("#241812")
FIL = M.hexa("#3a2418")
H = Vector((0.0, -0.560, 0.390))              # le centre de la tête


def construire():
    a = K.Animal("capybara")
    a.taille = 1.10

    # ----- le corps : un long tonneau, le dos bas et droit, la croupe plus haute, le ventre rond, plus clair dessous -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(SABLE, (len(ang), 1))
        t[(ang > 2.35)] = CLAIR
        t[(ang < 0.85)] = SABLE * 0.92
        return t
    rayon = O.interp([(0.0, 0.0), (0.04, 0.115), (0.15, 0.178), (0.40, 0.205), (0.68, 0.205), (0.88, 0.195), (0.96, 0.168), (1.0, 0.070)])
    O.corps_h(a, "corps", (0.0, 0.42, 0.340), 0.82, rayon, peint, None, cotes=52, pitch=-2.0,
              deforme=O.gabarit(poitrail=0.06, taille=0.0, croupe=0.04, garrot=0.04, ventre=0.0))

    # ----- la tête : large, carrée, le front plat ; le museau émoussé et sombre ; les narines en haut du nez -----
    RT = A.repere(H, (4, 0, 14))
    crane = A.boule(1.0, 52, 26).sculpte(lambda v: K.emousse(v, 0.62))
    for c in (1, -1):
        crane.sculpte(lambda v, c=c: K.bosse(v, (c * 0.9, -0.3, -0.25), 0.20, 0.22))
    u = crane.v / np.maximum(np.linalg.norm(crane.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(SABLE, (len(u), 1))
    t[(u[:, 1] < -0.30) & (u[:, 2] < 0.15)] = CLAIR * 0.92                                # les joues, le menton
    t[(u[:, 1] < -0.74)] = MUFLE                                                           # le bout du nez
    crane.teinte = t
    a.piece("tete", crane.etire(0.112, 0.168, 0.108), None, mat=RT)
    nez = A.boule(1.0, 28, 14).sculpte(lambda v: K.emousse(v, 0.7)).etire(0.098, 0.062, 0.088)
    a.piece("nez", O.teinte(nez, MUFLE), None, mat=RT @ A.repere((0.0, -0.152, -0.008)))
    for c in (1, -1):
        a.piece("narine_%d" % c, A.boule(1.0, 12, 6).etire(0.017, 0.012, 0.012), NEZ, mat=RT @ A.repere((c * 0.038, -0.206, 0.028)), poil=False)
    O.paire_yeux(a, "tete", H, (0.86, -0.38, 0.36), 0.0160, couleur_lourde=tuple(SABLE * 0.94), coupe=0.60, decolle=0.002, R=RT)
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.boule(1.0, 20, 10).etire(0.028, 0.014, 0.030)
        a.piece("oreille_" + nom, O.teinte(ore, SABLE * 0.88), None, mat=RT @ A.repere((c * 0.074, 0.060, 0.094)))
    O.broder(a, "bouche", "nez", RT @ Vector((0, -0.152, -0.008)), [(0.62 * u_, -0.80, -0.34 + 0.06 * u_ * u_) for u_ in np.linspace(-1, 1, 7)], 0.0024, FIL, R=RT)
    a.tete = H + Vector((0.0, -0.20, 0.0))

    # ----- les pattes courtes et fortes, les pieds palmés à gros doigts ; pas de queue -----
    for sgn, nom in ((1, "G"), (-1, "D")):
        O.jambe(a, "avant_" + nom, (sgn * 0.120, -0.230, 0.320), (sgn * 0.124, -0.265, 0.044), 0.088, SABLE, bas=SABLE * 0.90, bas_frac=0.60,
                sorte="av", plie=0.020, pied_dim=(0.054, 0.082, 0.026), griffes=0)
        O.jambe(a, "arriere_" + nom, (sgn * 0.112, 0.300, 0.300), (sgn * 0.118, 0.340, 0.044), 0.094, SABLE, bas=SABLE * 0.90, bas_frac=0.60,
                sorte="ar", plie=0.045, pied_dim=(0.056, 0.086, 0.026), griffes=0)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("capybara", styles.style_de("capybara"), sys.modules[__name__]), "Capybara")
