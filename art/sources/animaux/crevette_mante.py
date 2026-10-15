"""La crevette-mante en peluche, deuxième dessin, d'après les photos du paon de mer (Odontodactylus scyllarus) : le boxeur du
récif, une VRAIE crevette (un long corps arqué en six anneaux, la carapace en bouclier devant, l'éventail de la queue à
piquants), turquoise vif ; deux gros yeux montés sur des tiges, chacun de son côté, qui regardent tout ; deux longues
antennes ; et les deux poings orange, hérissés de piquants, repliés sous le menton en garde haute, comme ceux d'une mante.
Accroupie sur ses petites pattes, prête à cogner.

    python crevette_mante.py        fabrique la fiche art/apercus/animaux/crevette_mante.png (style du palier : C, velours ras)
    (le premier dessin, jugé le 15/10 : « on ne lit pas l'animal, on dirait deux têtes bleues »)
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

TURQUOISE = np.array(M.hexa("#22b8b0"))       # la dominante (registre : turquoise)
SOMBRE = np.array(M.hexa("#157f86"))          # les arêtes des anneaux, la queue
ORANGE = np.array(M.hexa("#f2862a"))          # l'accent : les poings, les pattes
CLAIR = np.array(M.hexa("#7fdcd2"))           # le ventre, les yeux
VERT = np.array(M.hexa("#3bbf6a"))            # les yeux : le vert du paon de mer
FIL = M.hexa("#1a2e33")

# de la queue à la tête : l'abdomen à plat, le corselet qui se relève
CHEMIN = [(0.0, 0.44, 0.050), (0.0, 0.32, 0.066), (0.0, 0.18, 0.078), (0.0, 0.04, 0.092), (0.0, -0.08, 0.112), (0.0, -0.16, 0.140)]
NANNEAUX = 6


def rayon(f):
    base = O.interp([(0.0, 0.0), (0.02, 0.030), (0.12, 0.048), (0.40, 0.064), (0.62, 0.070), (0.80, 0.076), (0.93, 0.062), (0.985, 0.036), (1.0, 0.0)])(f)
    ann = 1.0 + 0.10 * math.cos(2.0 * math.pi * NANNEAUX * f / 0.66) * (1.0 if f < 0.66 else 0.0)
    return base * ann


def construire():
    a = K.Animal("crevette_mante")
    a.taille = 0.52

    # ----- le corps : un long fuseau arqué, six anneaux qui s'emboîtent (le rayon onde, les gorges plus sombres) ; le ventre clair -----
    def peint(m, L):
        f = m.v[:, 2] / L
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(TURQUOISE, (len(f), 1))
        t[(f < 0.66) & (np.cos(2.0 * math.pi * NANNEAUX * f / 0.66) < -0.80)] = SOMBRE
        t[ang > 2.2] = CLAIR
        t[(f > 0.66) & (f < 0.90) & (ang < 0.5)] = TURQUOISE * 1.08
        return t
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=36, flanc=(1.0, 0.0, 0.0))

    # ----- la carapace en bouclier : une cape plate sur le corselet, deux carènes ; le rostre -----
    cc, ac, nc = (Vector(q) for q in fil.cadre(0.80 * L))
    bouclier = A.boule(1.0, 36, 18).sculpte(lambda v: np.stack([v[:, 0], v[:, 1], np.where(v[:, 2] < 0, v[:, 2] * 0.25, v[:, 2])], axis=1))
    bouclier.teinte = np.tile(TURQUOISE * 1.04, (len(bouclier.v), 1))
    a.piece("bouclier", bouclier.etire(0.088, 0.115, 0.050), None, pos=tuple(cc + Vector((0.0, 0.0, 0.020))))
    rostre = O.couche(O.teinte(O.pointe(0.060, 0.022, 8), SOMBRE), A.cadre(cc + Vector((0.0, -0.100, 0.060)), Vector((0.0, -1.0, 0.25)), (0, 0, 1)))
    a.piece("rostre", rostre, None, poil=False)

    # ----- les yeux : deux tiges qui s'écartent, deux gros globes verts barrés de rouge, la pupille ; les antennes -----
    tete_c, at, nt = (Vector(q) for q in fil.cadre(0.985 * L))
    for nom, c in (("G", 1), ("D", -1)):
        tige = O.tube_r([tuple(tete_c + Vector((c * 0.020, 0.010, 0.030))), tuple(tete_c + Vector((c * 0.050, -0.030, 0.085))),
                         tuple(tete_c + Vector((c * 0.070, -0.050, 0.120)))], [0.014, 0.012, 0.011], 10)
        a.piece("tige_" + nom, O.teinte(tige, CLAIR), None, poil=False)
        globe = A.boule(1.0, 24, 12).etire(0.034, 0.030, 0.040)
        tg = np.tile(VERT, (len(globe.v), 1))
        tg[np.abs(globe.v[:, 2]) < 0.006] = np.array(M.hexa("#e03a2a"))                  # la bande rouge de l'œil
        globe.teinte = tg
        a.piece("globe_" + nom, globe, None, pos=tuple(tete_c + Vector((c * 0.075, -0.056, 0.135))), poil=False)
        a.oeil("oeil_" + nom, tete_c + Vector((c * 0.092, -0.080, 0.140)), Vector((c * 0.60, -0.70, 0.20)).normalized(), 0.016)
        ant = O.tube_r([tuple(tete_c + Vector((c * 0.020, -0.050, 0.035))), tuple(tete_c + Vector((c * 0.080, -0.150, 0.090))),
                        tuple(tete_c + Vector((c * 0.170, -0.230, 0.050)))], [0.006, 0.0045, 0.0030], 8)
        a.piece("antenne_" + nom, O.teinte(ant, ORANGE), None, poil=False)
    a.tete = tete_c + Vector((0.0, -0.12, 0.08))

    # ----- les deux poings repliés en garde haute : le bras, le coude, la massue orange hérissée de piquants ; six pattes -----
    for nom, c in (("G", 1), ("D", -1)):
        bras = O.tube_r([tuple(tete_c + Vector((c * 0.055, -0.020, -0.050))), tuple(tete_c + Vector((c * 0.090, -0.100, -0.040))),
                         tuple(tete_c + Vector((c * 0.060, -0.150, 0.010))), tuple(tete_c + Vector((c * 0.030, -0.095, 0.045)))],
                        [0.020, 0.018, 0.020, 0.024], 12)
        a.piece("bras_" + nom, O.teinte(bras, ORANGE), None, poil=False)
        poing = A.boule(1.0, 24, 12).etire(0.030, 0.050, 0.030)
        a.piece("poing_" + nom, O.teinte(poing, ORANGE * 0.96), None, pos=tuple(tete_c + Vector((c * 0.030, -0.100, 0.050))), rot=(-30, 0, c * 10), poil=False)
        piques = None
        for k in range(5):
            u = k / 4
            p = tete_c + Vector((c * 0.030, -0.100 + 0.050 * (u - 0.5) - 0.010, 0.050 + 0.030))
            d = O.couche(O.teinte(O.pointe(0.034, 0.0080, 6), ORANGE * 0.80),
                         A.cadre(p + Vector((0.0, -0.040 * (u - 0.5), 0.0)), Vector((c * 0.25, -0.50 + 0.60 * (u - 0.5), 0.80)), (0, 1, 0)))
            piques = d if piques is None else piques + d
        a.piece("piques_" + nom, piques, None, poil=False)
        for k in range(3):
            y = 0.10 - 0.075 * k
            pts = [(c * 0.060, y, 0.070), (c * (0.130 + 0.010 * k), y - 0.030, 0.085), (c * (0.170 + 0.014 * k), y - 0.050, 0.008)]
            m = O.tube_r(pts, [0.011, 0.009, 0.006], 10)
            a.piece("patte_%s%d" % (nom, k), O.teinte(m, ORANGE), None, poil=False)

    # ----- l'éventail de la queue : un telson central et deux uropodes de chaque côté, hérissés de piquants -----
    c0, a0, n0 = (Vector(q) for q in fil.cadre(0.0))
    ev = None
    for k, ang in enumerate((-60, -30, 0, 30, 60)):
        r = math.radians(ang)
        long = 0.150 if abs(ang) < 40 else 0.120
        pts = [(0.0, 0.0), (0.040, 0.030), (0.036, long * 0.7), (0.0, long), (-0.036, long * 0.7), (-0.040, 0.030)]
        f = A.decoupe(pts, 0.010, 0.004)
        f.teinte = np.tile(SOMBRE if k % 2 == 0 else TURQUOISE, (len(f.v), 1))
        f = O.couche(f, O.plan(c0 + Vector((0.0, -0.005, 0.0)), Vector((math.cos(r), -math.sin(r), 0.0)), Vector((math.sin(r), math.cos(r), 0.0))))
        ev = f if ev is None else ev + f
    a.piece("eventail", ev, None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("crevette_mante", styles.style_de("crevette_mante"), sys.modules[__name__]), "Crevette-mante")
