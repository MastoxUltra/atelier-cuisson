"""Le tamarin en peluche de velours ras (2e dessin, d'après photos : un petit singe, plus un fauve) : un or flamme
lumineux, un corps mince et nerveux, assis droit comme un écureuil ; la crinière n'est qu'une collerette de longs poils
dorés autour du cou et derrière les oreilles, qui laisse voir la petite FACE noire et nue aux grands yeux d'ambre ; des
bras et des jambes fins, de minuscules mains, et une très longue queue fine qui s'enroule. Le seigneur des branches :
assis, le torse droit, la tête de trois quarts, les mains sur le ventre, un regard de curieux.

    python tamarin.py        fabrique la fiche art/apercus/animaux/tamarin.png (velours ras, palier 3)
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


OR = np.array(M.hexa("#ffb030"))              # la dominante : or flamme lumineux
CLAIR = np.array(M.hexa("#ffd070"))           # la collerette, le dessous
FACE = np.array(M.hexa("#5a4044"))            # la face nue, les mains
AMBRE = M.hexa("#f0b030")
CHARBON = M.hexa("#2e2428")
CORPS = Vector((0.0, 0.050, 0.200))
TETE = Vector((0.0, -0.030, 0.390))
LACET = 28.0
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=36, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 5)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("tamarin")
    a.taille = 0.55                           # queue comprise

    # ----- le corps : un œuf mince, assis droit, la poitrine un peu plus claire -----
    corps = A.boule(1.0, 48, 24)
    corps.teinte = np.where((corps.v[:, 1] < -0.55)[:, None], tuple(CLAIR), tuple(OR))
    a.piece("corps", corps.etire(0.074, 0.070, 0.115), None, pos=tuple(CORPS), rot=(-6, 0, 0))

    # ----- la tête : petite et ronde ; la FACE nue et noire en avant, le museau court, de grands yeux d'ambre ; la collerette
    #       de longs poils dorés autour du cou et derrière la tête (pas autour de la face) ; de petites oreilles rondes -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.where(((tete.v[:, 1] < -0.30) & (np.abs(tete.v[:, 0]) < 0.78))[:, None], tuple(FACE), tuple(OR))
    a.piece("tete", tete.etire(0.050, 0.052, 0.048), None, mat=H)
    a.piece("museau", A.boule(1.0, 24, 12).etire(0.024, 0.026, 0.020), tuple(FACE), mat=H @ A.repere((0, -0.046, -0.014)))
    a.tete = H @ Vector((0, -0.060, 0.0))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.46, -0.84, 0.20))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.30, AMBRE, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0145)
        a.piece("oreille_" + nom, A.boule(1.0, 20, 10).etire(0.024, 0.010, 0.026), tuple(FACE), mat=A.cadre(H @ Vector((c * 0.046, 0.016, 0.034)), H3 @ Vector((c * 0.7, 0.2, 0.6)), (0, 0, 1)), poil=False)
    # la collerette : un anneau de longs poils qui retombent sur les épaules et la nuque
    rng = np.random.default_rng(5)
    poils = None
    for i in range(30):
        ang = 2 * math.pi * i / 30
        if math.sin(ang) < -0.35:
            continue                                                                 # rien devant : la face reste dégagée
        base = np.array(TETE) + np.array([0.060 * math.cos(ang), 0.050 * math.sin(ang) + 0.004, -0.030])
        l = 0.034 + 0.018 * rng.random()
        m = A.boule(1.0, 10, 8).etire(0.016, 0.016, l).pose(tuple(base + np.array([0.0, 0.0, -l * 0.7])), (10 * math.sin(ang), -12 * math.cos(ang), 0))   # des mèches rondes, plus de rabats plats
        poils = m if poils is None else poils + m
    a.piece("collerette", poils, tuple(CLAIR))

    # ----- les bras : fins, les mains sur le ventre ; les jambes : repliées, fines, les pieds à plat ; la queue : très longue -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.070, -0.010, 0.290), (c * 0.092, -0.050, 0.210), (c * 0.040, -0.098, 0.190)]
        a.piece("bras_" + nom, A.tube(A.courbe(propres(ch), 5), lambda t: 0.019 - 0.005 * t, 12), tuple(OR))
        a.piece("main_" + nom, A.boule(1.0, 16, 8).etire(0.018, 0.022, 0.014), tuple(FACE), pos=ch[-1], poil=False)
        # la jambe : un membre d'une pièce, qui descend de la hanche et finit par un pied à trois doigts (plus de boules)
        a.piece("cuisse_" + nom, A.tube(A.courbe(propres([(c * 0.070, 0.050, 0.150), (c * 0.092, 0.036, 0.085), (c * 0.084, -0.030, 0.034)]), 5),
                                         lambda t_: 0.034 - 0.012 * t_, 14), tuple(OR))
        doigts = None
        for dg in (-24, 0, 24):
            r_ = math.radians(dg)
            d_ = A.boule(1.0, 12, 6).etire(0.0105, 0.034, 0.009).pose((0.026 * math.sin(r_), -0.026 * math.cos(r_), 0.0), (0, 0, dg))
            doigts = d_ if doigts is None else doigts + d_
        a.piece("pied_" + nom, doigts, tuple(FACE), pos=(c * 0.084, -0.050, 0.012), poil=False)
    qf = K.Fil([(0.0, 0.130, 0.100), (0.0, 0.230, 0.060), (0.060, 0.320, 0.100), (0.100, 0.310, 0.230), (0.060, 0.230, 0.300),
                (0.0, 0.200, 0.250)], (1, 0, 0))
    queue = fuseau([(0.0, 0.022), (0.50, 0.024), (0.94, 0.018), (1.0, 0.0)], qf.long, 20, 0.006)
    queue.teinte = np.where((queue.v[:, 2] > 0.88 * qf.long)[:, None], tuple(FACE), tuple(OR))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tamarin", styles.style_de("tamarin"), sys.modules[__name__]), "Tamarin")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py tamarin). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.274                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.077, 0.131)),
    ('tete', 'corps', (-0.000, -0.014, 0.346)),
    ('oreille_G', 'tete', (0.021, -0.010, 0.409)),
    ('patte_av_G', 'corps', (0.076, -0.018, 0.274)),
    ('queue', 'corps', (0.000, 0.143, 0.095)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('collerette', 'corps'), ('oreille', 'oreille', True), ('museau', 'tete'),
    ('cuisse', 'patte_av', True), ('corps', 'corps'), ('queue', 'queue'), ('tete', 'tete'),
    ('main', 'patte_av', True), ('pied', 'patte_av', True), ('iris', 'tete'), ('oeil', 'tete'),
    ('bras', 'patte_av', True), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'),
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
    pas = 18.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_av_D', -1)]:
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
    p.add('corps', rot=(34 * bas + 3 * coups, 0, 0))
    p.paire('patte_av', rot=(-30 * bas, 0, 0))
    p.add('tete', rot=(16 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.082 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.02), rot=(36, 0, 6), ech=(1 + 0.010 * r, 1, 1 + 0.020 * r))
    p.paire('patte_av', rot=(-30, 0, 0))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
