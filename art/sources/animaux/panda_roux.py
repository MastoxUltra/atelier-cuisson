"""Le panda roux en peluche : le petit prince cannelle des sapins. À quatre pattes (16/10, d'après les vues d'un vrai : il était
debout comme un nounours), le ventre et les pattes brun sombre, la face blanche ornée de deux larmes rousses qui descendent de l'œil à la bouche, les oreilles triangulaires
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
TETE = Vector((0.0, -0.470, 0.400))           # 16/10 : à quatre pattes, la tête devant


def construire():
    a = K.Animal("panda_roux")
    a.taille = 0.95

    # 16/10 (planches 19-20 : « manque de réalisme ») : À QUATRE PATTES, d'après les vues d'un vrai panda roux (CC-BY, rien
    # d'importé) : un long corps bas, cannelle dessus, brun sombre dessous ; les pattes courtes et noires ; une longue queue
    # épaisse et annelée, aussi longue que le corps ; la tête ronde au masque blanc (elle était sur un corps de nounours debout)

    # ----- le corps : long et bas, le dos cannelle, le ventre et la poitrine brun sombre -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))              # 0 : le dos ; pi : le ventre
        t_ = np.tile(CANNELLE, (len(ang), 1))
        t_[ang > 2.05] = SOMBRE
        return t_
    rayon = O.interp([(0.0, 0.0), (0.05, 0.110), (0.18, 0.160), (0.45, 0.172), (0.72, 0.168), (0.90, 0.148), (1.0, 0.070)])
    O.corps_h(a, "corps", (0.0, 0.300, 0.300), 0.640, rayon, peint, None, cotes=52, pitch=3.0,
              deforme=O.gabarit(poitrail=0.04, taille=0.04, croupe=0.05, garrot=0.03, ventre=0.03))

    # ----- la tête : large et plate, les joues pleines ; face blanche, deux larmes rousses, la calotte cannelle -----
    tete = A.boule(1.0, 56, 28)
    for c in (1, -1):
        tete.sculpte(lambda v, c=c: K.bosse(v, (c * 0.9, -0.3, -0.20), 0.22, 0.30))
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(BLANC, (len(u), 1))
    t[(u[:, 2] > 0.42) | (u[:, 1] > 0.15) & (u[:, 2] > 0.0)] = CANNELLE                       # la calotte et la nuque
    larme = (u[:, 1] < -0.30) & (np.abs(np.abs(u[:, 0]) - 0.45 - 0.10 * (0.25 - u[:, 2])) < 0.10) & (u[:, 2] < 0.28) & (u[:, 2] > -0.50)
    t[larme] = LARME
    t[(u[:, 1] > -0.20) & (u[:, 2] < -0.35)] = SOMBRE                                       # la gorge sombre, sous la tête
    tete.teinte = t
    RT = A.repere(TETE, (4, 0, 18))                                                         # la tête un peu tournée vers nous
    a.piece("tete", tete.etire(0.140, 0.120, 0.108), None, mat=RT)
    museau = A.boule(1.0, 28, 14).etire(0.058, 0.054, 0.042)
    a.piece("museau", O.teinte(museau, BLANC), None, mat=RT @ A.repere((0.0, -0.100, -0.036)))
    a.piece("nez", A.boule(1.0, 16, 8).etire(0.022, 0.016, 0.014), NEZ, mat=RT @ A.repere((0.0, -0.148, -0.020)), poil=False)
    O.paire_yeux(a, "tete", TETE, (0.50, -0.82, 0.22), 0.0185, couleur_lourde=tuple(BLANC), coupe=0.60, decolle=0.003, R=RT)
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.tour(A.profil([(0.050, 0), (0.044, 0.030), (0.026, 0.070), (0.009, 0.095), (0, 0.104)], 4), 22).etire(1.0, 0.45, 1.0)
        a.piece("oreille_" + nom, O.couche(O.teinte(ore, CANNELLE), RT @ A.cadre(Vector((c * 0.096, 0.010, 0.078)), (c * 0.45, 0.10, 1.0), (0, 1, 0))), None)
        our = A.tour(A.profil([(0.036, 0), (0.030, 0.026), (0.016, 0.060), (0.005, 0.082), (0, 0.090)], 4), 20).etire(1.0, 0.40, 1.0)
        a.piece("ourlet_" + nom, O.couche(O.teinte(our, BLANC), RT @ A.cadre(Vector((c * 0.096, -0.006, 0.082)), (c * 0.45, 0.10, 1.0), (0, 1, 0))), None, poil=False)
    O.broder(a, "bouche", "museau", RT @ Vector((0, -0.100, -0.036)), [(0.46 * u_, -0.82, -0.50 + 0.08 * u_ * u_) for u_ in np.linspace(-1, 1, 7)], 0.0020, FIL, R=RT)
    a.tete = RT @ Vector((0.0, -0.170, 0.0))
    cou = O.tube_r([(0.0, -0.290, 0.360), (0.0, -0.350, 0.375), (0.0, -0.400, 0.380)], [0.130, 0.118, 0.106], 22)
    a.piece("cou", O.teinte(cou, CANNELLE), None)

    # ----- les pattes : courtes, noires, sur de petites pattes rondes en poil -----
    for sgn, nom in ((1, "G"), (-1, "D")):
        O.jambe(a, "avant_" + nom, (sgn * 0.098, -0.210, 0.290), (sgn * 0.108, -0.245, 0.034), 0.066, SOMBRE, bas=SOMBRE * 0.85,
                bas_frac=0.60, sorte="av", plie=0.020, pied_dim=(0.046, 0.066, 0.022), griffes=0)
        O.jambe(a, "arriere_" + nom, (sgn * 0.104, 0.210, 0.290), (sgn * 0.114, 0.250, 0.034), 0.076, SOMBRE, bas=SOMBRE * 0.85,
                bas_frac=0.60, sorte="ar", plie=0.040, pied_dim=(0.048, 0.070, 0.022), griffes=0)
    for p in a._toutes():                                             # les pieds en poil, comme les jambes
        if p["nom"].startswith("pied_"):
            p["poil"], p["zone"] = "teinte", "poil"

    # ----- la queue : longue et épaisse, annelée de huit bagues, qui part de la croupe et s'allonge derrière, le bout au sol -----
    chemin = [(0.0, 0.300, 0.340), (0.0, 0.440, 0.330), (0.020, 0.580, 0.270), (0.050, 0.700, 0.180), (0.080, 0.790, 0.100), (0.100, 0.850, 0.072)]
    paliers = [((k + 1) / 8, CANNELLE if k % 2 == 0 else CREME) for k in range(8)]
    queue = K.tube_peint(A.courbe(chemin, 6), lambda t_: (0.070 + 0.010 * math.sin(math.pi * t_)) * (1.0 - 0.55 * max(0.0, (t_ - 0.86) / 0.14) ** 1.6), paliers, 22)
    a.piece("queue", queue, None)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("panda_roux", styles.style_de("panda_roux"), sys.modules[__name__]), "Panda roux")
