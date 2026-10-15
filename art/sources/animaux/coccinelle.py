"""La coccinelle en peluche : un dôme corail à gros pois rapiécés, la tête basse, une antenne pliée, l'air de bouder.

    python coccinelle.py        fabrique la fiche art/apercus/animaux/coccinelle.png
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

SUIE = M.hexa("#2b2725")                      # le noir de la tête : un charbon, pour que le poil se lise encore
CORPS = Vector((0.0, 0.018, 0.066))
TETE = Vector((0.0, -0.078, 0.058))


def construire():
    a = K.Animal("coccinelle")
    a.taille = 0.26
    a.tete = TETE + Vector((0, -0.034, 0.004))

    # ----- le corps : une demi-boule, plate dessous ; la couture du dos sépare les deux élytres -----
    def dome(v):
        s = v * [0.088, 0.096, 0.082]
        s[:, 2] *= 1 - 0.50 * K.lisse(-4 * v[:, 2])
        return s
    corps = A.boule(1.0, 56, 28).sculpte(dome)
    G.sillons(corps, [14, 42], 0.0055, 1.1)             # le tissu se creuse entre les élytres
    a.piece("corps", corps, K.CORAIL, pos=CORPS)
    a.couture("dos_arriere", "corps", 14, 0.40, 1.0, "croix", fil=SUIE, large=0.010, haut=0.004, pas=0.013)
    a.couture("dos_avant", "corps", 42, 0.68, 1.0, "croix", fil=SUIE, large=0.010, haut=0.004, pas=0.013)

    # ----- les pois : de gros ronds de feutrine noire tenus au point de feston, pas tout à fait de la même taille -----
    pois = (((0.52, -0.46, 0.62), 0.34), ((0.88, 0.16, 0.34), 0.30), ((0.44, 0.72, 0.50), 0.32))
    for i, (axe, ouverture) in enumerate(pois):
        a.rustine("pois%d" % i, "corps", CORPS, axe, ouverture, K.NOIR, 0.003, 16, paire=True)

    # ----- la tête : une petite boule charbon rentrée sous le dôme, deux pièces blanches pour porter les yeux -----
    a.piece("tete", A.boule(1.0, 48, 24).etire(0.051, 0.041, 0.040), SUIE, pos=TETE)
    regard = Vector((0.62, -0.70, 0.38))
    a.rustine("masque", "tete", TETE, regard, 0.46, K.BLANC, 0.0025, 12, paire=True)
    p, n = a.surface("tete", TETE, regard)
    a.bouton("oeil", p + n * 0.0025, n, 0.014, paire=True)

    # ----- la bouche : un trait crème qui retombe d'un côté -----
    moue = [Vector((-0.24 + 0.48 * s, -1.0, -0.34 - 0.10 * s + 0.09 * math.sin(math.pi * s))) for s in np.linspace(0, 1, 8)]
    a.broderie("moue", a.trace("tete", TETE, moue, 0.0045), 0.0022, K.CREME)

    # ----- les antennes : deux fils de feutrine à boule ; celle de droite a pris un pli -----
    droite = A.courbe([TETE + Vector(q) for q in ((0.020, -0.008, 0.034), (0.028, -0.020, 0.066), (0.038, -0.040, 0.088), (0.044, -0.062, 0.094))], 6)
    a.piece("antenne_gauche", A.tube(droite, 0.0036, 8) + A.boule(0.0092, 16, 8).pose(tuple(droite[-1])), SUIE, poil=False)
    pliee = [tuple(q) for q in A.courbe([TETE + Vector(q) for q in ((-0.020, -0.008, 0.034), (-0.027, -0.016, 0.062), (-0.034, -0.026, 0.082))], 5)]
    pliee += [tuple(TETE + Vector(q)) for q in ((-0.046, -0.036, 0.079), (-0.060, -0.048, 0.066))]
    a.piece("antenne_droite", A.tube(pliee, 0.0036, 8) + A.boule(0.0092, 16, 8).pose(pliee[-1]), SUIE, poil=False)

    # ----- les pattes : trois petits fils coudés de chaque côté, qui dépassent à peine du dôme -----
    pattes = None
    for y, x in ((-0.040, 0.082), (0.014, 0.096), (0.066, 0.086)):
        patte = A.tube(A.courbe([(0.040, y, 0.040), (x, y, 0.039), (x + 0.012, y - 0.004, 0.005)], 5), 0.0055, 8)
        pattes = patte if pattes is None else pattes + patte
    a.piece("pattes", pattes, SUIE, poil=False, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py coccinelle)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.018, 0.045)),
    ("elytre_G", "corps", (0.012, -0.045, 0.100)),   # la charnière d'un élytre, sous le haut du dos, derrière la tête
    ("tete", "corps", (0, -0.055, 0.060)),           # la nuque, cachée sous le dôme
    ("antenne_G", "tete", (0.020, -0.086, 0.092)),
    ("patte1_G", "corps", (0.045, -0.040, 0.040)),   # les hanches, de l'avant vers l'arrière, juste sous le bord du dôme
    ("patte2_G", "corps", (0.060, 0.014, 0.040)),
    ("patte3_G", "corps", (0.050, 0.066, 0.040)),
]


def elytres(points, cote):
    """Le dôme est d'une seule pièce, mais ses deux moitiés s'entrouvrent : le haut du dos suit l'os de son élytre,
    le dessous du dôme reste au corps, et rien ne bouge le long de la couture ni au ras de la tête.
    Les pois et la couture du dos prennent les mêmes poids que le tissu qui les porte."""
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    dos = K.lisse((z - 0.050) / 0.014) * K.lisse((y + 0.050) / 0.035)
    ici, en_face = dos * K.lisse(x / 0.012), dos * K.lisse(-x / 0.012)
    gauche, droite = ("elytre_D", "elytre_G") if cote == "_D" else ("elytre_G", "elytre_D")   # une pièce de droite arrive en miroir
    return {"corps": 1 - ici - en_face, gauche: ici, droite: en_face}


def pattes(points, cote):
    """Les trois pattes d'un côté sont une seule pièce, trois fils de même longueur mis bout à bout : un os par tiers."""
    tiers = np.arange(len(points)) * 3 // len(points)
    return {"patte%d%s" % (i + 1, cote): (tiers == i).astype(float) for i in range(3)}


PORTEURS = [("corps", elytres, "corps"), ("dos", elytres, "corps"), ("pois", elytres, "corps"), ("tete", "tete"),
            ("masque", "tete"), ("oeil", "tete"), ("moue", "tete"), ("antenne_gauche", "antenne_G"), ("antenne_droite", "antenne_D"),
            ("pattes", pattes, "patte1*")]


def doux(x):
    """De 0 à 1 en douceur, pour un geste qui part et s'arrête sans à-coup."""
    x = borne(x)
    return x * x * (3 - 2 * x)


def ouvre(p, combien):
    """Entrouvre les élytres : ils se soulèvent par le bord et par l'arrière, et s'écartent le long de la couture
    du dos, qui se tend. combien : 1 pour une belle ouverture."""
    p.paire("elytre", rot=(8 * combien, -14 * combien, -10 * combien))


def trepied(p, t, pas, leve):
    """La marche à six pattes : un trépied avance en l'air (l'avant et l'arrière d'un côté, le milieu de l'autre)
    pendant que l'autre pousse au sol, puis ils échangent. pas, leve : les angles du balancement et du lever."""
    for i in (1, 2, 3):
        for cote, signe in (("_G", 1), ("_D", -1)):
            phase = math.tau * t + (math.pi if (i == 2) == (signe > 0) else 0.0)
            p.add("patte%d%s" % (i, cote), rot=(0, -signe * leve * max(0.0, -math.sin(phase)), -signe * pas * math.cos(phase)))


def repos(t):
    """Elle boude : la tête basse, un gros soupir qui soulève le dôme, un coup d'œil de côté,
    l'antenne pliée qui tressaute, puis la patte avant qui tapote d'impatience."""
    p = Pose()
    r = onde(t, 2)
    soupir = cloche(t, 0.26, 0.12)
    cote = cloche(t, 0.56, 0.14)
    tape = cloche(t, 0.84, 0.12) * max(0.0, onde(t, 12))
    p.add("corps", ech=(1 + 0.010 * r + 0.015 * soupir, 1 + 0.010 * soupir, 1 + 0.020 * r + 0.05 * soupir))
    ouvre(p, 0.35 * soupir)
    p.add("tete", rot=(-5 * soupir + 3 * cloche(t, 0.36, 0.06), 6 * cote, 20 * cote))
    p.add("antenne_G", rot=(5 * onde(t, 3), 0, 4 * onde(t, 2)))
    p.add("antenne_D", rot=(16 * cloche(t, 0.44, 0.03) - 12 * cloche(t, 0.70, 0.03), 0, -3 * onde(t, 3)))
    p.add("patte1_G", rot=(0, -24 * tape, -6 * cloche(t, 0.84, 0.12)))
    p.ouvert = 1 - cloche(t, 0.10, 0.02) - cloche(t, 0.66, 0.02)
    return p


def avance(t):
    """Elle trottine sur ses six pattes, en trépied alterné : le dôme roule d'un bord sur l'autre, la tête basse
    dodeline, les antennes rebondissent."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    trepied(p, t, 22, 24)
    p.add("corps", pos=(0, 0, 0.003 * abs(c)), rot=(0, 3 * s, 2.5 * c))
    p.add("tete", rot=(3 * math.cos(2 * math.tau * t), -2 * s, -4 * c))
    p.add("antenne_G", rot=(7 * onde(t, 2), 0, 0))
    p.add("antenne_D", rot=(7 * onde(t, 2, 0.25), 0, 0))
    return p


def mange(t):
    """Le derrière en l'air, elle broute au ras du sol à petits coups de tête, les antennes qui tapotent ;
    puis elle relève le nez et surveille les environs, méfiante."""
    p = Pose()
    leve = cloche(t, 0.85, 0.13)
    bas = 1 - leve
    coups = max(0.0, onde(t, 5)) ** 2 * bas
    p.add("corps", rot=(8 * bas, 0, 0))
    p.add("tete", rot=(12 * bas + 6 * coups - 6 * leve, 0, 16 * leve * onde(t, 4)))
    p.add("antenne_G", rot=(14 * bas + 12 * coups, 0, 0))
    p.add("antenne_D", rot=(10 * bas + 12 * max(0.0, onde(t, 5, 0.5)) ** 2 * bas, 0, 0))
    for i in (1, 2, 3):
        p.paire("patte%d" % i, rot=(-8 * bas, 0, 0))             # les pattes restent d'aplomb sous le dôme qui bascule
    return p


def joie(t):
    """Pour une fois elle relève la tête : elle se hausse sur ses pattes, entrouvre ses élytres et frémit de tout
    son dôme, les antennes dressées ; puis tout se referme et elle reprend sa moue."""
    p = Pose()
    env = doux(t / 0.22) * (1 - doux((t - 0.68) / 0.22))
    fremit = onde(t, 12) * env
    p.add("corps", pos=(0, 0, 0.012 * env), rot=(-6 * env, 0, 2.5 * fremit))
    ouvre(p, env + 0.25 * fremit)
    p.add("tete", rot=(-14 * env, 0, -2.5 * fremit))
    p.add("antenne_G", rot=(-12 * env + 5 * fremit, 0, 0))
    p.add("antenne_D", rot=(-12 * env - 5 * fremit, 0, 0))
    for i in (1, 2, 3):
        p.paire("patte%d" % i, rot=(6 * env, 15 * env, 0))
    return p


def dort(t):
    """Ramassée : le dôme posé par terre, les pattes rentrées dessous, la tête tirée sous le bord, une antenne couchée
    sur le dôme, l'autre tombée devant, les yeux fermés ; le dos se soulève à peine."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.022), ech=(1.02, 1.01, 0.97 + 0.025 * r))
    ouvre(p, 0.10 + 0.10 * r)
    p.add("tete", rot=(12, 5, 0), pos=(0, 0.020, 0.006))
    p.add("antenne_G", rot=(-70 - 3 * r, 0, 0))                 # couchée en arrière : tombée devant, elle barrait le visage
    p.add("antenne_D", rot=(30 + 3 * r, -10, 0))
    for i in (1, 2, 3):
        p.paire("patte%d" % i, rot=(0, -12, 0), pos=(-0.034, 0, 0.014))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Coccinelle")
