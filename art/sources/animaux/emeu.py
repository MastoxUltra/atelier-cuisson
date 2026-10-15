"""L'émeu en peluche de velours ras (2e dessin, d'après photos : plus de jupe jusqu'au sol) : un grand oiseau debout, un
gros corps ovoïde recouvert d'un plumage hirsute en mèches courtes qui retombent sur le dos et les flancs (la poitrine
et le dessous plus lisses), un taupe lavande chiné de plus sombre ; un cou fort, long et nu, bleuté, qui porte une tête
moyenne au grand œil d'ambre sous de longs cils et au bec court et sombre ; et surtout de LONGUES jambes grises bien
visibles, aux gros pieds à trois doigts, plantées droites sous lui. Il se tient haut, le cou tendu vers nous.

    python emeu.py        fabrique la fiche art/apercus/animaux/emeu.png (velours ras, palier 3)
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


TAUPE = np.array(M.hexa("#bcaabc"))           # la dominante : taupe lavande (le poil la fonce : on la prend claire)
SOMBRE = np.array(M.hexa("#8a7888"))          # les mèches du dos, la croupe
COU = np.array(M.hexa("#9ec0d8"))             # le cou nu, bleuté
AMBRE = M.hexa("#e8a830")
CHARBON = M.hexa("#3a3036")
PATTE = np.array(M.hexa("#8a7a78"))
BEC = M.hexa("#6a5a5c")
CORPS = Vector((0.0, 0.080, 0.640))
LACET = 0.0                                   # la tête droite : le corps symétrique, les deux yeux de face


def construire():
    a = K.Animal("emeu")
    a.taille = 1.80

    # ----- le corps : un gros œuf bien posé sur les jambes, le dos arrondi ; le dessous lisse, plus clair -----
    def oeuf(v):
        s = v * [0.230, 0.320, 0.260]
        s[:, 1] += 0.020 * v[:, 2]
        return s
    corps = A.boule(1.0, 56, 28)
    corps.teinte = np.where((corps.v[:, 2] < -0.35)[:, None], tuple(TAUPE * 1.05), tuple(TAUPE))
    a.piece("corps", corps.sculpte(oeuf), None, pos=CORPS, rot=(-6, 0, 0))

    # ----- le plumage hirsute : des touffes de mèches courtes et épaisses, qui retombent du dos et des flancs, le plus
    #       long à la croupe ; elles couvrent le haut, pas le ventre, et s'arrêtent bien au-dessus des jambes -----
    rng = np.random.default_rng(9)
    touffes = None
    for i in range(46):
        z = rng.uniform(-0.15, 0.95)
        t = rng.uniform(0.0, 2 * math.pi)
        r = math.sqrt(max(0.0, 1 - z * z))
        d = np.array([r * math.cos(t), r * math.sin(t), z])
        if d[1] < -0.55 and z < 0.3:
            continue                                                              # pas sur la poitrine, plus lisse
        p = np.array(CORPS) + d * np.array([0.236, 0.326, 0.266])
        long_ = 0.080 + 0.060 * rng.random() + 0.040 * max(0.0, d[1])
        m = A.boule(1.0, 10, 6).etire(0.036, 0.030, long_).pose(tuple(p + np.array([d[0] * 0.01, d[1] * 0.01, -long_ * 0.70])),
                                                                 (12 * d[1], -14 * d[0], 0))
        touffes = m if touffes is None else touffes + m
    a.piece("plumage", touffes, tuple(SOMBRE))

    # ----- le cou : long, fort et nu, bleuté, qui part de la poitrine et se tend vers nous en S doux ; la tête moyenne -----
    fil = K.Fil([(0.0, -0.200, 0.780), (0.0, -0.310, 0.950), (0.0, -0.300, 1.150), (0.0, -0.360, 1.320)], (1, 0, 0))
    L = fil.long
    pc = A.profil([(0, 0), (0.095, 0.03 * L), (0.068, 0.30 * L), (0.056, 0.70 * L), (0.052, 0.95 * L), (0, 1.01 * L)], 6)
    cou = A.tour(pc, 28)
    cou.teinte = np.tile(COU, (len(cou.v), 1))
    a.piece("cou", cou.sculpte(fil.couche), None)
    bout = Vector(fil.cadre(L)[0])
    H = A.repere(bout + Vector((0.0, -0.030, 0.020)), (6, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 36, 18)
    tete.teinte = np.tile(TAUPE * 1.04, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.062, 0.082, 0.060), None, mat=H)
    a.tete = H @ Vector((0, -0.100, -0.010))
    bec = A.tour(A.profil([(0, 0), (0.034, 0.006), (0.030, 0.030), (0.018, 0.055), (0, 0.068)], 5), 24)
    a.piece("bec", bec.etire(1.0, 0.70, 1.0), BEC, mat=A.cadre(H @ Vector((0, -0.070, -0.014)), H3 @ Vector((0, -0.96, -0.20)), (0, 0, 1)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.82, -0.40, 0.18))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.30, AMBRE, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0190)
        # (paupière retirée : yeux ouverts, bouton net, sans air fatigué ni fâché)

    # ----- les pattes : très longues, grises, le genou marqué, les gros pieds à trois doigts, plantées droites ; bien visibles -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.100, 0.070, 0.470), (c * 0.108, 0.060, 0.300), (c * 0.108, 0.120, 0.140), (c * 0.108, 0.110, 0.030)]
        m = A.tube(A.courbe(propres(ch), 6), lambda t: 0.050 - 0.020 * t, 14)
        m.teinte = np.tile(PATTE, (len(m.v), 1))
        a.piece("patte_" + nom, m, None, poil=False)
        doigts = None
        for ang in (-28, 0, 28):
            d = A.boule(1.0, 14, 8).etire(0.016, 0.075, 0.014).pose((0, -0.060, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("doigts_" + nom, doigts, tuple(PATTE), pos=(c * 0.108, 0.090, 0.014), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("emeu", styles.style_de("emeu"), sys.modules[__name__]), "Émeu")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py emeu). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.249                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.235, 0.655)),
    ('cou', 'corps', (0.000, -0.155, 0.819)),
    ('tete', 'cou', (-0.003, -0.367, 1.285)),
    ('patte_ar_G', 'corps', (0.101, 0.067, 0.471)),
    ('patte_av_G', 'corps', (0.090, 0.036, 0.027)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('plumage', 'corps'), ('doigts', 'patte_av', True), ('corps', 'corps'),
    ('patte', 'patte_ar', True), ('tete', 'tete'), ('iris', 'tete'), ('oeil', 'tete'), ('cils', 'tete'),
    ('cou', 'cou'), ('bec', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
    ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('cou', rot=(2 * r, 0, 8 * g - 6 * d))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
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
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.075 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.137), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
