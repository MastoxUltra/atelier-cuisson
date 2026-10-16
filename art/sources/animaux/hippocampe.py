"""L'hippocampe en peluche, deuxième dessin : le gentleman du lagon, poussé à 150 %. Jaune safran, le ventre bombé comme
un gilet de notaire, le cou en S, la tête en proue : une grosse couronne de cinq pointes sur le crâne, un groin
en pipette qui avance, un œil grave sous une paupière lourde. Le corps annelé comme un bambou (les anneaux sont dans la
forme, pas du fil), un grand éventail dans le dos, deux petites nageoires aux oreilles, et la queue qui s'enroule sur le
sable en un seul tour de crosse. Il est très droit : il a rentré le menton en nous voyant.

    python hippocampe.py        fabrique la fiche art/apercus/animaux/hippocampe.png (style du palier : C, velours ras)
    (le premier dessin, jugé bon mais « tout petit sur la fiche » le 15/10)
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

SAFRAN = M.hexa("#d8423a")                    # la dominante : ROUGE corail (l'auteur, 16/10 : « mets-le en rouge » ; était jaune safran)
PALE = M.hexa("#f07a62")                      # le plastron, les nageoires : un ton plus clair (registre)
ANNEAU = M.hexa("#ee6a52")                    # la couronne (la crête) : un ton plus clair (registre)
CREME = K.CREME
FIL = M.hexa("#7a3a14")

# le fil du corps, de la nuque au bout de la queue enroulée : un grand S, le ventre en avant, puis la queue qui descend,
# revient et s'enroule sur le sable
CHEMIN = [(0.0, -0.040, 0.640), (0.0, 0.010, 0.560), (0.0, -0.065, 0.450), (0.0, -0.105, 0.340), (0.0, -0.045, 0.235), (0.0, 0.060, 0.155),
          (0.0, 0.125, 0.085), (0.0, 0.095, 0.036), (0.0, 0.010, 0.030), (0.0, -0.045, 0.072), (0.0, -0.020, 0.122), (0.0, 0.030, 0.100)]
RAYONS = [0.056, 0.064, 0.088, 0.100, 0.086, 0.062, 0.050, 0.044, 0.038, 0.032, 0.024, 0.014]   # plus fin (16/10, d'après un vrai)


def construire():
    a = K.Animal("hippocampe")
    a.taille = 0.72

    # ----- le corps : un seul tube, annelé dans sa forme (le rayon pulse) ; le ventre plus clair vient en plastron -----
    ch = A.courbe(CHEMIN, 9)
    nodes = np.linspace(0, 1, len(RAYONS))

    def rayon(t):
        base = float(np.interp(t, nodes, RAYONS))
        return base * (1.0 + 0.045 * math.cos(math.tau * 14.0 * t) * min(1.0, 4.0 * (1 - t)))     # les anneaux, doux (0,07 : des boules empilées)
    corps = K.tube_peint(ch, rayon, [(1.0, SAFRAN)], 28)
    a.piece("corps", corps, None)
    poitrail = A.boule(1.0, 40, 20).etire(0.050, 0.040, 0.135)                                         # plus discret
    a.piece("poitrail", poitrail, PALE, pos=(0.0, -0.140, 0.355), rot=(8, 0, 0))

    # ----- la tête en proue : grosse, bien en avant, le museau-pipette, la couronne de cinq pointes, la paupière lourde -----
    H = Vector((0.0, -0.095, 0.745))
    tete = A.boule(1.0, 44, 22)
    tete.teinte = np.tile(np.array(SAFRAN), (len(tete.v), 1))
    RT = A.repere(H, (-10, 0, 0))
    a.piece("tete", tete.etire(0.068, 0.088, 0.072), None, mat=RT)
    museau = A.tour(A.profil([(0.030, 0.0), (0.024, 0.030), (0.020, 0.060), (0.0185, 0.090), (0.0180, 0.118), (0.0150, 0.128), (0, 0.130)], 4), 28)
    dirm = Vector((0.0, -0.97, -0.22)).normalized()
    a.piece("museau", museau, SAFRAN, mat=A.cadre(H + Vector((0.0, -0.062, -0.016)), dirm, (0, 0, 1)))
    a.piece("bout", A.boule(1.0, 16, 8).etire(0.0095, 0.0075, 0.0050), CREME,
            mat=A.cadre(H + Vector((0.0, -0.062, -0.016)) + dirm * 0.129, dirm, (0, 0, 1)), poil=False)
    # la couronne : cinq petites bosses arrondies serrées sur le crâne, comme sur un vrai (plus une crête de pointes)
    for k, (x, hh, lean) in enumerate(((-0.030, 0.066, -22), (-0.015, 0.078, -9), (0.0, 0.084, 0), (0.015, 0.078, 9), (0.030, 0.066, 22))):
        bosse = A.boule(1.0, 16, 8).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.0165, 0.0165, 0.032)   # assez grandes pour se voir
        a.piece("couronne_%d" % k, O.couche(O.teinte(bosse, np.array(ANNEAU)), A.cadre(H + Vector((x, 0.016, hh - 0.008)),
                (math.sin(math.radians(lean)), 0.18, 1.0), (0, 1, 0))), None, poil=False)
    O.paire_yeux(a, "tete", H, (0.64, -0.74, 0.22), 0.0200, couleur_lourde=tuple(SAFRAN), coupe=0.60, decolle=0.003, R=RT)
    a.tete = H + Vector((0.0, -0.17, -0.04))

    # ----- les nageoires : le grand éventail du dos, un petit éventail à chaque joue ; l'éventail porte un liseré -----
    dorsal = A.boule(1.0, 32, 14).etire(0.006, 0.060, 0.092)
    dorsal.teinte = np.where((np.hypot(dorsal.v[:, 1] / 0.060, dorsal.v[:, 2] / 0.092) > 0.84)[:, None], np.array(ANNEAU), np.array(PALE))
    a.piece("nageoire_dos", dorsal, None, pos=(0.0, 0.090, 0.290), rot=(-14, 0, 0), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        petite = A.boule(1.0, 20, 10).etire(0.006, 0.034, 0.042)
        a.piece("nageoire_" + nom, O.teinte(petite, np.array(PALE)), None, pos=(c * 0.082, 0.000, 0.562), rot=(0, 0, c * 22), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("hippocampe", styles.style_de("hippocampe"), sys.modules[__name__]), "Hippocampe")
