"""Le mouton en peluche : une toison en grosses boules de laine, la tête et les pattes en feutrine ardoise.

    python mouton.py        fabrique la fiche art/apercus/animaux/mouton.png
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
import peluche as K

CORPS = Vector((0.0, 0.04, 0.28))
NUQUE = Vector((0.0, -0.175, 0.42))                 # l'arrière du crâne, enfoui dans la laine du cou
NEZ = Vector((0.0, -0.906, -0.423))                 # la tête pique du nez : c'est l'axe de la pièce tournée
HAUT = Vector((0.0, -0.423, 0.906))                 # le dessus du crâne, d'équerre avec NEZ
COTE = Vector((1.0, 0.0, 0.0))
TETE = NUQUE + NEZ * 0.12


def toison(boules):
    """Des boules de laine (centre, rayon) réunies en une seule pièce. On retire les faces enfouies
    dans une voisine : le poil ne pousse que sur ce qui se voit, et la pièce reste légère."""
    tout = None
    for i, (c, r) in enumerate(boules):
        b = A.boule(r, 32, 16).pose(c)
        for j, (c2, r2) in enumerate(boules):
            if j != i:
                dedans = np.linalg.norm(b.v - np.array(c2), axis=1) < r2
                b.f = [f for f in b.f if not all(dedans[k] for k in f)]
        tout = b if tout is None else tout + b
    return tout


def construire():
    a = K.Animal("mouton")
    a.taille = 1.05
    a.tete = TETE

    # ----- la toison : trois couronnes de boules décalées autour d'un cœur caché, puis les bouts -----
    boules = [(CORPS + Vector((0, -0.05, 0)), 0.120), (CORPS + Vector((0, 0.07, 0)), 0.120)]
    for y, rx, rz, n, r in ((-0.105, 0.085, 0.080, 5, 0.082), (0.010, 0.110, 0.100, 6, 0.090), (0.125, 0.090, 0.085, 5, 0.085)):
        for k in range(n):
            t = math.pi / 2 + (k + 0.5 * (n % 2)) * 2 * math.pi / n
            boules.append((CORPS + Vector((rx * math.cos(t), y, rz * math.sin(t))), r))
    flanc = boules[2 + 5 + 5][0]                                     # la boule du milieu, en haut à gauche
    boules += [(CORPS + Vector((0, -0.185, -0.035)), 0.085),         # le poitrail
               (CORPS + Vector((0, -0.180, 0.095)), 0.090),          # le cou
               (CORPS + Vector((0, 0.195, 0.0)), 0.085),             # la croupe
               (CORPS + Vector((0, 0.262, 0.045)), 0.045),           # la queue
               (NUQUE + HAUT * 0.078 + NEZ * 0.045, 0.048),          # le toupet, entre les oreilles
               (NUQUE + HAUT * 0.070 + NEZ * 0.090, 0.036)]
    a.piece("toison", toison(boules), K.CREME)
    a.rustine("piece", "toison", flanc, (0.80, -0.25, 0.50), 0.42, K.ROSE, feston=16)

    # ----- la tête : une pièce tournée, du crâne rond au museau camus -----
    tete = A.tour(A.profil([(0, 0), (0.068, 0.016), (0.093, 0.082), (0.087, 0.138), (0.068, 0.192), (0.059, 0.226), (0, 0.244)], 6), 48)
    tete.etire(1.0, 0.90, 1.0)
    G.sillons(tete, [12], 0.004, 1.1)
    a.piece("tete", tete, K.ARDOISE, pos=NUQUE, rot=A.viser(NEZ), poil=False)
    a.couture("chanfrein", "tete", 12, 0.42, 0.93)                  # le côté 12 de la pièce est le dessus du nez
    regard = (COTE * 0.72 + HAUT * 0.60 + NEZ * 0.35).normalized()
    oeil = a.trace("tete", TETE, [regard], 0.0)[0]
    a.bouton("oeil", oeil, a.trace("tete", TETE, [regard], 1.0)[0] - oeil, 0.026, paire=True)

    # ----- le nez et la bouche, brodés en rose au bout du museau -----
    bout = NUQUE + NEZ * 0.182
    a.broderie("nez", a.trace("tete", bout, [NEZ + COTE * x + HAUT * (0.10 + 0.9 * abs(x)) for x in (0.42, 0.21, 0.0, -0.21, -0.42)]), 0.0022, K.ROSE)
    a.broderie("levre", a.trace("tete", bout, [NEZ + HAUT * h for h in (0.10, -0.15, -0.40)]), 0.0022, K.ROSE)
    a.broderie("bouche", a.trace("tete", bout, [NEZ + COTE * x - HAUT * (0.40 + 0.5 * abs(x)) for x in (0.40, 0.20, 0.0, -0.20, -0.40)]), 0.0022, K.ROSE)

    # ----- les oreilles tombantes : une feuille ardoise, son dedans rose -----
    tombe = Vector((0.74, 0.10, -0.66)).normalized()
    racine = NUQUE + NEZ * 0.066 + (COTE * 0.92 + HAUT * 0.38).normalized() * 0.077
    feuille = lambda v: v * np.stack([1 - 0.45 * K.lisse((v[:, 2] + 0.2) / 1.2), np.ones(len(v)), np.ones(len(v))], axis=1)
    a.piece("oreille", A.boule(1.0, 28, 14).sculpte(feuille).etire(0.044, 0.011, 0.088), K.ARDOISE,
            pos=racine + tombe * 0.072, rot=A.viser(tombe), poil=False, paire=True)
    a.piece("dedans", A.boule(1.0, 24, 12).sculpte(feuille).etire(0.028, 0.007, 0.062), K.ROSE,
            pos=racine + tombe * 0.076 + Vector((0, -0.007, 0)), rot=A.viser(tombe), poil=False, paire=True)

    # ----- les quatre pattes en feutrine, un point avant au-dessus du sabot -----
    for nom, x, y in (("avant", 0.078, -0.080), ("arriere", 0.082, 0.160)):
        patte = A.tour(A.profil([(0, 0), (0.038, 0.004), (0.041, 0.035), (0.034, 0.070), (0.033, 0.14), (0.036, 0.21), (0, 0.22)], 5), 24)
        a.piece("patte_" + nom, patte, K.ARDOISE, pos=(x, y, 0.0), poil=False, paire=True)
        a.ourlet("sabot_" + nom, "patte_" + nom, 0.42, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py mouton)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.04, 0.24)),              # le milieu du mouton : il tangue autour
    ("tronc", "corps", (0, 0.04, 0.28)),               # la toison seule : elle respire, elle s'étale
    ("tete", "corps", (0, -0.165, 0.42)),              # la nuque, enfouie dans la laine du cou
    ("oreille_G", "tete", (0.071, -0.247, 0.419)),
    ("avant_G", "corps", (0.078, -0.080, 0.21)),       # le haut de chaque patte
    ("arriere_G", "corps", (0.082, 0.160, 0.21)),
    ("queue", "corps", (0, 0.27, 0.32)),
]
TOUPET = ((NUQUE + HAUT * 0.078 + NEZ * 0.045, 0.048), (NUQUE + HAUT * 0.070 + NEZ * 0.090, 0.036))
BOUT_DE_QUEUE = (CORPS + Vector((0, 0.262, 0.045)), 0.045)


def _toison(points, cote):
    """La toison est d'une seule pièce : le toupet suit la tête, la boule de la queue suit la queue, le reste le tronc."""
    def sur(boule):
        return (np.abs(np.linalg.norm(points - np.array(boule[0]), axis=1) - boule[1]) < 0.004).astype(float)
    tete = np.maximum(sur(TOUPET[0]), sur(TOUPET[1]))
    queue = sur(BOUT_DE_QUEUE) * (1 - tete)
    return {"tete": tete, "queue": queue, "tronc": 1.0 - tete - queue}


PORTEURS = [("toison", _toison, "tronc"), ("piece", _toison, "tronc"),
            ("patte_avant", "avant", True), ("sabot_avant", "avant", True), ("patte_arriere", "arriere", True), ("sabot_arriere", "arriere", True),
            ("oreille", "oreille", True), ("dedans", "oreille", True),
            ("tete", "tete"), ("chanfrein", "tete"), ("oeil", "tete"), ("nez", "tete"), ("levre", "tete"), ("bouche", "tete")]


def repos(t):
    """Il rumine : la tête tourne en petits ronds, lentement. Il regarde au loin, une oreille bat, la queue s'agite."""
    p = Pose()
    r = onde(t, 2)
    rumine = cloche(t, 0.30, 0.22)
    loin = cloche(t, 0.74, 0.14)
    p.add("tronc", ech=(1 + 0.012 * r, 1 + 0.006 * r, 1 + 0.018 * r))
    p.add("tete", rot=(2.5 * onde(t, 7) * rumine - 10 * loin, 3 * onde(t, 7, 0.25) * rumine, 14 * loin))
    p.add("oreille_D", rot=(0, -20 * cloche(t, 0.56, 0.03) + 10 * cloche(t, 0.60, 0.03), 0))
    p.add("queue", rot=(0, 0, 28 * cloche(t, 0.90, 0.07) * onde(t, 9)))
    p.ouvert = 1 - cloche(t, 0.52, 0.025) - cloche(t, 0.96, 0.025)
    return p


def avance(t):
    """Une marche lourde et tranquille, les pattes en diagonale, la toison qui ballotte, la tête qui hoche à chaque pas."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    p.add("corps", rot=(0, 3 * c, 2.5 * s), pos=(0, 0, 0.006 * abs(s)))
    p.add("tronc", ech=(1 + 0.015 * abs(c), 1, 1 - 0.015 * abs(c)))
    for nom, sens in (("avant_G", 1), ("arriere_D", 1), ("avant_D", -1), ("arriere_G", -1)):
        p.add(nom, rot=(19 * s * sens, 0, 0), pos=(0, 0, 0.016 * max(0.0, c * sens)))
    p.add("tete", rot=(4 + 4 * math.cos(2 * math.tau * t), -2 * c, -2.5 * s))
    p.paire("oreille", rot=(0, -5 * abs(s), 0))
    p.add("queue", rot=(0, 0, 10 * s))
    return p


def mange(t):
    """Il broute : le nez dans l'herbe, il arrache à petits coups secs, puis relève la tête et mâche de travers."""
    p = Pose()
    leve = cloche(t, 0.84, 0.13)
    bas = 1 - leve
    arrache = max(0.0, onde(t, 5)) ** 2 * bas
    p.add("corps", rot=(10 * bas, 0, 0))
    p.paire("avant", rot=(-10 * bas, 0, 0), ech=(1, 1, 1 - 0.17 * bas))
    p.paire("arriere", rot=(-10 * bas, 0, 0), ech=(1, 1, 1 + 0.10 * bas))
    p.add("tete", rot=(65 * bas - 7 * arrache, 4 * onde(t, 8) * leve, 6 * onde(t, 5) * bas), pos=(0, 0, -0.08 * bas))
    p.add("queue", rot=(0, 0, 14 * onde(t, 3)))
    p.ouvert = 1 - 0.5 * leve
    return p


def joie(t):
    """Il gambade : un bond des quatre pattes, une ruade, les oreilles qui volent, la queue qui frétille."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    saut = abs(onde(t, 2)) * env
    ruade = cloche(t, 0.55, 0.14, False)
    p.add("corps", pos=(0, 0, 0.11 * saut), rot=(16 * ruade - 6 * env, 0, 8 * onde(t, 2) * env))
    p.paire("avant", rot=(-20 * saut, 0, 0))
    p.paire("arriere", rot=(18 * saut + 34 * ruade, 0, 0))
    p.add("tete", rot=(-12 * env - 10 * ruade, 0, 0))
    p.paire("oreille", rot=(0, -38 * saut, 0))
    p.add("queue", rot=(0, 0, 30 * onde(t, 8) * env))
    return p


def dort(t):
    """Couché, les pattes repliées sous la laine, la tête tournée et posée dans l'herbe, les yeux fermés."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.150))
    p.add("tronc", ech=(1.08 + 0.012 * r, 1.0, 0.90 + 0.030 * r))
    p.paire("avant", ech=(1, 1, 0.30))
    p.paire("arriere", ech=(1, 1, 0.30))
    p.add("tete", pos=(0, 0, -0.060 + 0.004 * r), rot=(20, 0, 40))
    p.add("queue", rot=(0, 0, 12 * cloche(t, 0.6, 0.04) * onde(t, 9)))
    return p


ANIMATIONS = {"repos": (150, repos, True), "avance": (30, avance, True), "mange": (72, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
