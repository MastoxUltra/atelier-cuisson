"""Le caméléon en peluche, cousu main (2e dessin, d'après photos : une vraie tête de caméléon, plus de chien rose) : un
rose vif zébré de bandes turquoise, un corps haut et aplati comme une feuille, la crête du dos en dents de scie, la
queue enroulée en escargot, des pattes en pinces à deux doigts opposés ; et la TÊTE : un casque triangulaire qui
dépasse en arrière du crâne, une bouche en fente à la lèvre claire, et surtout ses yeux : deux tourelles rondes et
saillantes, chacune sa pupille. Il avance au ralenti, une patte levée au-dessus du vide, un œil rivé sur nous.

    python cameleon.py        fabrique la fiche art/apercus/animaux/cameleon.png (cousu main, palier 2)
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


ROSE = np.array(M.hexa("#ff8db4"))            # la dominante : rose vif (le poil la fonce un peu)
TURQUOISE = np.array(M.hexa("#3fdcd0"))       # l'accent : les bandes, l'iris
CITRON = np.array(M.hexa("#fff27a"))          # la crête, la lèvre, le dessous
CHARBON = M.hexa("#3a3236")                   # les griffes, le bout de la queue
LACET = 34.0


def construire():
    a = K.Animal("cameleon")
    a.taille = 0.55

    # ----- le corps : un disque haut, mince, couché en long, le ventre citron ; des bandes turquoise en travers du flanc -----
    corps = A.boule(1.0, 64, 32)
    v = corps.v
    bandes = np.sin(v[:, 1] * 9.5 + 0.4) > 0.30
    t = np.tile(ROSE, (len(v), 1))
    t[bandes & (v[:, 2] > -0.30)] = TURQUOISE
    t[v[:, 2] < -0.62] = CITRON
    corps.teinte = t
    a.piece("corps", corps.etire(0.050, 0.150, 0.125), None, pos=(0.0, 0.060, 0.200))
    # la crête du dos : une rangée de petites dents jaunes
    dents = None
    for k in range(9):
        y = -0.060 + 0.034 * k
        z = 0.200 + 0.125 * math.sqrt(max(0.0, 1.0 - ((y - 0.060) / 0.150) ** 2)) - 0.004
        d = A.tour(A.profil([(0, 0), (0.012, 0.002), (0.007, 0.018), (0, 0.030)], 4), 8).pose((0.0, y, z))
        dents = d if dents is None else dents + d
    a.piece("crete", dents, tuple(CITRON), poil=False)

    # ----- la tête : un crâne en coin, la bouche en fente à lèvre claire, le CASQUE triangulaire qui dépasse derrière ;
    #       les tourelles des yeux, chacune sa pupille -----
    H = A.repere(Vector((0.0, -0.160, 0.215)), (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.where((tete.v[:, 2] < -0.35)[:, None], tuple(CITRON), tuple(ROSE))
    a.piece("tete", tete.etire(0.046, 0.082, 0.058), None, mat=H)
    a.tete = H @ Vector((0.0, -0.100, 0.0))
    casque = A.tour(A.profil([(0, 0), (0.044, 0.008), (0.040, 0.050), (0.020, 0.092), (0, 0.110)], 5), 24)
    casque.v[:, 0] *= 0.80
    a.piece("casque", casque, tuple(ROSE), mat=A.cadre(H @ Vector((0, 0.040, 0.034)), H3 @ Vector((0, 0.80, 0.60)), Vector((0, 0, 1))))
    a.piece("levre", A.boule(1.0, 24, 12).etire(0.034, 0.070, 0.012), tuple(CITRON), mat=H @ A.repere((0, -0.036, -0.044)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        base = H @ Vector((c * 0.040, -0.040, 0.034))
        a.piece("tourelle_" + nom, A.boule(1.0, 28, 14).etire(0.036, 0.036, 0.036), tuple(ROSE), pos=tuple(base))
        a.piece("cerne_" + nom, A.boule(1.0, 28, 14).etire(0.030, 0.030, 0.030), tuple(TURQUOISE),
                pos=tuple(base + H3 @ Vector((c * 0.012, -0.012, 0.004))), poil=False)
        # la pupille noire AU BOUT de la tourelle : posée sur le cerne turquoise (sa surface), pas dessous
        p, n = a.surface("cerne_" + nom, base, H3 @ Vector((c * 0.80, -0.50, 0.25)))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0145)

    # ----- les pattes : minces, deux doigts opposés en pince au bout ; la gauche avant levée ; la queue en escargot -----
    def pince(bout, c):
        m = None
        for ang in (-35, 35):
            d = A.boule(1.0, 12, 6).etire(0.0075, 0.026, 0.0075).pose((0.020 * math.sin(math.radians(ang)), -0.020 * math.cos(math.radians(ang)), 0), (0, 0, ang))
            m = d if m is None else m + d
        return m.pose(tuple(bout))
    for nom, c, y_, levee in (("av_G", 1, -0.050, True), ("av_D", -1, -0.050, False), ("ar_G", 1, 0.170, False), ("ar_D", -1, 0.170, False)):
        haut = (c * 0.030, y_, 0.180)
        if levee:
            ch = [haut, (c * 0.075, y_ - 0.040, 0.150), (c * 0.085, y_ - 0.090, 0.190), (c * 0.085, y_ - 0.120, 0.150)]
        else:
            ch = [haut, (c * 0.072, y_ - 0.010, 0.100), (c * 0.082, y_ - 0.030, 0.034), (c * 0.082, y_ - 0.040, 0.012)]
        m = A.tube(A.courbe(propres(ch), 5), lambda t: 0.017 - 0.006 * t, 12)
        m.teinte = np.tile(ROSE, (len(m.v), 1))
        a.piece("patte_" + nom, m, None)
        a.piece("pince_" + nom, pince(ch[-1], c), tuple(TURQUOISE), poil=False)
    # la queue part de la croupe, descend derrière lui puis s'enroule sous elle en escargot (dans le plan Y, Z)
    pts = []
    for k in range(0, 49):
        u = k / 48.0
        ang = math.radians(108.0) - 2 * math.pi * 1.6 * u
        r = 0.095 * (1.0 - 0.74 * u) + 0.005
        pts.append((0.0, 0.235 + r * math.cos(ang), 0.110 + r * math.sin(ang)))
    queue = A.tube(A.courbe(propres(pts), 3), lambda t: 0.026 - 0.016 * t, 14)
    nb = len(queue.v) // 14
    anneau = np.arange(len(queue.v)) // 14
    queue.teinte = np.where((anneau > 0.84 * nb)[:, None], np.array(M.hexa("#3a3236")), ROSE)
    a.piece("queue", queue, None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("cameleon", styles.style_de("cameleon"), sys.modules[__name__]), "Caméléon")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py cameleon). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.187                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.095, 0.200)),
    ('tete', 'corps', (-0.017, -0.094, 0.214)),
    ('patte_av_G', 'corps', (0.077, -0.126, 0.195)),
    ('patte_ar_G', 'corps', (0.035, 0.170, 0.179)),
    ('queue', 'corps', (-0.000, 0.173, 0.146)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('tourelle', 'corps'),
    ('pince_av', 'patte_av', True), ('pince_ar', 'patte_ar', True), ('casque', 'tete'), ('corps', 'corps'),
    ('queue', 'queue'), ('crete', 'tete'), ('levre', 'tete'), ('cerne', 'tete'), ('tete', 'tete'), ('oeil', 'tete'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
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
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('queue', rot=(-6, 0, -10 * s))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.056 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.103), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
