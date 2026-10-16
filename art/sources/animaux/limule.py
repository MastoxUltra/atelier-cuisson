"""La limule en peluche, deuxième dessin : étrange et ancienne. Un casque en fer à cheval, bas et lisse comme un
bouclier, le large bord évasé patiné de vert-de-gris, deux grands yeux noirs en haricot sur les côtés et deux petits
points au front ; derrière, la plaque de l'abdomen à six pointes de chaque côté et une arête de piquants ; et le telson, un long
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
    a.taille = 1.00
    T = A.repere((0.0, 0.0, 0.0), (0, 0, 18))        # elle avance de biais : un coin du casque levé (la fiche ; 0 pour le jeu)

    # ----- le casque : un dôme lisse bombé en fer à cheval ; le bord arrière en échancrure, deux pointes aux coins -----
    pc = A.profil([(0.0, 0.0), (0.150, 0.0), (0.228, 0.002), (0.252, 0.014), (0.234, 0.030), (0.198, 0.060), (0.150, 0.094), (0.100, 0.120),
                   (0.050, 0.136), (0, 0.141)], 6)
    casque = A.tour(pc, 64)
    r_ = np.hypot(casque.v[:, 0], casque.v[:, 1]) / 0.252
    bord = np.clip((r_ - 0.62) / 0.30, 0.0, 1.0)[:, None]
    casque.teinte = BRONZE * (1 - bord) + PATINE * bord

    def fer_a_cheval(v):
        s = v.copy()
        y = v[:, 1]
        x = v[:, 0]
        arriere = y > 0.0
        s[arriere, 1] = (y * 0.55 - 0.045 * np.exp(-(x / 0.115) ** 2))[arriere]          # le bord arrière : une échancrure au milieu
        s[:, 1] -= 0.020 * (y < 0) * np.clip(-y / 0.25, 0, 1)                            # le front avance un peu
        return s
    casque = casque.sculpte(fer_a_cheval)
    a.piece("casque", casque, None, mat=T @ A.repere((0.0, -0.060, 0.034), (-6, 0, 0)))
    RC = T @ A.repere((0.0, -0.060, 0.034), (-6, 0, 0))
    for c in (1, -1):                                                           # les pointes aux coins arrière du casque
        pointe = O.pointe(0.080, 0.022, 10)
        a.piece("genale_" + ("G" if c > 0 else "D"), O.couche(O.teinte(pointe, SOMBRE), T @ A.cadre(Vector((c * 0.215, 0.040, 0.026)), (c * 0.55, 1.0, -0.02), (0, 0, 1))),
                None, poil=False)

    # ----- les arêtes du dôme : une médiane et deux latérales, basses, posées sur la peau du casque ; les yeux : deux grands, sur
    #       les CÔTÉS, en haricot, et deux petits points serrés près du front -----
    haut_ = (RC.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()

    def sur_casque(x, y):
        p_, n_ = a.surface("casque", RC @ Vector((x, y, 0.010)), haut_)
        return p_, n_
    for k, x0 in enumerate((0.0, -0.085, 0.085)):
        pts = []
        for f in np.linspace(0.0, 1.0, 9):
            p_, n_ = sur_casque(x0 * (0.5 + 0.5 * f), -0.120 + 0.190 * f)
            pts.append(tuple(p_ + n_ * 0.002))
        a.piece("arete_%d" % k, O.teinte(O.tube_r(pts, [0.008, 0.011, 0.0125, 0.0125, 0.0120, 0.0115, 0.0105, 0.0095, 0.0080], 12), SOMBRE), None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        pos, n_ = a.surface("casque", RC @ Vector((0.0, -0.030, 0.030)), RC.to_3x3() @ Vector((c * 0.70, -0.70, 0.40)))
        a.oeil("oeil_" + nom, pos + n_ * 0.003, n_, 0.0330)                          # de vrais yeux noirs et brillants, plus des bosses grises
    for nom, c in (("g", 1), ("d", -1)):
        pos, n_ = sur_casque(c * 0.020, -0.135)
        riv = A.boule(1.0, 14, 8).etire(0.0062, 0.0062, 0.0042)
        a.piece("point_" + nom, O.teinte(riv, CHARBON), None, mat=A.cadre(pos + n_ * 0.001, n_, (0, 1, 0)), poil=False)
    a.tete = Vector(RC @ Vector((0.0, -0.160, 0.090)))

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
    telson = A.tour(A.profil([(0.026, 0), (0.023, 0.100), (0.018, 0.250), (0.012, 0.400), (0.006, 0.520), (0, 0.580)], 4), 3 * 8)
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
