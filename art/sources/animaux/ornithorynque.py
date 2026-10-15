"""L'ornithorynque en peluche de magasin (3e dessin, d'après photos) : un castor aplati à bec de canard. Le corps est un
long coussin de poil brun acajou, plat, plaqué au sol, le ventre plus clair ; une tête ronde sans cou et un large BEC
spatulé gris sombre, plat comme une cuillère, aux narines en haut du bout ; une queue en PAGAIE plate comme celle d'un
castor, relevée ; quatre pattes courtes qui sortent sur les côtés, terminées par de larges palmes. Le curieux : la
tête un peu relevée qui renifle, le bec tendu, un petit œil tourné vers nous.

    python ornithorynque.py        fabrique la fiche art/apercus/animaux/ornithorynque.png (peluche de magasin, palier 3)
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


def propres(points, eps=2e-4):
    """Les points d'un tracé sans doublons consécutifs (deux points identiques à la suite déforment un tube en NaN)."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie


# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
ACAJOU = np.array(M.hexa("#8a5a42"))          # la dominante : brun acajou
VENTRE = np.array(M.hexa("#c8a890"))          # le ventre, le dessous des pattes
BEC = M.hexa("#5c5a66")                       # le bec : gris sombre bleuté
PALME = M.hexa("#c89c88")                     # les palmes
CHARBON = M.hexa("#2a2428")
LACET = 24.0
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("ornithorynque")
    a.taille = 0.55

    # ----- le corps : un long coussin plat, bas, le dos acajou, le ventre clair -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.220, 0.050), (0.100, 0.062), (-0.040, 0.070), (-0.140, 0.074))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.052), (0.22, 0.086), (0.55, 0.092), (0.86, 0.078), (0.97, 0.054), (1.0, 0.0)], L, 56)
    corps.v[:, 1] *= 0.62                                                         # plat
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.teinte = np.where((th > 2.2)[:, None], tuple(VENTRE), tuple(ACAJOU))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- la tête : un dôme rond, sans cou ; le BEC plat et large, spatulé, qui prolonge le museau ; les narines en haut -----
    H = A.repere(Vector((0.0, -0.200, 0.082)), (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.where((tete.v[:, 2] < -0.30)[:, None], tuple(VENTRE), tuple(ACAJOU))
    a.piece("tete", tete.etire(0.074, 0.082, 0.056), None, mat=H)
    bec = A.boule(1.0, 40, 20)
    a.piece("bec", bec.etire(0.082, 0.125, 0.016), BEC, mat=H @ A.repere((0.0, -0.140, -0.006), (-4, 0, 0)), poil=False)
    a.tete = H @ Vector((0, -0.200, -0.010))
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("narine_" + nom, A.boule(1.0, 12, 6).etire(0.010, 0.012, 0.006), CHARBON,
                mat=H @ A.repere((c * 0.024, -0.238, 0.014)), poil=False)
        regard = H3 @ Vector((c * 0.66, -0.40, 0.62))
        a.rustine("cerne_" + nom, "tete", H.to_translation(), regard, 0.20, tuple(VENTRE), 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0105)

    # ----- la queue en pagaie, plate et large, relevée au bout ; les quatre pattes : courtes, écartées, à larges palmes -----
    a.piece("queue", A.boule(1.0, 36, 18).etire(0.072, 0.155, 0.016), tuple(ACAJOU) and tuple(ACAJOU), pos=(0.0, 0.340, 0.050), rot=(10, 0, 0))
    for nom, c, y_ in (("av_G", 1, -0.100), ("av_D", -1, -0.100), ("ar_G", 1, 0.150), ("ar_D", -1, 0.150)):
        ch = [(c * 0.070, y_, 0.046), (c * 0.115, y_ - 0.010, 0.036), (c * 0.140, y_ - 0.020, 0.016)]
        m = A.tube(A.courbe(propres(ch), 5), lambda t: 0.024 - 0.008 * t, 12)
        m.teinte = np.tile(ACAJOU, (len(m.v), 1))
        a.piece("patte_" + nom, m, None)
        a.piece("palme_" + nom, A.boule(1.0, 20, 10).etire(0.062, 0.050, 0.008), PALME, pos=(c * 0.175, y_ - 0.040, 0.010), rot=(0, 0, c * -14), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("ornithorynque", styles.style_de("ornithorynque"), sys.modules[__name__]), "Ornithorynque")
