"""La genette en peluche : le félin qui n'en est pas un, sable crème tacheté de charbon, long et bas, avec un museau
pointu de fouine, de grandes oreilles rondes et une queue très longue annelée de noir. Ramassée à ras du sol, elle
vient de s'arrêter en plein pas, une patte avant levée, la tête tournée, les yeux grands ouverts dans le noir : elle
vous a entendu avant que vous ne la voyiez.

    python genette.py        fabrique la fiche art/apercus/animaux/genette.png (style du palier : C, velours ras)
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

SABLE = np.array(M.hexa("#e2cfa8"))           # la dominante (registre : sable crème) ; le velours éclaircit un peu
CHARBON = np.array(M.hexa("#2e2a28"))         # les taches, les bagues
CLAIR = np.array(M.hexa("#f3ead6"))           # le museau, le ventre
NEZ = M.hexa("#1a1514")
FIL = M.hexa("#3a302c")

# le fil du corps, de la queue à la nuque : un grand S à ras du sol, le poitrail qui se redresse un peu devant
CHEMIN = [(0.0, 0.62, 0.095), (0.0, 0.46, 0.105), (0.0, 0.30, 0.120), (0.0, 0.14, 0.140), (0.0, -0.02, 0.150), (0.0, -0.18, 0.165),
          (0.0, -0.32, 0.195)]


def rayon(f):
    return O.interp([(0.0, 0.0), (0.03, 0.055), (0.20, 0.080), (0.50, 0.092), (0.80, 0.086), (0.95, 0.070), (1.0, 0.062)])(f)


def construire():
    a = K.Animal("genette")
    a.taille = 0.95

    # ----- le corps : un long fuseau sable, moucheté de charbon, plus clair dessous ; la raie sombre du dos -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(SABLE, (len(ang), 1))
        t[ang > 2.2] = CLAIR
        t = O.moucheter(m, SABLE, CHARBON, graine=9, nombre=130, taille=0.085, depart=t)
        t[(ang < 0.20)] = CHARBON * 0.9 + SABLE * 0.1                         # la raie du dos
        return t
    fil, L = O.fil_corps(a, "corps", CHEMIN, lambda f: rayon(f), peint, None, cotes=40, flanc=(1.0, 0.0, 0.0))

    # ----- la tête : petite, pointue, les grandes oreilles rondes ; le masque : deux taches sombres autour des yeux -----
    cb, ab, nb = (Vector(q) for q in fil.cadre(L))
    TETE = cb + Vector((0.0, -0.075, 0.040))
    tete = A.boule(1.0, 40, 20)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(SABLE, (len(u), 1))
    t[(np.abs(u[:, 2] - 0.05) < 0.22) & (u[:, 1] < 0.0) & (np.abs(u[:, 0]) > 0.25)] = CHARBON * 1.2
    t[u[:, 2] < -0.30] = CLAIR
    tete.teinte = t
    a.piece("tete", tete.etire(0.066, 0.078, 0.062), None, pos=tuple(TETE), rot=(8, 0, 22))
    museau = A.tour(A.profil([(0.036, 0), (0.030, 0.030), (0.020, 0.060), (0.010, 0.082), (0, 0.092)], 4), 22)
    a.piece("museau", O.couche(O.teinte(museau, CLAIR), A.cadre(TETE + Vector((0.0, -0.062, -0.010)), (0.0, -1.0, -0.20), (0, 1, 0))), None)
    a.piece("nez", A.boule(1.0, 14, 8).etire(0.012, 0.010, 0.010), NEZ, pos=tuple(TETE + Vector((0.0, -0.150, -0.030))), poil=False)
    O.paire_yeux(a, "tete", TETE, (0.64, -0.74, 0.20), 0.0175, decolle=0.002, R=A.repere((0.0, 0.0, 0.0), (8, 0, 22)))
    for nom, c in (("G", 1), ("D", -1)):
        ore = A.boule(1.0, 20, 10).etire(0.032, 0.010, 0.040)
        a.piece("oreille_" + nom, O.teinte(ore, SABLE * 0.94), None, pos=(c * 0.052, TETE.y + 0.020, TETE.z + 0.072), rot=(0, c * 14, 0))
    a.tete = TETE + Vector((0.0, -0.10, 0.0))

    # ----- les pattes : courtes ; l'antérieur droit levé, plié en l'air ; les autres posées -----
    plantees = (("avant_G", [(0.062, -0.150, 0.150), (0.072, -0.185, 0.090), (0.068, -0.205, 0.016)]),
                ("arriere_G", [(0.068, 0.450, 0.110), (0.080, 0.470, 0.060), (0.074, 0.440, 0.016)]),
                ("arriere_D", [(-0.068, 0.420, 0.110), (-0.080, 0.440, 0.060), (-0.074, 0.410, 0.016)]))
    for nom, points in plantees:
        patte = O.tube_r(points, [0.034, 0.028, 0.024], 12)
        a.piece("patte_" + nom, O.teinte(patte, SABLE * 0.96), None)
        pied = A.boule(1.0, 18, 8).etire(0.026, 0.040, 0.012)
        a.piece("pied_" + nom, O.teinte(pied, CHARBON * 1.3), None, pos=(points[-1][0], points[-1][1] - 0.012, 0.012), poil=False)
    levee = O.tube_r([(-0.062, -0.150, 0.150), (-0.076, -0.215, 0.115), (-0.070, -0.250, 0.080)], [0.034, 0.028, 0.024], 12)
    a.piece("patte_avant_D", O.teinte(levee, SABLE * 0.96), None)
    a.piece("pied_avant_D", O.teinte(A.boule(1.0, 18, 8).etire(0.026, 0.040, 0.012), CHARBON * 1.3), None,
            pos=(-0.070, -0.264, 0.080), rot=(30, 0, 0), poil=False)

    # ----- la queue : très longue, annelée de charbon, qui part en S derrière ; les bagues sont des tronçons peints -----
    pts = [(0.0, 0.600, 0.090), (0.0, 0.760, 0.075), (0.04, 0.900, 0.090), (0.10, 1.030, 0.085), (0.08, 1.150, 0.070)]
    paliers = [((k + 1) / 9, SABLE if k % 2 == 0 else CHARBON) for k in range(9)]
    a.piece("queue", K.tube_peint(A.courbe(pts, 6), lambda t_: 0.045 - 0.012 * t_, paliers, 16), None)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad", souple=True)


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("genette", styles.style_de("genette"), sys.modules[__name__]), "Genette")
