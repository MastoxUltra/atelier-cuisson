"""Le tapir en peluche de velours ras (2e dessin, d'après photos : un corps en POIRE, pas un blob) : l'avant et les
pattes d'un ardoise bleutée, la selle crème qui tombe d'un trait net derrière les épaules et couvre le dos jusqu'à la
croupe, le dos voûté, l'arrière-train large et haut, le cou court et épais, et une TÊTE en coin dont le museau se
prolonge en une courte trompe qui déborde la bouche (le profil de la tête et du nez ne font qu'une ligne) ; de petites
oreilles rondes bordées de blanc, de petits yeux, des pattes courtes à trois sabots, un moignon de queue. Il flaire,
la tête basse, tout le poids sur l'arrière.

    python tapir.py        fabrique la fiche art/apercus/animaux/tapir.png (velours ras, palier 3)
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

GONFLAGE = True       # la base aux volumes gonflés de l'Artiste (fusion.py) : jointures fondues, bouts arrondis


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


ARDOISE = np.array(M.hexa("#7189ad"))         # la dominante : ardoise bleutée moyenne (le poil la fonce)
CREME = np.array(M.hexa("#fbf4e4"))           # l'accent : la selle, le bord des oreilles
SOMBRE = np.array(M.hexa("#4e5d7c"))          # le museau, le dedans des oreilles
SABOT = M.hexa("#3a3a44")                     # les sabots, les narines
PAS = 0.010


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=72, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("tapir")
    a.taille = 2.00

    # ----- le corps, le cou, la tête et la trompe d'un seul tenant, couchés le long d'une courbe : la croupe haute et large,
    #       le dos voûté, les épaules plus étroites, le cou court, la tête en coin qui descend, le nez qui déborde -----
    chemin = [(0.0, y, z) for y, z in ((0.580, 0.620), (0.380, 0.710), (0.120, 0.740), (-0.140, 0.700), (-0.400, 0.600),
                                       (-0.650, 0.480), (-0.860, 0.390), (-1.040, 0.320))]
    fil = K.Fil(chemin, (1, 0, 0))
    L = fil.long
    pts = [(0.0, 0.0), (0.02, 0.150), (0.10, 0.240), (0.24, 0.282), (0.40, 0.268), (0.52, 0.222), (0.60, 0.170), (0.68, 0.152),
           (0.76, 0.130), (0.84, 0.108), (0.90, 0.086), (0.95, 0.074), (0.99, 0.062), (1.0, 0.0)]
    bloc = fuseau(pts, L, 80)
    x, y, z = bloc.v[:, 0], bloc.v[:, 1], bloc.v[:, 2]
    f = z / L
    th = np.abs(np.arctan2(x, y))
    bloc.v[:, 1] += 0.040 * np.exp(-((f - 0.36) / 0.12) ** 2) * (y > 0)                 # le dos voûté
    t = np.tile(ARDOISE, (len(z), 1))
    t[(f < 0.50) & (th < 2.45)] = CREME                                                   # la selle, d'un trait net
    t[(f > 0.86) & (y < -0.020)] = SOMBRE                                                 # le dessous du museau
    bloc.teinte = t
    a.piece("bloc", bloc.sculpte(fil.couche), None)
    centre, avant, nuque = fil.cadre(0.995 * L)
    a.tete = Vector(fil.cadre(0.90 * L)[0])

    # ----- la mâchoire du bas, plus courte que le nez ; les narines ; l'œil minuscule ; l'oreille ronde bordée de blanc -----
    c1, av1, nq1 = fil.cadre(0.90 * L)
    a.piece("machoire", A.boule(1.0, 24, 12).etire(0.044, 0.092, 0.030), tuple(SOMBRE),
            mat=A.cadre(Vector(c1) - Vector(nq1) * 0.052 - Vector(av1) * 0.030, Vector(av1), Vector(nq1)))
    flanc = np.array([1.0, 0.0, 0.0])
    for nom, c in (("G", 1), ("D", -1)):
        c2, av2, nq2 = fil.cadre(0.97 * L)
        a.piece("narine_" + nom, A.boule(1.0, 14, 8).etire(0.016, 0.022, 0.012), SABOT,
                pos=tuple(np.array(c2) - np.array(nq2) * 0.020 + np.array([c * 0.030, 0.0, 0.0])), poil=False)
        c3, av3, nq3 = fil.cadre(0.800 * L)
        p, n = a.surface("bloc", Vector(c3), Vector(flanc * c * 0.92 + np.array(nq3) * 0.38 - np.array(av3) * 0.36))
        a.oeil("oeil_" + nom, p + n * 0.008, n, 0.0260)
        c4, av4, nq4 = fil.cadre(0.700 * L)
        E = A.cadre(Vector(c4) + Vector(nq4) * 0.150 + Vector((c * 0.075, 0.0, 0.0)), Vector((c * 0.55, 0.15, 0.80)), Vector((c * 0.3, -0.9, 0.0)))
        po = A.profil([(0, 0), (0.044, 0.010), (0.054, 0.040), (0.044, 0.074), (0.020, 0.094), (0, 0.102)], 6)
        a.piece("oreille_" + nom, A.tour(po, 28).etire(1.0, 0.45, 1.0), tuple(ARDOISE), mat=E)
        a.piece("bord_" + nom, A.tour(po, 24).etire(0.62, 0.40, 0.70).pose((0, 0.010, 0.008)), tuple(CREME), mat=E, poil=False)

    # ----- les pattes : courtes, épaisses, trois sabots devant ; l'avant gauche avancée à tâtons ; un moignon de queue -----
    def pilier(haut, bas, r):
        fl = K.Fil([haut, ((haut[0] + bas[0]) / 2, (haut[1] + bas[1]) / 2, (haut[2] + bas[2]) / 2), bas], (1, 0, 0))
        m = fuseau([(0.0, r * 1.15), (0.30, r * 0.84), (0.62, r * 0.58), (0.86, r * 0.52), (1.0, r * 0.62)], fl.long, 40, 0.010)   # une patte qui s'affine à la cheville : plus de sacs
        m.teinte = np.tile(ARDOISE, (len(m.v), 1))
        return m.sculpte(fl.couche)
    for nom, x_, y_, r, av in (("av_G", 0.150, -0.440, 0.092, -0.140), ("av_D", -0.150, -0.440, 0.092, 0.0),
                               ("ar_G", 0.175, 0.470, 0.108, 0.0), ("ar_D", -0.175, 0.470, 0.108, 0.0)):
        a.piece("patte_" + nom, pilier((x_, y_, 0.560), (x_ * 1.02, y_ + av, 0.040), r), None)
        for k in (-1, 0, 1):
            a.piece("sabot_%s%d" % (nom, k), A.boule(1.0, 12, 6).etire(0.028, 0.036, 0.024), SABOT,
                    pos=(x_ * 1.02 + k * 0.050, y_ + av - r * 0.95, 0.026), poil=False)
    a.piece("queue", A.boule(1.0, 20, 10).etire(0.040, 0.050, 0.044), tuple(CREME), pos=(0.0, 0.620, 0.600))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tapir", styles.style_de("tapir"), sys.modules[__name__]), "Tapir")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py tapir). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.540                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.193, 0.653)),
    ('tete', 'corps', (0.000, -0.707, 0.496)),
    ('oreille_G', 'tete', (0.081, -0.636, 0.656)),
    ('patte_av_G', 'corps', (0.150, -0.473, 0.542)),
    ('patte_ar_G', 'corps', (0.173, 0.477, 0.538)),
    ('queue', 'corps', (-0.000, 0.573, 0.604)),
]

PORTEURS = [
    ('sabot_av_G-1', 'patte_av_G'), ('sabot_av_D-1', 'patte_av_D'), ('sabot_ar_G-1', 'patte_ar_G'),
    ('sabot_ar_D-1', 'patte_ar_D'), ('sabot_av_G0', 'patte_av_G'), ('sabot_av_G1', 'patte_av_G'),
    ('sabot_av_D0', 'patte_av_D'), ('sabot_av_D1', 'patte_av_D'), ('sabot_ar_G0', 'patte_ar_G'),
    ('sabot_ar_G1', 'patte_ar_G'), ('sabot_ar_D0', 'patte_ar_D'), ('sabot_ar_D1', 'patte_ar_D'),
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('machoire', 'corps'),
    ('oreille', 'oreille', True), ('narine', 'tete'), ('queue', 'queue'), ('bloc', 'corps'), ('oeil', 'tete'),
    ('bord', 'corps'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'),
    ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
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
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
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
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.162 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.297), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
