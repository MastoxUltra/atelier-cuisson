"""La chouette en peluche : une effraie, le dos or pâle moucheté de gris, le ventre blanc, et la face en cœur : deux
grandes plaques blanches qui se rejoignent au-dessus du bec, bordées d'un liseré roux, avec deux yeux noirs profonds.
Debout, la tête penchée sur le côté à angle droit, elle vous regarde comme on regarde un rongeur : avec une immense
patience, et très peu d'espoir de se tromper.

    python chouette.py        fabrique la fiche art/apercus/animaux/chouette.png (style du palier : A, cousu main)
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

OR = np.array(M.hexa("#dcb36a"))              # la dominante (registre : dos or pâle)
BLANC = np.array(M.hexa("#fbf7ee"))
ROUX = np.array(M.hexa("#c48f4c"))            # le liseré de la face
GRIS = np.array(M.hexa("#9aa0a8"))            # les mouchetures
BEC = M.hexa("#e8dcc4")
PATTE = M.hexa("#e0c8a8")
NOIR = M.hexa("#16130f")


def construire():
    a = K.Animal("chouette")
    a.taille = 0.46

    r = O.oiseau(a, dos=OR, ventre=BLANC, tete=BLANC, aile=OR * 0.96, queue=OR * 0.9, bec=BEC, patte=PATTE, long=0.38, ray=0.120,
                 incline=10.0, z0=0.140, tete_r=(0.100, 0.090, 0.090), tete_pos=(0.0, -0.040, 0.075), bec_long=0.030, bec_ray=0.016,
                 bec_baisse=-0.30, aile_dim=(0.026, 0.085, 0.210), aile_pos=(0.0, 0.030, 0.0), queue_dim=(0.050, 0.060, 0.012),
                 queue_haut=-30.0, patte_long=0.110, patte_ray=0.012, yeux=False, coupe_dos=1.15, tete_rot=(-4, 0, 28))
    H, T, haut = r["H"], r["T"], r["haut"]

    # ----- la face en cœur : deux disques blancs bordés de roux, qui se rejoignent au-dessus du bec ; les yeux noirs -----
    mat_tete = A.repere(H, (-4, 0, 28))
    for nom, c in (("G", 1), ("D", -1)):
        bord = A.boule(1.0, 28, 14).etire(0.054, 0.014, 0.060)
        a.piece("bord_" + nom, O.teinte(bord, ROUX), None, mat=mat_tete @ A.repere((c * 0.040, -0.082, 0.008), (0, 0, c * 8)), poil=False)
        disque = A.boule(1.0, 28, 14).etire(0.048, 0.014, 0.054)
        a.piece("disque_" + nom, O.teinte(disque, BLANC), None, mat=mat_tete @ A.repere((c * 0.040, -0.088, 0.008), (0, 0, c * 8)), poil=False)
        a.oeil("oeil_" + nom, Vector(mat_tete @ Vector((c * 0.040, -0.112, 0.004))), Vector((c * 0.10, -1.0, 0.0)), 0.0265)      # DEVANT le disque : plus coupés en D
    a.tete = Vector(mat_tete @ Vector((0.0, -0.12, 0.0)))

    # ----- les mouchetures grises sur le dos ; le bec crochu sous l'angle de la face ; les ailes un peu serrées -----
    rng = np.random.default_rng(5)
    for k in range(16):
        x = rng.uniform(-0.055, 0.055)
        z = rng.uniform(0.06, 0.30)
        tache = A.boule(1.0, 10, 6).etire(0.012, 0.008, 0.012)
        a.piece("moucheture_%d" % k, O.teinte(tache, GRIS), None, mat=T @ A.repere((x, 0.115, z)), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("chouette", styles.style_de("chouette"), sys.modules[__name__]), "Chouette")
