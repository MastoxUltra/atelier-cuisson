"""Le grandgousier en peluche : l'anguille-pélican des plateaux, noir d'encre, un fouet de corps qui n'en finit pas, et devant,
une tête qui n'est presque que bouche : une immense poche rosée, ouverte, qui avalerait plus gros que lui et qui, pour l'heure,
bâille. Deux points pour yeux tout au bout du museau ; et à l'autre bout, le fouet de la queue s'enroule et allume une
petite lanterne rose, pour qu'on la prenne pour de la nourriture. Il avance en ouvrant la bouche : c'est sa façon d'arriver.

    python grandgousier.py        fabrique la fiche art/apercus/animaux/grandgousier.png (style du palier : voir styles.py)
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

ENCRE = np.array(M.hexa("#2c2a36"))           # la dominante (registre : noir d'encre), un cran plus clair pour qu'il se lise
DESSOUS = np.array(M.hexa("#3a3848"))
POCHE = np.array(M.hexa("#c98693"))           # l'accent : la bouche en poche rosée
LUEUR = np.array(M.hexa("#ffb98a"))           # la lanterne au bout du fouet
FIL = M.hexa("#1a1820")

# du bout du fouet à la tête : une grande courbe en S posée sur le sol
CHEMIN = [(0.34, 1.00, 0.092), (0.30, 0.86, 0.096), (0.20, 0.72, 0.104), (0.06, 0.60, 0.114), (-0.06, 0.46, 0.124), (-0.08, 0.30, 0.132),
          (-0.02, 0.14, 0.140), (0.04, 0.00, 0.148), (0.04, -0.12, 0.156), (0.00, -0.22, 0.162)]


def rayon(f):
    return O.interp([(0.0, 0.0), (0.01, 0.0050), (0.25, 0.0100), (0.50, 0.024), (0.72, 0.040), (0.86, 0.054), (0.93, 0.062),
                     (0.98, 0.040), (1.0, 0.0)])(f)


TOURNE = 25                                   # la fiche tourne la bête vers la caméra (25° devant) : on compte les DEUX yeux ; 0 pour le jeu


def construire():
    a = K.Animal("grandgousier")
    a.taille = 1.00

    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(ENCRE, (len(ang), 1))
        t[ang > 2.2] = DESSOUS
        return t
    fil, L = O.fil_corps(a, "corps", CHEMIN, rayon, peint, None, cotes=34, flanc=(1.0, 0.0, 0.0))

    # ----- la poche : la mâchoire du bas, immense, rosée, qui pend et s'ouvre sous le museau ; le palais rose dedans ; une lèvre -----
    ch, av, nq = (Vector(q) for q in fil.cadre(0.955 * L))
    poche = A.boule(1.0, 40, 20).sculpte(lambda v: np.stack([v[:, 0], v[:, 1], np.where(v[:, 2] > 0, v[:, 2] * 0.85, v[:, 2])], axis=1))
    poche.teinte = np.tile(POCHE, (len(poche.v), 1))
    a.piece("poche", poche.etire(0.066, 0.088, 0.056), None, pos=tuple(ch + Vector((0.0, -0.070, -0.070))), rot=(-30, 0, 0), poil=False)      # lisse : plus un coussin rose duveteux
    palais = A.boule(1.0, 24, 12).etire(0.080, 0.120, 0.016)
    palais.teinte = np.tile(POCHE * 0.80, (len(palais.v), 1))
    a.piece("palais", palais, None, pos=tuple(ch + Vector((0.0, -0.090, 0.005))), rot=(-18, 0, 0), poil=False)
    for k in range(10):                                        # de toutes petites dents au bord de la mâchoire du haut
        th = math.pi * (0.12 + 0.76 * k / 9)
        d = O.couche(O.teinte(O.pointe(0.016, 0.0040, 6), np.array(M.hexa("#e8dcc8"))),
                     A.cadre(ch + Vector((0.098 * math.cos(th), -0.150 - 0.020 * math.sin(th), -0.028)), Vector((0.0, 0.1, -1.0)), (0, 1, 0)))
        a.piece("dent_%d" % k, d, None, poil=False)

    # ----- deux petits yeux au bout du museau, dessus -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = O.sur_corps(fil, L, rayon, 0.930, 85, c, 1.0, 1.0, 0.003)
        a.oeil("oeil_" + nom, p, n, 0.036)               # deux yeux ronds bien visibles sur la tête

    # ----- la lanterne : au bout du fouet, une perle rose lumineuse ; une petite nageoire de chaque côté de la nuque -----
    c0, av0, nq0 = (Vector(q) for q in fil.cadre(0.0))
    lanterne = A.boule(1.0, 20, 10).etire(0.026, 0.026, 0.026)
    a.piece("lanterne", O.teinte(lanterne, LUEUR), None, pos=tuple(c0 + Vector((0.0, 0.0, 0.010))), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        p, n = O.sur_corps(fil, L, rayon, 0.88, 100, c, 1.0, 1.0, -0.003)
        pec = A.boule(1.0, 14, 8).etire(0.006, 0.034, 0.016)
        pec.teinte = np.tile(DESSOUS, (len(pec.v), 1))
        a.piece("pectorale_" + nom, O.couche(pec, A.cadre(p, Vector((c * 0.8, 0.5, -0.1)), (0, 0, 1))), None, poil=False)
    a.tete = ch + Vector((0.0, -0.20, 0.03))
    if TOURNE:
        O.tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "serpent")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("grandgousier", styles.style_de("grandgousier"), sys.modules[__name__]), "Grandgousier")
