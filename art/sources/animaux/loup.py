"""Le loup en peluche, deuxième dessin : le chanteur de la forêt, gris fumé, le dos plus sombre, le masque et le ventre
pâles. Debout sur quatre jambes à genoux et jarrets marqués, la poitrine profonde, la fraise de poils hérissée autour
du cou, il hurle : la tête renversée presque à la verticale, les yeux fermés en deux petits arcs brodés, le museau au
ciel, les mâchoires entrouvertes sur une langue rose et quatre crocs, les oreilles plaquées en arrière. La queue pend,
lourde, le bout sombre. On ne voit pas la lune ; on la comprend.

    python loup.py        fabrique la fiche art/apercus/animaux/loup.png (style du palier : B, peluche de magasin)
    (le premier dessin, jugé le 15/10 : « des pattes en bâtons »)
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

FUMEE = np.array(M.hexa("#7f858c"))           # la dominante (registre : gris fumé)
SOMBRE = np.array(M.hexa("#555a61"))          # le dos, le bout des oreilles et de la queue, les chaussettes
CLAIR = np.array(M.hexa("#d4d2cc"))           # le masque, le ventre, la gorge, la fraise
NEZ = M.hexa("#16130f")
LANGUE = M.hexa("#e0788a")
DENT = M.hexa("#f8f4ea")
FIL = M.hexa("#2a2724")


TOURNE = 25                                   # la fiche tourne la bête vers la caméra (25° devant) : on compte les DEUX yeux ; 0 pour le jeu


def construire():
    a = K.Animal("loup")
    a.taille = 1.55

    # ----- le corps : un long tonneau à la poitrine profonde, le garrot saillant, la taille creusée, la croupe osseuse -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        f = m.v[:, 2] / L
        t = np.tile(FUMEE, (len(ang), 1))
        t[ang < 0.95] = SOMBRE * 0.45 + FUMEE * 0.55                # la selle sombre sur le dos
        t[ang > 2.10] = CLAIR
        t[(f > 0.80) & (ang > 1.30)] = CLAIR * 0.8 + FUMEE * 0.2    # la poitrine
        return t
    rayon = O.interp([(0.0, 0.0), (0.05, 0.080), (0.18, 0.130), (0.45, 0.142), (0.75, 0.168), (0.93, 0.150), (1.0, 0.108)])
    O.corps_h(a, "corps", (0.0, 0.46, 0.50), 0.80, rayon, peint, None, cotes=52, pitch=7.0,
              deforme=O.gabarit(poitrail=0.22, taille=0.14, croupe=0.14, garrot=0.16, ventre=0.24))

    # ----- le cou levé presque à la verticale, la fraise de poils, la tête renversée -----
    cou = O.tube_r([(0.0, -0.27, 0.58), (0.0, -0.36, 0.69), (0.0, -0.43, 0.79), (0.0, -0.47, 0.89)], [0.136, 0.118, 0.100, 0.090], 22)
    cou.teinte = np.tile(FUMEE, (len(cou.v), 1))
    a.piece("cou", cou, None)
    # la fraise : un épais col de poils (un boudin moelleux autour du cou, pas des pointes blanches qui font un collier de dents)
    col = A.tore(0.092, 0.046, 40, 14)
    col.teinte = np.tile(CLAIR * 0.85 + FUMEE * 0.15, (len(col.v), 1))
    a.piece("fraise", col.etire(1.0, 1.0, 1.15), None, pos=(0.0, -0.39, 0.745), rot=(33, 0, 0))

    H = Vector((0.0, -0.51, 0.99))
    RT = A.repere(H, (-10, 0, 0))                 # la tête relevée sans se renverser : les deux yeux restent de face
    crane = A.boule(1.0, 48, 24)
    for c in (1, -1):
        crane.sculpte(lambda v, c=c: K.bosse(v, (c * 0.9, -0.4, -0.2), 0.16, 0.28))      # les joues
    crane.teinte = np.tile(FUMEE, (len(crane.v), 1))
    a.piece("tete", crane.sculpte(lambda v: K.bosse(v, (0.0, -0.5, 0.8), 0.14, 0.30)).etire(0.076, 0.094, 0.078), None, mat=RT)
    haut_m = A.tour(A.profil([(0.052, 0), (0.048, 0.050), (0.038, 0.112), (0.026, 0.158), (0.013, 0.180), (0, 0.188)], 4), 24).etire(1.0, 0.78, 1.0)
    bas_m = A.tour(A.profil([(0.040, 0), (0.036, 0.050), (0.028, 0.106), (0.017, 0.146), (0, 0.164)], 4), 20).etire(1.0, 0.62, 1.0)
    a.piece("museau_haut", O.couche(O.teinte(haut_m, CLAIR * 0.55 + FUMEE * 0.45), RT @ A.cadre(Vector((0.0, -0.060, 0.012)), (0.0, -1.0, 0.0), (0, 0, 1))), None)
    a.piece("museau_bas", O.couche(O.teinte(bas_m, CLAIR), RT @ A.cadre(Vector((0.0, -0.058, -0.030)), (0.0, -1.0, -0.42), (0, 0, 1))), None)
    a.piece("nez", A.boule(1.0, 16, 8).etire(0.021, 0.017, 0.016), NEZ, mat=RT @ A.repere((0.0, -0.250, 0.010)), poil=False)
    a.piece("langue", A.boule(1.0, 20, 8).etire(0.020, 0.054, 0.008), LANGUE, mat=RT @ A.repere((0.0, -0.140, -0.030), (-10, 0, 0)), poil=False)
    for k, dx in enumerate((-0.026, -0.009, 0.009, 0.026)):
        dent = O.pointe(0.022, 0.0065, 8)
        a.piece("croc_%d" % k, O.couche(O.teinte(dent, np.array(DENT)), RT @ A.cadre(Vector((dx, -0.150, -0.010)), (0.0, 0.20, -1.0), (0, 1, 0))), None, poil=False)
    # les yeux : ouverts (ils ne se ferment que dans « dort »), deux petits yeux vifs sous le front
    O.paire_yeux(a, "tete", H, (0.52, -0.72, 0.42), 0.0180, decolle=0.003, R=RT)
    for nom, c in (("G", 1), ("D", -1)):                       # de vraies oreilles DROITES en triangle (plus plaquées en arrière) ; l'œil reste sans cercle
        tri = A.decoupe([(-0.046, 0.0), (0.046, 0.0), (0.0, 0.128)], 0.022, 0.008)
        tri.teinte = np.where((tri.v[:, 1] > 0.085)[:, None], np.asarray(SOMBRE), np.asarray(FUMEE))
        a.piece("oreille_" + nom, O.couche(tri, O.plan(RT @ Vector((c * 0.056, 0.030, 0.062)), RT.to_3x3() @ Vector((1.0, 0.0, 0.0)), RT.to_3x3() @ Vector((c * 0.18, 0.04, 1.0)))), None)
    a.tete = H + Vector((0.0, -0.17, 0.14))

    # ----- les jambes : à genoux et jarrets marqués, les chaussettes sombres, les pieds ronds ; la queue pendante, lourde -----
    for sgn, nom in ((1, "G"), (-1, "D")):
        O.jambe(a, "avant_" + nom, (sgn * 0.098, -0.250, 0.500), (sgn * 0.086, -0.292, 0.056), 0.070, FUMEE, bas=SOMBRE, sorte="av", plie=0.045,
                pied_dim=(0.044, 0.082, 0.024), griffes=3)
        O.jambe(a, "arriere_" + nom, (sgn * 0.102, 0.330, 0.520), (sgn * 0.094, 0.375, 0.056), 0.086, FUMEE, bas=SOMBRE, sorte="ar", plie=0.12,
                pied_dim=(0.046, 0.088, 0.024), griffes=3)
    queue = K.tube_peint(A.courbe([(0.0, 0.440, 0.540), (0.0, 0.560, 0.470), (0.0, 0.625, 0.340), (0.0, 0.640, 0.200)], 6),
                         lambda t: 0.054 + 0.028 * math.sin(math.pi * min(t * 1.15, 1.0)) ** 0.8, [(0.80, FUMEE), (1.0, SOMBRE)], 18)
    a.piece("queue", queue, None)
    bout = A.boule(1.0, 18, 9).etire(0.034, 0.034, 0.038)
    a.piece("queue_bout", O.teinte(bout, SOMBRE), None, pos=(0.0, 0.640, 0.190))
    if TOURNE:
        O.tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("loup", styles.style_de("loup"), sys.modules[__name__]), "Loup")
