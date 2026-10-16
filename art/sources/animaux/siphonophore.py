"""Le siphonophore en peluche : la plus longue bête du monde, qui n'est pas une bête : une colonie. Un flotteur pâle en tête,
avec deux yeux dessinés pour le visage qu'il n'a pas, puis une chaîne translucide lilas qui court sur le fond en S, quinze
mètres de petits individus en cloche, de deux en deux, qui chacun nagent, mangent ou tirent ; et de loin en loin, une
lanterne ambre. Chacun fait son métier, et l'ensemble avance ; on ne sait pas lequel commande, et ça marche très bien.

    python siphonophore.py        fabrique la fiche art/apercus/animaux/siphonophore.png (style du palier : voir styles.py)
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

LILAS = np.array(M.hexa("#cdbbe8"))           # la dominante (registre : chaîne translucide lilas pâle)
LILAS_PROFOND = np.array(M.hexa("#a592cc"))
AMBRE = np.array(M.hexa("#ffb347"))           # l'accent : les lanternes ambre
FLOTTEUR = np.array(M.hexa("#ece4f6"))
FIL = M.hexa("#5a4a7a")


def tige(t):
    """Le chemin de la colonie : un S posé sur le fond, de la queue (t = 0) au flotteur (t = 1), tout en longueur le long de Y."""
    y = 2.30 - 4.40 * t
    x = 0.55 * math.sin(math.tau * (t * 1.35 + 0.1)) * (0.4 + 0.6 * t) + 0.10
    z = 0.050 + 0.040 * math.sin(math.tau * t * 2.2) + 0.090 * t ** 3
    return Vector((x, y, z))


def construire():
    a = K.Animal("siphonophore")
    a.taille = 5.00

    # ----- la tige : un fil translucide, lilas, qui porte toute la colonie -----
    pts = [tuple(tige(t)) for t in np.linspace(0.0, 1.0, 46)]
    fil = A.tube(A.courbe(pts, 3), lambda t_: 0.016 + 0.006 * t_, 10)
    fil.teinte = np.tile(LILAS_PROFOND, (len(fil.v), 1))
    a.piece("tige", fil, None, poil=False)

    # ----- les individus : des bouquets de cloches lilas (cormidies) espacés le long de la tige, jamais en file continue ;
    #       chacun porte une lanterne ambre et de longs fils qui retombent ; des cloches plus grosses en tête (le nectosome) -----
    cloches, lanternes, fils_ = None, None, None
    NB = 11
    for k in range(NB):
        t = 0.04 + 0.92 * k / (NB - 1)
        p = tige(t)
        p2 = tige(min(t + 0.01, 1.0))
        d = (p2 - p).normalized()
        cote = (Vector((0.0, 0.0, 1.0)).cross(d)).normalized()
        gros = 1.0 + 0.9 * (1.0 - t) ** 2 if t > 0.5 else 1.0
        for s_ in (-1, 0, 1):
            taille = (0.055 + 0.020 * math.sin(math.pi * t)) * (1.0 if s_ else 0.8) * (1.15 if t > 0.7 else 1.0)
            c = p + cote * (s_ * 0.075) + Vector((0.0, 0.0, 0.050 + (0.030 if s_ == 0 else 0.0)))
            m = A.boule(1.0, 16, 8).sculpte(lambda v: np.stack([v[:, 0], v[:, 1], np.where(v[:, 2] < 0, v[:, 2] * 0.50, v[:, 2])], axis=1)).etire(taille, taille * 1.20, taille * 1.0)
            m = O.couche(O.teinte(m, LILAS * (0.95 + 0.07 * ((k + s_) % 3 == 0))), A.cadre(c, d, (0, 0, 1)))
            cloches = m if cloches is None else cloches + m
        c = p + Vector((0.0, 0.0, 0.110))
        lan = O.couche(O.teinte(A.boule(1.0, 16, 8).etire(0.058, 0.058, 0.058), AMBRE), A.cadre(c, d, (0, 0, 1)))
        lanternes = lan if lanternes is None else lanternes + lan
        for s_ in (-1, 0, 1):
            base = p + cote * (s_ * 0.070) + Vector((0.0, 0.0, 0.020))
            long = 0.20 + 0.10 * ((k * 7 + s_) % 3) / 2.0
            m = O.tube_r([tuple(base), tuple(base + cote * (s_ * 0.050) + d * 0.020 + Vector((0.0, 0.0, -0.010))),
                          tuple(base + cote * (s_ * 0.130) + d * (0.060 + 0.020 * s_) + Vector((0.0, 0.0, -0.030)) + Vector((0.0, 0.0, 0.0))),
                          tuple(base + cote * (s_ * 0.230) + d * (0.140 + long * 0.4) + Vector((0.0, 0.0, -0.046)))],
                         [0.0060, 0.0050, 0.0036, 0.0022], 6)
            m = O.teinte(m, LILAS_PROFOND)
            fils_ = m if fils_ is None else fils_ + m
    a.piece("cloches", cloches, None, poil=False)
    a.piece("lanternes", lanternes, None, poil=False)
    a.piece("fils", fils_, None, poil=False)

    # ----- le flotteur : un grand ballon allongé, nacré, avec sa crête ; deux petits yeux dessinés ; la queue : un bouton -----
    f = tige(1.0)
    ball = A.boule(1.0, 36, 18)
    ball.teinte = np.tile(FLOTTEUR, (len(ball.v), 1))
    def goutte(v):                                    # une goutte allongée : large et bombée devant, qui s'effile en fondant vers l'arrière
        s = v.copy()
        q = np.clip(v[:, 1], 0.0, 1.0) ** 1.2
        s[:, 0] *= 1.0 - 0.55 * q
        s[:, 2] *= 1.0 - 0.50 * q
        q2 = np.clip(v[:, 2] + 0.15, 0.0, 1.2) / 1.2                                  # la goutte DEBOUT : ronde en bas, effilée vers le haut (lisible de face)
        s[:, 0] *= 1.0 - 0.62 * q2 ** 1.4
        s[:, 1] *= 1.0 - 0.30 * q2 ** 1.4
        s[:, 2] += 0.62 * q2 ** 1.6
        return s
    a.piece("flotteur", ball.sculpte(goutte).etire(0.115, 0.230, 0.150), None, pos=tuple(f + Vector((0.0, -0.150, 0.150))), poil=False)      # nacré et lisse : plus une boule de fourrure grise
    # (la crête est la pointe de la goutte : plus de cône posé dessus)
    centre = f + Vector((0.0, -0.150, 0.150))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("flotteur", centre, Vector((c * 0.40, -0.91, 0.22)))
        a.oeil("oeil_" + nom, pos + n * 0.003, n, 0.040)
    a.tete = centre + Vector((0.0, -0.28, 0.0))
    a.cap_tete = (0.0, -1.0, 0.0)                         # l'avant de la tête : la vue de près se place devant elle (peluche.py, 16/10)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "serpent", n=8)


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("siphonophore", styles.style_de("siphonophore"), sys.modules[__name__]), "Siphonophore")
