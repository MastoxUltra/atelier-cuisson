"""Le poisson-clown en peluche, deuxième dessin : pas le rigolo du dessin animé, un vieux grincheux de l'anémone. Orange
vif à trois bandes blanches bordées de noir, bossu du front, la grosse lèvre inférieure avancée et boudeuse, les yeux
lourds sous des paupières qui tombent, la bouche tirée vers le bas. Couché sur le ventre, un coude sur le sable, le
corps en C, il lève ses grandes nageoires bordées de noir comme des éventails de vieille dame et attend qu'on lui
demande pardon : il habite là depuis trente ans.

    python poisson_clown.py        fabrique la fiche art/apercus/animaux/poisson_clown.png (style du palier : A, cousu main)
    (le premier dessin, refusé le 15/10 : « la silhouette ronde et souriante qu'on connaît »)
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

ORANGE = np.array(M.hexa("#ff7a1c"))          # la dominante (registre : orange vif)
BLANC = np.array(M.hexa("#fff7ea"))
NOIR = np.array(M.hexa("#1d1716"))
CHAIR = np.array(M.hexa("#ff9a56"))           # la lèvre, un cran plus claire
FIL = M.hexa("#5a2410")
LONG = 0.44


def nageoire(ry, rz, couleur=ORANGE, ourlet=0.80, festons=0):
    """Une nageoire ronde, plate, bordée de noir ; avec festons : le bord ondulé comme un éventail déchiré."""
    m = A.boule(1.0, 40, 16).etire(0.007, ry, rz)
    u = np.hypot(m.v[:, 1] / ry, m.v[:, 2] / rz)
    ang = np.arctan2(m.v[:, 2] / rz, m.v[:, 1] / ry)
    r = u * (1 + (0.10 * np.cos(festons * ang) if festons else 0.0))
    m.teinte = np.where((r > ourlet)[:, None], NOIR, couleur)
    if festons:
        m.v[:, 1] *= 1 + 0.06 * np.cos(festons * ang) * u ** 3
        m.v[:, 2] *= 1 + 0.06 * np.cos(festons * ang) * u ** 3
    return m


def construire():
    a = K.Animal("poisson_clown")
    a.taille = 0.46

    # ----- le corps : un fuseau haut et bossu (le front en bosse, le dos qui monte), plié en C, les bandes peintes en place -----
    prof = A.profil([(0, 0), (0.044, 0.008), (0.086, 0.040), (0.118, 0.105), (0.126, 0.175), (0.108, 0.250), (0.074, 0.320), (0.046, 0.380),
                     (0.036, LONG)], 5)
    corps = A.tour(prof, 52).etire(0.80, 1.18, 1.0)
    z = corps.v[:, 2]
    t = np.tile(ORANGE, (len(z), 1))
    for centre, demi in ((0.112, 0.020), (0.222, 0.024), (0.362, 0.012)):               # derrière l'œil, au milieu, au pédoncule
        d = np.abs(z - centre)
        t[d < demi + 0.013] = NOIR
        t[d < demi] = BLANC
    corps.teinte = t

    def forme(v):
        s = v.copy()
        f = v[:, 2] / LONG
        s[:, 1] += 0.050 * np.exp(-((f - 0.17) / 0.10) ** 2) * (v[:, 1] > 0)          # la bosse du front
        s[:, 1] -= 0.020 * np.exp(-((f - 0.04) / 0.06) ** 2) * (v[:, 1] < 0)          # le menton qui avance (lèvre)
        s[:, 0] -= 0.100 * f ** 2                                                      # le C : (X local = -X monde une fois couché)
        return s
    T = A.cadre((0.0, -0.220, 0.152), (0, 1, 0), (0, 0, 1))
    a.piece("corps", corps.sculpte(forme), None, mat=T)

    # ----- la lèvre boudeuse : un bourrelet épais sous le museau, la bouche tirée vers le bas ; deux sourcils lourds -----
    levre = A.boule(1.0, 28, 14).etire(0.026, 0.018, 0.013)                          # une petite lèvre, plus la grosse boule orange
    a.piece("levre", O.teinte(levre, CHAIR), None, pos=(0.0, -0.258, 0.132), rot=(10, 0, 0))
    centre = Vector((0.0, -0.140, 0.162))
    O.paire_yeux(a, "corps", centre, (0.88, -0.38, 0.14), 0.0230, couleur_lourde=tuple(ORANGE * 0.9), coupe=0.60, decolle=0.002)
    O.broder(a, "moue", "corps", centre, [(0.17 * u_, -0.95, -0.40 + 0.10 * u_ * u_) for u_ in np.linspace(-1, 1, 9)], 0.0026, FIL, decolle=0.003)      # une petite bouche fendue
    a.tete = Vector((0.0, -0.285, 0.162))

    # ----- les nageoires : l'éventail du dos (bordé de noir, déchiré), la queue de côté, deux grandes pectorales levées -----
    dos = O.couche(nageoire(0.150, 0.150, festons=7), A.cadre((0.012, -0.040, 0.237), (0, 1, 0), (0, 0, 1)))
    a.piece("dorsale", dos, None, poil=False)
    queue = O.couche(nageoire(0.100, 0.115, festons=5), A.cadre((0.108, 0.255, 0.162), (0.30, 1.0, 0.0), (0, 0, 1)))
    a.piece("queue", queue, None, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        p = O.couche(nageoire(0.095, 0.075, festons=6), A.cadre((c * 0.100, -0.140, 0.142), (c * 0.8, 0.45, -0.20 if c > 0 else 0.35), (0, 0, 1)))
        a.piece("pectorale_" + nom, p, None, poil=False)
    a.piece("ventrale", O.couche(nageoire(0.060, 0.034), A.cadre((0.0, -0.095, 0.050), (0, 1, 0), (0, 0, 1))), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("poisson_clown", styles.style_de("poisson_clown"), sys.modules[__name__]), "Poisson-clown")
