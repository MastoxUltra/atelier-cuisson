"""La gerboise en peluche cousue main : un petit corps rond sable rosé, le ventre crème, une grosse tête aux yeux
immenses et aux oreilles hautes, un museau court au petit nez rose, des moustaches ; de minuscules mains serrées sur la
poitrine, des cuisses énormes et de longs pieds ; et une très longue queue, mince, qui se termine en plumet noir et
blanc. Le sauteur de minuit : debout sur ses pattes arrière, droit comme un point d'exclamation, sur le point de
bondir.

    python gerboise.py        fabrique la fiche art/apercus/animaux/gerboise.png (cousu main, palier 2)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import garnitures as G
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


SABLE = np.array(M.hexa("#f2c8a4"))           # la dominante : sable rosé (le poil le fonce)
CLAIR = np.array(M.hexa("#fff0e0"))           # le ventre, le dedans des pattes, le plumet blanc
DOS = np.array(M.hexa("#e0aa88"))             # le dos, le dessus de la tête
ROSE = M.hexa("#f0a8a0")                      # le dedans des oreilles, le nez
NOIR = np.array(M.hexa("#2e2826"))            # les yeux, le plumet noir
LACET = 22.0


def construire():
    a = K.Animal("gerboise")
    a.taille = 0.30

    # ----- le corps : un petit œuf debout, penché en arrière, le dos plus sombre, le ventre crème -----
    def oeuf(v):
        v = K.bosse(v, (0, -0.9, 0.1), 0.12, 0.40)
        return v * [0.074, 0.082, 0.108]
    corps = A.boule(1.0, 48, 24)
    corps.teinte = np.where((corps.v[:, 1] > 0.20)[:, None], DOS, np.where((corps.v[:, 1] < -0.45)[:, None], CLAIR, SABLE))
    a.piece("corps", corps.sculpte(oeuf), None, pos=(0.0, 0.030, 0.190), rot=(-14, 0, 0))

    # ----- la tête : grosse et ronde, le museau court, le petit nez rose ; les yeux IMMENSES ; les grandes oreilles -----
    TETE = Vector((0.0, -0.030, 0.318))
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.where((tete.v[:, 2] > 0.35)[:, None], DOS, SABLE)
    a.piece("tete", tete.etire(0.070, 0.066, 0.062), None, mat=H)
    a.piece("museau", A.boule(1.0, 28, 14).etire(0.032, 0.036, 0.030), tuple(CLAIR), mat=H @ A.repere((0.0, -0.058, -0.014)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.012, 0.010, 0.010), ROSE, mat=H @ A.repere((0.0, -0.092, -0.008)), poil=False)
    a.tete = H @ Vector((0.0, -0.080, -0.010))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.60, -0.62, 0.32))
        a.rustine("cerne_" + nom, "tete", H.to_translation(), regard, 0.26, tuple(NOIR), 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0195)
        # l'oreille : un grand ovale dressé, le dedans rose
        E = A.cadre(H @ Vector((c * 0.040, 0.014, 0.050)), H3 @ Vector((c * 0.26, 0.06, 0.96)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, A.boule(1.0, 28, 14).etire(0.030, 0.009, 0.086).pose((0, 0, 0.074)), tuple(SABLE), mat=E)
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).etire(0.019, 0.008, 0.068).pose((0, -0.005, 0.072)), ROSE, mat=E, poil=False)
        # trois moustaches de chaque côté : de longs fils clairs
        for k, (haut, ouvert) in enumerate(((0.012, 0.30), (0.0, 0.0), (-0.012, -0.30))):
            d = H3 @ Vector((c * 1.0, -0.40 + 0.30 * ouvert, 0.10 * ouvert * 2.0))
            dep = H @ Vector((c * 0.030, -0.078, -0.012 + haut))
            a.piece("moustache_%s%d" % (nom, k), A.tube([tuple(dep), tuple(dep + d.normalized() * 0.100)], 0.0022, 6), tuple(CLAIR), poil=False)

    # ----- les bras : minuscules, les mains serrées sur la poitrine ; les cuisses énormes, les longs pieds ; la queue -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.056, -0.016, 0.246), (c * 0.066, -0.060, 0.214), (c * 0.032, -0.082, 0.218)]
        a.piece("bras_" + nom, A.tube(A.courbe(propres(ch), 5), 0.014, 10), tuple(SABLE))
        a.piece("main_" + nom, A.boule(1.0, 14, 8).etire(0.014, 0.014, 0.012), tuple(CLAIR), pos=ch[-1])
        a.piece("cuisse_" + nom, A.boule(1.0, 28, 14).etire(0.046, 0.066, 0.084), tuple(SABLE), pos=(c * 0.062, 0.040, 0.120), rot=(-12, 0, c * 4))
        jam = [(c * 0.062, 0.020, 0.090), (c * 0.066, 0.056, 0.050), (c * 0.064, 0.050, 0.022)]
        a.piece("jambe_" + nom, A.tube(A.courbe(propres(jam), 5), lambda t: 0.026 - 0.012 * t, 10), tuple(SABLE))
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.020, 0.090, 0.016), tuple(CLAIR), pos=(c * 0.064, -0.010, 0.016), rot=(0, 0, c * 6))
    chemin = [(0.0, 0.100, 0.150), (0.0, 0.200, 0.100), (0.050, 0.310, 0.040), (0.150, 0.380, 0.030), (0.250, 0.360, 0.040), (0.290, 0.300, 0.070)]
    a.piece("queue", K.tube_peint(A.courbe(propres(chemin), 8), lambda t: 0.014 - 0.006 * t + 0.016 * max(0.0, (t - 0.80) / 0.20) ** 1.2,
                                  [(0.78, tuple(SABLE)), (0.90, tuple(NOIR)), (1.0, tuple(CLAIR))], 12), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("gerboise", styles.style_de("gerboise"), sys.modules[__name__]), "Gerboise")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py gerboise). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.222                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.070, 0.190)),
    ('tete', 'corps', (0.000, -0.008, 0.261)),
    ('oreille_G', 'tete', (0.029, -0.004, 0.361)),
    ('patte_av_G', 'corps', (0.059, -0.026, 0.243)),
    ('patte_ar_G', 'corps', (0.061, 0.047, 0.201)),
    ('queue', 'corps', (-0.001, 0.109, 0.148)),
]

PORTEURS = [
    ('moustache_G0', 'tete'), ('moustache_G1', 'tete'), ('moustache_G2', 'tete'), ('moustache_D0', 'tete'),
    ('moustache_D1', 'tete'), ('moustache_D2', 'tete'), ('oeil_reflet', 'tete'), ('oreille', 'oreille', True),
    ('museau', 'tete'), ('dedans', 'oreille', True), ('cuisse', 'patte_ar', True), ('corps', 'corps'),
    ('queue', 'queue'), ('cerne', 'tete'), ('jambe', 'patte_ar', True), ('tete', 'tete'), ('main', 'patte_av', True),
    ('pied', 'patte_av', True), ('oeil', 'tete'), ('bras', 'patte_av', True), ('nez', 'tete'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.067 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.122), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
