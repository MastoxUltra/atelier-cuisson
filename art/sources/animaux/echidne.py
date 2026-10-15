"""L'échidné en peluche de velours ras : un brun prune, tout le dos hérissé de piquants crème à pointe sombre, une
petite face ronde qui se prolonge en long bec fin et courbe, de minuscules yeux, des pattes courtes aux griffes
puissantes, et un ventre de poil. Le hérisson-fourmilier : trapu, bas, le museau au ras du sol qui renifle, une patte
avant creusant la terre, les piquants dressés en couronne, un œil en coin qui vérifie qu'on ne le suit pas.

    python echidne.py        fabrique la fiche art/apercus/animaux/echidne.png (velours ras, palier 3)
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

PRUNE = M.hexa("#8a6070")                     # la dominante : brun prune (le poil la fonce : on la prend claire)
CREME = M.hexa("#fff2d0")                     # l'accent : les piquants
POINTE = M.hexa("#5a4048")                    # le bout des piquants, le museau
CHARBON = M.hexa("#3a2c30")
CORPS = Vector((0.0, 0.050, 0.130))
TETE = Vector((0.0, -0.200, 0.115))
LACET = 22.0


def construire():
    a = K.Animal("echidne")
    a.taille = 0.50

    # ----- le corps : un dôme bas, large ; dessus, des rangs de piquants de feutrine (le geste des plumes du cygne) -----
    def dome(v):
        s = v * [0.150, 0.230, 0.118]
        s[:, 2] = np.where(s[:, 2] < 0, s[:, 2] * 0.55, s[:, 2])
        return s
    dos = A.boule(1.0, 48, 24).sculpte(dome)
    dos.teinte = np.tile(np.asarray(PRUNE, float), (len(dos.v), 1))
    a.piece("corps", dos, None, pos=CORPS)
    piquants = G.franges(dos, 0.080, 0.016, 0.022, 0.030,
                         lambda rang, t: tuple(np.asarray(CREME) * (0.88 + 0.12 * (rang % 2)) * (0.7 + 0.3 * t) + np.asarray(POINTE) * (0.25 * (1 - t))),
                         5, 1, 0.10, 0.98)
    a.piece("piquants", piquants, None, pos=CORPS, poil=False)

    # ----- la tête : une petite boule ronde sans cou, qui se prolonge en long bec fin, courbé vers le bas -----
    H = A.repere(TETE, (14, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.058, 0.060, 0.055), PRUNE, mat=H)

    def courbe_(v):
        s = v.copy()
        s[:, 1] -= 0.030 * np.clip(v[:, 2] / 0.200, 0, 1) ** 2
        return s
    bec = A.tour(A.profil([(0, 0), (0.030, 0.006), (0.024, 0.040), (0.014, 0.110), (0.008, 0.175), (0.004, 0.205), (0, 0.215)], 5), 24)
    a.piece("bec", bec.sculpte(courbe_), POINTE, mat=H @ A.repere((0, -0.040, -0.010), (90, 0, 0)))
    a.tete = H @ Vector((0, -0.150, -0.030))
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.82, -0.50, 0.22)))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0095)

    # ----- les pattes : quatre troncs courts, aux grandes griffes ; l'avant droite creuse -----
    for nom, x, y, creuse in (("av_G", 0.115, -0.090, False), ("av_D", -0.115, -0.090, True), ("ar_G", 0.115, 0.190, False), ("ar_D", -0.115, 0.190, False)):
        c = 1 if x > 0 else -1
        chemin = [(x * 0.8, y, 0.080), (x * 1.04, y - 0.010, 0.040), (x * 1.06, y - (0.050 if creuse else 0.020), 0.016)]
        a.piece("patte_" + nom, A.tube(A.courbe(chemin, 5), 0.030, 12), PRUNE)
        griffes = None
        for k in (-1, 0, 1):
            g = A.tour(A.profil([(0, 0), (0.008, 0.003), (0.006, 0.026), (0.003, 0.048), (0, 0.058)], 5), 10)
            g = g.pose((0, 0, 0), (-84, 0, 0)).pose((k * 0.018, -0.020, 0.0), (0, 0, k * 8))
            griffes = g if griffes is None else griffes + g
        a.piece("griffes_" + nom, griffes, CHARBON, pos=(x * 1.06, y - (0.050 if creuse else 0.020), 0.012), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("echidne", styles.style_de("echidne"), sys.modules[__name__]), "Échidné")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py echidne). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.075                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.182, 0.162)),
    ('tete', 'corps', (-0.000, -0.145, 0.124)),
    ('patte_av_G', 'corps', (0.105, -0.095, 0.075)),
    ('patte_ar_G', 'corps', (0.105, 0.185, 0.075)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('griffes_av', 'patte_av', True), ('griffes_ar', 'patte_ar', True),
    ('piquants', 'corps'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('corps', 'corps'),
    ('tete', 'tete'), ('oeil', 'tete'), ('bec', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
    ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
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
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.022 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.041), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
