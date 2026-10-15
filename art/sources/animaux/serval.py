"""Le serval en peluche de velours ras (3e dessin) : un abricot vif, un chat tout en hauteur, le corps assis très droit,
les cuisses fondues dans les hanches, les deux pattes avant d'une seule pièce qui descendent droit du poitrail jusqu'au
sol, fines et longues, avec un poignet net et une petite patte crème ; un cou long et fin semé de petits points noirs,
une toute petite tête aux immenses oreilles rondes (le dos noir à tache blanche), le museau court, de larges
mouchetures rondes sur le corps, une queue courte annelée. L'écouteur : assis à l'affût, les oreilles braquées sur un
bruit que lui seul entend, un œil sur nous.

    python serval.py        fabrique la fiche art/apercus/animaux/serval.png (velours ras, palier 3)
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


ABRICOT = np.array(M.hexa("#ffb860"))         # la dominante : abricot vif (le poil le fonce)
CREME = np.array(M.hexa("#fff2dc"))           # le ventre, le menton, la tache de l'oreille, les petites pattes
NOIR = np.array(M.hexa("#2e2824"))            # l'accent : les mouchetures, le dos des oreilles
OEIL = M.hexa("#e8b84a")
CHARBON = M.hexa("#2e2824")
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def mouchetures(v, cote, rayon, graine=0, proba=0.72):
    """Vrai là où un point tombe dans une tache : des sphères posées au hasard dans un quadrillage en 3D (une par case,
    certaines absentes) ; la surface les coupe en ronds de tailles variées, jamais en carrés."""
    v = np.asarray(v, float)
    base = np.floor(v / cote).astype(np.int64)
    dedans = np.zeros(len(v), bool)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                c = base + np.array([dx, dy, dz], dtype=np.int64)
                h = ((c[:, 0] * 73856093) ^ (c[:, 1] * 19349663) ^ (c[:, 2] * 83492791) ^ (graine * 40503)) & 0x7FFFFFFF

                def alea(m):
                    return ((((h * m) + 12345) >> 9) & 0xFFFF) / 65535.0
                present = alea(1103515245) < proba
                centre = (c + np.stack([alea(214013), alea(1664525), alea(22695477)], axis=1)) * cote
                r = rayon * (0.55 + 0.9 * alea(134775813))
                dedans |= present & (np.linalg.norm(v - centre, axis=1) < r)
    return dedans


def construire():
    a = K.Animal("serval")
    a.taille = 1.10

    # ----- le tronc : d'une seule pièce, des hanches assises jusqu'au cou fin ; assis très droit ; moucheté de ronds noirs
    #       (gros sur le corps, petits sur le cou), la poitrine crème -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.290, 0.130), (0.250, 0.330), (0.170, 0.560), (0.080, 0.770), (0.010, 0.940), (-0.040, 1.070))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.03, 0.140), (0.12, 0.200), (0.28, 0.200), (0.46, 0.160), (0.60, 0.128), (0.72, 0.092), (0.84, 0.072),
                    (0.96, 0.066), (1.0, 0.0)], L, 96, 0.005)
    x, y, z = corps.v[:, 0], corps.v[:, 1], corps.v[:, 2]
    f = z / L
    corps.v[:, 0] *= 1 + 0.22 * np.exp(-((f - 0.12) / 0.10) ** 2)                      # les hanches larges où les cuisses se fondent
    taches = np.where(f > 0.70, mouchetures(corps.v, 0.034, 0.0105, 3), mouchetures(corps.v, 0.052, 0.024, 7))
    t = np.tile(ABRICOT, (len(z), 1))
    t[taches] = NOIR
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t[(th > 2.4) & (f > 0.20) & (f < 0.86)] = CREME                                     # la poitrine
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- les cuisses : deux gros ovales à demi enfoncés dans les hanches, assis dessus ; les grands pieds crème -----
    for nom, c in (("G", 1), ("D", -1)):
        cu = A.boule(1.0, 36, 18)
        cu.teinte = np.where(mouchetures(cu.v * [0.10, 0.17, 0.14], 0.052, 0.024, 11 + (c > 0))[:, None], NOIR, ABRICOT)
        a.piece("cuisse_" + nom, cu.etire(0.100, 0.170, 0.140), None, mat=A.cadre(Vector((c * 0.120, 0.170, 0.182)), Vector((c * 0.10, -0.95, 0.10)), (0, 0, 1)))
        a.piece("pied_ar_" + nom, A.boule(1.0, 20, 10).etire(0.040, 0.090, 0.026), tuple(CREME), pos=(c * 0.132, -0.050, 0.026), rot=(0, 0, c * 6))

    # ----- la tête : toute petite, le museau court ; de grandes oreilles rondes dressées, le dos noir à tache blanche -----
    T = A.cadre(Vector((0.0, -0.060, 1.130)), Vector((0.46, -1.0, -0.10)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.08, 0.075), (0.30, 0.094), (0.58, 0.080), (0.78, 0.066), (0.90, 0.056), (0.96, 0.042), (0.99, 0.024), (1.0, 0.0)], 0.240, 56, 0.004)
    tt = np.where(mouchetures(tete.v, 0.040, 0.011, 5)[:, None], NOIR, ABRICOT)
    tt[((tete.v[:, 2] > 0.170) & (tete.v[:, 1] < 0.012)) | (np.abs(np.arctan2(tete.v[:, 0], tete.v[:, 1])) > 2.3)] = CREME
    tete.teinte = tt
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.060)))
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.022, 0.016, 0.014), CHARBON, mat=T @ A.repere((0, 0.006, 0.172)), poil=False)
    a.tete = T @ Vector((0, 0.0, 0.120))
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.74, 0.22, 0.14))
        a.rustine("iris_" + nom, "tete", T.to_translation(), regard, 0.20, OEIL, 0.003, 0)
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0165)
        # l'oreille : une grande feuille ronde DRESSÉE ; le dos noir, la tache blanche, le dedans abricot
        E = A.cadre(T @ Vector((c * 0.058, 0.060, -0.010)), T3 @ Vector((c * 0.26, 0.95, -0.10)), T3 @ Vector((c * 0.25, 0.0, 1.0)))
        a.piece("oreille_" + nom, A.boule(1.0, 36, 18).etire(0.080, 0.022, 0.150).pose((0, 0, 0.120)), tuple(NOIR), mat=E)
        a.piece("tache_" + nom, A.boule(1.0, 24, 12).etire(0.040, 0.012, 0.052).pose((0, -0.016, 0.140)), tuple(CREME), mat=E, poil=False)
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).etire(0.058, 0.014, 0.124).pose((0, 0.017, 0.120)), tuple(ABRICOT), mat=E, poil=False)

    # ----- les pattes avant : d'une seule pièce, de l'épaule noyée dans le poitrail jusqu'au sol ; longues, fines, le poignet net,
    #       la petite patte crème vers l'avant -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.082, 0.100, 0.640), (c * 0.080, 0.020, 0.470), (c * 0.078, -0.030, 0.280), (c * 0.078, -0.056, 0.100), (c * 0.078, -0.086, 0.034),
              (c * 0.078, -0.150, 0.026)]
        fa = K.Fil(ch, (1, 0, 0))
        av = fuseau([(0.0, 0.030), (0.05, 0.056), (0.15, 0.064), (0.35, 0.048), (0.55, 0.036), (0.70, 0.028), (0.77, 0.034), (0.82, 0.026),
                     (0.90, 0.034), (0.97, 0.028), (1.0, 0.0)], fa.long, 28, 0.006)
        ta = np.tile(ABRICOT, (len(av.v), 1))
        ta[mouchetures(av.v, 0.040, 0.014, 21 + (c > 0))] = NOIR
        ta[av.v[:, 2] > 0.80 * fa.long] = CREME
        av.teinte = ta
        a.piece("patte_av_" + nom, av.sculpte(fa.couche), None)
    # la queue : courte, annelée de noir, qui s'enroule contre les pattes
    chemin = [(0.0, 0.340, 0.080), (0.120, 0.400, 0.040), (0.220, 0.300, 0.034), (0.200, 0.140, 0.034)]
    bagues, fz, c = [], 0.0, tuple(ABRICOT)
    while fz < 0.86:
        fz += 0.14
        bagues.append((min(fz, 0.86), c))
        c = tuple(NOIR) if c == tuple(ABRICOT) else tuple(ABRICOT)
    bagues[-1] = (0.86, bagues[-1][1])
    bagues.append((1.0, tuple(NOIR)))
    a.piece("queue", K.tube_peint(A.courbe(chemin, 6), lambda t: 0.046 - 0.014 * t, bagues, 14), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("serval", styles.style_de("serval"), sys.modules[__name__]), "Serval")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py serval). Les mesures sont celles du modèle (assis très droit), avant a.taille.
# Le tronc est d'une seule pièce, du bassin aux oreilles : il pivote autour des hanches (« corps »), la tête et les
# oreilles s'articulent au bout. Les pattes avant se contre-tournent pour que les petites pattes restent au sol.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.20, 0.15)),            # les hanches : il se penche, se cabre, se couche autour
    ("tete", "corps", (0.0, -0.05, 1.06)),             # la nuque
    ("oreille_G", "tete", (0.060, -0.06, 1.16)),       # la base de l'oreille
    ("patte_av_G", "corps", (0.082, 0.10, 0.64)),      # l'épaule
    ("cuisse_G", "corps", (0.120, 0.17, 0.18)),        # la hanche : la cuisse et le grand pied arrière
    ("queue", "corps", (0.0, 0.33, 0.08)),
]

PORTEURS = [("corps", "corps"), ("tete", "tete"), ("truffe", "tete"), ("iris", "tete"), ("oeil", "tete"),
            ("oreille", "oreille", True), ("tache", "oreille", True), ("dedans", "oreille", True),
            ("patte_av", "patte_av", True), ("cuisse", "cuisse", True), ("pied_ar", "cuisse", True), ("queue", "queue"),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def pattes(p, rx):
    """Le tronc pique de rx degrés autour des hanches : les pattes avant se contre-tournent, et restent plantées."""
    p.paire("patte_av", rot=(-rx, 0, 0))


def repos(t):
    """Assis très droit, il écoute : les oreilles se tournent l'une après l'autre vers des bruits que lui seul entend ; la
    tête se tend, un regard de côté ; le bout de la queue remue."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.30, 0.17), cloche(t, 0.74, 0.13)
    p.add("corps", ech=(1 + 0.008 * r, 1, 1 + 0.010 * r), rot=(0.6 * r, 0, 0))
    p.add("tete", rot=(4 * g - 3 * d, -5 * g + 4 * d, 20 * g - 16 * d))
    p.add("oreille_G", rot=(0, 0, 22 * cloche(t, 0.52, 0.05) - 10 * g))
    p.add("oreille_D", rot=(0, 0, -22 * cloche(t, 0.90, 0.05) + 8 * d))
    p.add("queue", rot=(0, 0, 14 * onde(t, 1)))
    p.ouvert = borne(1 - 0.30 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.62, 0.02))
    return p


def avance(t):
    """Il avance par petits bonds, penché en avant, les pattes avant qui tendent le pas l'une après l'autre, la queue qui fouette."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    saut = max(0.0, s)
    rx = 14 + 4 * onde(t, 2, 0.1)
    p.add("corps", pos=(0, 0, 0.05 * saut), rot=(rx, 2 * c, 2 * s))
    pattes(p, rx)
    p.add("patte_av_G", rot=(-16 * max(0.0, s), 0, 0))
    p.add("patte_av_D", rot=(-16 * max(0.0, -s), 0, 0))
    p.paire("cuisse", rot=(-10 * saut, 0, 0))
    p.add("tete", rot=(-10 + 3 * onde(t, 2, -0.2), -3 * c, -2 * s))
    p.paire("oreille", rot=(-14, 0, 0))
    p.add("queue", rot=(-10, 0, -18 * s))
    return p


def mange(t):
    """Il se penche en avant jusqu'au sol, flaire, trois coups de dents, puis se redresse et mâche l'oreille en l'air."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    rx = 38 * bas + 3 * coups
    p.add("corps", rot=(rx, 0, 0))
    pattes(p, rx)
    p.add("tete", rot=(18 * bas + 8 * coups + 3 * leve * onde(t, 12), -4 * leve, 12 * leve))
    p.paire("oreille", rot=(-6 * bas + 6 * leve, 0, 0))
    p.add("queue", rot=(-8 * bas, 0, -6 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Le bond du chasseur d'oiseaux : il se tasse, jaillit tout droit très haut, les pattes en croix, les oreilles dressées,
    retombe sur les pattes avant et fouette de la queue."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    rx = 18 * tasse - 10 * vol + 14 * salut
    p.add("corps", pos=(0, 0, -0.04 * tasse + 0.34 * vol), rot=(rx, 0, 0))
    pattes(p, rx)
    p.paire("patte_av", rot=(-24 * vol, 0, 14 * vol))
    p.paire("cuisse", rot=(-30 * vol, 0, 0))
    p.add("tete", rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire("oreille", rot=(-16 * vol, 0, 0))
    p.add("queue", rot=(-18 * vol, 0, -24 * fouet))
    return p


def dort(t):
    """Il s'assoupit assis : le tronc glisse en avant, la tête tombe sur la poitrine, les pattes avant repliées, les
    oreilles rabattues, la queue ramenée devant ; une oreille tressaille."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    rx = 42
    p.add("corps", pos=(0, 0, -0.02), rot=(rx, 0, 6), ech=(1 + 0.010 * r, 1, 1 + 0.020 * r))
    pattes(p, rx * 0.8)
    p.add("tete", rot=(38, 0, 22))
    p.paire("oreille", rot=(-30, 0, 0))
    p.add("oreille_D", rot=(0, 0, -14 * cloche(t, 0.55, 0.05)))
    p.add("queue", rot=(0, 0, 70))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
