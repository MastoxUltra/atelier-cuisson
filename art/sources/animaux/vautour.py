"""Le vautour en peluche de velours ras : un brun sombre en grandes plumes lisses, le cou nu et ridé d'un rose gris, la
collerette de duvet blanc à la base du cou, la petite tête chauve au bec crochu fort, les yeux enfoncés sous un front
bas, de grandes ailes repliées en cape, des serres. L'attente : perché sur un tronc invisible, le dos voûté, le cou
rentré dans la collerette puis étiré, la tête de profil tournée vers nous, le bec en crochet, un regard patient de
croque-mort qui prend son temps.

    python vautour.py        fabrique la fiche art/apercus/animaux/vautour.png (velours ras, palier 3)
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


BRUN = np.array(M.hexa("#7a6250"))            # la dominante : brun sombre (le poil le fonce : on le prend plus clair)
PLUME = np.array(M.hexa("#9a8068"))           # les couvertures claires
PEAU = np.array(M.hexa("#e0a8a0"))            # le cou nu, la tête : rose gris
DUVET = np.array(M.hexa("#fff6e8"))           # la collerette
BEC = M.hexa("#c8b898")
OEIL = M.hexa("#c8903a")
CHARBON = M.hexa("#3a3230")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("vautour")
    a.taille = 1.10

    # ----- le corps : un œuf lourd, voûté, penché en avant ; les ailes en cape, de grandes plumes rangées -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.240, 0.250), (0.150, 0.420), (0.040, 0.570), (-0.060, 0.690))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.05, 0.150), (0.20, 0.230), (0.55, 0.240), (0.85, 0.180), (1.0, 0.0)], L, 64, 0.009)
    corps.teinte = np.where((np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1])) > 2.5)[:, None], PLUME, BRUN)
    a.piece("corps", corps.sculpte(fil.couche), None)
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 36, 18)
        aile.teinte = np.where((np.sin(16 * aile.v[:, 2]) > 0.7)[:, None], PLUME, BRUN)

        def galet(v):
            s = K.emousse(v, 0.88)
            s[:, 1] *= 1 - 0.42 * K.lisse((v[:, 2] + 0.2) / 1.2)
            return s
        a.piece("aile_" + nom, aile.sculpte(galet).etire(0.060, 0.120, 0.380), None, pos=(c * 0.205, 0.140, 0.430), rot=(-22, 0, c * 8))

    # ----- la collerette de duvet blanc ; le cou nu et ridé qui s'étire ; la petite tête chauve au bec crochu -----
    a.piece("collerette", A.boule(1.0, 36, 18).etire(0.150, 0.110, 0.090), tuple(DUVET), pos=(0.0, -0.040, 0.700))
    cou = K.tube_peint(A.courbe([(0.0, -0.020, 0.720), (0.0, -0.100, 0.800), (0.0, -0.160, 0.870)], 5), lambda t: 0.062 - 0.016 * t,
                       [(1, tuple(PEAU))], 18)
    a.piece("cou", cou, None)
    H = A.cadre(Vector((0.0, -0.200, 0.900)), Vector((0.62, -1.0, -0.12)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.056, 0.070, 0.058), tuple(PEAU), mat=H)
    bec = A.tour(A.profil([(0, 0), (0.040, 0.008), (0.040, 0.044), (0.030, 0.080), (0.016, 0.110), (0.004, 0.126), (0, 0.130)], 6), 28)
    bec.sculpte(lambda v: v + np.stack([np.zeros(len(v)), -0.030 * np.clip((v[:, 2] - 0.06) / 0.07, 0, 1) ** 1.6, np.zeros(len(v))], axis=1))
    a.piece("bec", bec, BEC, mat=A.cadre(H @ Vector((0, 0.0, 0.0)) + H3 @ Vector((0, -0.064, -0.006)), H3 @ Vector((0, -1.0, -0.10)), (0, 0, 1)), poil=False)
    a.tete = H @ Vector((0, -0.100, -0.010))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.84, -0.30, 0.30))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.20, OEIL, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0120)
        a.piece("lourde_" + nom, K.paupiere(0.0150, 0.18), tuple(PEAU), mat=A.cadre(p + n * 0.005, n, H3 @ Vector((0, 0, 1))), poil=False)

    # ----- la queue : un court éventail ; les serres : deux gros pieds gris à griffes noires, plantés sur le perchoir -----
    a.piece("queue", A.boule(1.0, 24, 12).etire(0.080, 0.180, 0.030), tuple(BRUN), pos=(0.0, 0.340, 0.180), rot=(-30, 0, 0))
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("jambe_" + nom, A.tube(A.courbe([(c * 0.080, 0.100, 0.300), (c * 0.086, 0.080, 0.160), (c * 0.088, 0.060, 0.050)], 5), 0.036, 12), tuple(PEAU), poil=False)
        doigts = None
        for ang in (-30, 0, 30):
            d = A.boule(1.0, 14, 8).etire(0.016, 0.076, 0.014).pose((0, -0.060, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("serres_" + nom, doigts, M.hexa("#8a7a74"), pos=(c * 0.088, 0.040, 0.018), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("vautour", styles.style_de("vautour"), sys.modules[__name__]), "Vautour")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py vautour). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.168                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.254, 0.504)),
    ('cou', 'corps', (0.000, -0.011, 0.735)),
    ('tete', 'cou', (-0.004, -0.161, 0.853)),
    ('patte_ar_G', 'corps', (0.088, 0.086, 0.305)),
    ('patte_av_G', 'corps', (0.069, -0.013, 0.031)),
    ('aile_G', 'corps', (0.187, 0.273, 0.778)),
    ('queue', 'corps', (-0.000, 0.215, 0.267)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('collerette', 'corps'), ('lourde', 'tete'), ('serres', 'patte_av', True),
    ('corps', 'corps'), ('jambe', 'patte_ar', True), ('queue', 'queue'), ('aile', 'aile', True), ('tete', 'tete'),
    ('iris', 'tete'), ('oeil', 'tete'), ('cou', 'cou'), ('bec', 'tete'), ('paupiere_0', 'paupiere_0'),
    ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('cou', rot=(2 * r, 0, 8 * g - 6 * d))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add('queue', rot=(0, 0, 10 * onde(t, 1)))
    p.paire('aile', rot=(0, -3 * cloche(t, 0.55, 0.06), 0))
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
    p.add('queue', rot=(-6, 0, -10 * s))
    p.paire('aile', rot=(0, -2 + 2 * onde(t, 2), 0))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.050 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    p.paire('aile', rot=(0, -48 * vol, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.092), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
