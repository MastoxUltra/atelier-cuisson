"""Le diable de Tasmanie en peluche de magasin (4e dessin, repris d'une autre base : un quadrupède trapu à la façon de
la mouffette, pas un monstre à la bouche ouverte) : un petit fauve noir et ramassé, le dos arqué et la croupe basse, une
TÊTE énorme, large et lourde portée bas, le museau court et la gueule fermée, de petits yeux, des oreilles rondes qui
rougissent, de courtes pattes épaisses, une queue courte et grasse, et une barre blanche en travers de la poitrine. Il
avance la tête basse, un œil sur nous : il a l'air de mauvaise humeur, c'est son métier.

    python diable_de_tasmanie.py        fabrique la fiche art/apercus/animaux/diable_de_tasmanie.png (peluche de magasin, palier 4)
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


# le style B adoucit les couleurs (vers leur gris) : le noir reste noir, le blanc doit rester franc
CHARBON = np.array(M.hexa("#3a3638"))         # la dominante : charbon profond
BLANC = M.hexa("#fffaf2")                     # l'accent : la barre de la poitrine
CENDRE = np.array(M.hexa("#7a7478"))          # le dessous du museau, le dessous des pattes
OREILLE = M.hexa("#e0586a")                   # le dedans des oreilles : elles rougissent
NEZ = M.hexa("#b8606c")
LACET, PIQUE = 30.0, -6.0
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
    a = K.Animal("diable_de_tasmanie")
    a.taille = 0.75

    # ----- le corps : un tonneau court et lourd, le dos arqué (le haut aux épaules), la croupe basse et large -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.320, 0.150), (0.170, 0.205), (0.000, 0.240), (-0.150, 0.250), (-0.250, 0.225))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.090), (0.16, 0.130), (0.46, 0.145), (0.76, 0.142), (0.93, 0.118), (0.985, 0.075), (1.0, 0.0)], L, 72)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.teinte = np.where((th > 2.5)[:, None], CENDRE, CHARBON)
    a.piece("corps", corps.sculpte(fil.couche), None)
    # la barre blanche : une large bande en croissant en travers de la poitrine (devant, de flanc à flanc)
    a.rustine("poitrine", "corps", Vector((0.0, -0.100, 0.190)), Vector((0.0, -0.90, -0.34)), 0.42, BLANC, 0.003, 0)

    # ----- le cou fort et la TÊTE : large, lourde, portée bas ; le museau court, la gueule fermée -----
    a.piece("cou", A.tube(A.courbe([(0.0, -0.200, 0.235), (0.0, -0.290, 0.225), (0.0, -0.350, 0.205)], 5), lambda t: 0.125 - 0.012 * t, 24), tuple(CHARBON))
    T = A.cadre(Vector((0.0, -0.400, 0.215)), Vector((0.50, -1.0, -0.22)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.082), (0.22, 0.118), (0.46, 0.114), (0.70, 0.094), (0.90, 0.074), (0.98, 0.048), (1.0, 0.0)], 0.290, 64, 0.005)
    tete.v[:, 0] *= 1.10
    tete.v[:, 1] *= 0.90
    tt = np.tile(CHARBON, (len(tete.v), 1))
    tt[(np.abs(np.arctan2(tete.v[:, 0], tete.v[:, 1])) > 2.3) & (tete.v[:, 2] > 0.12)] = CENDRE
    tete.teinte = tt
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.100)))
    a.piece("nez", A.boule(1.0, 24, 12).etire(0.034, 0.024, 0.022), NEZ, mat=T @ A.repere((0.0, 0.010, 0.182)), poil=False)
    a.tete = T @ Vector((0, 0.0, 0.140))
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.62, 0.50, 0.50))
        a.rustine("amande_" + nom, "tete", T @ Vector((0, 0.0, 0.020)), regard, 0.26, tuple(CENDRE), 0.003, 0)
        p, n = a.surface("tete", T @ Vector((0, 0.0, 0.020)), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0135)
        # l'oreille : ronde, plantée haut sur le côté, le dedans qui rougit
        po, no = a.surface("tete", T @ Vector((0, 0.0, 0.0)), T3 @ Vector((c * 0.66, 0.72, -0.28)))
        face, dresse = T3 @ Vector((c * 0.55, 0.45, 0.70)), no + T3 @ Vector((0, 0.2, -0.9))
        E = A.cadre(po + no * 0.010, face, dresse)
        a.piece("oreille_" + nom, A.boule(1.0, 28, 14).etire(0.046, 0.052, 0.016), tuple(CHARBON), mat=E)
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).etire(0.030, 0.036, 0.008), OREILLE, mat=E @ A.repere((0, -0.002, 0.011)), poil=False)
    bouche = a.trace("tete", T @ Vector((0, 0.0, 0.110)), [T3 @ Vector(d) for d in ((0.30, -0.90, 0.30), (0.62, -0.72, 0.10), (0.84, -0.40, -0.02))], 0.004)
    a.broderie("bouche", A.courbe(propres(bouche), 4), 0.0028, tuple(CENDRE))

    # ----- les pattes : courtes, épaisses, l'épaule et la cuisse fondues dans le corps ; les postérieures plus coudées ;
    #       de larges pieds ronds -----
    def patte(pts, r0):
        ft = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.30, r0 * 0.84), (0.62, r0 * 0.66), (0.90, r0 * 0.60), (1.0, 0.0)], ft.long, 28, 0.006)
        m.teinte = np.tile(CHARBON, (len(m.v), 1))
        return m.sculpte(ft.couche)
    for nom, c in (("G", 1), ("D", -1)):
        av = [(c * 0.100, -0.170, 0.215), (c * 0.108, -0.190, 0.120), (c * 0.108, -0.200, 0.032)]
        a.piece("patte_av_" + nom, patte(av, 0.074), None)
        a.piece("pied_av_" + nom, A.boule(1.0, 24, 12).etire(0.054, 0.070, 0.030), tuple(CHARBON), pos=(c * 0.108, -0.222, 0.030))
        ar = [(c * 0.110, 0.200, 0.205), (c * 0.130, 0.150, 0.120), (c * 0.118, 0.215, 0.036)]
        a.piece("patte_ar_" + nom, patte(ar, 0.084), None)
        a.piece("pied_ar_" + nom, A.boule(1.0, 24, 12).etire(0.054, 0.078, 0.030), tuple(CHARBON), pos=(c * 0.118, 0.195, 0.030))
    # la queue : courte et grasse, qui se termine en pointe émoussée
    qf = K.Fil([(0.0, 0.290, 0.170), (0.0, 0.370, 0.160), (0.0, 0.450, 0.130), (0.020, 0.510, 0.090)], (1, 0, 0))
    queue = fuseau([(0.0, 0.066), (0.30, 0.060), (0.75, 0.044), (0.94, 0.028), (1.0, 0.0)], qf.long, 32, 0.006)
    queue.teinte = np.tile(CHARBON, (len(queue.v), 1))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("diable_de_tasmanie", styles.style_de("diable_de_tasmanie"), sys.modules[__name__]), "Diable de Tasmanie")
