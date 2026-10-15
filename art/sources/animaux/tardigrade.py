"""Le tardigrade en peluche : l'ours d'eau, le petit boudin beige rosé qui a survécu à tout, aux volcans comme au vide. Un
corps rond en quatre tranches douillettes, huit pattes courtes et trapues aux griffes minuscules, une tête sans cou,
juste un petit museau rond, la bouche en cercle brodé et deux points noirs pour les yeux. Il avance, extrêmement lentement,
sur l'idée que rien ne peut lui arriver. Rien ne lui est jamais arrivé.

    python tardigrade.py        fabrique la fiche art/apercus/animaux/tardigrade.png (style du palier : C, velours ras)
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

BEIGE = np.array(M.hexa("#ebcdb9"))           # la dominante (registre : beige rosé #e0c3b0), un cran plus clair (style C)
PLI = np.array(M.hexa("#d6ae98"))             # les plis entre les tranches
GRIFFE = np.array(M.hexa("#f6ece0"))          # les griffes
FIL = M.hexa("#8a5a46")

# du fond vers la tête : un boudin presque droit, un peu courbé, qui se redresse à peine
CHEMIN = [(0.02, 0.26, 0.082), (0.00, 0.14, 0.092), (-0.01, 0.00, 0.098), (0.00, -0.14, 0.094), (0.02, -0.24, 0.088), (0.03, -0.31, 0.086)]
CORPS = O.interp([(0.0, 0.0), (0.03, 0.060), (0.10, 0.090), (0.30, 0.105), (0.55, 0.108), (0.80, 0.098), (0.92, 0.074), (0.985, 0.042), (1.0, 0.0)])


def construire():
    a = K.Animal("tardigrade")
    a.taille = 0.34

    # ----- le corps : un boudin à quatre bourrelets (le rayon onde cinq fois), plus foncé dans les plis -----
    def rayon(f):
        return CORPS(f) * (1.0 + 0.085 * math.cos(2.0 * math.pi * 4.0 * f))

    def peint(m, L):
        f = m.v[:, 2] / L
        t = np.tile(BEIGE, (len(f), 1))
        t[np.cos(2.0 * math.pi * 4.0 * f) < -0.75] = PLI
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t[ang > 2.4] = BEIGE * 0.97
        return t
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=36, flanc=(1.0, 0.0, 0.0))

    # ----- le visage : la bouche en cercle brodé au bout du museau, deux petits points noirs pour les yeux -----
    centre, avant, nq = (Vector(q) for q in fil.cadre(0.995 * L))
    cote = nq.cross(avant)
    cercle = []
    for k in range(13):
        th = 2.0 * math.pi * k / 12
        cercle.append(tuple(centre + avant * 0.006 + nq * (0.020 * math.sin(th) + 0.006) + cote * (0.020 * math.cos(th))))
    a.broderie("bouche", A.courbe(cercle, 2), 0.0042, FIL)
    for nom, c in (("G", 1), ("D", -1)):
        cc, dd = fil.vise(0.925 * L, 0.30, c * 0.75, 0.62)
        pos, n = a.surface("corps", cc, dd)
        a.bouton("oeil_" + nom, pos + n * 0.002, n, 0.0120)

    # ----- les huit pattes : quatre de chaque côté, courtes et trapues, quatre griffes crème au bout ; une patte avant levée -----
    for c, nm in ((1, "G"), (-1, "D")):
        for k, f in enumerate((0.20, 0.42, 0.62, 0.82)):
            cen, av, nq2 = (Vector(q) for q in fil.cadre(f * L))
            cote2 = nq2.cross(av)
            racine = cen + cote2 * (c * 0.060) - nq2 * 0.030
            genou = cen + cote2 * (c * 0.108) - nq2 * 0.020
            genou.z = 0.052
            pied = cen + cote2 * (c * 0.118)
            pied.z = 0.024
            if c < 0 and k == 3:                                                    # la patte avant droite levée, qui sonde l'air
                pied = Vector((pied.x - 0.020, pied.y - 0.060, 0.092))
                genou.z = 0.082
            pts = [tuple(racine), tuple(racine + (genou - racine) * 0.6), tuple(genou), tuple(pied)]
            m = O.membre(pts, [0.050, 0.044, 0.039, 0.035], [(1.0, tuple(BEIGE * 0.98))], 14)
            m = m + A.boule(1.0, 14, 8).etire(0.038, 0.038, 0.034).pose(tuple(pied))
            a.piece("patte_%s%d" % (nm, k), m, None)
            dev = (av if (c < 0 and k == 3) else -av)
            dev = Vector((c * 0.45, -0.85, 0.0)).normalized()
            for g, dx in enumerate((-0.020, -0.007, 0.007, 0.020)):
                gr = O.couche(O.teinte(O.pointe(0.020, 0.0070, 6), GRIFFE),
                              A.cadre(pied + Vector((dx * c, 0.0, -0.002)) + dev * 0.028, dev + Vector((0.0, 0.0, -0.45)), (0, 0, 1)))
                a.piece("griffe_%s%d_%d" % (nm, k, g), gr, None, poil=False)
    a.tete = Vector(fil.cadre(0.97 * L)[0]) + Vector((0.0, -0.05, 0.02))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres", souple=True)


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tardigrade", styles.style_de("tardigrade"), sys.modules[__name__]), "Tardigrade")
