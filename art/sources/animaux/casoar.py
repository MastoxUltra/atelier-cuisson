"""Le casoar en peluche de magasin : un noir bleuté, le plumage en crin hirsute qui retombe comme une jupe de paille,
le cou nu d'un bleu cobalt éclatant strié de pourpre, deux caroncules écarlates qui pendent comme des mentons, et sur
le crâne un casque d'ivoire en proue. Le dinosaure de la forêt : debout, le cou tendu droit vers nous, le casque
en avant, la tête de profil, l'œil d'or rond et fixe, un pied levé avec ses trois énormes griffes.

    python casoar.py        fabrique la fiche art/apercus/animaux/casoar.png (peluche de magasin, palier 4)
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
NOIR = M.hexa("#35405a")                      # la dominante : noir bleuté (le poil la fonce)
COBALT = M.hexa("#2f7cf0")                    # l'accent : le cou
ROUGE = M.hexa("#f02838")                     # les caroncules, la nuque
IVOIRE = M.hexa("#f4e8c0")                    # le casque
OR = M.hexa("#ffc83a")                        # les yeux
PATTE = M.hexa("#a89078")
CHARBON = M.hexa("#3a3030")
CORPS = Vector((0.0, 0.100, 0.680))


def meche(chemin, large, face, plat=0.40, cotes=12):
    """Une mèche plate (le geste du cheval) couchée le long d'un chemin."""
    p = A.courbe(chemin, 8)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    n0 = np.asarray(face, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.linalg.norm(t, axis=1, keepdims=True)
        x = np.cross(n0, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.60 * large, 0.05 * L), (0.95 * large, 0.22 * L), (large, 0.42 * L), (0.72 * large, 0.70 * L),
                     (0.30 * large, 0.93 * L), (0.06 * large, 0.985 * L), (0, L)], 5)
    return A.tour(prof, cotes).etire(1.0, plat, 1.0).sculpte(couche)


def construire():
    a = K.Animal("casoar")
    a.taille = 1.70

    # ----- le corps : un gros œuf couché vers l'arrière, le dos arrondi ; une jupe de crins qui tombe des flancs -----
    def oeuf(v):
        s = v * [0.280, 0.360, 0.290]                 # gros et lourd (vues de la référence, 16/10)
        s[:, 1] += 0.040 * v[:, 2]
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(oeuf), NOIR, pos=CORPS, rot=(-8, 0, 0))
    rng = np.random.default_rng(13)
    # le dos et les flancs couverts de plumes longues et serrées qui retombent (lisse, le corps se lisait comme un sac noir : 16/10)
    toison = None
    for i in range(140):
        z = rng.uniform(-0.25, 0.95)
        t = rng.uniform(0.0, 2 * math.pi)
        r = math.sqrt(max(0.0, 1 - z * z))
        d = np.array([r * math.cos(t), r * math.sin(t), z])
        p = np.array(CORPS) + d * np.array([0.276, 0.356, 0.286])
        long_ = 0.090 + 0.070 * rng.random()
        m = A.boule(1.0, 10, 6).etire(0.060, 0.044, long_).pose(tuple(p + np.array([d[0] * 0.012, d[1] * 0.012, -long_ * 0.65])),
                                                                 (14 * d[1], -16 * d[0], 0))
        toison = m if toison is None else toison + m
    a.piece("plumage", toison, NOIR)
    jupe = None
    for i in range(56):
        t = 2 * math.pi * (i + rng.uniform(-0.3, 0.3)) / 56
        base = np.array([0.272 * math.cos(t), CORPS.y + 0.348 * math.sin(t)])
        radial = np.array([math.cos(t), math.sin(t) * 0.80])
        radial /= np.linalg.norm(radial)
        hz = CORPS.z + rng.uniform(0.00, 0.10)
        k = 0.8 + 0.7 * rng.random()
        chemin = [(base[0] * 0.92, CORPS.y + (base[1] - CORPS.y) * 0.92, hz + 0.05), (base[0], base[1], hz - 0.04),
                  (base[0] + radial[0] * 0.040, base[1] + radial[1] * 0.040, hz - 0.18 * k),
                  (base[0] + radial[0] * 0.060, base[1] + radial[1] * 0.060, hz - 0.34 * k)]
        m = meche(chemin, 0.042 + 0.012 * rng.random(), (radial[0], radial[1], 0.0))
        jupe = m if jupe is None else jupe + m
    a.piece("jupe", jupe, NOIR)

    # ----- le cou : long et nu, cobalt, en S qui monte vers la tête tendue vers nous ; la nuque rouge -----
    fil = K.Fil([(0.0, -0.200, 0.860), (0.0, -0.290, 0.980), (0.0, -0.290, 1.100), (0.0, -0.350, 1.200)], (1, 0, 0))   # plus court (référence)
    L = fil.long
    pc = A.profil([(0, 0), (0.140, 0.03 * L), (0.108, 0.30 * L), (0.084, 0.70 * L), (0.070, 0.96 * L), (0, 1.02 * L)], 6)   # plus épais
    cou = A.tour(pc, 40)
    cou.teinte = np.where((cou.v[:, 1] > 0.02)[:, None] & (cou.v[:, 2] > 0.55 * L)[:, None], np.asarray(ROUGE), np.asarray(COBALT))
    cou.teinte[cou.v[:, 2] < 0.22 * L] = np.asarray(NOIR)                        # le pied du cou emplumé de noir : il sort du plumage, pas d'un sac
    a.piece("cou", cou.sculpte(fil.couche), None)
    bout = Vector(fil.cadre(L)[0])

    # ----- la tête : un petit crâne, le bec fort et droit, le casque d'ivoire en proue dessus ; de profil -----
    H = A.repere(bout + Vector((0.0, -0.030, 0.010)), (4, 0, 14))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.060, 0.080, 0.062), COBALT, mat=H)
    bec = A.tour(A.profil([(0, 0), (0.038, 0.006), (0.036, 0.040), (0.024, 0.090), (0.010, 0.125), (0, 0.140)], 6), 28)
    a.piece("bec", bec.etire(0.80, 0.70, 1.0), M.hexa("#d8c8a0"), mat=A.cadre(H @ Vector((0, -0.068, -0.014)), H3 @ Vector((0, -0.98, -0.10)), (0, 0, 1)), poil=False)
    casque = A.boule(1.0, 36, 18)
    a.piece("casque", casque.etire(0.034, 0.100, 0.070), IVOIRE, mat=H @ A.repere((0, -0.004, 0.060), (-18, 0, 0)), poil=False)
    a.tete = H @ Vector((0, -0.100, -0.010))
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.60, -0.62, 0.20)))
        a.rustine("iris_" + nom, "tete", H.to_translation(), H3 @ Vector((c * 0.60, -0.62, 0.20)), 0.30, OR, 0.003, 0)
        a.oeil("oeil_" + nom, p + n * 0.006, n, 0.0215)
    # les caroncules : deux gouttes écarlates qui pendent sous le menton
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("caroncule_" + nom, A.boule(1.0, 20, 10).etire(0.016, 0.014, 0.060), ROUGE, mat=H @ A.repere((c * 0.022, -0.020, -0.100)), poil=False)

    # ----- les pattes : deux piliers épais gris-beige, le pied à trois énormes doigts ; la droite levée -----
    plantee = [(0.110, 0.130, 0.480), (0.118, 0.150, 0.300), (0.118, 0.160, 0.130), (0.118, 0.150, 0.030)]
    levee = [(-0.110, 0.130, 0.480), (-0.118, 0.100, 0.330), (-0.118, 0.000, 0.300), (-0.118, -0.040, 0.180)]
    for nom, chemin, pied, rot in (("G", plantee, (0.118, 0.130, 0.012), (0, 0, 0)), ("D", levee, (-0.118, -0.080, 0.160), (-14, 0, 0))):
        a.piece("patte_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.060 - 0.020 * t, 14), PATTE, poil=False)
        doigts = None
        for ang in (-30, 0, 30):
            d = A.boule(1.0, 16, 8).etire(0.020, 0.090, 0.018).pose((0, -0.075, 0.0)).pose((0, 0, 0), (0, 0, ang))
            griffe = A.tour(A.profil([(0, 0), (0.014, 0.004), (0.010, 0.030), (0.004, 0.060), (0, 0.072)], 5), 12).pose((0, 0, 0), (-84, 0, 0)).pose((0, -0.150, 0.0), (0, 0, ang))
            doigts = (d + griffe) if doigts is None else doigts + d + griffe
        a.piece("doigts_" + nom, doigts, PATTE, pos=pied, rot=rot, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("casoar", styles.style_de("casoar"), sys.modules[__name__]), "Casoar")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py casoar). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.255                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.275, 0.570)),
    ('cou', 'corps', (0.000, -0.200, 0.880)),           # (16/10 : cou plus court, d'après la référence)
    ('tete', 'cou', (0.000, -0.335, 1.180)),
    ('patte_ar_G', 'corps', (0.112, 0.133, 0.481)),
    ('patte_av_G', 'corps', (0.118, 0.050, 0.028)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('caroncule', 'tete'), ('casque', 'tete'), ('doigts', 'patte_av', True),
    ('corps', 'corps'), ('patte', 'patte_ar', True), ('patte', 'patte_av', True), ('jupe', 'corps'), ('plumage', 'corps'), ('tete', 'tete'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.076 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.140), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
