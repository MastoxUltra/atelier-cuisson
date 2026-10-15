"""La raie manta en peluche, deuxième dessin : une vraie raie, en virage. Une seule pièce, du bout d'une aile à l'autre,
la tête en lobes qui avancent, les bouts d'ailes relevés en vagues et filant vers l'arrière ; elle penche de tout le
corps et laisse voir son ventre blanc, les cinq fentes des branchies, la bouche tirée sur toute la largeur du museau,
entre les deux cornes céphaliques, deux palettes déroulées. Noir bleuté dessus, deux croissants blancs sur les épaules,
de petits yeux sages sur le côté des lobes et la longue queue en fouet qui traîne dans le sable.

    python raie_manta.py        fabrique la fiche art/apercus/animaux/raie_manta.png (style du palier : B, peluche de magasin)
    (le premier dessin, refusé le 15/10 : « une aile plate, et une tête qui fait pièce rapportée »)
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

NOIR = np.array(M.hexa("#2d384f"))            # la dominante (registre : noir bleuté), un peu soutenue (le style B adoucit)
BLANC = np.array(M.hexa("#f6f4ee"))           # le ventre, les croissants des épaules
GRIS = np.array(M.hexa("#a7adb7"))            # le bord du ventre, les fentes
FIL = M.hexa("#171d2b")
ROLL = 0.0                                    # à plat : les ailes horizontales, le bout relevé (Cohérence, 15/10 : « posée sur la tranche »)


def planforme(v):
    """La forme de la raie, d'une sphère unité : une aile en losange aux bouts qui filent vers l'arrière et se relèvent en
    vague, deux lobes à l'avant pour la tête."""
    u, y, w = v[:, 0], v[:, 1], v[:, 2]
    ax = np.abs(u)
    s = np.zeros_like(v)
    s[:, 0] = 0.52 * u
    s[:, 1] = 0.19 * y * (1 - 0.40 * ax ** 1.4) + 0.20 * ax ** 1.8
    s[:, 1] -= 0.075 * np.exp(-((ax - 0.20) / 0.13) ** 2) * np.clip(-y, 0, 1)                  # les lobes de tête avancent
    s[:, 2] = 0.050 * w * (1 - 0.55 * ax) + 0.095 * ax ** 2.3 + 0.020 * np.sin(8.0 * ax + 0.6) * ax
    return s


def construire():
    a = K.Animal("raie_manta")
    a.taille = 5.00                                # l'envergure (règle d'l'auteur du 15/10)

    # ----- le corps : une seule pièce ; noir dessus, blanc dessous (le bord gris), deux croissants blancs aux épaules -----
    corps = A.boule(1.0, 72, 36)
    u = corps.v / np.maximum(np.linalg.norm(corps.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(NOIR, (len(u), 1))
    t[u[:, 2] < -0.04] = BLANC
    t[(u[:, 2] < -0.04) & (np.hypot(u[:, 0], u[:, 1]) > 0.94)] = GRIS
    for c in (1, -1):
        t[(u[:, 2] > 0.10) & (u[:, 0] * c > 0.10) & (u[:, 0] * c < 0.46) & (u[:, 1] < -0.10) & (u[:, 1] > -0.52 - 0.3 * (u[:, 0] * c - 0.10))] = BLANC
    corps.teinte = t
    corps.v = planforme(corps.v)
    # le roulis : on tourne le corps autour de Y, puis on le descend pour que le bout bas frôle le sable
    th = math.radians(ROLL)
    xr = corps.v[:, 0] * math.cos(th) + corps.v[:, 2] * math.sin(th)
    zr = -corps.v[:, 0] * math.sin(th) + corps.v[:, 2] * math.cos(th)
    lift = 0.014 - float(zr.min())
    RM = A.repere((0.0, 0.0, lift), (0.0, ROLL, 0.0))
    a.piece("corps", corps, None, mat=RM)
    R3 = RM.to_3x3()

    # ----- les cornes céphaliques : deux lobes charnus qui avancent devant la tête (des cuillères rondes, épaisses à la base
    #       et qui s'arrondissent au bout, du même poil que le corps : plus de planches grises) -----
    for nom, c in (("G", 1), ("D", -1)):
        lobe = A.tour(A.profil([(0.030, 0), (0.040, 0.030), (0.043, 0.085), (0.034, 0.135), (0.018, 0.168), (0, 0.185)], 5), 28).etire(1.0, 0.62, 1.0)
        lobe.teinte = np.tile(NOIR * 0.95, (len(lobe.v), 1))
        base = RM @ Vector((c * 0.078, -0.180, 0.022))
        a.piece("corne_" + nom, lobe, None, mat=A.cadre(base, R3 @ Vector((c * 0.22, -1.0, 0.06)), (0, 0, 1)))
    # la bouche : une grande fente sur toute la largeur du museau, dessous ; on l'écrit sur le bord avant, côté blanc
    bouche = [RM @ Vector((0.20 * (k - 5) / 5 * 1.0, -0.196 + 0.020 * (1 - ((k - 5) / 5) ** 2) * 0 - 0.020 * abs((k - 5) / 5) ** 2, -0.016)) for k in range(11)]
    a.broderie("bouche", A.courbe([tuple(p) for p in bouche], 3), 0.0044, FIL)
    # les cinq fentes branchiales de chaque côté, sur le ventre blanc
    for nom, c in (("G", 1), ("D", -1)):
        for k in range(5):
            x0 = c * (0.050 + 0.030 * k)
            y0 = -0.035 + 0.018 * k
            fente = [RM @ Vector((x0, y0, -0.028 - 0.004 * k)), RM @ Vector((x0 + c * 0.020, y0 + 0.020, -0.034 - 0.004 * k))]
            a.broderie("fente_%s%d" % (nom, k), fente, 0.0030, FIL)

    # ----- les yeux : petits, sages, sur le côté des lobes ; un sourcil lourd -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("corps", RM @ Vector((c * 0.120, -0.150, 0.0)), R3 @ Vector((c * 0.25, -0.15, 1.0)))     # sur le dessus de la tête, devant : on les compte d'en haut
        a.oeil("oeil_" + nom, pos + n * 0.002, n, 0.0230)
        h = Vector((0, 0, 1))
        a.piece("lourde_" + nom, K.paupiere(0.0230, 0.60), tuple(NOIR), mat=A.cadre(pos + n * 0.002, n, (h - n * n.dot(h)).normalized()), poil=False)
    a.tete = RM @ Vector((0.0, -0.26, 0.04))

    # ----- la queue : un long fouet qui part du croupion et se couche en S dans le sable ; l'aileron minuscule à sa base -----
    pts = [RM @ Vector(p) for p in ((0.0, 0.180, 0.030), (0.0, 0.320, 0.020), (0.045, 0.480, 0.012), (0.120, 0.650, 0.010), (0.100, 0.800, 0.008))]
    queue = O.tube_r([tuple(p) for p in pts], [0.026, 0.020, 0.014, 0.009, 0.004], 12)
    a.piece("queue", O.teinte(queue, NOIR * 0.9), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("raie_manta", styles.style_de("raie_manta"), sys.modules[__name__]), "Raie manta")
