"""Le colibri en peluche, cousu main : un violet améthyste irisé, la gorge rubis, le ventre crème, un long bec-aiguille
charbon, des ailes en lames pointues levées en V et une queue en fourche. Le plus petit des gros bavards : posé en
pleine envolée, penché en avant, le bec pointé comme une épée, les ailes à demi dressées, une patte minuscule qui
touche à peine le sol : il s'arrête en route juste le temps de nous toiser.

    python colibri.py        fabrique la fiche art/apercus/animaux/colibri.png (cousu main, palier 2)
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

AMETHYSTE = M.hexa("#b080f0")                 # la dominante : améthyste irisé (le poil le fonce : on le prend clair)
INDIGO = M.hexa("#6a4fd0")                    # le bout des ailes et de la queue : un ton plus bas
RUBIS = M.hexa("#f0305f")                     # l'accent : la gorge
CREME = M.hexa("#fff2e4")                     # le ventre
CHARBON = M.hexa("#3a3236")                   # le bec, les pattes
CORPS = Vector((0.0, 0.050, 0.215))
TETE = Vector((0.0, -0.075, 0.345))
LACET = 26.0                                  # la tête tournée vers nous


def construire():
    a = K.Animal("colibri")
    a.taille = 0.42

    # ----- le corps : un œuf penché en avant ; le ventre crème devant, le dos améthyste ; une couture de dos -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(AMETHYSTE, float), (len(v), 1))
    t[(v[:, 1] < -0.30) & (v[:, 2] < 0.45)] = CREME
    corps.teinte = t

    def oeuf(v):
        s = v * [0.080, 0.088, 0.120]
        s[:, 1] -= 0.030 * K.lisse((v[:, 2] + 0.1) / 1.0)
        return s
    a.piece("corps", corps.sculpte(oeuf), None, pos=CORPS, rot=(-26, 0, 0))

    # ----- la tête : ronde, le front bombé ; la gorge rubis posée en bavoir dessous -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 40, 20).etire(0.062, 0.060, 0.060), AMETHYSTE, mat=H)
    a.rustine("gorge", "tete", TETE + Vector((0, 0.01, 0.0)), H3 @ Vector((0, -0.50, -0.86)), lambda th: 0.78 + 0.10 * math.cos(2 * th), RUBIS, 0.003, 0)
    a.tete = H @ Vector((0, -0.080, 0.0))

    # ----- le bec : une aiguille charbon, longue et fine, un tout petit peu courbée vers le bas -----
    B = A.cadre(H @ Vector((0, -0.052, -0.004)), H3 @ Vector((0, -0.97, -0.16)), H3 @ Vector((0, 0.2, 0.98)))

    def aiguille(v):
        s = v.copy()
        s[:, 1] -= 0.014 * np.clip(v[:, 2] / 0.20, 0, 1) ** 2
        return s
    a.piece("bec", A.tour(A.profil([(0, 0), (0.013, 0.004), (0.010, 0.060), (0.006, 0.160), (0.003, 0.215), (0, 0.228)], 5), 16).sculpte(aiguille),
            CHARBON, mat=B, poil=False)

    # ----- les yeux : un seul bouton de chaque côté, petit, brillant, sous un sourcil d'indigo -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, H3 @ Vector((c * 0.66, -0.66, 0.16)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0125)

    # ----- les ailes : deux lames pointues levées en V, le bout indigo ; la gauche (vers nous) plus haute -----
    for nom, c, vers in (("G", 1, (0.80, 0.30, 0.55)), ("D", -1, (-0.74, 0.34, 0.50))):
        aile = A.boule(1.0, 36, 18)
        aile.teinte = np.where((aile.v[:, 2] > 0.25)[:, None], np.asarray(INDIGO), np.asarray(AMETHYSTE))

        def lame(v):
            s = v.copy()
            s[:, 1] *= 1 - 0.55 * K.lisse((v[:, 2] + 0.1) / 1.1)
            s[:, 0] *= 1 - 0.35 * K.lisse((v[:, 2] + 0.2) / 1.2)
            return s
        a.piece("aile_" + nom, aile.sculpte(lame).etire(0.018, 0.050, 0.150).pose((0, 0, 0.130)), None,
                mat=A.cadre(Vector((c * 0.050, 0.070, 0.260)), Vector(vers), Vector((c * 0.2, -0.2, 0.9))))

    # ----- la queue : un petit éventail fourchu, indigo, qui retombe derrière -----
    for nom, c, cap in (("G", 1, 14), ("D", -1, -14)):
        lobe = A.boule(1.0, 20, 10).etire(0.018, 0.012, 0.085).pose((0, 0, 0.060), (0, 0, 0))
        a.piece("queue_" + nom, lobe, INDIGO, pos=(c * 0.012, 0.165, 0.195), rot=(150, 0, c * cap), poil=False)

    # ----- les pattes : deux brins de charbon, de minuscules doigts ; il touche à peine le sol -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("patte_" + nom, A.tube(A.courbe([(c * 0.026, 0.030, 0.130), (c * 0.030, 0.010, 0.060), (c * 0.032, -0.008, 0.014)], 4), 0.008, 10),
                CHARBON, poil=False)
        a.piece("doigts_" + nom, A.boule(1.0, 14, 8).etire(0.016, 0.026, 0.008), CHARBON, pos=(c * 0.032, -0.014, 0.008), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("colibri", styles.style_de("colibri"), sys.modules[__name__]), "Colibri")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py colibri). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde
GONFLAGE = True      # gardée par l'auteur sur la base GONFLÉE (planche 17, 15/10) : toujours gonflée

JAMBE = 0.130                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.088, 0.137)),
    ('tete', 'corps', (0.000, -0.038, 0.301)),
    ('patte_av_G', 'corps', (0.026, 0.030, 0.130)),
    ('aile_G', 'corps', (0.264, 0.149, 0.412)),
    ('queue', 'corps', (0.002, 0.113, 0.121)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('doigts', 'patte_av', True), ('corps', 'corps'), ('gorge', 'tete'),
    ('patte', 'patte_av', True), ('queue', 'queue'), ('aile', 'aile', True), ('tete', 'tete'), ('oeil', 'tete'),
    ('bec', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'),
    ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.039 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
