"""La seiche en peluche, deuxième dessin, d'après les photos de Sepia officinalis : un manteau long, plat et ovale comme une
semelle, zébré de crème sur le taupe, bordé tout du long par la frange ondulante des nageoires ; devant, la tête étroite, deux
gros yeux sur les côtés, chacun cerclé d'un iris pâle où la pupille en W se lit d'un coup, et le bouquet des huit bras courts
qui retombent comme une barbe, entre lesquels deux longs tentacules sortent, tendus vers l'avant, une massue au bout. Elle
flotte à ras du sable, immobile : on la prendrait pour un caillou rayé si elle ne vous regardait pas.

    python seiche.py        fabrique la fiche art/apercus/animaux/seiche.png (style du palier : voir styles.py)
    (le premier dessin, jugé le 15/10 : « on dirait un scarabée à yeux » ; le deuxième, du contrôleur : un escargot à tiges et
    un cloporte rayé — d'où les bras en couronne vers l'avant, les tentacules à palette et la grande nageoire en ruban)
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

    # ----- le manteau : une galette ovale, plus large devant, qui s'effile derrière ; le dessous plat ; des zébrures sinueuses en
    #       travers (jamais des anneaux réguliers : ce serait un cloporte), la ligne du dos plus sombre, des points clairs -----
    def semelle(v):
        s = v.copy()
        z = v[:, 2]
        y = v[:, 1]
        s[:, 2] = np.where(z < 0, z * 0.22, z)                                    # le dessous presque plat
        arriere = np.clip(y / 0.40, 0.0, 1.0)
        s[:, 0] *= 1.0 - 0.55 * arriere ** 1.5                                   # le bout arrière s'effile
        return s
    manteau = A.boule(1.0, 72, 36).sculpte(semelle).etire(0.190, 0.430, 0.068)
    yv, xv, zv = manteau.v[:, 1], manteau.v[:, 0], manteau.v[:, 2]
    t = np.tile(TAUPE, (len(yv), 1))
    onde = yv * 21.0 + 2.6 * np.sin(xv * 17.0 + 0.9) + 1.4 * np.sin(yv * 9.0 - xv * 11.0)
    zeb = (np.sin(onde) > 0.38) & (zv > 0.0)
    t[zeb] = ZEBRE * 0.88 + TAUPE * 0.12
    bord_sombre = (np.sin(onde) > 0.18) & (np.sin(onde) <= 0.38) & (zv > 0.0)
    t[bord_sombre] = OMBRE * 0.55 + TAUPE * 0.45
    t[(np.abs(xv) < 0.014) & (zv > 0.0)] = OMBRE                                  # la ligne du dos
    rng_m = np.random.default_rng(11)
    pts_cl = rng_m.uniform(-1.0, 1.0, (46, 2)) * np.array([0.150, 0.360])
    for px, py in pts_cl:
        t[((xv - px) ** 2 + (yv - py) ** 2 < 0.0004) & (zv > 0.02) & ~zeb] = ZEBRE
    manteau.teinte = t
    a.piece("manteau", manteau, None, pos=(0.0, 0.140, 0.068))

    # ----- la frange : la grande nageoire ondulée, un ruban qui borde le manteau de chaque côté, de la tête jusqu'à la pointe,
    #       plus large au milieu, le bord froncé ; double face ; elle s'éteint devant, derrière la tête -----
    n_f = 90
    pts_f, faces_f = [], []
    th0, th1 = -math.pi / 2 + 0.55, 1.5 * math.pi - 0.55
    for k in range(n_f + 1):
        u = k / n_f
        th = th0 + (th1 - th0) * u
        env = math.sin(math.pi * u) ** 0.55                                         # le ruban naît et meurt devant
        sx = 1.0 - 0.45 * max(0.0, math.sin(th)) ** 1.5
        px = 0.186 * math.cos(th) * sx
        py = 0.435 * math.sin(th)
        nx, ny = math.cos(th) / 0.186, math.sin(th) / 0.435                          # la normale de l'ellipse
        nn = math.hypot(nx, ny)
        nx, ny = nx / nn, ny / nn
        larg = 0.052 * env * (0.80 + 0.20 * math.cos(2.0 * math.sin(th)))
        zf = 0.058 + 0.014 * math.sin(th * 15.0 + 0.8) * env
        pts_f.append((px, py + 0.140, 0.062))                                        # le pied du ruban, collé au manteau
        pts_f.append((px + nx * larg, py + 0.140 + ny * larg, zf))                   # le bord libre, qui ondule
    for k in range(n_f):
        b = 2 * k
        faces_f.append((b, b + 1, b + 3, b + 2))
    Pf = np.array(pts_f)
    nf = len(Pf)
    tous = np.vstack([Pf + np.array([0.0, 0.0, 0.0035]), Pf - np.array([0.0, 0.0, 0.0035])])
    toutes = list(faces_f) + [tuple(q + nf for q in reversed(f)) for f in faces_f]
    frange = A.Maille(tous, toutes)
    frange.teinte = np.tile(ZEBRE * 0.62 + TAUPE * 0.38, (len(tous), 1))
    a.piece("frange", frange, None, poil=False)

    # ----- la tête : large et basse, dans le prolongement ; de gros yeux sur les côtés, iris pâle ; la bouche cachée sous les bras -----
    tete = A.boule(1.0, 40, 20).etire(0.135, 0.115, 0.070)
    tete.teinte = np.tile(OMBRE * 0.7 + TAUPE * 0.3, (len(tete.v), 1))
    a.piece("tete", tete, None, pos=(0.0, -0.248, 0.082))
    centre = Vector((0.0, -0.248, 0.082))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n_ = a.surface("tete", centre, Vector((c * 0.95, -0.22, 0.18)))
        iris = A.boule(1.0, 24, 12).etire(0.056, 0.056, 0.012)
        a.piece("iris_" + nom, O.couche(O.teinte(iris, IRIS), A.cadre(pos + n_ * 0.001, n_, (0, 0, 1))), None, poil=False)
        a.oeil("oeil_" + nom, pos + n_ * 0.010, n_, 0.036)
        haut_oeil = (Vector((0, 0, 1)) - n_ * n_.z).normalized()
        a.piece("lourde_" + nom, K.paupiere(0.058, 0.55), tuple(OMBRE * 0.7 + TAUPE * 0.3), mat=A.cadre(pos + n_ * 0.004, n_, haut_oeil), poil=False)
    a.tete = centre + Vector((0.0, -0.12, 0.0))

    # ----- les huit bras : un bouquet serré qui part vers l'AVANT, en couronne autour de la bouche, épais à la base et qui
    #       s'effilent ; les bouts se recourbent un peu ; le bout sombre -----
    for k in range(8):
        psi = math.tau * (k + 0.5) / 8.0
        sx, cz = math.sin(psi), math.cos(psi)
        base = (0.040 * sx, -0.330, 0.082 + 0.030 * cz)
        pts = [base,
               (0.062 * sx, -0.395, 0.080 + 0.040 * cz),
               (0.088 * sx, -0.460, 0.078 + 0.046 * cz - 0.006),
               (0.108 * sx, -0.520, 0.082 + 0.044 * cz + (0.014 if k % 2 else 0.004))]
        bras = K.tube_peint(A.courbe(pts, 5), lambda t_: 0.034 - 0.026 * t_, [(0.65, TAUPE), (1.0, OMBRE)], 12)
        a.piece("bras_%d" % k, bras, None)

    # (les deux tentacules à palette sont rentrés dans le bouquet de bras : seiche au repos, plus de grosses palettes qui font « deux boules »)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "bras", noms_bras=("bras_", "tentacule_"))


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("seiche", styles.style_de("seiche"), sys.modules[__name__]), "Seiche")
