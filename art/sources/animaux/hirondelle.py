"""L'hirondelle en peluche : une flèche bleu nuit luisant, le ventre crème, la gorge et le front brique, et surtout la
queue : deux longs rubans fourchus qui dépassent des ailes croisées. Posée à l'horizontale, le corps tendu comme un
trait, la tête de côté, le bec plat un peu ouvert : elle est arrivée du Sud hier soir, elle repart demain, elle vous
le dira dès qu'elle aura repris son souffle.

    python hirondelle.py        fabrique la fiche art/apercus/animaux/hirondelle.png (style du palier : A, cousu main)
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

NUIT = np.array(M.hexa("#2a3f8e"))            # la dominante (registre : bleu nuit luisant) ; le poil fonce un peu
CREME = np.array(M.hexa("#f7ecd2"))
BRIQUE = np.array(M.hexa("#c4502f"))          # l'accent : la gorge, le front
BEC = M.hexa("#2a2528")
PATTE = M.hexa("#6a5048")


def construire():
    a = K.Animal("hirondelle")
    a.taille = 0.32

    # ----- l'oiseau : fuselé, presque couché (55°), les ailes longues qui dépassent derrière -----
    r = O.oiseau(a, dos=NUIT, ventre=CREME, tete=NUIT, aile=NUIT, queue=NUIT * 0.9, bec=BEC, patte=PATTE, long=0.30, ray=0.082,
                 incline=58.0, z0=0.085, tete_r=(0.052, 0.062, 0.050), tete_pos=(0.0, -0.075, 0.020), bec_long=0.044, bec_ray=0.0155, bec_suit=True,
                 aile_dim=(0.018, 0.045, 0.215), aile_pos=(0.0, 0.040, -0.010), queue_dim=(0.020, 0.060, 0.010), queue_haut=-10.0,
                 patte_long=0.050, patte_ray=0.007, oeil_r=0.0135, oeil_dir=(0.76, -0.55, 0.20), bout_aile=NUIT * 0.7, coupe_dos=1.4)
    H = r["H"]

    # ----- la gorge et le front brique : deux petites taches en feutrine posées sur le visage -----
    gorge = A.boule(1.0, 24, 12).etire(0.036, 0.034, 0.030)
    a.piece("gorge", O.teinte(gorge, BRIQUE), None, pos=tuple(H + Vector((0.0, -0.030, -0.034))))
    front = A.boule(1.0, 20, 10).etire(0.030, 0.026, 0.016)
    a.piece("front", O.teinte(front, BRIQUE), None, pos=tuple(H + Vector((0.0, -0.040, 0.030))))

    # ----- la queue en ciseaux : deux longs rubans qui partent en V, plus longs que le reste -----
    for nom, c in (("G", 1), ("D", -1)):
        ruban = A.boule(1.0, 20, 8).etire(0.0075, 0.012, 0.130)
        ruban.teinte = np.tile(NUIT * 0.85, (len(ruban.v), 1))
        a.piece("ruban_" + nom, ruban, None, mat=A.cadre(Vector((c * 0.020, 0.250, 0.115)), (c * 0.22, 1.0, -0.20), (0, 0, 1)))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("hirondelle", styles.style_de("hirondelle"), sys.modules[__name__]), "Hirondelle")
