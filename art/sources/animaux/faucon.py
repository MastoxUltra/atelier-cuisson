"""Le faucon en peluche : roux brique moucheté de brun, la tête gris bleu coiffée d'une moustache noire sous chaque
œil, la poitrine mouchetée, un bec crochu court et sombre sur une cire jaune. Droit sur ses serres, les ailes en lame
repliées plus longues que la queue, il regarde par-dessus l'épaule avec un air de ne pas aimer ce qu'il voit :
il n'y a pas de quoi, c'est un faucon.

    python faucon.py        fabrique la fiche art/apercus/animaux/faucon.png (style du palier : C, velours ras)
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

BRIQUE = np.array(M.hexa("#b5623e"))          # la dominante (registre : roux brique moucheté)
TACHE = np.array(M.hexa("#6a3a28"))
CLAIR = np.array(M.hexa("#e8cfb0"))           # le ventre, moucheté
GRISBLEU = np.array(M.hexa("#7f8c9a"))        # la tête
NOIR = M.hexa("#1d1a1c")                      # la moustache
JAUNE = M.hexa("#f0c030")                     # la cire, les pattes
BEC = M.hexa("#3a3a42")


def construire():
    a = K.Animal("faucon")
    a.taille = 0.58

    r = O.oiseau(a, dos=BRIQUE, ventre=CLAIR, tete=GRISBLEU, aile=BRIQUE * 0.92, queue=BRIQUE * 0.85, bec=BEC, patte=JAUNE, long=0.36,
                 ray=0.115, incline=36.0, z0=0.140, tete_r=(0.064, 0.074, 0.062), tete_pos=(0.0, -0.100, 0.052), bec_long=0.050,
                 bec_ray=0.0245, bec_baisse=-0.35, aile_dim=(0.026, 0.085, 0.230), aile_pos=(0.0, 0.035, 0.0),
                 queue_dim=(0.044, 0.140, 0.012), queue_haut=-16.0, patte_long=0.120, patte_ray=0.0135, oeil_r=0.0185,
                 oeil_dir=(0.76, -0.50, 0.20), bout_aile=BRIQUE * 0.55, coupe_dos=1.25, tete_rot=(-6, 0, 18))
    H, T, haut = r["H"], r["T"], r["haut"]

    # ----- les mouchetures : de petites taches brunes sur le dos, des traits sur le ventre -----
    rng = np.random.default_rng(12)
    for k in range(18):
        x = rng.uniform(-0.05, 0.05)
        z = rng.uniform(0.07, 0.26)
        tache = A.boule(1.0, 12, 6).etire(0.016, 0.010, 0.016)
        a.piece("moucheture_%d" % k, O.teinte(tache, TACHE), None, mat=T @ A.repere((x, 0.108, z)), poil=False)
    for k in range(10):
        x = rng.uniform(-0.05, 0.05)
        z = rng.uniform(0.08, 0.24)
        trait = A.boule(1.0, 12, 6).etire(0.006, 0.008, 0.020)
        a.piece("trait_%d" % k, O.teinte(trait, TACHE), None, mat=T @ A.repere((x, -0.108, z)), poil=False)

    # ----- la moustache noire sous l'œil, la cire jaune, le bec crochu : deux sourcils lourds -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", H, Vector((c * 0.74, -0.50, -0.10)))
        mous = A.boule(1.0, 16, 8).etire(0.0075, 0.012, 0.040)
        a.piece("moustache_" + nom, O.teinte(mous, np.array(NOIR)), None, mat=A.cadre(pos + n * 0.001, n, (0, 0, 1)), poil=False)
    cire = A.boule(1.0, 16, 8).etire(0.018, 0.014, 0.012)
    a.piece("cire", cire, JAUNE, pos=tuple(H + Vector((0.0, -0.072, -0.004))), poil=False)
    # les ailes plus longues que la queue : les pointes dépassent
    for nom, c in (("G", 1), ("D", -1)):
        pointe = A.boule(1.0, 20, 8).etire(0.014, 0.036, 0.100)
        a.piece("pointe_" + nom, O.teinte(pointe, BRIQUE * 0.55), None, mat=T @ A.repere((c * 0.112, 0.060, -0.020), (0, 0, c * 5)), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("faucon", styles.style_de("faucon"), sys.modules[__name__]), "Faucon")
