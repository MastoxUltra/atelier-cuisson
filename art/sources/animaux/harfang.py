"""Le harfang en peluche de velours ras : tout blanc, moucheté de barres charbon qui s'épaississent sur le dos et les
ailes, la tête ronde sans aigrettes, deux grands yeux soufre sous des sourcils de plumes lourds, un petit bec noir
presque noyé dans la bavette. Une statue de givre sur sa souche : droit comme un i, les pieds en pantoufles de plumes,
la tête tournée de trois quarts et un peu baissée, qui nous toise.

    python harfang.py        fabrique la fiche art/apercus/animaux/harfang.png (velours ras, palier 3)
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

NEIGE = M.hexa("#fdfcf8")                     # la dominante : blanc moucheté (le poil le grise à peine)
CHARBON = M.hexa("#3a3638")                   # les barres
SOUFRE = M.hexa("#ffd21e")                    # l'accent : les yeux
BEC = M.hexa("#26222a")                       # le bec et les griffes
CORPS = Vector((0.0, 0.03, 0.262))
TETE = Vector((0.0, -0.040, 0.545))
LACET, PENCHE, PIQUE = 34.0, 9.0, -8.0        # la tête tournée vers nous, un peu de travers, le nez baissé


def barrer(m, dos=0.50, face=0.16, graine=1, une_sur=2):
    """Peint la boule encore unité en blanc et la mouchette de barres charbon : sur un anneau sur « une_sur », des
    tirets au hasard, plus drus vers le dos (+Y) que sur la face (-Y)."""
    rng = np.random.default_rng(graine)
    t = np.tile(np.asarray(NEIGE, float), (len(m.v), 1))
    for i, anneau in enumerate(m.anneaux):
        if len(anneau) < 2 or i % une_sur:
            continue
        for k in anneau:
            densite = face + (dos - face) * float(K.lisse(m.v[k, 1] * 0.8 + 0.5))
            if rng.random() < densite:
                t[k] = CHARBON
    m.teinte = t
    return m


def construire():
    a = K.Animal("harfang")
    a.taille = 0.85

    # ----- le corps : un œuf droit, le poitrail un peu rond, qui s'effile en bas vers les pieds ; barré -----
    def oeuf(v):
        v = K.bosse(v, (0, -0.9, 0.25), 0.10, 0.5)
        s = v * [0.150, 0.150, 0.215]
        s[:, 0] *= 1 - 0.18 * K.lisse((-v[:, 2] + 0.1) / 1.0)
        s[:, 1] *= 1 - 0.14 * K.lisse((-v[:, 2] + 0.1) / 1.0)
        return s
    a.piece("corps", barrer(A.boule(1.0, 56, 28), 0.40, 0.12, 1).sculpte(oeuf), None, pos=CORPS, rot=(-4, 0, 0))

    # ----- la tête : ronde, sans aigrettes, le front bombé ; blanche, quelques points charbon sur le crâne -----
    H = A.repere(TETE, (PIQUE, PENCHE, LACET))
    H3 = H.to_3x3()

    def crane(v):
        v = K.bosse(v, (0, -0.8, 0.3), 0.08, 0.5)
        return v * [0.118, 0.108, 0.108]
    a.piece("tete", barrer(A.boule(1.0, 48, 24), 0.22, 0.04, 3, 3).sculpte(crane), None, mat=H)
    a.tete = H @ Vector((0, -0.100, -0.005))

    # ----- les yeux : un disque soufre cerné de blanc, la pupille noire et son reflet ; sous un sourcil lourd, en biais -----
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.50, -0.82, 0.12))
        a.rustine("iris_" + nom, "tete", TETE, regard, 0.34, SOUFRE, 0.003, 0)
        p, n = a.surface("tete", TETE, regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0200)
        P = A.cadre(p + n * 0.006, n, H3 @ Vector((c * -0.45, 0.20, 1.0)))
        # (paupière retirée : yeux ouverts, bouton net, sans air fatigué ni fâché)

    # ----- le bec : un petit crochet noir entre les yeux, à demi noyé dans les plumes de la bavette -----
    B = A.cadre(H @ Vector((0, -0.100, -0.030)), H3 @ Vector((0, -0.86, -0.50)), H3 @ Vector((0, 0.5, 0.86)))
    bec = A.tour(A.profil([(0, 0), (0.020, 0.006), (0.019, 0.022), (0.012, 0.040), (0.004, 0.052), (0, 0.056)], 5), 28)
    bec.sculpte(lambda v: v + np.stack([np.zeros(len(v)), -0.014 * (v[:, 2] / 0.056) ** 2, np.zeros(len(v))], axis=1))
    a.piece("bec", bec, BEC, mat=B, poil=False)
    a.piece("bavette", A.boule(1.0, 28, 14).etire(0.034, 0.024, 0.030), NEIGE, mat=H @ A.repere((0, -0.088, -0.042)))

    # ----- les ailes : deux galets plaqués sur les flancs, plus drus en barres, la pointe qui croise sous la queue -----
    def galet(v):
        s = K.emousse(v, 0.85)
        s[:, 2] *= 1 - 0.40 * K.lisse((v[:, 1] + 0.2) / 1.2)
        return s
    for nom, c in (("G", 1), ("D", -1)):
        aile = barrer(A.boule(1.0, 40, 20), 0.42, 0.26, 5 + (c > 0), 2)
        a.piece("aile_" + nom, aile.sculpte(galet).etire(0.032, 0.180, 0.135), None, pos=(c * 0.125, 0.055, 0.250), rot=(-8, 0, c * 4))

    # ----- la queue : un court éventail barré qui descend derrière -----
    queue = barrer(A.tour(A.profil([(0, 0), (0.060, 0.010), (0.056, 0.070), (0.040, 0.130), (0.020, 0.170), (0, 0.185)], 6), 36), 0.62, 0.50, 7, 1)
    a.piece("queue", queue.etire(1.0, 0.34, 1.0), None, pos=(0, 0.150, 0.215), rot=(168, 0, 0))

    # ----- les pieds : deux grosses pantoufles de plumes blanches, les griffes noires qui dépassent -----
    for nom, c in (("G", 1), ("D", -1)):
        # des pieds comme ceux du hibou gardé : trois doigts séparés qui dépassent sous le ventre, les serres sombres au bout
        def doigt(degres):
            t = math.radians(degres)
            return A.boule(1.0, 16, 8).etire(0.017, 0.050, 0.014).pose((0.034 * math.sin(t), -0.034 * math.cos(t), 0.0), (0, 0, degres))
        a.piece("pied_" + nom, doigt(-26) + doigt(0) + doigt(26), NEIGE, pos=(c * 0.060, -0.052, 0.016), poil=False)
        for k in (-1, 0, 1):
            griffe = A.tour(A.profil([(0, 0), (0.008, 0.004), (0.006, 0.026), (0.003, 0.046), (0, 0.058)], 5), 14)
            a.piece("griffe_%s%d" % (nom, k), griffe, BEC, mat=A.cadre(Vector((c * 0.060 + k * 0.036, -0.128, 0.012)), Vector((k * 0.30, -0.95, -0.20)), (0, 0, 1)), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("harfang", styles.style_de("harfang"), sys.modules[__name__]), "Harfang")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py harfang). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde
GONFLAGE = True      # gardée par l'auteur sur la base GONFLÉE (planche 17, 15/10) : toujours gonflée

JAMBE = 0.085                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.098, 0.122)),
    ('tete', 'corps', (0.005, -0.028, 0.440)),
    ('patte_av_G', 'corps', (0.061, -0.027, 0.085)),
    ('aile_G', 'corps', (0.127, 0.026, 0.384)),
    ('queue', 'corps', (0.000, 0.114, 0.119)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('griffe_G-1', 'patte_av_G'), ('griffe_D-1', 'patte_av_D'), ('griffe_G0', 'patte_av_G'),
    ('griffe_G1', 'patte_av_G'), ('griffe_D0', 'patte_av_D'), ('griffe_D1', 'patte_av_D'), ('bavette', 'corps'),
    ('lourde', 'tete'), ('corps', 'corps'), ('queue', 'queue'), ('tete', 'tete'), ('aile', 'aile', True),
    ('iris', 'tete'), ('oeil', 'tete'), ('pied', 'patte_av', True), ('bec', 'tete'), ('paupiere_0', 'paupiere_0'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.026 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
