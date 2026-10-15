"""Le lièvre arctique en peluche cousue main (2e dessin : un vrai LIÈVRE, plus la boule lilas) : le lilas pâle de la
robe d'été, le ventre et le pompon de la queue blancs ; assis HAUT sur l'arrière-train, la croupe et les cuisses
énormes, les très longs pieds arrière à plat devant lui, le dos qui monte en pente vers des épaules étroites, de fines
pattes avant, une petite tête de lièvre aux yeux sombres, et deux LONGUES oreilles dressées, bien plus longues que la
tête, noires au bout. Il guette : il est prêt à bondir, un œil sur nous.

    python lievre_arctique.py        fabrique la fiche art/apercus/animaux/lievre_arctique.png (cousu main, palier 2)
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


LILAS = np.array(M.hexa("#e1d6f8"))           # la dominante : lilas pâle (le poil la dore : on la prend nettement plus claire)
OMBRE = np.array(M.hexa("#c7b8ec"))           # le dos, le dessous des pattes, un ton plus bas
CHARBON = np.array(M.hexa("#2d2831"))         # le bout des oreilles (l'accent), la truffe
NEIGE = np.array(M.hexa("#fffaf4"))           # le ventre, le pompon, le museau
JAUNE = M.hexa("#e8d070")                     # les yeux
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("lievre_arctique")
    a.taille = 0.80

    # ----- le corps : un tronc qui monte en pente de la croupe basse aux épaules étroites ; le dos plus sombre, le ventre blanc -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.200, 0.095), (0.110, 0.200), (0.000, 0.300), (-0.070, 0.370))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.05, 0.100), (0.22, 0.150), (0.50, 0.140), (0.80, 0.105), (0.96, 0.070), (1.0, 0.0)], L, 64)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.teinte = np.where((th > 2.3)[:, None], NEIGE, np.where((th < 1.0)[:, None], OMBRE, LILAS))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- les cuisses : énormes, fondues dans la croupe ; les longs pieds arrière, à plat devant elles -----
    for nom, c in (("G", 1), ("D", -1)):
        cu = A.boule(1.0, 36, 18)
        cu.teinte = np.tile(LILAS, (len(cu.v), 1))
        a.piece("cuisse_" + nom, cu.etire(0.074, 0.130, 0.120), None, mat=A.cadre(Vector((c * 0.108, 0.135, 0.150)), Vector((c * 0.10, -0.90, 0.30)), (0, 0, 1)))
        pd = A.boule(1.0, 24, 12)
        pd.teinte = np.where((pd.v[:, 2] < 0.0)[:, None], tuple(OMBRE), tuple(LILAS))
        a.piece("pied_ar_" + nom, pd.etire(0.040, 0.170, 0.030), None, pos=(c * 0.112, 0.020, 0.030), rot=(0, 0, c * 6))

    # ----- les pattes avant : fines, droites, serrées sous le menton, les petites mains blanches -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.050, -0.045, 0.300), (c * 0.054, -0.085, 0.160), (c * 0.054, -0.100, 0.034)]
        a.piece("patte_av_" + nom, A.tube(A.courbe(propres(ch), 5), lambda t: 0.028 - 0.010 * t, 12), tuple(LILAS))
        a.piece("main_" + nom, A.boule(1.0, 16, 8).etire(0.024, 0.036, 0.018), tuple(NEIGE), pos=(c * 0.054, -0.112, 0.020))

    # ----- la tête : petite, le museau fin et blanc, les joues pleines ; haute, tournée vers nous -----
    T = A.cadre(Vector((0.0, -0.120, 0.420)), Vector((0.38, -1.0, 0.06)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.08, 0.062), (0.30, 0.078), (0.58, 0.068), (0.84, 0.050), (0.97, 0.034), (1.0, 0.0)], 0.180, 48, 0.004)
    tete.teinte = np.where((tete.v[:, 2] > 0.60 * 0.180)[:, None], tuple(NEIGE), tuple(LILAS))
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.060)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.016, 0.012, 0.012), tuple(CHARBON), mat=T @ A.repere((0, 0.004, 0.116)), poil=False)
    a.tete = T @ Vector((0, 0.0, 0.080))
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.80, 0.32, 0.30))
        a.rustine("iris_" + nom, "tete", T.to_translation(), regard, 0.17, JAUNE, 0.003, 0)
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0155)
        # l'oreille : LONGUE, étroite, dressée un peu en arrière, le bout noir
        po = A.profil([(0, 0), (0.036, 0.010), (0.040, 0.060), (0.034, 0.130), (0.024, 0.190), (0.010, 0.228), (0, 0.240)], 6)
        vers = (T3 @ Vector((c * 0.26, 0.94, -0.18))).normalized()
        E = A.cadre(T @ Vector((c * 0.040, 0.050, -0.030)) - vers * 0.008, vers, T3 @ Vector((c * 0.2, 0.0, 1.0)))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 36).etire(1.0, 0.30, 1.0), [(0.190, tuple(LILAS)), (9, tuple(CHARBON))]), None, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 28).etire(0.58, 0.26, 0.84).pose((0, 0.008, 0.010)), M.hexa("#f2c6d8"), mat=E, poil=False)

    # ----- le pompon : une petite boule blanche à la croupe -----
    q = A.boule(1.0, 20, 10)
    q.teinte = np.tile(NEIGE, (len(q.v), 1))
    a.piece("queue", q.etire(0.040, 0.040, 0.040), None, pos=(0.0, 0.232, 0.130))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lievre_arctique", styles.style_de("lievre_arctique"), sys.modules[__name__]), "Lièvre arctique")
