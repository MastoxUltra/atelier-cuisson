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
BEC = M.hexa("#cfc8b4")                       # le bec : corne claire, bien visible sur la tête bleu-gris


def peint_tete(m, t):
    """La moustache noire du faucon : une goutte PEINTE sous chaque œil (jamais des poils posés au bec)."""
    u = m.v / np.maximum(np.linalg.norm(m.v, axis=1, keepdims=True), 1e-9)
    t = t.copy()
    for c in (1, -1):
        d = np.array([c * 0.42, -0.84, -0.30]); d /= np.linalg.norm(d)
        t[(u @ d) > 0.955] = np.array(NOIR)
        d2 = np.array([c * 0.40, -0.78, -0.55]); d2 /= np.linalg.norm(d2)
        t[(u @ d2) > 0.975] = np.array(NOIR)
    return t


def construire():
    a = K.Animal("faucon")
    a.taille = 0.58

    r = O.oiseau(a, dos=BRIQUE, ventre=CLAIR, tete=GRISBLEU, aile=BRIQUE * 0.92, queue=BRIQUE * 0.85, bec=BEC, patte=JAUNE, long=0.36,
                 ray=0.115, incline=36.0, z0=0.140, tete_r=(0.064, 0.074, 0.062), tete_pos=(0.0, -0.100, 0.052), bec_long=0.070,
                 bec_ray=0.0330, bec_baisse=-0.35, aile_dim=(0.026, 0.085, 0.230), aile_pos=(0.0, 0.035, 0.0),
                 queue_dim=(0.044, 0.140, 0.012), queue_haut=-16.0, patte_long=0.120, patte_ray=0.0135, oeil_r=0.0230,
                 oeil_dir=(0.32, -0.93, 0.20), bout_aile=BRIQUE * 0.55, coupe_dos=1.25, tete_rot=(-6, 0, 0), cou_ray=0.062, aile_pointue=True, peint_tete=peint_tete)
    H, T, haut = r["H"], r["T"], r["haut"]

    # le bec crochu : le bout du bec se recourbe vers le bas en un crochet pointu
    a.piece("crochet", O.couche(O.teinte(O.pointe(0.052, 0.0190, 8), np.array(M.hexa("#4a4650"))), A.cadre(H + Vector((0.0, -0.126, -0.016)), Vector((0.0, -0.10, -1.0)), (0, 1, 0))), None, poil=False)

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
    # (plus de moustaches noires : elles se lisaient comme des poils au bec)
    cire = A.boule(1.0, 16, 8).etire(0.018, 0.014, 0.012)
    a.piece("cire", cire, JAUNE, pos=tuple(H + Vector((0.0, -0.072, -0.004))), poil=False)
    # les ailes plus longues que la queue : les pointes dépassent
    for nom, c in (("G", 1), ("D", -1)):
        pointe = A.boule(1.0, 20, 8).etire(0.014, 0.036, 0.100)
        a.piece("pointe_" + nom, O.teinte(pointe, BRIQUE * 0.55), None, mat=T @ A.repere((c * 0.112, 0.060, -0.020), (0, 0, c * 5)), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("faucon", styles.style_de("faucon"), sys.modules[__name__]), "Faucon")
