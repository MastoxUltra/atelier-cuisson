"""L'ornithorynque en peluche de magasin (2e dessin) : un castor aplati à bec de canard. Le corps tout entier est un
long coussin de poil brun acajou, plaqué au sol ; la tête et le large bec spatulé gris rosé ne font qu'une pièce (le
bec est fondu dans la tête, sans couture) ; une queue en pagaie plate comme une raquette ; quatre pattes palmées qui
sortent sur les côtés, aux ongles crème. Le curieux : la tête relevée qui renifle, le bec en l'air, un œil tourné vers
nous, le ventre sur la terre, les pattes écartées.

    python ornithorynque.py        fabrique la fiche art/apercus/animaux/ornithorynque.png (peluche de magasin, palier 4)
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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
ACAJOU = M.hexa("#9a5238")                    # la dominante : brun acajou
VENTRE = M.hexa("#e8d0b0")                    # le ventre
BEC = M.hexa("#b8a0a4")                       # l'accent : le bec gris rosé
CHARBON = M.hexa("#3a2c2c")
CORPS = Vector((0.0, 0.100, 0.100))
LACET = 22.0


def construire():
    a = K.Animal("ornithorynque")
    a.taille = 0.90

    # ----- le corps : un long coussin plat, le ventre clair dessous (un castor aplati) -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(ACAJOU, float), (len(v), 1))
    t[v[:, 2] < -0.30] = VENTRE
    corps.teinte = t

    def aplati(v):
        s = v * [0.172, 0.310, 0.100]
        s[:, 2] = np.where(s[:, 2] < 0, s[:, 2] * 0.70, s[:, 2])
        return s
    a.piece("corps", corps.sculpte(aplati), None, pos=CORPS)

    # ----- la tête et le bec : d'une seule pièce ; le crâne rond, qui s'aplatit et s'élargit en spatule gris rosé ;
    #       la tête relevée, qui renifle -----
    T = A.repere(Vector((0.0, -0.200, 0.150)), (-22, 0, LACET))
    T3 = T.to_3x3()
    prof = A.profil([(0, 0), (0.064, 0.012), (0.092, 0.050), (0.098, 0.100), (0.084, 0.150), (0.078, 0.200), (0.082, 0.260),
                     (0.092, 0.320), (0.098, 0.380), (0.086, 0.420), (0.050, 0.440), (0, 0.446)], 6)
    tete = A.tour(prof, 56)
    K.bandes(tete, [(0.160, ACAJOU), (0.200, (0.52 * ACAJOU[0] + 0.48 * BEC[0], 0.52 * ACAJOU[1] + 0.48 * BEC[1], 0.52 * ACAJOU[2] + 0.48 * BEC[2])), (9, BEC)])

    def spatule(v):
        s = v.copy()
        z = v[:, 2]
        s[:, 1] *= 1 - 0.68 * K.lisse((z - 0.15) / 0.12)                          # le bec s'aplatit
        s[:, 0] *= 1 + 0.35 * K.lisse((z - 0.28) / 0.14)                          # et s'élargit au bout
        return s
    a.piece("tete", tete.sculpte(spatule), None, mat=T @ A.repere((0, 0, 0), (90, 0, 0)), poil=False)
    a.tete = T @ Vector((0, -0.300, -0.010))
    for c in (1, -1):
        a.piece("narine_" + ("G" if c > 0 else "D"), A.boule(1.0, 12, 6).etire(0.010, 0.012, 0.005), CHARBON,
                mat=T @ A.repere((c * 0.032, -0.400, 0.014)), poil=False)
        p, n = a.surface("tete", T @ Vector((0, -0.050, 0.0)), T3 @ Vector((c * 0.72, -0.45, 0.52)))
        a.oeil("oeil_" + ("G" if c > 0 else "D"), p + n * 0.003, n, 0.0128)

    # ----- la queue : une pagaie plate et large, comme celle du castor, qui traîne par terre -----
    a.piece("queue", A.boule(1.0, 32, 16).etire(0.100, 0.200, 0.022), ACAJOU, pos=(0, 0.480, 0.032), rot=(-3, 0, 0))

    # ----- les pattes : quatre pattes courtes qui sortent sur les côtés, les palmes plates de feutrine clair aux ongles -----
    for nom, x, y, cap in (("av_G", 0.190, -0.060, 36), ("av_D", -0.190, -0.060, -36), ("ar_G", 0.170, 0.280, 24), ("ar_D", -0.170, 0.280, -24)):
        c = 1 if x > 0 else -1
        chemin = [(x * 0.70, y, 0.090), (x * 1.00, y - 0.012, 0.050), (x * 1.18, y - 0.034, 0.022)]
        a.piece("patte_" + nom, A.tube(A.courbe(chemin, 5), 0.030, 12), ACAJOU)
        a.piece("palme_" + nom, A.boule(1.0, 24, 12).etire(0.062, 0.070, 0.010), VENTRE, pos=(x * 1.30, y - 0.080, 0.012), rot=(0, 0, cap), poil=False)
        for k in (-1, 0, 1):
            a.piece("ongle_%s%d" % (nom, k), A.boule(1.0, 8, 4).etire(0.007, 0.016, 0.006), M.hexa("#fff6e0"),
                    pos=(x * 1.30 + k * 0.026 + c * 0.020, y - 0.150, 0.012), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("ornithorynque", styles.style_de("ornithorynque"), sys.modules[__name__]), "Ornithorynque")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py ornithorynque). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.097                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.251, 0.103)),
    ('tete', 'corps', (0.025, -0.191, 0.162)),
    ('patte_av_G', 'corps', (0.155, -0.064, 0.097)),
    ('patte_ar_G', 'corps', (0.141, 0.276, 0.097)),
    ('queue', 'corps', (0.001, 0.294, 0.044)),
]

PORTEURS = [
    ('ongle_av_G-1', 'corps'), ('ongle_av_D-1', 'corps'), ('ongle_ar_G-1', 'corps'), ('ongle_ar_D-1', 'corps'),
    ('oeil_reflet', 'tete'), ('ongle_av_G0', 'corps'), ('ongle_av_G1', 'corps'), ('ongle_av_D0', 'corps'),
    ('ongle_av_D1', 'corps'), ('ongle_ar_G0', 'corps'), ('ongle_ar_G1', 'corps'), ('ongle_ar_D0', 'corps'),
    ('ongle_ar_D1', 'corps'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True),
    ('palme_av', 'patte_av', True), ('palme_ar', 'patte_ar', True), ('narine', 'tete'), ('corps', 'corps'),
    ('queue', 'queue'), ('tete', 'tete'), ('oeil', 'tete'), ('paupiere_0', 'paupiere_0'),
    ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.029 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.053), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
