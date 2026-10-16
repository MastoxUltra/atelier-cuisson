"""L'ours en peluche, quatrième dessin (16/10, planches 19-20 : « manque de réalisme ») : l'ours brun des sapins à QUATRE
PATTES, d'après les vues d'un modèle de référence (references_3d/ours, CC-BY : vues seulement, rien d'importé). Noisette
cendré, une longue masse posée sur quatre piliers ; la bosse de muscle au-dessus des épaules, plus haute que la croupe ;
la tête portée bas, devant, au museau allongé plus clair et au gros nez noir ; les petites oreilles rondes plantées sur
les coins du crâne ; de petits yeux calmes ; des pattes épaisses, sombres, aux griffes pâles ; un moignon de queue.
Il marche, la tête un peu tournée vers nous.

    python ours.py        fabrique la fiche art/apercus/animaux/ours.png (style du palier : B, peluche de magasin)
    (1er dessin : « le nounours de supermarché » ; 2e : « très géométrique » ; 3e : debout, un bras levé, refusé le 16/10)
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

GONFLAGE = True                               # la base aux volumes de l'Artiste (fusion + gonflage), validée le 15/10

NOISETTE = np.array(M.hexa("#7a5c46"))        # la dominante (registre : brun noisette cendré #6e5846), un peu plus chaud (style B)
CLAIR = np.array(M.hexa("#a88c70"))           # le museau, le givre de la bosse
SOMBRE = np.array(M.hexa("#5a4435"))          # les pattes
GRIFFE = (0.91, 0.86, 0.77)
NEZ = M.hexa("#16110e")
FIL = M.hexa("#2a1c14")
H = Vector((0.0, -0.640, 0.505))              # le centre du crâne


def construire():
    a = K.Animal("ours")
    a.taille = 2.20

    # ----- le corps : une longue masse, la bosse au-dessus des épaules (le garrot), la croupe un peu plus basse ; le dos
    #       givré sur la bosse, le ventre un ton plus sombre -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))              # 0 : le dos ; pi : le ventre
        f = m.v[:, 2] / L
        t = np.tile(NOISETTE, (len(ang), 1))
        t[ang > 2.30] = NOISETTE * 0.86
        t[(ang < 0.75) & (f > 0.62) & (f < 0.92)] = NOISETTE * 0.62 + CLAIR * 0.38    # le givre de la bosse
        return t
    rayon = O.interp([(0.0, 0.0), (0.04, 0.140), (0.15, 0.205), (0.40, 0.222), (0.66, 0.232), (0.83, 0.228), (0.94, 0.195), (1.0, 0.085)])
    O.corps_h(a, "corps", (0.0, 0.400, 0.440), 0.860, rayon, peint, None, cotes=56, pitch=4.0,
              deforme=O.gabarit(poitrail=0.06, taille=0.04, croupe=0.05, garrot=0.16, ventre=0.04, pos_poitrail=0.80))

    # ----- le cou épais, la tête portée bas devant le poitrail -----
    cou = O.tube_r([(0.0, -0.380, 0.540), (0.0, -0.480, 0.530), (0.0, -0.575, 0.510)], [0.170, 0.150, 0.128], 24)
    a.piece("cou", O.teinte(cou, NOISETTE), None)
    RT = A.repere(H, (8, 0, 16))                                   # le nez un peu bas, la tête tournée vers nous
    R3 = RT.to_3x3()
    crane = A.boule(1.0, 52, 26).sculpte(lambda v: K.emousse(v, 0.80))
    for c in (1, -1):
        crane.sculpte(lambda v, c=c: K.bosse(v, (c * 0.9, -0.2, -0.25), 0.22, 0.26))   # les bajoues
    a.piece("tete", O.teinte(crane.etire(0.132, 0.140, 0.118), NOISETTE), None, mat=RT)
    # le museau : allongé, qui s'affine, plus clair ; le gros nez noir au bout
    museau = A.tour(A.profil([(0.074, 0.0), (0.072, 0.040), (0.064, 0.090), (0.054, 0.130), (0.042, 0.160), (0, 0.170)], 5), 36)
    museau.etire(1.0, 0.86, 1.0)
    a.piece("museau", O.teinte(museau, CLAIR), None, mat=RT @ A.cadre(Vector((0.0, -0.080, -0.040)), (0.0, -1.0, -0.16), (0, 0, 1)))
    bout = RT @ Vector((0.0, -0.080 - 0.155, -0.040 - 0.025))
    # la truffe (16/10, 4e passage : elle se lisait comme un trou, noyée dans le museau gonflé) : en relief, ronde et
    # brillante (une pièce dure, vernie comme un bouton), qui avance de 3 cm au bout du museau
    nez = A.boule(1.0, 24, 12).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.038, 0.026, 0.028)
    a._poser(a._jouet(a._durs, NEZ, "d"), "nez", nez, "bouton", A.repere(bout + R3 @ Vector((0.0, -0.016, 0.012))), False, "volume", "dur")
    O.broder(a, "bouche", "museau", RT @ Vector((0.0, -0.140, -0.040)), [(0.55 * u_, -0.55, -0.80 + 0.10 * u_ * u_) for u_ in np.linspace(-1, 1, 7)],
             0.0030, FIL, R=RT)
    # les yeux : petits, rapprochés, à la racine du museau ; les oreilles rondes sur les coins du crâne
    O.paire_yeux(a, "tete", H, (0.50, -0.80, 0.34), 0.0175, decolle=0.002, R=RT)
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", H, R3 @ Vector((c * 0.50, 0.12, 0.86)))            # plus haut : elles se voient de face
        ore = A.boule(1.0, 24, 12).sculpte(lambda v: v + np.stack([0 * v[:, 0], 0 * v[:, 1], 0.6 * (v[:, 0] ** 2 + v[:, 1] ** 2)], axis=1))
        a.piece("oreille_" + nom, O.teinte(ore.etire(0.058, 0.028, 0.062), NOISETTE * 0.85), None,          # plus saillantes
                mat=A.cadre(pos + n * 0.024, n, R3 @ Vector((0.0, -1.0, 0.0))))   # épaisseur d'avant en arrière
    a.tete = RT @ Vector((0.0, -0.250, -0.020))

    # ----- les pattes : quatre piliers épais, sombres, sur de larges pattes rondes du même brun foncé, EN POIL (16/10 : les
    #       pieds de feutrine gris pâle et les longues lames blanches faisaient des chaussons) ; cinq griffes crème courtes,
    #       à moitié cachées dans le poil, au bord de chaque patte -----
    for sgn, nom in ((1, "G"), (-1, "D")):
        for sorte, haut_, pied_, R_, dim, bf, pl in (
                ("avant", (sgn * 0.135, -0.290, 0.440), (sgn * 0.145, -0.345 - 0.030 * sgn, 0.050), 0.108, (0.094, 0.118, 0.030), 0.34, 0.025),
                ("arriere", (sgn * 0.140, 0.260, 0.420), (sgn * 0.150, 0.300 + 0.030 * sgn, 0.050), 0.122, (0.098, 0.128, 0.030), 0.40, 0.050)):
            pts = O.jambe(a, sorte + "_" + nom, haut_, pied_, R_, NOISETTE, bas=SOMBRE, bas_frac=bf, sorte="av" if sorte == "avant" else "ar",
                          plie=pl, pied_dim=dim, griffes=0)
            fin = pts[-1]
            centre = Vector((fin[0], fin[1] - dim[1] * 0.35, dim[2] * 0.95))
            for k in range(5):
                dx = (k - 2) * 0.30 * dim[0]
                g = O.couche(O.teinte(O.griffe(0.026, 0.0090), np.array(GRIFFE)),          # courtes (16/10)
                             A.cadre(centre + Vector((dx, -dim[1] * 0.90 + 0.004 * abs(k - 2), -dim[2] * 0.30)), (0.0, -1.0, -0.35), (0, 0, 1)))
                a.piece("griffe_%s_%s%d" % (sorte, nom, k), g, None, poil=False)
    for p in a._toutes():                                             # les pattes en poil, comme les jambes
        if p["nom"].startswith("pied_"):
            p["poil"], p["zone"] = "teinte", "poil"
    # (16/10, 4e passage : fondus et gonflés, les pieds plats devenaient des boules) : posés à part, larges et plats
    a.fusion_a_part = ("pied",)

    # ----- la queue : un moignon rond derrière -----
    queue = A.boule(1.0, 20, 10).sculpte(lambda v: K.emousse(v, 0.9)).etire(0.050, 0.052, 0.048)
    a.piece("queue", O.teinte(queue, NOISETTE), None, pos=(0.0, 0.395, 0.560))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("ours", styles.style_de("ours"), sys.modules[__name__]), "Ours")
