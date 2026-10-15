"""La seiche en peluche, deuxième dessin, d'après les photos de Sepia officinalis : un manteau long, plat et ovale comme une
semelle, zébré de crème sur le taupe, bordé tout du long par la frange ondulante des nageoires ; devant, la tête étroite, deux
gros yeux sur les côtés, chacun cerclé d'un iris pâle où la pupille en W se lit d'un coup, et le bouquet des huit bras courts
qui retombent comme une barbe, entre lesquels deux longs tentacules sortent, tendus vers l'avant, une massue au bout. Elle
flotte à ras du sable, immobile : on la prendrait pour un caillou rayé si elle ne vous regardait pas.

    python seiche.py        fabrique la fiche art/apercus/animaux/seiche.png (style du palier : voir styles.py)
    (le premier dessin, jugé le 15/10 : « on dirait un scarabée à yeux »)
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

TAUPE = np.array(M.hexa("#8c7a72"))           # la dominante (registre : taupe zébré de crème #8c7a72)
ZEBRE = np.array(M.hexa("#e9dccb"))           # les zébrures crème
OMBRE = np.array(M.hexa("#5d4b46"))           # le dessus de la tête, le bout des bras
IRIS = np.array(M.hexa("#d9c9a2"))            # l'iris pâle qui entoure la pupille
FIL = M.hexa("#2a1f1c")


def construire():
    a = K.Animal("seiche")
    a.taille = 0.70

    # ----- le manteau : une semelle ovale, plus large devant, qui s'effile derrière ; le dessous plat ; des zébrures en travers,
    #       la ligne du dos plus sombre -----
    def semelle(v):
        s = v.copy()
        z = v[:, 2]
        y = v[:, 1]
        s[:, 2] = np.where(z < 0, z * 0.30, z)                                    # le dessous presque plat
        arriere = np.clip(y / 0.40, 0.0, 1.0)
        s[:, 0] *= 1.0 - 0.55 * arriere ** 1.5                                   # le bout arrière s'effile
        return s
    manteau = A.boule(1.0, 64, 32).sculpte(semelle).etire(0.190, 0.430, 0.085)
    yv, xv, zv = manteau.v[:, 1], manteau.v[:, 0], manteau.v[:, 2]
    t = np.tile(TAUPE, (len(yv), 1))
    zeb = (np.sin(yv * 36.0 + 1.2 * np.abs(xv) * 9.0) > 0.30) & (zv > 0.0)
    t[zeb] = ZEBRE * 0.90 + TAUPE * 0.10
    t[(np.abs(xv) < 0.016) & (zv > 0.0)] = OMBRE                                  # la ligne du dos
    manteau.teinte = t
    a.piece("manteau", manteau, None, pos=(0.0, 0.140, 0.085))

    # ----- la frange des nageoires : un ruban ondulé qui court tout le long du manteau, des deux côtés, plus clair -----
    pts = []
    n = 70
    for k in range(n + 1):
        th = math.tau * k / n
        x = 0.215 * math.cos(th) * (1.0 - 0.45 * max(0.0, math.sin(th)) ** 1.5)
        y = 0.140 + 0.440 * math.sin(th)
        pts.append((x, y - 0.140, 0.012 * math.sin(th * 14.0)))
    frange = A.tube(A.courbe(pts, 2), 0.020, 8).etire(1.0, 1.0, 0.45).pose((0.0, 0.140, 0.062))
    frange.teinte = np.tile(ZEBRE * 0.72 + TAUPE * 0.28, (len(frange.v), 1))
    a.piece("frange", frange, None, poil=False)

    # ----- la tête : étroite, dans le prolongement ; les yeux sur les côtés, iris pâle ; la bouche cachée sous les bras -----
    tete = A.boule(1.0, 40, 20).etire(0.120, 0.110, 0.078)
    tete.teinte = np.tile(OMBRE * 0.7 + TAUPE * 0.3, (len(tete.v), 1))
    a.piece("tete", tete, None, pos=(0.0, -0.250, 0.098))
    centre = Vector((0.0, -0.250, 0.098))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n_ = a.surface("tete", centre, Vector((c * 0.95, -0.22, 0.15)))
        iris = A.boule(1.0, 24, 12).etire(0.042, 0.042, 0.011)
        a.piece("iris_" + nom, O.couche(O.teinte(iris, IRIS), A.cadre(pos + n_ * 0.001, n_, (0, 0, 1))), None, poil=False)
        a.oeil("oeil_" + nom, pos + n_ * 0.009, n_, 0.026)
        haut_oeil = (Vector((0, 0, 1)) - n_ * n_.z).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.044, 0.05), tuple(OMBRE * 0.7 + TAUPE * 0.3), mat=A.cadre(pos + n_ * 0.003, n_, haut_oeil), poil=False)
    a.tete = centre + Vector((0.0, -0.12, 0.0))

    # ----- les huit bras courts : en bouquet devant la tête, retombant en barbe, les bouts qui se recourbent ; le bout sombre -----
    for k in range(8):
        th = math.radians(-77 + 22 * k)
        base = (0.060 * math.sin(th), -0.330, 0.100 + 0.030 * math.cos(th) - 0.040)
        pts = [base,
               (0.100 * math.sin(th), -0.395, 0.062 + 0.010 * math.cos(th)),
               (0.140 * math.sin(th), -0.445, 0.034),
               (0.170 * math.sin(th) * 1.05, -0.480, 0.020 + (0.026 if k % 2 else 0.0))]
        bras = K.tube_peint(A.courbe(pts, 5), lambda t_: 0.036 - 0.024 * t_, [(0.7, TAUPE), (1.0, OMBRE)], 12)
        a.piece("bras_%d" % k, bras, None)

    # ----- les deux tentacules : longs, tendus vers l'avant et un peu vers le haut, une massue crème au bout ; ils sortent d'entre les bras -----
    for nom, c in (("G", 1), ("D", -1)):
        pts = [(c * 0.030, -0.335, 0.100), (c * 0.075, -0.440, 0.120), (c * 0.115, -0.560, 0.150), (c * 0.135, -0.680, 0.160),
               (c * 0.130, -0.760, 0.150)]
        a.piece("tentacule_" + nom, K.tube_peint(A.courbe(pts, 5), lambda t_: 0.016 - 0.005 * t_, [(1.0, TAUPE)], 10), None)
        massue = A.boule(1.0, 18, 10).etire(0.026, 0.050, 0.020)
        massue.teinte = np.tile(ZEBRE * 0.82 + TAUPE * 0.18, (len(massue.v), 1))
        a.piece("massue_" + nom, massue, None, pos=(c * 0.128, -0.780, 0.146), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "bras", noms_bras=("bras_", "tentacule_"))


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("seiche", styles.style_de("seiche"), sys.modules[__name__]), "Seiche")
