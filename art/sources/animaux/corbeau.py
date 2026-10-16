"""Le corbeau en peluche : noir à reflets violets, taillé dans le charbon, avec un bec énorme, épais comme un pouce,
et une gorge hérissée de plumes. Il se tient haut sur ses pattes, la tête penchée de côté comme un juge, l'œil
sombre qui vous jauge ; il a l'air d'être dans le secret de tout, et de ne rien dire par pur plaisir.

    python corbeau.py        fabrique la fiche art/apercus/animaux/corbeau.png (style du palier : A, cousu main)
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

NOIR = np.array(M.hexa("#2b2338"))            # la dominante (registre : noir à reflets violets)
REFLET = np.array(M.hexa("#463a5e"))          # les reflets des ailes
BEC = M.hexa("#16141a")
GRIS = M.hexa("#5a5560")
OEIL = M.hexa("#e8e2d8")


def construire():
    a = K.Animal("corbeau")
    a.taille = 0.66

    r = O.oiseau(a, dos=NOIR, ventre=NOIR * 1.15, tete=NOIR * 1.35, aile=REFLET, queue=NOIR * 0.9, bec=BEC, patte=GRIS, long=0.40, ray=0.120,
                 incline=40.0, z0=0.165, tete_r=(0.074, 0.088, 0.072), tete_pos=(0.0, -0.110, 0.050), bec_long=0.140, bec_ray=0.048,
                 bec_baisse=-0.10, aile_dim=(0.028, 0.100, 0.230), aile_pos=(0.0, 0.040, 0.0), queue_dim=(0.050, 0.130, 0.014),
                 queue_haut=-16.0, patte_long=0.160, patte_ray=0.014, oeil_r=0.0270, oeil_dir=(0.32, -0.93, 0.20), coupe_dos=1.30, cou_ray=0.066, aile_pointue=True,
                 tete_rot=(-6, 0, 0))
    H, T, haut = r["H"], r["T"], r["haut"]

    # ----- le sourcil lourd : un bourrelet noir au-dessus de chaque œil, qui donne l'air sévère -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", H, Vector((c * 0.78, -0.50, 0.20)))
        brow = A.boule(1.0, 20, 10).etire(0.030, 0.016, 0.016)
        a.piece("sourcil_" + nom, O.teinte(brow, NOIR * 0.7), None, pos=tuple(pos + Vector((0.0, 0.0, 0.026))), rot=(0, 0, c * -20))

    # ----- la gorge hérissée : cinq petites plumes pointues sous le bec -----
    for k, dx in enumerate(()):                          # plus de pointes sous le bec : elles se lisaient comme des dents
        plume = O.pointe(0.060, 0.016, 10)
        d = Vector((dx * 4, -0.20, -1.0)).normalized()
        a.piece("barbe_%d" % k, O.couche(O.teinte(plume, NOIR * 0.85), A.cadre(H + Vector((dx, -0.050, -0.050)), d, (0, 1, 0))), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("corbeau", styles.style_de("corbeau"), sys.modules[__name__]), "Corbeau")
