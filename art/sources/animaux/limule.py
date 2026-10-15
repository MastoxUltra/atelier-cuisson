"""La limule en peluche, deuxième dessin : étrange et ancienne. Un casque en fer à cheval, lisse et bombé comme un
bouclier, bronze patiné de vert-de-gris sur le bord, deux rivets noirs sur le dessus pour yeux et deux plus petits au
front ; derrière, la plaque de l'abdomen à six pointes de chaque côté et une arête de piquants ; et le telson, un long
sabre charbon, droit, qui part vers l'arrière et vers le haut. Pas de visage, pas de sourire : elle n'a pas changé
depuis quatre cents millions d'années et ne compte pas commencer. Elle avance un coin du casque levé, sur de
petites pattes serrées sous le bord.

    python limule.py        fabrique la fiche art/apercus/animaux/limule.png (style du palier : C, velours ras)
    (le premier dessin, refusé le 15/10 : « un petit animal mignon à deux yeux »)
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

BRONZE = np.array(M.hexa("#a8864c"))          # la dominante (registre : bronze vert-de-gris) ; un peu clair, le velours
PATINE = np.array(M.hexa("#6f9a87"))          # le vert-de-gris des bords (jamais un vert franc)
CHARBON = np.array(M.hexa("#26272b"))         # l'accent : le telson, les rivets
SOMBRE = np.array(M.hexa("#7d6034"))          # les arêtes, un ton plus foncé


def construire():
    a = K.Animal("limule")
    a.taille = 0.66
    T = A.repere((0.0, 0.0, 0.0), (0, 0, 18))        # elle avance de biais : un coin du casque levé (la fiche ; 0 pour le jeu)

    # ----- le casque : un dôme lisse bombé en fer à cheval ; le bord arrière en échancrure, deux pointes aux coins -----
    pc = A.profil([(0.0, 0.0), (0.150, 0.0), (0.205, 0.006), (0.222, 0.020), (0.205, 0.050), (0.170, 0.095), (0.120, 0.135), (0.060, 0.155), (0, 0.162)], 6)
    casque = A.tour(pc, 64)
    r_ = np.hypot(casque.v[:, 0], casque.v[:, 1]) / 0.222
    bord = np.clip((r_ - 0.70) / 0.26, 0.0, 1.0)[:, None]
    casque.teinte = BRONZE * (1 - bord) + PATINE * bord

    def fer_a_cheval(v):
        s = v.copy()
        y = v[:, 1]
        x = v[:, 0]
        arriere = y > 0.0
        s[arriere, 1] = (y * 0.55 - 0.045 * np.exp(-(x / 0.115) ** 2))[arriere]          # le bord arrière : une échancrure au milieu
        s[:, 1] -= 0.020 * (y < 0) * np.clip(-y / 0.22, 0, 1)                            # le front avance un peu
        return s
    casque = casque.sculpte(fer_a_cheval)
    a.piece("casque", casque, None, mat=T @ A.repere((0.0, -0.060, 0.034), (-6, 0, 0)))
    RC = T @ A.repere((0.0, -0.060, 0.034), (-6, 0, 0))
    for c in (1, -1):                                                           # les pointes aux coins arrière du casque
        pointe = O.pointe(0.080, 0.022, 10)
        a.piece("genale_" + ("G" if c > 0 else "D"), O.couche(O.teinte(pointe, SOMBRE), T @ A.cadre(Vector((c * 0.200, 0.030, 0.048)), (c * 0.55, 1.0, -0.05), (0, 0, 1))),
                None, poil=False)

    # ----- les arêtes du dôme : une médiane et deux latérales, basses, d'un bout à l'autre ; les rivets-yeux -----
    for k, x0 in enumerate((0.0, -0.085, 0.085)):
        pts = [tuple(RC @ Vector((x0 * (0.4 + 0.6 * f), -0.130 + 0.250 * f, 0.150 - 0.060 * f - 0.050 * abs(x0) * 4 * f))) for f in np.linspace(0, 1, 7)]
        a.piece("arete_%d" % k, O.teinte(O.tube_r(pts, [0.009, 0.0125, 0.0135, 0.0135, 0.0125, 0.0105, 0.0080], 12), SOMBRE), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        pos = RC @ Vector((c * 0.092, -0.030, 0.147))
        riv = A.boule(1.0, 20, 10).etire(0.0125, 0.0160, 0.0085)
        a.piece("rivet_" + nom, O.teinte(riv, CHARBON), None, mat=A.cadre(pos, RC.to_3x3() @ Vector((c * 0.25, -0.1, 1.0)), (0, 1, 0)), poil=False)
    for nom, c in (("g", 1), ("d", -1)):
        pos = RC @ Vector((c * 0.018, -0.120, 0.150))
        riv = A.boule(1.0, 14, 8).etire(0.0062, 0.0062, 0.0042)
        a.piece("point_" + nom, O.teinte(riv, CHARBON), None, pos=tuple(pos), poil=False)
    a.tete = Vector(RC @ Vector((0.0, -0.160, 0.130)))

    # ----- l'abdomen : une plaque en hexagone derrière le casque, six pointes par côté, une arête de piquants -----
    def hexa(v):
        s = K.emousse(v, 0.70)
        s[:, 2] = np.maximum(s[:, 2], -0.20)
        return s
    ab = A.boule(1.0, 48, 24).sculpte(hexa).etire(0.150, 0.155, 0.056)
    ab.teinte = np.tile(BRONZE * 0.95, (len(ab.v), 1))
    a.piece("abdomen", ab, None, mat=T @ A.repere((0.0, 0.200, 0.040)))
    epines = None
    for c in (1, -1):
        for k in range(6):
            y = 0.120 + 0.050 * k
            x = 0.145 - 0.010 * abs(k - 2.5) / 2.5
            d = Vector((c * 1.0, 0.45, 0.05)).normalized()
            m = O.couche(O.pointe(0.052, 0.0135, 8), A.cadre(Vector((c * x, y, 0.040)), d, (0, 0, 1)))
            epines = m if epines is None else epines + m
    a.piece("epines", O.teinte(O.couche(epines, T), SOMBRE), None, poil=False)
    dos = None
    for k in range(6):
        y = 0.125 + 0.048 * k
        m = O.couche(O.pointe(0.034 - 0.003 * k, 0.0105, 8), A.cadre(Vector((0.0, y, 0.088 - 0.002 * k)), (0.0, 0.2, 1.0), (0, 1, 0)))
        dos = m if dos is None else dos + m
    a.piece("piquants", O.teinte(O.couche(dos, T), SOMBRE), None, poil=False)

    # ----- le telson : un long sabre charbon, droit, qui part vers l'arrière et vers le haut, un peu relevé au bout -----
    telson = A.tour(A.profil([(0.034, 0), (0.030, 0.100), (0.024, 0.250), (0.016, 0.400), (0.008, 0.510), (0, 0.560)], 4), 3 * 8)
    telson.teinte = np.tile(CHARBON, (len(telson.v), 1))
    a.piece("telson", O.couche(telson, T @ A.cadre(Vector((0.0, 0.340, 0.040)), (0.0, 1.0, 0.34), (0, 0, 1))), None, poil=False)

    # ----- les pattes : cinq paires de petits boudins serrés sous le bord du casque, à demi cachés ; la première tend le coin -----
    for c in (1, -1):
        for k, (x, y, dx, dy) in enumerate(((0.100, -0.140, 0.040, -0.050), (0.165, -0.085, 0.036, -0.016), (0.185, -0.020, 0.032, 0.010),
                                            (0.170, 0.050, 0.030, 0.034), (0.130, 0.120, 0.024, 0.050))):
            long_ = 1.7 if (c == 1 and k == 0) else 1.0
            p = O.tube_r([(c * x, y, 0.020), (c * (x + 0.6 * dx * long_), y + 0.6 * dy * long_, 0.014), (c * (x + dx * long_), y + dy * long_, 0.006)],
                         [0.0135, 0.0125, 0.0100], 10)
            pts = [tuple(T @ Vector(q)) for q in [(c * x, y, 0.020), (c * (x + 0.6 * dx * long_), y + 0.6 * dy * long_, 0.014), (c * (x + dx * long_), y + dy * long_, 0.006)]]
            a.piece("patte_%s%d" % ("G" if c > 0 else "D", k), O.teinte(O.tube_r(pts, [0.0135, 0.0125, 0.0100], 10), PATINE * 0.9), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("limule", styles.style_de("limule"), sys.modules[__name__]), "Limule")
