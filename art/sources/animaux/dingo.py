"""Le dingo en peluche de velours ras (2e dessin) : un crème sable clair, le dos juste lavé de fauve doré, la poitrine
et le bout des pattes blancs, la queue en brosse au bout blanc. Et une attitude : le chien sauvage au TROT, debout,
la tête basse et les oreilles en avant, la patte avant gauche levée au milieu de la foulée, la poitrine large, les
cuisses pleines, l'œil d'ambre fixé sur ce qu'il piste ; un seul regard en coin vers nous.

    python dingo.py        fabrique la fiche art/apercus/animaux/dingo.png (velours ras, palier 3)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K

SABLE = M.hexa("#fff0cc")                     # la dominante : crème sable clair (le poil la dore)
FAUVE = M.hexa("#e8c490")                     # le dos lavé de fauve
BLANC = M.hexa("#fffaf0")                     # la poitrine, le bout des pattes et de la queue
AMBRE = M.hexa("#f0b838")
CHARBON = M.hexa("#3a2e2c")
CORPS = Vector((0.0, 0.090, 0.480))
TETE = Vector((0.0, -0.480, 0.490))
LACET, PIQUE = 24.0, 22.0


def construire():
    a = K.Animal("dingo")
    a.taille = 1.20

    # ----- le corps : un long tonneau musclé, la poitrine large et profonde, le dos qui descend vers la croupe -----
    corps = A.boule(1.0, 64, 32)
    v = corps.v
    t = np.tile(np.asarray(SABLE, float), (len(v), 1))
    t[(v[:, 2] > 0.20) & (np.abs(v[:, 0]) < 0.82)] = FAUVE
    t[(v[:, 1] < -0.45) & (v[:, 2] < 0.30)] = BLANC
    corps.teinte = t

    def tonneau(v):
        v = K.bosse(v, (0, -0.85, -0.20), 0.18, 0.45)                          # la poitrine large
        s = v * [0.170, 0.480, 0.200]
        s[:, 2] *= 1 - 0.10 * K.lisse((v[:, 1] + 0.1) / 1.0)                  # la croupe un peu plus basse
        s[:, 0] *= 1 - 0.16 * K.lisse((v[:, 1] + 0.1) / 1.0)
        return s
    a.piece("corps", corps.sculpte(tonneau), None, pos=CORPS)

    # ----- la tête : un coin fin, le museau pointu ; basse, tournée de trois quarts, les oreilles en avant -----
    H = A.repere(TETE, (PIQUE, 0, LACET))
    H3 = H.to_3x3()

    def crane(v):
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.9, -0.30, -0.30), 0.14, 0.30)
        return v * [0.115, 0.112, 0.104]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(crane), FAUVE, mat=H)
    museau = A.tour(A.profil([(0, 0), (0.058, 0.006), (0.060, 0.034), (0.046, 0.074), (0.032, 0.108), (0.024, 0.128), (0, 0.140)], 6), 36)
    a.piece("museau", museau.etire(1.0, 0.82, 1.0), SABLE, mat=H @ A.repere((0, -0.070, -0.026), (90, 0, 0)))
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.024, 0.016, 0.016), CHARBON, mat=H @ A.repere((0, -0.210, -0.040)), poil=False)
    a.tete = H @ Vector((0, -0.150, -0.030))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.50, -0.82, 0.24))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.22, AMBRE, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0158)
        po = A.profil([(0, 0), (0.044, 0.010), (0.050, 0.050), (0.036, 0.100), (0.014, 0.140), (0, 0.158)], 6)
        E = A.cadre(H @ Vector((c * 0.078, 0.034, 0.070)), H3 @ Vector((c * 0.30, -0.50, 0.80)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, A.tour(po, 28).etire(1.0, 0.36, 1.0), FAUVE, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 20).etire(0.62, 0.30, 0.78).pose((0, 0.008, 0.010)), BLANC, mat=E, poil=False)

    # ----- le cou : épais, qui relie la poitrine à la tête basse ; les pattes : minces et nerveuses, au trot -----
    a.piece("cou", A.tube(A.courbe([(0.0, -0.250, 0.470), (0.0, -0.380, 0.490), (0.0, -0.460, 0.490)], 5), lambda t: 0.085 - 0.010 * t, 18), FAUVE)

    def patte(points, r0):
        return K.tube_peint(A.courbe(points, 8), lambda t: r0 * (1 - 0.40 * t) + 0.010 * math.exp(-((t - 0.52) / 0.09) ** 2),
                            [(0.80, SABLE), (1, BLANC)], 16)
    for nom, pts, r0 in (("av_D", [(-0.110, -0.260, 0.520), (-0.125, -0.250, 0.340), (-0.130, -0.230, 0.170), (-0.130, -0.250, 0.040)], 0.064),
                         ("ar_G", [(0.120, 0.380, 0.480), (0.150, 0.340, 0.330), (0.140, 0.430, 0.190), (0.140, 0.410, 0.040)], 0.080),
                         ("ar_D", [(-0.120, 0.380, 0.480), (-0.150, 0.420, 0.330), (-0.140, 0.480, 0.200), (-0.140, 0.560, 0.150)], 0.080)):
        a.piece("patte_" + nom, patte(pts, r0), None)
        x, y, z = pts[-1]
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.046, 0.074, 0.028), BLANC, pos=(x, y - 0.030, max(z, 0.028)),
                rot=(-20 if nom == "ar_D" else 0, 0, 0))
    levee = [(0.110, -0.260, 0.520), (0.125, -0.300, 0.400), (0.130, -0.400, 0.380), (0.130, -0.430, 0.260)]
    a.piece("patte_av_G", patte(levee, 0.064), None)
    a.piece("pied_av_G", A.boule(1.0, 24, 12).etire(0.046, 0.074, 0.028), BLANC, pos=(0.130, -0.462, 0.235), rot=(-50, 0, 0))

    # ----- la queue : en brosse, pendante et légèrement relevée, le bout blanc -----
    chemin = [(0.0, 0.520, 0.500), (0.0, 0.640, 0.440), (0.0, 0.740, 0.350)]
    queue = K.tube_peint(A.courbe(chemin, 6), lambda t: 0.050 + 0.022 * math.sin(math.pi * t) - 0.010 * t, [(0.82, FAUVE), (1, BLANC)], 16)
    a.piece("queue", queue, None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("dingo", styles.style_de("dingo"), sys.modules[__name__]), "Dingo")
