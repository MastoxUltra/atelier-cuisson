"""Le quetzal en peluche de velours ras : un turquoise profond, penché vers le bleu (jamais le vert de l'herbe), le ventre
cramoisi, la tête coiffée d'une crête ronde en pompon, un petit bec jaune, et surtout les deux très longues plumes de
queue qui retombent à ses pieds comme des rubans de soie. Le dieu des cimes, perché sur ses pattes courtes : le
poitrail bombé, le dos droit, la tête de profil et le bec levé, une aile dépliée à moitié qui reflète le ciel.

    python quetzal.py        fabrique la fiche art/apercus/animaux/quetzal.png (velours ras, palier 3)
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

TURQUOISE = M.hexa("#1f9ad8")                 # la dominante : turquoise profond, qui penche vers le bleu
NUIT = M.hexa("#1560b8")                      # le dos, le bout des plumes : un ton plus bas
CRAMOISI = M.hexa("#e8244a")                  # l'accent : le ventre
BEC = M.hexa("#ffd22a")                       # le bec
BLANC = M.hexa("#fff8f0")                     # le dessous de la queue
CORPS = Vector((0.0, 0.040, 0.320))
TETE = Vector((0.0, -0.065, 0.560))
LACET = 32.0


def plume(chemin, large, face, paliers, plat=0.30, cotes=14):
    """Une longue plume plate (le geste des mèches du cheval) peinte par tronçons : paliers = [(fraction, couleur), ...]."""
    p = A.courbe(chemin, 8)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    n0 = np.asarray(face, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.linalg.norm(t, axis=1, keepdims=True)
        x = np.cross(n0, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.55 * large, 0.03 * L), (0.95 * large, 0.18 * L), (large, 0.40 * L), (0.85 * large, 0.70 * L),
                     (0.45 * large, 0.93 * L), (0, L)], 5)
    m = A.tour(prof, cotes).etire(1.0, plat, 1.0)
    t = np.zeros((len(m.v), 3))
    reste = np.ones(len(m.v), bool)
    for fr, c in paliers:
        ici = reste & (m.v[:, 2] <= fr * L)
        t[ici] = c
        reste &= ~ici
    t[reste] = paliers[-1][1]
    m.teinte = t
    return m.sculpte(couche)


def construire():
    a = K.Animal("quetzal")
    a.taille = 1.00                           # queue comprise

    # ----- le corps : un œuf dressé, le poitrail cramoisi devant (peint avant d'être sculpté), le dos bleu -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(TURQUOISE, float), (len(v), 1))
    t[(v[:, 1] < -0.18) & (v[:, 2] < 0.55)] = CRAMOISI
    t[(v[:, 1] > 0.45)] = NUIT
    corps.teinte = t

    def oeuf(v):
        v = K.bosse(v, (0, -0.9, 0.2), 0.14, 0.45)
        s = v * [0.098, 0.088, 0.160]
        s[:, 0] *= 1 - 0.18 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s
    a.piece("corps", corps.sculpte(oeuf), None, pos=CORPS, rot=(-10, 0, 0))

    # ----- la tête : ronde, la crête en pompon ; tournée de trois quarts, le bec levé -----
    H = A.repere(TETE, (-6, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 40, 20).etire(0.062, 0.060, 0.060), TURQUOISE, mat=H)
    a.piece("crete", A.boule(1.0, 28, 14).etire(0.060, 0.058, 0.052), TURQUOISE, mat=H @ A.repere((0, 0.018, 0.040)))
    a.tete = H @ Vector((0, -0.070, -0.005))
    B = A.cadre(H @ Vector((0, -0.054, -0.008)), H3 @ Vector((0, -0.97, 0.10)), H3 @ Vector((0, 0, 1)))
    bec = A.tour(A.profil([(0, 0), (0.024, 0.006), (0.021, 0.030), (0.012, 0.056), (0.004, 0.072), (0, 0.078)], 5), 24)
    a.piece("bec", bec.etire(0.88, 0.78, 1.0), BEC, mat=B, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.70, -0.62, 0.14)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0108)

    # ----- les ailes : deux galets bleus plaqués sur les flancs ; la gauche (vers nous) à moitié dépliée -----
    for nom, c, rot in (("G", 1, (-10, 0, 18)), ("D", -1, (-8, 0, -4))):
        aile = A.boule(1.0, 36, 18)
        aile.teinte = np.where((aile.v[:, 2] > 0.35)[:, None], np.asarray(NUIT), np.asarray(TURQUOISE))

        def galet(v):
            s = K.emousse(v, 0.88)
            s[:, 1] *= 1 - 0.50 * K.lisse((v[:, 2] + 0.2) / 1.2)
            return s
        a.piece("aile_" + nom, aile.sculpte(galet).etire(0.026, 0.052, 0.170), None, pos=(c * 0.100, 0.050, 0.290), rot=rot)

    # ----- la queue : deux très longues plumes plates, le dessus turquoise, qui retombent presque au sol, le bout nuit -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.020, 0.150, 0.280), (c * 0.050, 0.240, 0.140), (c * 0.075, 0.320, 0.040), (c * 0.110, 0.470, 0.018), (c * 0.140, 0.640, 0.016)]
        a.piece("plume_" + nom, plume(chemin, 0.034, (1, 0, 0), [(0.40, TURQUOISE), (0.88, NUIT), (1.0, BLANC)]), None, poil=False)

    # ----- les pattes : deux petits jonc, les doigts serrés en pince -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("patte_" + nom, A.tube(A.courbe([(c * 0.044, 0.030, 0.170), (c * 0.048, 0.000, 0.080), (c * 0.050, -0.030, 0.026)], 5), 0.017, 12),
                M.hexa("#c8a050"), poil=False)
        doigts = None
        for ang in (-28, 0, 28):
            d = A.boule(1.0, 14, 8).etire(0.011, 0.044, 0.010).pose((0, -0.034, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("doigts_" + nom, doigts, M.hexa("#c8a050"), pos=(c * 0.050, -0.030, 0.010), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("quetzal", styles.style_de("quetzal"), sys.modules[__name__]), "Quetzal")
