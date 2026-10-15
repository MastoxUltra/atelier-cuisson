"""Le quetzal en peluche de velours ras : un turquoise profond, penché vers le bleu (jamais le vert de l'herbe), le ventre
cramoisi, la tête coiffée d'une crête ronde en pompon, un petit bec jaune, et surtout les deux très longues plumes de
queue qui retombent à ses pieds comme des rubans de soie. Le dieu des cimes, perché sur ses pattes courtes : le
poitrail bombé, le dos droit, la tête de profil et le bec levé, une aile dépliée à moitié qui reflète le ciel.

    python quetzal.py        fabrique la fiche art/apercus/animaux/quetzal.png (velours ras, palier 3)
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

TURQUOISE = M.hexa("#1f9ad8")                 # la dominante : turquoise profond, qui penche vers le bleu
NUIT = M.hexa("#1560b8")                      # le dos, le bout des plumes : un ton plus bas
CRAMOISI = M.hexa("#e8244a")                  # l'accent : le ventre
BEC = M.hexa("#ffd22a")                       # le bec
BLANC = M.hexa("#fff8f0")                     # le dessous de la queue
CORPS = Vector((0.0, 0.040, 0.320))
TETE = Vector((0.0, -0.065, 0.560))
LACET = 32.0


def plume(chemin, large, face, paliers, plat=0.30, cotes=14):
    """Une longue plume plate (le geste des mèches du cheval) peinte par tronçons : paliers = [(fraction, couleur), ...]."""
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
    prof = A.profil([(0, 0), (0.55 * large, 0.03 * L), (0.95 * large, 0.18 * L), (large, 0.40 * L), (0.85 * large, 0.70 * L),
                     (0.45 * large, 0.93 * L), (0, L)], 5)
    m = A.tour(prof, cotes).etire(1.0, plat, 1.0)
    t = np.zeros((len(m.v), 3))
    reste = np.ones(len(m.v), bool)
    for fr, c in paliers:
        ici = reste & (m.v[:, 2] <= fr * L)
        t[ici] = c
        reste &= ~ici
    t[reste] = paliers[-1][1]
    m.teinte = t
    return m.sculpte(couche)


def construire():
    a = K.Animal("quetzal")
    a.taille = 1.00                           # queue comprise

    # ----- le corps : un œuf dressé, le poitrail cramoisi devant (peint avant d'être sculpté), le dos bleu -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(TURQUOISE, float), (len(v), 1))
    t[(v[:, 1] < -0.18) & (v[:, 2] < 0.55)] = CRAMOISI
    t[(v[:, 1] > 0.45)] = NUIT
    corps.teinte = t

    def oeuf(v):
        v = K.bosse(v, (0, -0.9, 0.2), 0.14, 0.45)
        s = v * [0.098, 0.088, 0.160]
        s[:, 0] *= 1 - 0.18 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s
    a.piece("corps", corps.sculpte(oeuf), None, pos=CORPS, rot=(-10, 0, 0))

    # ----- la tête : ronde, la crête en pompon ; tournée de trois quarts, le bec levé -----
    H = A.repere(TETE, (-6, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 40, 20).etire(0.062, 0.060, 0.060), TURQUOISE, mat=H)
    a.piece("crete", A.boule(1.0, 28, 14).etire(0.060, 0.058, 0.052), TURQUOISE, mat=H @ A.repere((0, 0.018, 0.040)))
    a.tete = H @ Vector((0, -0.070, -0.005))
    B = A.cadre(H @ Vector((0, -0.054, -0.008)), H3 @ Vector((0, -0.97, 0.10)), H3 @ Vector((0, 0, 1)))
    bec = A.tour(A.profil([(0, 0), (0.024, 0.006), (0.021, 0.030), (0.012, 0.056), (0.004, 0.072), (0, 0.078)], 5), 24)
    a.piece("bec", bec.etire(0.88, 0.78, 1.0), BEC, mat=B, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.70, -0.62, 0.14)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0108)

    # ----- les ailes : deux galets bleus plaqués sur les flancs ; la gauche (vers nous) à moitié dépliée -----
    for nom, c, rot in (("G", 1, (-10, 0, 18)), ("D", -1, (-8, 0, -4))):
        aile = A.boule(1.0, 36, 18)
        aile.teinte = np.where((aile.v[:, 2] > 0.35)[:, None], np.asarray(NUIT), np.asarray(TURQUOISE))

        def galet(v):
            s = K.emousse(v, 0.88)
            s[:, 1] *= 1 - 0.50 * K.lisse((v[:, 2] + 0.2) / 1.2)
            return s
        a.piece("aile_" + nom, aile.sculpte(galet).etire(0.026, 0.052, 0.170), None, pos=(c * 0.100, 0.050, 0.290), rot=rot)

    # ----- la queue : deux très longues plumes plates, le dessus turquoise, qui retombent presque au sol, le bout nuit -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.020, 0.150, 0.280), (c * 0.050, 0.240, 0.140), (c * 0.075, 0.320, 0.040), (c * 0.110, 0.470, 0.018), (c * 0.140, 0.640, 0.016)]
        a.piece("plume_" + nom, plume(chemin, 0.034, (1, 0, 0), [(0.40, TURQUOISE), (0.88, NUIT), (1.0, BLANC)]), None, poil=False)

    # ----- les pattes : deux petits jonc, les doigts serrés en pince -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("patte_" + nom, A.tube(A.courbe([(c * 0.044, 0.030, 0.170), (c * 0.048, 0.000, 0.080), (c * 0.050, -0.030, 0.026)], 5), 0.017, 12),
                M.hexa("#c8a050"), poil=False)
        doigts = None
        for ang in (-28, 0, 28):
            d = A.boule(1.0, 14, 8).etire(0.011, 0.044, 0.010).pose((0, -0.034, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("doigts_" + nom, doigts, M.hexa("#c8a050"), pos=(c * 0.050, -0.030, 0.010), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("quetzal", styles.style_de("quetzal"), sys.modules[__name__]), "Quetzal")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py quetzal). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.163                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.083, 0.209)),
    ('tete', 'corps', (0.001, -0.045, 0.505)),
    ('patte_av_G', 'corps', (0.044, 0.027, 0.163)),
    ('aile_G', 'corps', (0.091, 0.078, 0.455)),
    ('queue', 'corps', (0.000, 0.151, 0.244)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('doigts', 'patte_av', True), ('corps', 'corps'), ('plume', 'queue'), ('crete', 'tete'),
    ('patte', 'patte_av', True), ('aile', 'aile', True), ('tete', 'tete'), ('oeil', 'tete'), ('bec', 'tete'),
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
    p.paire('aile', rot=(0, -3 * cloche(t, 0.55, 0.06), 0))
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
    p.add('queue', rot=(-6, 0, -10 * s))
    p.paire('aile', rot=(0, -2 + 2 * onde(t, 2), 0))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.049 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    p.paire('aile', rot=(0, -48 * vol, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.02), rot=(36, 0, 6), ech=(1 + 0.010 * r, 1, 1 + 0.020 * r))
    p.paire('patte_av', rot=(-30, 0, 0))
    p.add('tete', rot=(32, 4, 40))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
