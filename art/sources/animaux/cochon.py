"""Le cochon en peluche : rose pêche et bien en chair, le groin en feutrine, la queue en tire-bouchon.

    python cochon.py        fabrique la fiche art/apercus/animaux/cochon.png
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

CORPS = Vector((0.0, 0.05, 0.235))
TETE = Vector((0.0, -0.19, 0.295))
GROIN = Vector((0.0, -0.970, 0.242))                # le groin pointe un peu en l'air : c'est l'axe de la pièce
HAUT = Vector((0.0, 0.242, 0.970))                  # le dessus du groin, d'équerre avec GROIN
COTE = Vector((1.0, 0.0, 0.0))
ROSE_PECHE = M.hexa("#ffc4bc")                      # le poil fonce la teinte : la pêche de la palette sortait caramel


def construire():
    a = K.Animal("cochon")
    a.taille = 1.00
    a.tete = TETE + Vector((0, -0.10, 0.03))       # la mise au point se fait sur le visage, pas derrière

    # ----- le corps : un tonneau dont le ventre pend un peu -----
    corps = A.boule(1.0, 56, 28).sculpte(lambda v: K.bosse(v, (0, 0.35, -0.8), 0.10, 0.6) * [0.185, 0.250, 0.170])
    G.sillons(corps, [14, 42], 0.005, 1.1)
    a.piece("corps", corps, ROSE_PECHE, pos=CORPS)
    a.couture("dos", "corps", 14, 0.50, 0.99)
    a.couture("echine", "corps", 42, 0.74, 0.99)
    a.rustine("piece", "corps", CORPS, (0.85, 0.05, 0.50), 0.27, K.FRAMBOISE, feston=16)

    # ----- la tête, sans cou, avec ses bajoues -----
    def hure(v):
        s = K.bosse(v, (0.6, -0.45, -0.5), 0.09, 0.25)
        return K.bosse(s, (-0.6, -0.45, -0.5), 0.09, 0.25) * [0.145, 0.135, 0.130]
    tete = A.boule(1.0, 56, 28).sculpte(hure)
    G.sillons(tete, [42], 0.004, 1.1)
    a.piece("tete", tete, ROSE_PECHE, pos=TETE)
    a.couture("front", "tete", 42, 0.66, 0.98)                    # du groin au sommet du crâne
    regard = Vector((0.60, -0.62, 0.50)).normalized()
    oeil = a.trace("tete", TETE, [regard], 0.0)[0]
    a.bouton("oeil", oeil, a.trace("tete", TETE, [regard], 1.0)[0] - oeil, 0.024, paire=True)

    # ----- le groin en feutrine, ses deux narines brodées, un sourire en coin par-dessous -----
    pied = TETE + GROIN * 0.090 - HAUT * 0.015
    a.piece("groin", A.cylindre(0.056, 0.085, 0.012, 32).etire(1.15, 0.92, 1.0), K.ROSE, pos=pied, rot=A.viser(GROIN), poil=False)
    face = pied + GROIN * 0.087
    a.broderie("narine", [face + COTE * (0.024 + 0.008 * math.cos(t)) + HAUT * 0.014 * math.sin(t) for t in np.linspace(0, 2 * math.pi, 13)], 0.0024, paire=True)
    a.broderie("sourire", a.trace("tete", TETE, [GROIN + COTE * x - HAUT * (0.78 - 0.5 * x * x) for x in np.linspace(-0.25, 0.62, 9)]), 0.0022)

    # ----- les oreilles : un triangle dont la pointe retombe vers l'avant, le dedans en feutrine rose -----
    def pavillon(v):
        s = v.copy()
        s[:, 0] *= 1 - 0.62 * K.lisse((v[:, 2] + 0.5) / 1.5)
        return s
    oreille = A.boule(1.0, 32, 16).sculpte(pavillon).etire(0.068, 0.011, 0.090).sculpte(K.plie(0.005, 115, 0.05))
    dedans = A.boule(1.0, 24, 12).sculpte(pavillon).etire(0.048, 0.006, 0.066).pose((0, -0.009, -0.004)).sculpte(K.plie(0.005, 115, 0.05))
    a.piece("oreille", oreille, ROSE_PECHE, pos=TETE + Vector((0.088, 0.015, 0.150)), rot=(10, 22, 0), paire=True)
    a.piece("dedans", dedans, K.ROSE, pos=TETE + Vector((0.088, 0.015, 0.150)), rot=(10, 22, 0), poil=False, paire=True)

    # ----- quatre pattes courtes, chaussées de sabots en feutrine -----
    for nom, x, y in (("avant", 0.100, -0.095), ("arriere", 0.108, 0.175)):
        patte = A.tour(A.profil([(0, 0.010), (0.046, 0.012), (0.048, 0.07), (0.054, 0.14), (0, 0.18)], 5), 28)
        sabot = A.tour(A.profil([(0, 0), (0.050, 0.003), (0.055, 0.022), (0.052, 0.048), (0, 0.052)], 5), 28)
        a.piece("patte_" + nom, patte, ROSE_PECHE, pos=(x, y, 0.0), paire=True)
        a.piece("sabot_" + nom, sabot, K.FRAMBOISE, pos=(x, y, 0.0), poil=False, paire=True)

    # ----- la queue en tire-bouchon : un boudin de feutrine le long d'une hélice qui s'ouvre -----
    helice = A.helice(0.034, 0.115, 2.3, 56)
    helice[:, :2] *= K.lisse(np.linspace(0, 1, len(helice)) / 0.3)[:, None]
    croupe = a.trace("corps", CORPS, [(0, 0.80, 0.60)], -0.012)[0]
    a.piece("queue", A.tube(helice, lambda t: 0.016 * (1 - 0.45 * t), 10), K.ROSE, pos=croupe, rot=A.viser((0, 0.55, 0.83)), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py cochon)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.05, 0.20)),              # le milieu du tonneau : tout le cochon tangue autour
    ("tronc", "corps", (0, 0.05, 0.235)),              # le tonneau seul : il respire, il s'étale
    ("tete", "corps", (0, -0.10, 0.27)),               # sans cou : elle pivote à l'avant du tonneau
    ("oreille_G", "tete", (0.088, -0.175, 0.370)),
    ("avant_G", "corps", (0.100, -0.095, 0.165)),      # le haut de chaque patte
    ("arriere_G", "corps", (0.108, 0.175, 0.165)),
    ("queue", "corps", (0, 0.25, 0.335)),              # sur la croupe
]
PORTEURS = [("patte_avant", "avant", True), ("sabot_avant", "avant", True), ("patte_arriere", "arriere", True), ("sabot_arriere", "arriere", True),
            ("oreille", "oreille", True), ("dedans", "oreille", True), ("tete", "tete"), ("front", "tete"), ("oeil", "tete"), ("groin", "tete"),
            ("narine", "tete"), ("sourire", "tete"), ("queue", "queue"),
            ("corps", "tronc"), ("dos", "tronc"), ("echine", "tronc"), ("piece", "tronc")]


def repos(t):
    """Il renifle l'air, le groin qui frémit, regarde d'un côté puis de l'autre ; une oreille chasse une mouche, la queue frétille."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.26, 0.16), cloche(t, 0.72, 0.16)
    flaire = (cloche(t, 0.10, 0.07) + cloche(t, 0.50, 0.07)) * onde(t, 12)
    p.add("tronc", ech=(1 + 0.014 * r, 1 + 0.006 * r, 1 + 0.020 * r))
    p.add("tete", rot=(-6 * cloche(t, 0.10, 0.08) + 3 * flaire, 4 * g - 4 * d, 16 * g - 14 * d))
    p.add("oreille_G", rot=(0, 0, 22 * cloche(t, 0.60, 0.03) - 12 * cloche(t, 0.64, 0.03)))
    p.add("queue", rot=(0, 0, 30 * cloche(t, 0.86, 0.07) * onde(t, 10)))
    p.ouvert = 1 - cloche(t, 0.38, 0.02) - cloche(t, 0.80, 0.02)
    return p


def avance(t):
    """Il trottine en se dandinant, les pattes en diagonale, la tête qui dodeline et la queue qui saute."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    p.add("corps", rot=(0, 5 * c, 4 * s), pos=(0, 0, 0.008 * abs(s)))
    for nom, sens in (("avant_G", 1), ("arriere_D", 1), ("avant_D", -1), ("arriere_G", -1)):
        p.add(nom, rot=(26 * s * sens, 0, 0), pos=(0, 0, 0.020 * max(0.0, c * sens)))
    p.add("tete", rot=(3 * math.cos(2 * math.tau * t), -4 * c, -4 * s))
    p.paire("oreille", rot=(6 * abs(s), 0, 0))
    p.add("queue", rot=(10 * math.cos(2 * math.tau * t), 0, 14 * s))
    return p


def mange(t):
    """Le groin au sol, il fouille la terre à petits coups, la queue en fête ; il relève la tête pour mâcher."""
    p = Pose()
    leve = cloche(t, 0.86, 0.12)
    bas = 1 - leve
    fouille = onde(t, 6) * bas
    p.add("corps", rot=(14 * bas, 0, 0))
    p.paire("avant", rot=(-14 * bas, 0, 0), ech=(1, 1, 1 - 0.32 * bas))
    p.paire("arriere", rot=(-14 * bas, 0, 0), ech=(1, 1, 1 + 0.16 * bas))
    p.add("tete", rot=(36 * bas + 5 * fouille, 0, 9 * fouille + 6 * leve), pos=(0, -0.02 * bas, -0.06 * bas))
    p.paire("oreille", rot=(10 * bas, 0, 0))
    p.add("queue", rot=(0, 0, 26 * onde(t, 9)))
    p.ouvert = 1 - 0.4 * leve
    return p


def joie(t):
    """Il bondit des quatre pattes en se tortillant, les oreilles qui claquent, la queue qui tourne."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    saut = abs(onde(t, 2.5)) * env
    p.add("corps", pos=(0, 0, 0.085 * saut), rot=(-8 * env, 0, 16 * onde(t, 2.5) * env))
    p.add("tronc", ech=(1, 1 + 0.05 * saut, 1 - 0.04 * saut))
    p.paire("avant", rot=(-24 * saut, 0, 0))
    p.paire("arriere", rot=(24 * saut, 0, 0))
    p.add("tete", rot=(-14 * env, 0, -8 * onde(t, 2.5) * env))
    p.paire("oreille", rot=(-30 * saut, 0, 0))
    p.add("queue", rot=(20 * onde(t, 7) * env, 0, 30 * onde(t, 7, 0.25) * env))
    return p


def dort(t):
    """Couché sur le ventre, les pattes étalées devant et derrière, le menton posé, les yeux fermés ; il ronfle doucement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.115))
    p.add("tronc", ech=(1.06 + 0.012 * r, 1.0, 0.92 + 0.030 * r))
    p.paire("avant", rot=(-65, 0, 0), ech=(1, 1, 0.8))
    p.paire("arriere", rot=(65, 0, 0), ech=(1, 1, 0.8))
    p.add("tete", pos=(0, 0, -0.050 + 0.004 * r), rot=(12, 8, 6))
    p.paire("oreille", rot=(15, 0, 0))
    p.add("queue", rot=(0, 0, 10 * cloche(t, 0.55, 0.04) * onde(t, 10)))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (20, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
