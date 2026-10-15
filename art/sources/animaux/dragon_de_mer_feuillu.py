"""Le dragon de mer feuillu en peluche : une longue bête de la couleur de l'algue sèche, ocre doré, toute hérissée de
feuilles plates, orange et olive pâle, qui poussent le long du dos, sous le ventre et au bout de la queue : on ne sait
plus où finit l'animal et où commence le varech. Une trompe fine, un œil rond sous une feuille ; sur les flancs, des
ponts bleu ciel, comme des gouttes de mer restées prises. Il se tient posé, la queue en crosse, le cou tendu.

    python dragon_de_mer_feuillu.py        fabrique la fiche art/apercus/animaux/dragon_de_mer_feuillu.png
                                           (style du palier : B, peluche de magasin)
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

OCRE = np.array(M.hexa("#d9a23a"))            # la dominante (registre du 14/10 : ocre doré)
ORANGE = np.array(M.hexa("#e8802f"))          # les feuilles orange
OLIVE = np.array(M.hexa("#c9b96a"))           # les feuilles olive pâle (jamais un vert franc : elles tirent sur le jaune)
CIEL = M.hexa("#8fd0ee")                      # l'accent : les ponts bleu ciel sur les flancs

CHEMIN = [(0.0, -0.58, 0.50), (0.0, -0.42, 0.42), (0.0, -0.20, 0.31), (0.0, 0.06, 0.25), (0.0, 0.34, 0.26),
          (0.0, 0.58, 0.34), (0.0, 0.76, 0.46), (0.0, 0.82, 0.60), (0.0, 0.72, 0.68)]        # le dernier point : la crosse
FIL = K.Fil(CHEMIN, flanc=(-1.0, 0.0, 0.0), pas=10)
L = FIL.long


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def rayon(f):
    """Le rayon du corps à la fraction f : la trompe fine, la tête, le cou pincé, le tronc, puis la queue qui s'effile."""
    pts = [(0.0, 0.0), (0.012, 0.025), (0.016, 0.100), (0.022, 0.150), (0.052, 0.200), (0.062, 0.245), (0.050, 0.300),
           (0.066, 0.380), (0.078, 0.480), (0.070, 0.580), (0.052, 0.700), (0.036, 0.820), (0.022, 0.920), (0.014, 1.0)]
    x = np.array([p[1] for p in pts])
    r = np.array([p[0] for p in pts])
    return float(np.interp(f, x, r))


def feuille(long, large, courbe=0.22):
    """Une feuille plate : un fuseau tourné très aplati sur X, qui se recourbe un peu vers Y ; le pied sur z = 0."""
    m = A.tour(A.profil([(0, 0), (0.50 * large, 0.10 * long), (large, 0.36 * long), (0.78 * large, 0.70 * long),
                         (0.30 * large, 0.92 * long), (0, long)], 4), 14)
    m.etire(0.16, 1.0, 1.0)
    return m.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] + courbe * long * (v[:, 2] / long) ** 2, v[:, 2]], axis=1))


def construire():
    a = K.Animal("dragon_de_mer_feuillu")
    a.taille = 0.62

    # ----- le corps : un seul fuseau tourné, la trompe devant, couché le long du fil ; ocre, un peu plus clair dessous -----
    fs = np.linspace(0.0, 1.0, 140)
    prof = [(0.0, 0.0)] + [(rayon(f), f * L) for f in fs[1:-1]] + [(0.0, L)]
    corps = A.tour(prof, 40)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(OCRE, (len(ang), 1))
    t[ang > 2.1] = OCRE * 1.18
    corps.teinte = t
    a.piece("corps", corps.sculpte(FIL.couche), None)

    # ----- les feuilles : trois rangs (le dos, le ventre, les flancs hauts) qui poussent le long du fil ; orange et olive
    #       alternées, plus grandes au milieu -----
    orange, olive = None, None
    marche = [(0.24, 0.0), (0.30, 1), (0.36, 0.0), (0.42, 1), (0.50, 0.0), (0.58, 1), (0.66, 0.0), (0.74, 1), (0.82, 0.0), (0.90, 1)]
    for k, (f, haut) in enumerate(marche):
        centre, avant, nuque = FIL.cadre(f * L)
        centre, avant, nuque = Vector(centre), Vector(avant), Vector(nuque)
        r = rayon(f)
        grand = 0.115 + 0.090 * math.sin(math.pi * (f - 0.2) / 0.75)
        for rang in ("dos", "ventre"):
            alt = (k + (0 if rang == "dos" else 1)) % 2
            sens = 1.0 if rang == "dos" else -1.0
            dir_ = (nuque * sens * 0.85 + avant * 0.52).normalized()
            pos = centre + nuque * sens * r * 0.88
            m = feuille(grand * (1.0 if rang == "dos" else 0.80), 0.052 + 0.016 * (alt))
            m.teinte = np.tile(ORANGE if alt else OLIVE, (len(m.v), 1))
            m = couche(m, A.cadre(pos, dir_, (0, 0, 1) if abs(dir_.z) < 0.92 else (0, 1, 0)))
            if alt:
                orange = m if orange is None else orange + m
            else:
                olive = m if olive is None else olive + m
    # la crosse : trois petites feuilles au bout de la queue
    for k, f in enumerate((0.93, 0.97, 1.0)):
        centre, avant, nuque = FIL.cadre(f * L)
        m = feuille(0.060 - 0.010 * k, 0.026)
        m.teinte = np.tile(OLIVE if k % 2 else ORANGE, (len(m.v), 1))
        m = couche(m, A.cadre(Vector(centre), (Vector(avant) * 0.4 + Vector(nuque) * 0.9).normalized(), (0, 0, 1)))
        if k % 2:
            olive = m if olive is None else olive + m
        else:
            orange = m if orange is None else orange + m
    # la crête de la tête : une feuille dressée entre les yeux, une autre sous le menton
    for sens, long_, alt in ((1.0, 0.085, 1), (-1.0, 0.060, 0)):
        centre, avant, nuque = FIL.cadre(0.200 * L)
        m = feuille(long_, 0.030)
        m.teinte = np.tile(ORANGE if alt else OLIVE, (len(m.v), 1))
        pos = Vector(centre) + Vector(nuque) * sens * rayon(0.200) * 0.90
        m = couche(m, A.cadre(pos, (Vector(nuque) * sens * 0.8 - Vector(avant) * 0.3).normalized(), (0, 0, 1)))
        if alt:
            orange = m if orange is None else orange + m
        else:
            olive = m if olive is None else olive + m
    a.piece("feuilles_orange", orange, None, poil=False)
    a.piece("feuilles_olive", olive, None, poil=False)

    # ----- les ponts bleu ciel : de petites pastilles plates sur les flancs, comme des gouttes prises -----
    for nom, c in (("G", 1), ("D", -1)):
        pastilles = None
        for f in (0.32, 0.40, 0.48, 0.56, 0.64, 0.72):
            centre, direction = FIL.vise(f * L, 0.0, -c * 1.0, 0.08)
            p, n = a.surface("corps", centre, direction)
            m = A.boule(1.0, 16, 8).etire(0.013, 0.013, 0.004)
            m = couche(m, A.cadre(p + n * 0.001, n))
            pastilles = m if pastilles is None else pastilles + m
        a.piece("ponts_" + nom, pastilles, CIEL, poil=False)

    # ----- l'œil rond sous une feuille : deux billes noires à l'arrière de la trompe -----
    for nom, c in (("G", 1), ("D", -1)):
        centre, direction = FIL.vise(0.205 * L, 0.20, -c * 0.95, 0.25)
        pos, n = a.surface("corps", centre, direction)
        a.bouton("oeil_" + nom, pos + n * 0.002, n, 0.0200)
    a.tete = Vector(FIL.cadre(0.14 * L)[0]) + Vector((0.0, -0.04, 0.03))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules[__name__], "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("dragon_de_mer_feuillu", styles.style_de("dragon_de_mer_feuillu"), sys.modules[__name__]),
              "Dragon de mer feuillu")
