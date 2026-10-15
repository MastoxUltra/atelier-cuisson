"""La tortue de mer en peluche, troisième dessin : une vieille marine. Une carapace d'une seule pièce, bombée en goutte
(large aux épaules, qui se resserre en pointe vers l'arrière), chocolat, sur laquelle les écailles caramel sont des
plaques plates à six côtés, cousues à plat, qui épousent le dôme : une rangée de cinq au milieu, quatre grandes de chaque
côté ; entre elles, le joint chocolat. Le cou ridé en plis de peau sable, une tête plus petite, haute et fière, le bec
corné bien crochu, les yeux lourds sous des paupières ridées, qui en ont vu d'autres. Une palette avant levée, en pleine
nage ; l'autre en appui ; les deux arrière traînant. Elle a l'air de ramer dans l'air du lagon, sans se presser.

    python tortue_de_mer.py        fabrique la fiche art/apercus/animaux/tortue_de_mer.png (style du palier : B, peluche de magasin)
    (refusés le 15/10 : « un galet avec quatre palettes », puis « des petits pains posés sur la carapace »)
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

CARAMEL = np.array(M.hexa("#cf9450"))         # la dominante (registre : carapace caramel) ; le style B adoucit
ECAILLE = np.array(M.hexa("#7a4a24"))         # le joint chocolat : le fond de la carapace
SABLE = np.array(M.hexa("#ecd0a0"))           # la peau
BEC = M.hexa("#8a6a44")
FIL = M.hexa("#5a3a22")

DOME = [(0.0, 0.315), (0.14, 0.300), (0.26, 0.250), (0.34, 0.180), (0.37, 0.100), (0.33, 0.035), (0.22, 0.0)]      # (rayon, hauteur)
CENTRE = Vector((0.0, 0.05, 0.12))


def goutte(v):
    """Le dôme tourné devient une goutte : large aux épaules (devant), resserré et allongé vers l'arrière."""
    s = v.copy()
    s[:, 0] *= 0.90
    s[:, 1] *= 1.12
    arriere = np.clip(v[:, 1] / 0.40, 0.0, 1.0)
    s[:, 0] *= 1 - 0.42 * arriere ** 1.4
    s[:, 1] += 0.10 * arriere ** 2
    return s


def hexagone(r0):
    """Une ouverture polygonale (six côtés) pour une rustine : le rayon d'un hexagone de rayon inscrit r0, selon l'angle."""
    return lambda th: r0 / max(math.cos((th % (math.pi / 3)) - math.pi / 6), 0.5)


def palette(long, large, courbe=0.0, epais=0.034):
    """Une palette : un fuseau tourné aplati, plus large au milieu, sable ; elle peut se courber."""
    m = A.tour(A.profil([(0, 0), (0.50 * large, 0.10 * long), (large, 0.40 * long), (0.74 * large, 0.78 * long), (0, long)], 4), 24)
    m.etire(epais / large, 1.0, 1.0)
    m = m.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] + courbe * long * (v[:, 2] / long) ** 2, v[:, 2]], axis=1))
    m.teinte = np.tile(SABLE, (len(m.v), 1))
    return m


def construire():
    a = K.Animal("tortue_de_mer")
    a.taille = 1.40

    # ----- la carapace : UNE pièce bombée en goutte, chocolat ; le plastron dessous, sable -----
    prof = A.profil([(r, z) for r, z in DOME][::-1], 6)
    carapace = A.tour(prof, 60)
    carapace.teinte = np.tile(ECAILLE, (len(carapace.v), 1))
    a.piece("carapace", carapace.sculpte(goutte), None, pos=tuple(CENTRE))
    a.piece("plastron", A.boule(1.0, 40, 20).sculpte(goutte).etire(0.30, 0.40, 0.055), tuple(SABLE), pos=tuple(CENTRE + Vector((0, 0, -0.005))))

    # ----- les écailles : des rustines à six côtés qui épousent le dôme (vues depuis un point au centre de la carapace) ;
    #       cinq au milieu, quatre grandes de chaque côté, la dernière paire plus petite -----
    c0 = CENTRE + Vector((0.0, 0.04, 0.130))
    k = 0
    plan = [((0.0, y), 0.40) for y in (-0.38, -0.19, 0.0, 0.19, 0.38)]                       # (x, y) sur le dôme ; ouverture en radians
    for c in (1, -1):
        plan += [((c * 0.25, y), 0.36) for y in (-0.28, -0.09, 0.10, 0.29)]

    def dessus(x, y):                                                       # la hauteur du dôme (goutte comprise) au point (x, y)
        yy = (y - 0.05) / 1.12
        arr = max(0.0, min(1.0, yy / 0.40))
        xx = x / (0.90 * (1 - 0.42 * arr ** 1.4))
        r = math.hypot(xx, yy)
        return 0.12 + (float(np.interp(r, [p[0] for p in DOME][::-1], [p[1] for p in DOME][::-1])) if r <= 0.37 else 0.0)
    for (x, y), ouv in plan:
        cible = Vector((x, 0.05 + y, dessus(x, 0.05 + y)))
        axe = (cible - c0).normalized()
        a.rustine("ecaille_%d" % k, "carapace", c0, axe, hexagone(ouv), tuple(CARAMEL * (0.96 + 0.05 * ((k * 5) % 3))), 0.006, 0)
        k += 1

    # ----- le cou ridé, la tête plus petite en bec, haute et tournée ; les yeux lourds -----
    cou = O.tube_r([(0.0, -0.30, 0.24), (0.0, -0.44, 0.32), (0.04, -0.54, 0.44), (0.08, -0.60, 0.52)], [0.100, 0.086, 0.076, 0.070], 22)
    cou.teinte = np.tile(SABLE, (len(cou.v), 1))
    a.piece("cou", cou, None)
    for j, (y, z, r) in enumerate(((-0.44, 0.33, 0.092), (-0.52, 0.41, 0.082))):                                         # les plis de peau
        a.piece("pli_%d" % j, A.tore(r, 0.0095, 28, 6), tuple(SABLE * 0.78), pos=(0.012 * j, y, z), rot=(52, 0, 0), poil=False)
    H = Vector((0.09, -0.65, 0.58))
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.tile(SABLE, (len(tete.v), 1))
    RT = A.repere(H, (-10, 0, 20))
    a.piece("tete", tete.etire(0.088, 0.115, 0.082), None, mat=RT)
    bec = A.tour(A.profil([(0.058, 0), (0.054, 0.026), (0.042, 0.052), (0.025, 0.074), (0.007, 0.088), (0, 0.093)], 4), 28).etire(1.0, 0.72, 1.0)
    bec = bec.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] - 0.036 * (v[:, 2] / 0.093) ** 3, v[:, 2]], axis=1))
    a.piece("bec", bec, BEC, mat=RT @ A.cadre(Vector((0.0, -0.098, -0.020)), (0.0, -1.0, -0.10), (0, 1, 0)), poil=False)
    O.paire_yeux(a, "tete", H, (0.88, -0.38, 0.30), 0.0240, couleur_lourde=tuple(SABLE * 0.92), coupe=-0.10, decolle=0.003)
    O.broder(a, "gueule", "tete", H, [(0.50 * u_ + 0.10, -0.90, -0.40 + 0.12 * u_ * u_) for u_ in np.linspace(-1, 1, 9)], 0.0035, FIL, decolle=0.003)
    a.tete = H + Vector((0.0, -0.12, 0.0))

    # ----- les palettes : l'avant gauche levée en pleine nage, l'avant droite en appui ; les deux arrière traînent -----
    g = palette(0.66, 0.150, courbe=-0.16)
    a.piece("palette_avant_G", O.couche(g, A.cadre((0.30, -0.12, 0.26), (0.84, -0.32, 0.46), (0, 0, 1))), None, poil=False)
    d = palette(0.52, 0.140, courbe=0.10)
    a.piece("palette_avant_D", O.couche(d, A.cadre((-0.30, -0.14, 0.18), (-0.90, -0.10, -0.06), (0, 0, 1))), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        ar = palette(0.30, 0.085)
        a.piece("palette_arriere_" + nom, O.couche(ar, A.cadre((c * 0.18, 0.40, 0.17), (c * 0.50, 0.85, -0.05), (0, 0, 1))), None, poil=False)
    queue = A.tour(A.profil([(0.040, 0), (0.026, 0.050), (0.010, 0.095), (0, 0.110)], 4), 14)
    queue.teinte = np.tile(SABLE, (len(queue.v), 1))
    a.piece("queue", O.couche(queue, A.cadre((0.0, 0.54, 0.15), (0.0, 1.0, -0.12), (0, 0, 1))), None, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tortue_de_mer", styles.style_de("tortue_de_mer"), sys.modules[__name__]), "Tortue de mer")
