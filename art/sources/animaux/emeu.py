"""L'émeu en peluche de velours ras : un taupe lavande tout effiloché, le plumage en longues mèches pendantes comme un
manteau de laine, le cou nu bleuté, la petite tête au grand œil d'ambre sous de longs cils, de très longues pattes aux
gros pieds à trois doigts. Un professeur distrait qui fait les cent pas : en pleine marche, le cou tendu vers nous, un
pied levé, l'œil rond et vide, le manteau qui flotte d'un côté.

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

TAUPE = M.hexa("#bcaabc")                     # la dominante : taupe lavande (le poil la fonce : on la prend claire)
SOMBRE = M.hexa("#8a7888")                    # les mèches du bas, la croupe
COU = M.hexa("#9ec0d8")                       # le cou nu, bleuté
AMBRE = M.hexa("#e8a830")
CHARBON = M.hexa("#3a3036")
PATTE = M.hexa("#8a7a78")
CORPS = Vector((0.0, 0.080, 0.600))
LACET = 20.0


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
    a = K.Animal("emeu")
    a.taille = 1.80

    # ----- le corps : un gros œuf couché, le dos en voûte ; dessus, un manteau de mèches qui retombent des flancs -----
    def oeuf(v):
        s = v * [0.240, 0.330, 0.270]
        s[:, 1] += 0.020 * v[:, 2]
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(oeuf), TAUPE, pos=CORPS, rot=(-6, 0, 0))
    rng = np.random.default_rng(9)
    meches = None
    for i in range(30):
        t = 2 * math.pi * (i + rng.uniform(-0.3, 0.3)) / 30
        base = np.array([0.232 * math.cos(t), CORPS.y + 0.318 * math.sin(t)])
        radial = np.array([math.cos(t) * 1.0, math.sin(t) * 0.70])
        radial /= np.linalg.norm(radial)
        hz = CORPS.z + rng.uniform(0.02, 0.12)
        k = 0.8 + 0.7 * rng.random()
        chemin = [(base[0] * 0.92, CORPS.y + (base[1] - CORPS.y) * 0.92, hz + 0.05), (base[0], base[1], hz - 0.03),
                  (base[0] + radial[0] * 0.040, base[1] + radial[1] * 0.040, hz - 0.14 * k),
                  (base[0] + radial[0] * 0.070, base[1] + radial[1] * 0.070, hz - 0.26 * k)]
        m = meche(chemin, 0.044 + 0.012 * rng.random(), (radial[0], radial[1], 0.0))
        meches = m if meches is None else meches + m
    a.piece("meches", meches, SOMBRE)

    # ----- le cou : long et nu, bleuté, qui part de l'épaule et se tend vers nous en S ; la tête : petite -----
    fil = K.Fil([(0.0, -0.250, 0.700), (0.0, -0.350, 0.860), (0.0, -0.360, 1.050), (0.0, -0.420, 1.200)], (1, 0, 0))
    L = fil.long
    pc = A.profil([(0, 0), (0.085, 0.03 * L), (0.060, 0.30 * L), (0.048, 0.70 * L), (0.046, 0.95 * L), (0, 1.01 * L)], 6)
    a.piece("cou", A.tour(pc, 28).sculpte(fil.couche), COU)
    bout = Vector(fil.cadre(L)[0])
    H = A.repere(bout + Vector((0.0, -0.030, 0.020)), (6, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.062, 0.078, 0.060), TAUPE, mat=H)
    a.tete = H @ Vector((0, -0.100, -0.010))
    bec = A.tour(A.profil([(0, 0), (0.034, 0.006), (0.030, 0.030), (0.018, 0.055), (0, 0.068)], 5), 24)
    a.piece("bec", bec.etire(1.0, 0.70, 1.0), M.hexa("#c8b0a0"), mat=A.cadre(H @ Vector((0, -0.070, -0.014)), H3 @ Vector((0, -0.96, -0.20)), (0, 0, 1)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.82, -0.40, 0.18))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.30, AMBRE, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0185)

    # ----- les pattes : très longues, charbon grisé, le genou marqué ; un pied levé, les gros pieds à trois doigts -----
    plantee = [(0.100, 0.060, 0.480), (0.108, 0.080, 0.300), (0.108, 0.140, 0.140), (0.108, 0.130, 0.030)]
    levee = [(-0.100, 0.060, 0.480), (-0.108, 0.030, 0.320), (-0.108, -0.080, 0.300), (-0.108, -0.130, 0.190)]
    for nom, chemin, pied in (("G", plantee, (0.108, 0.100, 0.014)), ("D", levee, (-0.108, -0.170, 0.170))):
        a.piece("patte_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.050 - 0.020 * t, 14), PATTE, poil=False)
        doigts = None
        for ang in (-28, 0, 28):
            d = A.boule(1.0, 14, 8).etire(0.016, 0.075, 0.014).pose((0, -0.060, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("doigts_" + nom, doigts, PATTE, pos=pied, rot=(-10 if nom == "D" else 0, 0, 0), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("emeu", styles.style_de("emeu"), sys.modules[__name__]), "Émeu")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py emeu). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.254                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.275, 0.586)),
    ('cou', 'corps', (0.000, -0.208, 0.738)),
    ('tete', 'cou', (-0.003, -0.425, 1.166)),
    ('patte_ar_G', 'corps', (0.101, 0.063, 0.481)),
    ('patte_av_G', 'corps', (0.090, 0.046, 0.027)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('meches', 'corps'), ('doigts', 'patte_av', True), ('corps', 'corps'),
    ('patte', 'patte_ar', True), ('patte', 'patte_av', True), ('tete', 'tete'), ('iris', 'tete'), ('oeil', 'tete'),
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
