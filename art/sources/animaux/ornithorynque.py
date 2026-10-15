"""L'ornithorynque en peluche de magasin (3e dessin, d'après photos) : un castor aplati à bec de canard. Le corps est un
long coussin de poil brun acajou, plat, plaqué au sol, le ventre plus clair ; une tête ronde sans cou et un large BEC
spatulé gris sombre, plat comme une cuillère, aux narines en haut du bout ; une queue en PAGAIE plate comme celle d'un
castor, relevée ; quatre pattes courtes qui sortent sur les côtés, terminées par de larges palmes. Le curieux : la
tête un peu relevée qui renifle, le bec tendu, un petit œil tourné vers nous.

    python ornithorynque.py        fabrique la fiche art/apercus/animaux/ornithorynque.png (peluche de magasin, palier 3)
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


# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
ACAJOU = np.array(M.hexa("#8a5a42"))          # la dominante : brun acajou
VENTRE = np.array(M.hexa("#c8a890"))          # le ventre, le dessous des pattes
BEC = M.hexa("#5c5a66")                       # le bec : gris sombre bleuté
PALME = M.hexa("#c89c88")                     # les palmes
CHARBON = M.hexa("#2a2428")
LACET = 24.0
PAS = 0.006


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
    a = K.Animal("ornithorynque")
    a.taille = 0.55

    # ----- le corps : un long coussin plat, bas, le dos acajou, le ventre clair -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.220, 0.050), (0.100, 0.062), (-0.040, 0.070), (-0.140, 0.074))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.052), (0.22, 0.086), (0.55, 0.092), (0.86, 0.078), (0.97, 0.054), (1.0, 0.0)], L, 56)
    corps.v[:, 1] *= 0.62                                                         # plat
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.teinte = np.where((th > 2.2)[:, None], tuple(VENTRE), tuple(ACAJOU))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- la tête : un dôme rond, sans cou ; le BEC plat et large, spatulé, qui prolonge le museau ; les narines en haut -----
    H = A.repere(Vector((0.0, -0.200, 0.082)), (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.where((tete.v[:, 2] < -0.30)[:, None], tuple(VENTRE), tuple(ACAJOU))
    a.piece("tete", tete.etire(0.074, 0.082, 0.056), None, mat=H)
    bec = A.boule(1.0, 40, 20)
    a.piece("bec", bec.etire(0.082, 0.125, 0.016), BEC, mat=H @ A.repere((0.0, -0.140, -0.006), (-4, 0, 0)), poil=False)
    a.tete = H @ Vector((0, -0.200, -0.010))
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("narine_" + nom, A.boule(1.0, 12, 6).etire(0.010, 0.012, 0.006), CHARBON,
                mat=H @ A.repere((c * 0.024, -0.238, 0.014)), poil=False)
        regard = H3 @ Vector((c * 0.66, -0.40, 0.62))
        a.rustine("cerne_" + nom, "tete", H.to_translation(), regard, 0.20, tuple(VENTRE), 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0105)

    # ----- la queue en pagaie, plate et large, relevée au bout ; les quatre pattes : courtes, écartées, à larges palmes -----
    a.piece("queue", A.boule(1.0, 36, 18).etire(0.072, 0.155, 0.016), tuple(ACAJOU) and tuple(ACAJOU), pos=(0.0, 0.340, 0.050), rot=(10, 0, 0))
    for nom, c, y_ in (("av_G", 1, -0.100), ("av_D", -1, -0.100), ("ar_G", 1, 0.150), ("ar_D", -1, 0.150)):
        ch = [(c * 0.070, y_, 0.046), (c * 0.115, y_ - 0.010, 0.036), (c * 0.140, y_ - 0.020, 0.016)]
        m = A.tube(A.courbe(propres(ch), 5), lambda t: 0.024 - 0.008 * t, 12)
        m.teinte = np.tile(ACAJOU, (len(m.v), 1))
        a.piece("patte_" + nom, m, None)
        a.piece("palme_" + nom, A.boule(1.0, 20, 10).etire(0.062, 0.050, 0.008), PALME, pos=(c * 0.175, y_ - 0.040, 0.010), rot=(0, 0, c * -14), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("ornithorynque", styles.style_de("ornithorynque"), sys.modules[__name__]), "Ornithorynque")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py ornithorynque). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.062                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.130, 0.065)),
    ('tete', 'corps', (-0.004, -0.125, 0.078)),
    ('patte_av_G', 'corps', (0.086, -0.104, 0.062)),
    ('patte_ar_G', 'corps', (0.086, 0.146, 0.062)),
    ('queue', 'corps', (-0.000, 0.197, 0.026)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True),
    ('palme_av', 'patte_av', True), ('palme_ar', 'patte_ar', True), ('narine', 'tete'), ('corps', 'corps'),
    ('cerne', 'tete'), ('queue', 'queue'), ('tete', 'tete'), ('oeil', 'tete'), ('bec', 'tete'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.019 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.034), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
