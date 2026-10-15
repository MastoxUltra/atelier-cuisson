"""La cigale en peluche : une grosse tête carrée bronze doré clair, deux yeux à fleur de crâne, un thorax bossu, et
sur le dos, deux grandes ailes fumées, nervurées comme des vitraux, qui retombent en toit ; le ventre rayé, un peu
creux : c'est une caisse de résonance. Plantée sur ses pattes courtes, la tête levée, le ventre gonflé : elle a
chanté tout l'été, elle y revient, et elle ne s'est jamais demandé si on l'aimait.

    python cigale.py        fabrique la fiche art/apercus/animaux/cigale.png (style du palier : A, cousu main)
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

BRONZE = np.array(M.hexa("#d6b068"))          # la dominante (registre : bronze doré clair)
RAIE = np.array(M.hexa("#8a6a30"))            # les rayures du ventre
FUMEE = M.hexa("#c8c2b6")                     # les ailes fumées
NERVURE = M.hexa("#6a5a44")
OEIL = M.hexa("#8a2a22")
PATTE = np.array(M.hexa("#a88848"))
FIL = M.hexa("#4a3a20")


def construire():
    a = K.Animal("cigale")
    a.taille = 0.34

    # ----- le corps : une tête large et carrée, un thorax bossu, un abdomen à rayures sombres qui s'effile -----
    tete = A.boule(1.0, 36, 18).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.085, 0.050, 0.060)
    tete.teinte = np.tile(BRONZE, (len(tete.v), 1))
    a.piece("tete", tete, None, pos=(0.0, -0.150, 0.135))
    thorax = A.boule(1.0, 36, 18).etire(0.080, 0.085, 0.080)
    thorax.teinte = np.tile(BRONZE * 0.96, (len(thorax.v), 1))
    a.piece("thorax", thorax, None, pos=(0.0, -0.070, 0.135))
    pc = A.profil([(0, 0.0), (0.050, 0.014), (0.068, 0.070), (0.058, 0.160), (0.036, 0.230), (0.012, 0.275), (0, 0.290)], 5)
    abd = A.tour(pc, 28)
    abd.teinte = np.where((np.sin(abd.v[:, 2] * 62) > 0.4)[:, None], RAIE, BRONZE)
    a.piece("abdomen", abd, None, mat=A.cadre(Vector((0.0, -0.020, 0.130)), (0.0, 1.0, -0.20), (0, 0, 1)))

    # ----- le visage : deux gros yeux saillants sur les côtés, deux petits boutons devant, les antennes -----
    H = Vector((0.0, -0.150, 0.135))
    for nom, c in (("G", 1), ("D", -1)):
        o = A.boule(1.0, 20, 10).etire(0.030, 0.034, 0.034)
        a.piece("globe_" + nom, O.teinte(o, np.array(OEIL)), None, pos=(c * 0.092, -0.158, 0.145), poil=False)
    O.paire_yeux(a, "tete", H, (0.38, -0.92, 0.18), 0.0140, decolle=0.002)
    for nom, c in (("G", 1), ("D", -1)):
        ant = O.tube_r([(c * 0.020, -0.190, 0.178), (c * 0.036, -0.230, 0.210)], [0.0050, 0.0040], 8)
        a.piece("antenne_" + nom, O.teinte(ant, RAIE), None, poil=False)
    a.tete = H + Vector((0.0, -0.06, 0.0))

    # ----- les ailes : deux grandes lames fumées, nervurées, qui retombent en toit sur le dos et dépassent l'abdomen -----
    contour = [(0.0, 0.0), (0.05, -0.012), (0.11, -0.016), (0.16, 0.050), (0.18, 0.170), (0.150, 0.300), (0.07, 0.330), (0.00, 0.120)]
    for nom, c in (("G", 1), ("D", -1)):
        m = A.decoupe(A.courbe(np.array(contour) * [c, 1], 5, fermee=True), 0.0050, 0.0020).peint(np.array(FUMEE))
        rep = A.repere((c * 0.034, -0.062, 0.210), (0, c * 34, 0))
        a.piece("aile_" + nom, m, None, mat=rep, poil=False)
        # les nervures : trois fils brodés d'un bout à l'autre de l'aile
        for k, off in enumerate((0.03, 0.07, 0.115)):
            nerv = [(c * off, 0.01), (c * (off + 0.02), 0.10), (c * (off + 0.025), 0.20), (c * (off + 0.005), 0.30)]
            pts = []
            for x, y in nerv:
                pts.append(Vector(rep @ Vector((x, y, 0.004))))
            a.broderie("nervure_%s%d" % (nom, k), A.courbe(pts, 4), 0.0020, NERVURE)

    # ----- les pattes : deux de chaque côté, courtes ; les antérieures plus fortes -----
    for k, (y, ep) in enumerate(((-0.100, 0.018), (-0.040, 0.014), (0.010, 0.012))):
        for nom, c in (("G", 1), ("D", -1)):
            p = O.tube_r([(c * 0.050, y, 0.105), (c * 0.115, y - 0.015, 0.090), (c * 0.140, y + 0.010, 0.007)], [ep, ep * 0.85, ep * 0.65], 8)
            a.piece("patte_%s%d" % (nom, k), O.teinte(p, PATTE), None, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("cigale", styles.style_de("cigale"), sys.modules[__name__]), "Cigale")
