"""La fourmi en peluche : trois boules framboise bien séparées, six pattes en plein pas, un sucre serré entre les mandibules.

    python fourmi.py        fabrique la fiche art/apercus/animaux/fourmi.png
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

GRENAT = M.hexa("#4a1b2a")                    # la feutrine sombre des pattes, des antennes et des mandibules
TETE = Vector((0.0, -0.088, 0.100))
THORAX = Vector((0.0, -0.004, 0.080))
POINTE = Vector((0.0, 0.143, 0.102))          # le bout arrière de l'abdomen, un peu relevé
PENTE = math.radians(12)
AXE = Vector((0.0, -math.cos(PENTE), -math.sin(PENTE)))     # l'abdomen file de sa pointe vers la taille
LONG, GROS = 0.100, 0.045                     # la longueur de l'abdomen et son plus gros rayon
ABDOMEN = POINTE + AXE * LONG * 0.55          # un point au cœur de l'abdomen
PLIS = (0.36, 0.63)                           # deux anneaux qui serrent un peu l'abdomen


def rayon(t):
    """Le rayon de l'abdomen à la fraction t de sa longueur : une goutte, pointue derrière, ronde devant."""
    u = t ** 1.35
    r = GROS * math.sqrt(max(0.0, 1 - (2 * u - 1) ** 2))
    return r * (1 - 0.05 * sum(math.exp(-((t - b) / 0.035) ** 2) for b in PLIS))


def patte(cote, hanche, genou, pied, pas):
    """Une patte coudée : la hanche dans le thorax, le genou haut, le pied à plat. cote : 1 à gauche, -1 à droite.
    pas : de combien le pied avance (négatif) ou traîne (positif), pour qu'elle ait l'air de marcher."""
    points = [(hanche[0], hanche[1], hanche[2]),
              (genou[0], genou[1] + pas * 0.45, genou[2]),
              (pied[0], pied[1] + pas, 0.013),
              (pied[0] + 0.017, pied[1] + pas * 1.25, 0.0058)]
    chemin = A.conges([(cote * x, y, z) for x, y, z in points], 0.009, 4)
    return A.tube(chemin, lambda t: 0.0064 - 0.0020 * t, 8)


def construire():
    a = K.Animal("fourmi")
    a.taille = 0.32
    a.tete = TETE + Vector((0, -0.036, -0.004))

    # ----- l'abdomen : une goutte tournée, la pointe en l'air, cousue sur le dos -----
    pas = 0.5 - 0.5 * np.cos(np.linspace(0, math.pi, 26))
    profil = [(rayon(t), t * LONG) for t in pas]
    profil[0], profil[-1] = (0.0, 0.0), (0.0, LONG)
    abdomen = A.tour(profil, 48)
    G.sillons(abdomen, [12], 0.003, 1.1)
    a.piece("abdomen", abdomen, K.FRAMBOISE, pos=POINTE, rot=(90 + math.degrees(PENTE), 0, 0))
    a.couture("dos", "abdomen", 12, 0.08, 0.96, large=0.007, haut=0.0032, pas=0.011)
    a.rustine("piece", "abdomen", ABDOMEN, (0.74, 0.30, 0.60), 0.44, K.PECHE, 0.0025, 14)

    # ----- le thorax, et les deux tailles de feutrine qui tiennent les trois boules -----
    thorax = A.boule(1.0, 48, 24).etire(0.030, 0.035, 0.029)
    G.sillons(thorax, [12, 36], 0.0025, 1.1)
    a.piece("thorax", thorax, K.FRAMBOISE, pos=THORAX)
    for cote in (12, 36):
        a.couture("echine%d" % cote, "thorax", cote, 0.66, 1.0, large=0.006, haut=0.003, pas=0.010)
    taille = A.tube([tuple(THORAX), tuple(ABDOMEN)], 0.0075, 10) + A.boule(0.0115, 20, 10).pose((0, 0.0375, 0.080))
    cou = A.tube([tuple(THORAX + Vector((0, -0.02, 0.004))), tuple(TETE + Vector((0, 0.015, -0.004)))], 0.0115, 12)
    a.piece("tailles", taille + cou, GRENAT, poil=False)

    # ----- la tête : grosse, qui s'affine vers les mandibules -----
    def crane(v):
        s = v * [0.040, 0.036, 0.037]
        s[:, 0] *= 1 - 0.24 * K.lisse((-v[:, 1] - v[:, 2]) * 0.7)
        return s
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(crane), K.FRAMBOISE, pos=TETE)
    a.couture("crane", "tete", 14, 0.56, 0.98, large=0.006, haut=0.003, pas=0.010)
    p, n = a.surface("tete", TETE, (0.76, -0.50, 0.40))
    a.bouton("oeil", p + n * 0.001, n, 0.0145, paire=True)

    # ----- les antennes coudées : la hampe monte, le fouet part vers l'avant, tâte le chemin -----
    coude = A.conges([TETE + Vector(q) for q in ((0.014, -0.016, 0.026), (0.036, -0.022, 0.076), (0.050, -0.086, 0.052))], 0.008, 4)
    a.piece("antenne", A.tube(coude, lambda t: 0.0042 + 0.0020 * float(K.lisse((t - 0.72) / 0.28)), 8), GRENAT, poil=False, paire=True)

    # ----- les mandibules : deux crochets de feutrine qui serrent un morceau de sucre -----
    crochet = A.courbe([TETE + Vector(q) for q in ((0.013, -0.026, -0.017), (0.027, -0.045, -0.021), (0.027, -0.060, -0.024), (0.017, -0.070, -0.025))], 5)
    a.piece("mandibule", A.tube(crochet, lambda t: 0.0078 - 0.0040 * t, 8), GRENAT, poil=False, paire=True)

    # ----- les six pattes, en plein pas : trois avancent, trois poussent (un trépied de chaque côté) -----
    for cote, nom in ((1, "pattes_g"), (-1, "pattes_d")):
        elan = 0.013 * cote
        pattes = patte(cote, (0.016, -0.026, 0.068), (0.056, -0.052, 0.106), (0.082, -0.090, 0), -elan) \
            + patte(cote, (0.022, -0.004, 0.066), (0.072, 0.000, 0.118), (0.104, 0.004, 0), elan) \
            + patte(cote, (0.016, 0.018, 0.068), (0.062, 0.052, 0.122), (0.092, 0.104, 0), -elan)
        a.piece(nom, pattes, GRENAT, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py fourmi)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, -0.004, 0.080)),         # le thorax : les six pattes y sont plantées
    ("abdomen", "corps", (0, 0.038, 0.080)),         # la taille
    ("tete", "corps", (0, -0.058, 0.094)),           # le cou
    ("antenne_G", "tete", (0.014, -0.104, 0.126)),
    ("mandibule_G", "tete", (0.013, -0.114, 0.083)),
    ("patte1_G", "corps", (0.016, -0.026, 0.068)),   # les hanches, de l'avant vers l'arrière
    ("patte2_G", "corps", (0.022, -0.004, 0.066)),
    ("patte3_G", "corps", (0.016, 0.018, 0.068)),
]

# le fil de chaque patte gauche : la hanche, le genou, le pied (les mêmes mesures que dans construire)
FILS = (((0.016, -0.026, 0.068), (0.056, -0.052, 0.106), (0.082, -0.090, 0.013)),
        ((0.022, -0.004, 0.066), (0.072, 0.000, 0.118), (0.104, 0.004, 0.013)),
        ((0.016, 0.018, 0.068), (0.062, 0.052, 0.122), (0.092, 0.104, 0.013)))


def pattes(points, cote):
    """Les trois pattes d'un côté sont une seule pièce : chaque point suit la patte dont le fil passe le plus près.
    Les deux côtés sont deux pièces sans « _G » ni « _D » : on reconnaît le côté au signe de x."""
    gauche = points[:, 0].mean() > 0
    q = points * ([1, 1, 1] if gauche else [-1, 1, 1])
    ecarts = []
    for fil in FILS:
        e = np.full(len(q), 9.0)
        for a, b in zip(fil[:-1], fil[1:]):
            a, b = np.array(a), np.array(b)
            u = np.clip((q - a) @ (b - a) / ((b - a) @ (b - a)), 0.0, 1.0)
            e = np.minimum(e, np.linalg.norm(q - a - u[:, None] * (b - a), axis=1))
        ecarts.append(e)
    proche = np.argmin(ecarts, axis=0)
    return {"patte%d_%s" % (i + 1, "G" if gauche else "D"): (proche == i).astype(float) for i in range(3)}


PORTEURS = [("abdomen", "abdomen"), ("dos", "abdomen"), ("piece", "abdomen"), ("thorax", "corps"), ("echine", "corps"),
            ("tailles", "corps"), ("tete", "tete"), ("crane", "tete"), ("oeil", "tete"), ("antenne", "antenne", True),
            ("mandibule", "mandibule", True), ("pattes_g", pattes, "patte1_G"), ("pattes_d", pattes, "patte1_D")]


def doux(x):
    """De 0 à 1 en douceur, pour un geste qui part et s'arrête sans à-coup."""
    x = borne(x)
    return x * x * (3 - 2 * x)


def devant(i, signe):
    """Le modèle est cousu en plein pas : ce trépied-ci a les pieds en avant (l'avant et l'arrière gauches, le milieu droit)."""
    return (i == 2) != (signe > 0)


def trepied(p, t, pas, leve, cale):
    """La marche à six pattes : un trépied avance en l'air pendant que l'autre pousse au sol, puis ils échangent.
    pas, leve : les angles du balancement et du lever. cale : l'angle qui ramène d'abord chaque patte au milieu
    de son pas, pour que les deux trépieds fassent la même foulée."""
    for i in (1, 2, 3):
        for cote, signe in (("_G", 1), ("_D", -1)):
            phase = math.tau * t + (0.0 if devant(i, signe) else math.pi)
            vers_l_avant = pas * math.cos(phase) - (cale if devant(i, signe) else -cale)
            p.add("patte%d%s" % (i, cote), rot=(0, -signe * leve * max(0.0, -math.sin(phase)), -signe * vers_l_avant))


def souleve(p, un, autre):
    """Lève les pieds du trépied de devant de « un » degrés, ceux de l'autre trépied de « autre » degrés."""
    for i in (1, 2, 3):
        for cote, signe in (("_G", 1), ("_D", -1)):
            p.add("patte%d%s" % (i, cote), rot=(0, -signe * (un if devant(i, signe) else autre), 0))


def repos(t):
    """Elle ne tient pas en place : les antennes tâtent l'air l'une après l'autre, deux coups d'œil secs à gauche
    puis à droite, les mandibules claquent, l'abdomen tressaute, et elle piétine comme si on la faisait attendre."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.16, 0.06), cloche(t, 0.34, 0.06)
    clac = cloche(t, 0.46, 0.025) + cloche(t, 0.52, 0.025)
    pietine = cloche(t, 0.78, 0.14)
    p.add("corps", ech=(1 + 0.010 * r, 1, 1 + 0.015 * r))
    p.add("abdomen", rot=(2.5 * r + 9 * cloche(t, 0.62, 0.04), 0, 0), ech=(1 + 0.015 * r, 1, 1 + 0.015 * r))
    p.add("tete", rot=(-4 * (g + d), 8 * g - 8 * d, 28 * g - 28 * d))
    p.add("antenne_G", rot=(11 * onde(t, 5), 0, 7 * onde(t, 3)))
    p.add("antenne_D", rot=(-11 * onde(t, 5), 0, 7 * onde(t, 2)))
    p.paire("mandibule", rot=(0, 0, 20 * clac))
    souleve(p, 14 * pietine * max(0.0, onde(t, 8)), 14 * pietine * max(0.0, -onde(t, 8)))
    p.ouvert = 1 - cloche(t, 0.25, 0.02) - cloche(t, 0.90, 0.02)
    return p


def avance(t):
    """Elle file à petits pas pressés, deux foulées par boucle, en trépied alterné ; les antennes tâtent le chemin
    l'une après l'autre, la tête balaie, l'abdomen suit en se dandinant."""
    p = Pose()
    c, s = math.cos(2 * math.tau * t), math.sin(2 * math.tau * t)
    trepied(p, 2 * t, 15, 16, 8)
    p.add("corps", pos=(0, 0, 0.002 * abs(s)), rot=(0, 2 * s, 2.5 * c))
    p.add("abdomen", rot=(3 * onde(t, 4), 0, -5 * c))
    p.add("tete", rot=(4, 0, 7 * onde(t, 1)))
    p.add("antenne_G", rot=(14 + 14 * onde(t, 3), 0, 6 * onde(t, 1)))
    p.add("antenne_D", rot=(14 + 14 * onde(t, 3, 0.5), 0, 6 * onde(t, 1)))
    return p


def mange(t):
    """Le nez au sol et l'abdomen en l'air, elle découpe sa trouvaille : les mandibules cisaillent, les antennes
    la palpent l'une après l'autre ; puis elle relève la tête, les mandibules ouvertes, et regarde autour d'elle."""
    p = Pose()
    leve = cloche(t, 0.85, 0.13)
    bas = 1 - leve
    coups = max(0.0, onde(t, 5)) ** 2 * bas
    p.add("corps", rot=(11 * bas, 0, 0))
    p.add("abdomen", rot=(6 * bas + 3 * coups, 0, 0))
    p.add("tete", rot=(13 * bas + 5 * coups - 8 * leve, 0, 18 * leve * onde(t, 4)))
    p.paire("mandibule", rot=(0, 0, (4 + 12 * onde(t, 10)) * bas + 14 * leve))
    p.add("antenne_G", rot=(14 * bas + 11 * onde(t, 5) * bas - 10 * leve, 0, 6 * bas))
    p.add("antenne_D", rot=(14 * bas - 11 * onde(t, 5) * bas - 10 * leve, 0, -6 * bas))
    for i in (1, 2, 3):
        p.paire("patte%d" % i, rot=(-11 * bas, 0, 0))            # les pattes restent d'aplomb sous le thorax qui bascule
    return p


def joie(t):
    """Elle se cabre sur ses quatre pattes arrière, bat l'air de ses pattes avant, les antennes en V et les mandibules
    grandes ouvertes, l'abdomen qui frétille ; puis elle retombe sur ses pattes."""
    p = Pose()
    env = doux(t / 0.22) * (1 - doux((t - 0.68) / 0.22))
    bat = onde(t, 6) * env
    p.add("corps", pos=(0, 0, 0.008 * env), rot=(-28 * env, 4 * bat, 0))
    p.add("abdomen", rot=(16 * env, 0, 12 * onde(t, 8) * env))
    p.add("tete", rot=(12 * env, -4 * bat, 0))
    p.add("antenne_G", rot=(-22 * env + 8 * bat, 14 * env, 0))
    p.add("antenne_D", rot=(-22 * env - 8 * bat, -14 * env, 0))
    p.paire("mandibule", rot=(0, 0, 22 * env))
    p.add("patte1_G", rot=(-10 * env + 16 * bat, -8 * env, 0))
    p.add("patte1_D", rot=(-10 * env - 16 * bat, 8 * env, 0))
    p.paire("patte2", rot=(28 * env, 7 * env, 0))                # les quatre pattes arrière restent plantées
    p.paire("patte3", rot=(28 * env, 0, 0))
    return p


def dort(t):
    """Tapie : le ventre par terre, les pattes repliées, genoux en l'air, la tête posée, les antennes rabattues
    en arrière le long du cou (devant, elles barraient le visage), les mandibules serrées, les yeux fermés ;
    seul l'abdomen respire."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.045))
    p.add("abdomen", rot=(-3 + 1.5 * r, 0, 0), ech=(1 + 0.03 * r, 1, 1 + 0.03 * r))
    p.add("tete", rot=(14 + 1.5 * r, 6, 0))
    p.add("antenne_G", rot=(0, 25 + 2 * r, 100))
    p.add("antenne_D", rot=(0, -20 - 2 * r, -85))
    p.paire("mandibule", rot=(0, 0, -8))
    for i in (1, 2, 3):
        p.paire("patte%d" % i, rot=(0, -30, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Fourmi")
