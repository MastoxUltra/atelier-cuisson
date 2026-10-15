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


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py saiga). Les mesures sont celles du modèle, avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.56                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.26, 0.58)),         # les hanches : il se penche, se cabre, se couche autour
    ("cou", "corps", (0.0, -0.20, 0.64)),
    ("tete", "cou", (0.0, -0.37, 0.70)),            # la nuque
    ("trompe", "tete", (0.0, -0.45, 0.75)),         # la racine du nez : il se balance et frémit
    ("oreille_G", "tete", (0.060, -0.44, 0.76)),
    ("patte_av_G", "corps", (0.095, -0.20, 0.60)),  # l'épaule
    ("patte_ar_G", "corps", (0.100, 0.25, 0.60)),   # la hanche
    ("queue", "corps", (0.0, 0.34, 0.58)),
]

PORTEURS = [("corps", "corps"), ("cou", "cou"), ("tete", "tete"), ("trompe", "trompe"), ("narine", "trompe"), ("oeil", "tete"),
            ("lourde", "tete"), ("corne", "tete"), ("oreille", "oreille", True), ("patte_av", "patte_av", True),
            ("sabot_av", "patte_av", True), ("patte_ar", "patte_ar", True), ("sabot_ar", "patte_ar", True), ("queue", "queue"),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def repos(t):
    """Debout, il respire ; l'énorme nez se balance et frémit ; il tourne la tête, une oreille puis l'autre pivote ; la queue claque."""
    p = Pose()
    r, b = onde(t, 2), onde(t, 1)
    g, d = cloche(t, 0.28, 0.17), cloche(t, 0.72, 0.13)
    p.add("corps", ech=(1 + 0.010 * r, 1, 1 + 0.016 * r))
    p.add("cou", rot=(2 * r, 0, 8 * g - 6 * d))
    p.add("tete", rot=(2 * g, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add("trompe", rot=(7 * onde(t, 2, 0.15), 0, 5 * onde(t, 1, 0.3)), ech=(1, 1, 1 + 0.03 * r))
    p.add("oreille_G", rot=(0, 0, 24 * cloche(t, 0.50, 0.05) - 8 * g))
    p.add("oreille_D", rot=(0, 0, -24 * cloche(t, 0.90, 0.05) + 6 * d))
    p.add("queue", rot=(0, 0, 10 * cloche(t, 0.44, 0.04) - 10 * cloche(t, 0.50, 0.04)))
    p.ouvert = borne(1 - 0.30 * g - cloche(t, 0.06, 0.02) - cloche(t, 0.60, 0.02))
    return p


def avance(t):
    """Le trot menu de la steppe : les pattes vont par diagonales, le corps ne bouge presque pas, la tête dodeline,
    et le grand nez balance d'un côté à l'autre."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 26.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s)))
    p.add("corps", pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2 * s))
    for nom, sens in (("patte_av_G", 1), ("patte_ar_D", 1), ("patte_av_D", -1), ("patte_ar_G", -1)):
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.035 * max(0.0, -sens * c)))
    p.add("cou", rot=(-4 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add("tete", rot=(4 - 3 * onde(t, 2, -0.2), -2 * c, -2 * s))
    p.add("trompe", rot=(10 * onde(t, 2, -0.1), 0, 14 * onde(t, 1, 0.1)))
    p.paire("oreille", rot=(-8 + 4 * onde(t, 2, -0.25), 0, 0))
    p.add("queue", rot=(-6, 0, -10 * s))
    return p


def mange(t):
    """Il baisse la tête jusqu'à l'herbe, le nez en avant, quelques bouchées qui font frémir la trompe, puis relève la tête."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add("cou", rot=(40 * bas + 4 * coups, 0, 5 * leve))
    p.add("tete", rot=(22 * bas + 6 * coups, -3 * leve, 12 * leve))
    p.add("trompe", rot=(8 * coups - 10 * bas, 0, 6 * onde(t, 4) * bas))
    p.paire("patte_av", rot=(-8 * bas, 0, 0))
    p.paire("oreille", rot=(-6 * bas + 5 * leve, 0, 0))
    p.add("queue", rot=(0, 0, -8 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il bondit sur place les quatre pattes raides, comme les antilopes qui « pronkent », deux fois de suite, le nez qui
    flotte, les oreilles en arrière, la queue en l'air."""
    p = Pose()
    tasse = cloche(t, 0.10, 0.10, False)
    saut = max(0.0, onde(t, 2, -0.25)) * cloche(t, 0.58, 0.40, False)
    vol = 0.30 * saut
    salut = cloche(t, 0.88, 0.10, False)
    p.add("corps", pos=(0, 0, -0.05 * tasse + vol), rot=(-6 * saut + 6 * tasse, 0, 0))
    p.paire("patte_av", rot=(-8 * saut, 0, 0))
    p.paire("patte_ar", rot=(10 * saut, 0, 0))
    p.add("cou", rot=(-10 * saut + 12 * salut, 0, 0))
    p.add("tete", rot=(-6 * saut, 0, 0))
    p.add("trompe", rot=(-20 * saut + 6 * salut, 0, 8 * onde(t, 4) * saut))
    p.paire("oreille", rot=(-20 * saut, 0, 0))
    p.add("queue", rot=(-30 * saut, 0, 0))
    return p


def dort(t):
    """Couché sur le flanc, pattes allongées, la tête reposée sur le sol de côté, le nez qui bat doucement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.30), rot=(0, 0, 0), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire("patte_av", rot=(-72, 0, 14))
    p.paire("patte_ar", rot=(70, 0, 10))
    p.add("cou", rot=(34, 0, 48))
    p.add("tete", rot=(18, 6, 30))
    p.add("trompe", rot=(10 + 4 * onde(t, 1, 0.1), 0, 0))
    p.paire("oreille", rot=(-26, 0, 0))
    p.add("oreille_D", rot=(0, 0, -12 * cloche(t, 0.60, 0.05)))
    p.add("queue", rot=(10, 0, 12))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
