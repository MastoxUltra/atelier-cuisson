"""La gazelle en peluche cousue main : un caramel clair, le ventre blanc, la bande sombre qui sépare le dos et le
flanc, deux lignes brunes sur le visage de l'œil au museau, de longues oreilles étroites, de grands yeux noirs aux
longs cils, deux cornes annelées en lyre, de très longues jambes fines, une courte queue noire. La nerveuse :
l'arrêt net : un antérieur levé, la tête haute et tournée vers nous, les oreilles dressées, les narines frémissantes :
elle va bondir.

    python gazelle.py        fabrique la fiche art/apercus/animaux/gazelle.png (cousu main, palier 2)
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


CARAMEL = np.array(M.hexa("#f2c88a"))         # la dominante : caramel clair (le poil le fonce)
BLANC = np.array(M.hexa("#fffaf0"))           # le ventre, la croupe, le museau
BANDE = np.array(M.hexa("#8a5a38"))           # la bande du flanc, les lignes du visage
NOIR = np.array(M.hexa("#2e2824"))            # la queue, les sabots, les cornes
PAS = 0.007


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
    a = K.Animal("gazelle")
    a.taille = 1.20

    # ----- le corps : un fuseau élancé ; le dos caramel, la bande brune du flanc, le ventre et la croupe blancs -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.380, 0.560), (0.200, 0.600), (0.000, 0.610), (-0.200, 0.640), (-0.320, 0.660))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.080), (0.14, 0.125), (0.45, 0.135), (0.78, 0.140), (0.94, 0.100), (1.0, 0.0)], L, 64)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    f = corps.v[:, 2] / L
    t = np.tile(CARAMEL, (len(f), 1))
    t[(th > 1.50) & (th < 1.95)] = BANDE                                          # la bande sombre du flanc
    t[th >= 1.95] = BLANC
    t[f < 0.10] = BLANC                                                           # la croupe
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou et la tête fine ; les deux lignes brunes de l'œil au museau ; les longues oreilles ; les cornes en lyre -----
    a.piece("cou", A.tube(A.courbe([(0.0, -0.250, 0.680), (0.0, -0.340, 0.790), (0.0, -0.390, 0.890)], 5), lambda t: 0.082 - 0.030 * t, 20), tuple(CARAMEL))
    H = A.cadre(Vector((0.0, -0.400, 0.900)), Vector((0.40, -1.0, -0.30)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.060), (0.24, 0.074), (0.50, 0.060), (0.78, 0.046), (0.96, 0.040), (1.0, 0.0)], 0.300, 48, 0.006)
    tete.teinte = np.where(((tete.v[:, 2] > 0.80 * 0.300) | (np.abs(np.arctan2(tete.v[:, 0], tete.v[:, 1])) > 2.3))[:, None], BLANC, CARAMEL)
    # les bandes sombres du visage : de l'œil au museau, de chaque côté (peintes à plat)
    ang_ = np.arctan2(np.abs(tete.v[:, 0]), tete.v[:, 1])
    zz_ = tete.v[:, 2]
    centre_ = 1.15 + 0.70 * (zz_ - 0.13) / 0.13                                              # du flanc de la tête, à hauteur de l'œil, vers le dessus du museau
    dans_ = (zz_ > 0.12) & (zz_ < 0.285)
    tete.teinte[dans_ & (np.abs(ang_ - centre_) < 0.30)] = NOIR                               # la bande NOIRE large, de l'œil au nez
    tete.teinte[dans_ & (np.abs(ang_ - (centre_ - 0.52)) < 0.20)] = BLANC                     # la bande BLANCHE au-dessus
    tete.teinte[dans_ & (np.abs(ang_ - (centre_ + 0.52)) < 0.20)] = BLANC                     # et la bande BLANCHE au-dessous
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0, -0.050)))
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.028, 0.020, 0.016), M.hexa("#2e2824"), mat=H @ A.repere((0, 0.012, 0.246)), poil=False)
    a.tete = H @ Vector((0, 0.010, 0.140))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.60, 0.30, 0.52))
        p, n = a.surface("tete", H @ Vector((0, 0.0, 0.030)), regard)
        a.oeil("oeil_" + nom, p + n * 0.006, n, 0.0250)
        ligne = [H3 @ Vector((c * (0.82 - 0.30 * t), 0.30 - 0.34 * t, 0.10 + 0.34 * t)) for t in np.linspace(0, 1, 6)]
        a.broderie("ligne_" + nom, A.courbe(propres(a.trace("tete", H @ Vector((0, 0.0, 0.030)), ligne, 0.003)), 4), 0.0075, tuple(BANDE * 0.62))
        po = A.profil([(0, 0), (0.026, 0.010), (0.034, 0.050), (0.026, 0.100), (0.010, 0.140), (0, 0.152)], 6)
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.36, 1.0), tuple(CARAMEL),
                mat=A.cadre(H @ Vector((c * 0.052, 0.070, -0.010)), H3 @ Vector((c * 0.62, 0.10, 0.70)), H3 @ Vector((c * 0.3, -0.9, 0.0))))
        # les cornes en lyre : deux courbes annelées qui montent en S
        ch = [H @ Vector(q) for q in ((c * 0.034, 0.060, 0.020), (c * 0.058, 0.130, 0.000), (c * 0.078, 0.215, -0.030), (c * 0.068, 0.300, -0.072), (c * 0.040, 0.358, -0.104))]
        a.piece("corne_" + nom, K.tube_peint(A.courbe(propres(ch), 6), lambda t: 0.020 - 0.014 * t,
                                             [(0.15, tuple(NOIR)), (0.28, tuple(CARAMEL * 0.7)), (0.42, tuple(NOIR)), (0.58, tuple(CARAMEL * 0.7)),
                                              (0.74, tuple(NOIR)), (1, tuple(NOIR))], 12), None)

    # ----- les pattes : très longues, fines, le genou marqué, les sabots noirs ; un antérieur levé -----
    def patte(pts, r0):
        f_ = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.40, r0 * 0.54), (0.50, r0 * 0.66), (0.60, r0 * 0.44), (0.94, r0 * 0.40), (1.0, 0.0)], f_.long, 24, 0.008)
        m.teinte = np.where((m.v[:, 2] > 0.55 * f_.long)[:, None], CARAMEL * 0.96, CARAMEL)
        return m.sculpte(f_.couche)
    for nom, pts, r0 in (("av_D", [(-0.075, -0.220, 0.640), (-0.080, -0.230, 0.440), (-0.080, -0.220, 0.250), (-0.080, -0.230, 0.040)], 0.044),
                         ("ar_G", [(0.085, 0.300, 0.540), (0.095, 0.250, 0.380), (0.095, 0.320, 0.210), (0.095, 0.310, 0.040)], 0.052),
                         ("ar_D", [(-0.085, 0.300, 0.540), (-0.095, 0.250, 0.380), (-0.095, 0.320, 0.210), (-0.095, 0.310, 0.040)], 0.052),
                         ("av_G", [(0.075, -0.220, 0.640), (0.082, -0.240, 0.480), (0.084, -0.330, 0.450), (0.084, -0.360, 0.330)], 0.044)):
        a.piece("patte_" + nom, patte(pts, r0), None)
        a.piece("sabot_" + nom, A.boule(1.0, 20, 10).etire(0.030, 0.042, 0.026), tuple(NOIR), pos=(pts[-1][0], pts[-1][1] - 0.010, max(pts[-1][2] - 0.012, 0.026)), poil=False)
    a.piece("queue", A.tube(A.courbe([(0.0, 0.390, 0.560), (0.0, 0.430, 0.500), (0.0, 0.440, 0.430)], 5), 0.020, 10), tuple(NOIR))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("gazelle", styles.style_de("gazelle"), sys.modules[__name__]), "Gazelle")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py gazelle). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.588                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.126, 0.690)),
    ('cou', 'corps', (0.000, -0.204, 0.724)),
    ('tete', 'cou', (0.005, -0.377, 0.845)),
    ('oreille_G', 'tete', (0.075, -0.430, 0.953)),
    ('patte_av_D', 'corps', (-0.075, -0.223, 0.617)),
    ('patte_ar_G', 'corps', (0.086, 0.278, 0.524)),
    ('patte_av_G', 'corps', (0.076, -0.224, 0.623)),
    ('queue', 'corps', (0.004, 0.378, 0.555)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True),
    ('sabot_av', 'patte_av', True), ('sabot_ar', 'patte_ar', True), ('oreille', 'oreille', True), ('truffe', 'corps'),
    ('corps', 'corps'), ('corne', 'tete'), ('queue', 'queue'), ('ligne', 'corps'), ('tete', 'tete'), ('oeil', 'tete'),
    ('cou', 'cou'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'),
    ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('cou', rot=(2 * r, 0, 8 * g - 6 * d))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add('oreille_G', rot=(0, 0, 20 * cloche(t, 0.50, 0.05) - 8 * g))
    p.add('oreille_D', rot=(0, 0, -20 * cloche(t, 0.88, 0.05) + 6 * d))
    p.add('queue', rot=(0, 0, 10 * onde(t, 1)))
    p.ouvert = borne(1 - 0.3 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.62, 0.02))
    return p


def avance(t):
    """Sa marche : les pattes alternent, le corps oscille, la tête dodeline."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 26.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('cou', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('tete', rot=(3 - 2 * onde(t, 2, -0.2), -2 * c, -2 * s))
    p.paire('oreille', rot=(-8 + 3 * onde(t, 2, -0.25), 0, 0))
    p.add('queue', rot=(-6, 0, -10 * s))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('cou', rot=(34 * bas + 4 * coups, 0, 5 * leve))
    p.add('tete', rot=(18 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.paire('oreille', rot=(-6 * bas + 5 * leve, 0, 0))
    p.add('queue', rot=(0, 0, -7 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.176 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.323), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
