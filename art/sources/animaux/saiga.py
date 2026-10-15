"""Le saïga en peluche de velours ras (2e dessin) : un TRAPU, un mouton de la steppe sur des jambes fines mais noueuses
(genoux et jarrets marqués, petits sabots noirs), le dos voûté, le poil épais d'un beige jaune ; et ce NEZ, poussé à
l'excès : une énorme trompe molle et bombée, plus grosse que le museau, qui pend devant la bouche, les deux narines
grandes ouvertes vers le bas ; deux petites cornes cireuses ambrées, annelées, droites. L'étonné : debout, la tête
basse et tournée vers nous, l'énorme nez en avant, l'air surpris et sérieux.

    python saiga.py        fabrique la fiche art/apercus/animaux/saiga.png (velours ras, palier 3)
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


BEIGE = np.array(M.hexa("#f0dc9a"))           # la dominante : beige jaune de steppe (le poil le fonce)
CLAIR = np.array(M.hexa("#fff4d8"))           # le ventre, le dedans des pattes, le dessous de la face
OMBRE = np.array(M.hexa("#d8b878"))           # le dos, le front, le dessus de la trompe
NEZ = np.array(M.hexa("#e6c88a"))             # la trompe
CORNE = M.hexa("#e8c878")                     # les cornes cireuses, ambrées
CORNE_FONCE = M.hexa("#c09a50")
NOIR = M.hexa("#3a302a")
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
    a = K.Animal("saiga")
    a.taille = 1.20

    # ----- le corps : un tonneau trapu de mouton, plus profond que long, le dos voûté au garrot, le poil épais ;
    #       le dos plus sombre, le ventre clair -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.330, 0.560), (0.190, 0.610), (-0.020, 0.630), (-0.190, 0.640), (-0.300, 0.610))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.120), (0.14, 0.186), (0.40, 0.208), (0.72, 0.212), (0.90, 0.176), (0.97, 0.120), (1.0, 0.0)], L, 72, 0.006)
    f = corps.v[:, 2] / L
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.v[:, 1] += 0.040 * np.exp(-((f - 0.70) / 0.14) ** 2) * (corps.v[:, 1] > 0)            # le garrot voûté
    corps.teinte = np.where((th > 2.3)[:, None], CLAIR, np.where((th < 0.65)[:, None], OMBRE, BEIGE))
    a.piece("corps", corps.sculpte(fil.couche), None)
    a.piece("cou", A.tube(A.courbe([(0.0, -0.200, 0.640), (0.0, -0.300, 0.680), (0.0, -0.370, 0.700)], 5), lambda t: 0.118 - 0.034 * t, 24), tuple(BEIGE))

    # ----- la tête : un crâne bombé, un museau court et large ; baissée, tournée vers nous -----
    T = A.cadre(Vector((0.0, -0.430, 0.700)), Vector((0.46, -1.0, -0.30)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.07, 0.066), (0.26, 0.086), (0.50, 0.078), (0.76, 0.066), (0.94, 0.050), (1.0, 0.0)], 0.250, 52, 0.005)
    tt = np.where((tete.v[:, 1] > 0.030)[:, None], OMBRE, BEIGE)
    tt[(np.abs(np.arctan2(tete.v[:, 0], tete.v[:, 1])) > 2.3)] = CLAIR
    tete.teinte = tt
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.080)))
    a.tete = T @ Vector((0, -0.020, 0.200))

    # ----- LE NEZ : une énorme trompe molle, bombée, qui prend la place du museau et pend devant la bouche ;
    #       deux grandes narines noires tournées vers le bas ; un pli au milieu -----
    nf = K.Fil([tuple(T @ Vector(q)) for q in ((0.0, 0.030, 0.090), (0.0, 0.042, 0.170), (0.0, 0.020, 0.250), (0.0, -0.050, 0.310), (0.0, -0.130, 0.330))],
               (1, 0, 0))
    LN = nf.long
    trompe = fuseau([(0.0, 0.056), (0.12, 0.086), (0.40, 0.098), (0.72, 0.090), (0.90, 0.072), (0.98, 0.046), (1.0, 0.0)], LN, 64, 0.005)
    xt, yt, zt = trompe.v[:, 0], trompe.v[:, 1], trompe.v[:, 2]
    trompe.teinte = np.where((np.arctan2(xt, yt) > -9)[:, None] & (yt > 0.020)[:, None], tuple(OMBRE), tuple(NEZ))
    trompe.v[:, 0] *= 1.0 + 0.08 * np.exp(-((zt / LN - 0.55) / 0.25) ** 2)                      # un peu plus large que haute
    a.piece("trompe", trompe.sculpte(nf.couche), None)
    for nom, c in (("G", 1), ("D", -1)):
        cn, av_n, nq_n = nf.cadre(0.90 * LN)
        pos = np.array(cn) - np.array(nq_n) * 0.052 + np.array([c * 0.034, 0.0, 0.0]) + np.array(av_n) * 0.020
        a.piece("narine_" + nom, A.boule(1.0, 20, 10).etire(0.026, 0.024, 0.018), NOIR, pos=tuple(pos), poil=False)

    # ----- les yeux : hauts et petits, sur les côtés ; les cornes : deux petites tiges cireuses annelées ; les oreilles -----
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.84, 0.36, -0.10))
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0160)
        a.piece("lourde_" + nom, K.paupiere(0.0200, 0.26), tuple(OMBRE), mat=A.cadre(p + n * 0.005, n, T3 @ Vector((0, 1, 0))), poil=False)
        ch = [T @ Vector(q) for q in ((c * 0.036, 0.074, -0.030), (c * 0.050, 0.130, -0.034), (c * 0.058, 0.200, -0.040))]
        a.piece("corne_" + nom, K.tube_peint(A.courbe(propres(ch), 6), lambda t: 0.020 - 0.008 * t,
                                             [(0.16, tuple(CORNE)), (0.26, tuple(CORNE_FONCE)), (0.40, tuple(CORNE)), (0.50, tuple(CORNE_FONCE)),
                                              (0.64, tuple(CORNE)), (0.74, tuple(CORNE_FONCE)), (0.88, tuple(CORNE)), (1, tuple(CORNE))], 12), None)
        po = A.profil([(0, 0), (0.026, 0.008), (0.032, 0.034), (0.024, 0.062), (0.009, 0.082), (0, 0.090)], 5)
        a.piece("oreille_" + nom, A.tour(po, 20).etire(1.0, 0.40, 1.0), tuple(BEIGE),
                mat=A.cadre(T @ Vector((c * 0.078, 0.036, -0.074)), T3 @ Vector((c * 0.90, 0.10, -0.30)), T3 @ Vector((c * 0.3, 0.0, 1.0))))

    # ----- les pattes : fines mais noueuses : la cuisse ou l'épaule épaisse, le genou (ou le jarret) net, le canon grêle,
    #       le boulet, le petit sabot noir ; les postérieurs aux jarrets marqués -----
    def patte(pts, r0):
        ft = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.20, r0 * 0.82), (0.40, r0 * 0.58), (0.47, r0 * 0.70), (0.54, r0 * 0.48), (0.88, r0 * 0.42), (0.94, r0 * 0.54), (1.0, 0.0)],
                   ft.long, 28, 0.005)
        m.teinte = np.where((m.v[:, 2] > 0.55 * ft.long)[:, None], CLAIR, BEIGE)
        return m.sculpte(ft.couche)
    for nom, pts, r0 in (("av_G", [(0.095, -0.200, 0.600), (0.100, -0.210, 0.400), (0.102, -0.200, 0.230), (0.100, -0.205, 0.040)], 0.066),
                         ("av_D", [(-0.095, -0.200, 0.600), (-0.100, -0.210, 0.400), (-0.102, -0.200, 0.230), (-0.100, -0.205, 0.040)], 0.066),
                         ("ar_G", [(0.100, 0.250, 0.600), (0.112, 0.180, 0.400), (0.108, 0.280, 0.230), (0.106, 0.270, 0.040)], 0.074),
                         ("ar_D", [(-0.100, 0.250, 0.600), (-0.112, 0.180, 0.400), (-0.108, 0.280, 0.230), (-0.106, 0.270, 0.040)], 0.074)):
        a.piece("patte_" + nom, patte(pts, r0), None)
        a.piece("sabot_" + nom, A.boule(1.0, 20, 10).etire(0.030, 0.044, 0.026), NOIR, pos=(pts[-1][0], pts[-1][1] - 0.012, 0.026), poil=False)
    a.piece("queue", A.tube(A.courbe([(0.0, 0.340, 0.580), (0.0, 0.390, 0.540), (0.0, 0.400, 0.470)], 5), 0.020, 10), tuple(BEIGE))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("saiga", styles.style_de("saiga"), sys.modules[__name__]), "Saïga")
