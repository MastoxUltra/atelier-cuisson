"""Le chat des sables en peluche de velours ras : un sable gris et froid, presque pâle, un petit chat trapu à la tête
LARGE et aplatie comme une galette, de grandes oreilles triangulaires plantées bas et écartées, des yeux dorés très
espacés, des favoris touffus en collerette, de courtes jambes à la plante poilue, une queue épaisse annelée au bout
noir. Le fantôme du désert : assis bien droit, les pattes avant côte à côte, la grosse tête tournée vers nous.

    python chat_des_sables.py        fabrique la fiche art/apercus/animaux/chat_des_sables.png (velours ras, palier 3)
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


SABLE = np.array(M.hexa("#ddd2bc"))           # la dominante : sable gris froid (le poil le fonce)
CLAIR = np.array(M.hexa("#faf4e6"))           # le ventre, le museau, le dedans des oreilles, les favoris
DOS = np.array(M.hexa("#c8b898"))             # le dos, le dessus de la tête
RAYE = np.array(M.hexa("#7a5c44"))            # l'accent : les barres des pattes, les anneaux de la queue
NOIR = np.array(M.hexa("#2e2826"))            # le bout de la queue, le nez
OR = M.hexa("#d8c060")                        # les yeux dorés
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=60, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("chat_des_sables")
    a.taille = 0.50

    # ----- le corps : une poire trapue assise, penchée en arrière, la poitrine claire ; les cuisses fondues dans les hanches -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.170, 0.070), (0.110, 0.180), (0.040, 0.300), (0.000, 0.390))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.05, 0.100), (0.20, 0.140), (0.55, 0.124), (0.86, 0.094), (1.0, 0.0)], L, 72)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.teinte = np.where((th > 2.3)[:, None], CLAIR, np.where((th < 1.0)[:, None], DOS, SABLE))
    corps.v[:, 0] *= 1 + 0.18 * np.exp(-((corps.v[:, 2] / L - 0.14) / 0.10) ** 2)
    a.piece("corps", corps.sculpte(fil.couche), None)
    for nom, c in (("G", 1), ("D", -1)):
        cu = A.boule(1.0, 32, 16)
        cu.teinte = np.tile(SABLE, (len(cu.v), 1))
        a.piece("cuisse_" + nom, cu.etire(0.062, 0.090, 0.082), None, mat=A.cadre(Vector((c * 0.092, 0.100, 0.104)), Vector((c * 0.10, -0.95, 0.10)), (0, 0, 1)))
        a.piece("pied_ar_" + nom, A.boule(1.0, 20, 10).etire(0.034, 0.070, 0.022), tuple(CLAIR), pos=(c * 0.100, -0.050, 0.022), rot=(0, 0, c * 5))

    # ----- la tête : LARGE et aplatie, le museau minuscule ; les favoris en collerette ; les grandes oreilles écartées -----
    T = A.cadre(Vector((0.0, -0.036, 0.462)), Vector((0.24, -1.0, -0.04)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    cr = A.boule(1.0, 56, 28)
    cr.teinte = np.where((cr.v[:, 1] > 0.30)[:, None], DOS, SABLE)
    a.piece("tete", cr.etire(0.118, 0.074, 0.088), None, mat=T)
    a.piece("museau", A.boule(1.0, 24, 12).etire(0.036, 0.030, 0.030), tuple(CLAIR), mat=T @ A.repere((0.0, -0.016, 0.074)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.013, 0.009, 0.009), tuple(NOIR), mat=T @ A.repere((0.0, 0.000, 0.098)), poil=False)
    a.tete = T @ Vector((0.0, 0.0, 0.080))
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("favori_" + nom, A.boule(1.0, 20, 10).etire(0.046, 0.034, 0.040), tuple(CLAIR), mat=T @ A.repere((c * 0.092, -0.026, 0.020), (0, 0, c * 18)))
        regard = T3 @ Vector((c * 0.72, 0.10, 0.52))
        a.rustine("iris_" + nom, "tete", T.to_translation(), regard, 0.17, OR, 0.003, 0)
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0170)
        a.piece("raie_" + nom, K.paupiere(0.0215, 0.24), tuple(RAYE), mat=A.cadre(p + n * 0.005, n, T3 @ Vector((0, 1, 0))), poil=False)
        po = A.profil([(0, 0), (0.054, 0.010), (0.056, 0.034), (0.044, 0.070), (0.026, 0.104), (0.010, 0.130), (0, 0.142)], 7)
        vers = (T3 @ Vector((c * 0.78, 0.60, -0.14))).normalized()
        E = A.cadre(T @ Vector((c * 0.088, 0.040, -0.016)) - vers * 0.010, vers, T3 @ Vector((c * 0.2, 0.0, 1.0)))
        a.piece("oreille_" + nom, A.tour(po, 36).etire(1.0, 0.30, 1.0), tuple(DOS), mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 28).etire(0.62, 0.30, 0.80).pose((0, 0.010, 0.012)), tuple(CLAIR), mat=E, poil=False)

    # ----- les pattes avant : d'une seule pièce, du poitrail au sol, des barres brunes ; la queue épaisse annelée -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.060, 0.030, 0.350), (c * 0.058, -0.020, 0.240), (c * 0.056, -0.050, 0.100), (c * 0.056, -0.066, 0.036), (c * 0.056, -0.108, 0.026)]
        fa = K.Fil(ch, (1, 0, 0))
        av = fuseau([(0.0, 0.050), (0.18, 0.046), (0.50, 0.032), (0.74, 0.026), (0.82, 0.030), (0.94, 0.030), (1.0, 0.0)], fa.long, 28, 0.005)
        zz = av.v[:, 2] / fa.long
        ta = np.tile(SABLE, (len(zz), 1))
        ta[(zz > 0.45) & (zz < 0.52)] = RAYE                                       # la barre brune de la patte
        ta[zz > 0.80] = CLAIR
        av.teinte = ta
        a.piece("patte_av_" + nom, av.sculpte(fa.couche), None)
    qf = K.Fil([(0.0, 0.150, 0.070), (0.0, 0.240, 0.050), (0.070, 0.310, 0.034), (0.160, 0.340, 0.030), (0.240, 0.300, 0.030)], (1, 0, 0))
    LQ = qf.long
    queue = fuseau([(0.0, 0.040), (0.30, 0.044), (0.70, 0.040), (0.90, 0.034), (0.98, 0.022), (1.0, 0.0)], LQ, 36, 0.006)
    zq = queue.v[:, 2] / LQ
    tq = np.tile(SABLE, (len(zq), 1))
    for c0 in (0.40, 0.56, 0.72):
        tq[(zq > c0) & (zq < c0 + 0.06)] = RAYE
    tq[zq > 0.86] = NOIR
    queue.teinte = tq
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("chat_des_sables", styles.style_de("chat_des_sables"), sys.modules[__name__]), "Chat des sables")
