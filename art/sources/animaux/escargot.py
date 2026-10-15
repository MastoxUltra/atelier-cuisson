"""L'escargot en peluche : une limace de tissu lilas, une coquille pleine au tourbillon en relief,
des yeux en boutons au bout des antennes.

    python escargot.py        fabrique la fiche art/apercus/animaux/escargot.png
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

AXE = A.repere((0, 0.33, 0.064), (90, 0, 0))            # l'axe de la limace : de la queue (0) à la tête (0,71)
TETE = Vector((0.0, -0.27, 0.172))                      # le milieu de la tête, une fois le cou redressé
COQUILLE = Vector((0.0, 0.07, 0.275))                   # le cœur de la spirale
RAYON, EPAIS = 0.155, 0.078                             # la coquille : son rayon, sa demi-épaisseur
ANTENNE, BOUT = Vector((0.04, -0.262, 0.238)), Vector((0.078, -0.305, 0.405))


def _limace(v):
    """Un boudin tourné devient une limace : plus large que haute, le ventre posé, le cou redressé."""
    s = v.copy()
    leve = K.lisse((v[:, 2] / 0.71 - 0.58) / 0.30)
    s[:, 0] = v[:, 0] * 1.18
    s[:, 1] = np.maximum(v[:, 1], -0.062 - 0.03 * leve) + 0.108 * leve
    s[:, 2] = v[:, 2] - 0.03 * leve
    return s


def _semelle(v):
    """Le pied : une galette de feutrine qui dépasse sous le corps, au bord festonné."""
    s = v.copy()
    s[:, 0] = v[:, 0] * (1.34 + 0.06 * np.sin(v[:, 2] * 95.0))
    s[:, 1] = np.clip(v[:, 1], -0.066, -0.036)
    return s


def _tourbillon(tours=2.6, dehors=0.132, dedans=0.014, n=160):
    """Le chemin du cordon cousu en spirale sur le flanc de la coquille, et son épaisseur en chaque point."""
    k = math.log(dehors / dedans) / (tours * A.TAU)
    corde, epais = [], []
    for i in range(n + 1):
        t = i / n
        angle = math.radians(-60.0) + tours * A.TAU * t
        r = dehors * math.exp(-k * tours * A.TAU * t)
        p = COQUILLE + Vector((0.0, -math.cos(angle), math.sin(angle))) * r
        corde.append(Vector((EPAIS * math.sqrt(max(1.0 - (r / RAYON) ** 2, 0.0)) + 0.004, p.y, p.z)))
        epais.append(0.006 + 0.008 * r / dehors)
    return corde, epais


def construire():
    a = K.Animal("escargot")
    a.taille = 0.48
    a.tete = TETE

    # ----- le corps et le pied -----
    corps = A.tour(A.profil([(0, 0), (0.035, 0.03), (0.07, 0.15), (0.095, 0.32), (0.09, 0.46), (0.075, 0.55), (0.085, 0.63), (0.07, 0.69), (0, 0.71)], 7), 64).sculpte(_limace)
    G.sillons(corps, [16], 0.006, 1.2)
    a.piece("corps", corps, K.LILAS, mat=AXE)
    pied = A.tour(A.profil([(0, 0), (0.035, 0.03), (0.07, 0.15), (0.095, 0.32), (0.085, 0.44), (0, 0.52)], 8), 64).sculpte(_semelle)
    a.piece("pied", pied, K.CREME, mat=AXE, poil=False)
    a.couture("dos", "corps", 16, 0.04, 0.50)
    a.couture("nuque", "corps", 16, 0.80, 0.97)

    # ----- la coquille : une galette pleine et bombée, avec son tourbillon en relief de chaque côté -----
    a.piece("coquille", A.boule(1.0, 64, 32).etire(EPAIS, RAYON, RAYON), K.CORAIL, pos=COQUILLE, poil=False)
    corde, epais = _tourbillon()
    spire = A.tube(corde, lambda t: epais[min(int(round(t * (len(epais) - 1))), len(epais) - 1)], 12)
    a.piece("spire", spire, K.CREME, poil=False, paire=True)
    a.couture("bord_arriere", "coquille", 16, 0.14, 0.97, "droit", fil=K.JAUNE, large=0.010, haut=0.0012, pas=0.018)
    a.couture("bord_avant", "coquille", 48, 0.30, 0.97, "droit", fil=K.JAUNE, large=0.010, haut=0.0012, pas=0.018)

    # ----- les antennes : une tige, une boule, un bouton pour l'œil ; et deux petits tentacules -----
    tige = A.tube(A.courbe([ANTENNE, ANTENNE.lerp(BOUT, 0.5) + Vector((0.004, 0.012, 0.0)), BOUT], 8), lambda t: 0.017 - 0.005 * t, 14)
    a.piece("antenne", tige + A.boule(0.027, 24, 12).pose(tuple(BOUT)), K.LILAS, paire=True)
    regard = Vector((0.22, -0.96, 0.10)).normalized()
    a.bouton("oeil", BOUT + regard * 0.024, regard, 0.022, paire=True)
    petit = A.tube(A.courbe([Vector((0.03, -0.335, 0.150)), Vector((0.04, -0.365, 0.146)), Vector((0.046, -0.388, 0.134))], 5), lambda t: 0.010 - 0.003 * t, 12)
    a.piece("tentacule", petit, K.LILAS, paire=True)

    # ----- le visage : deux joues roses tenues au point de feston, un sourire brodé -----
    a.rustine("joue", "corps", TETE, (0.80, -0.52, -0.20), 0.30, K.ROSE, 0.0028, 16, paire=True)
    sourire = [(math.sin(u), -math.cos(u) * 0.95, -0.36 + 0.42 * u * u) for u in np.linspace(-0.5, 0.5, 11)]
    a.broderie("bouche", a.trace("corps", TETE, sourire), 0.0019)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py escargot)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.05, 0.05)),
    ("queue", "corps", (0, 0.20, 0.04)),
    ("tete", "corps", (0, -0.17, 0.10)),             # la base du cou, là où le corps se redresse
    ("coquille", "corps", (0, 0.07, 0.14)),          # là où elle repose sur le dos
    ("antenne_G", "tete", tuple(ANTENNE)),
]


def _souple(points, cote):
    """Le corps est un seul boudin : la tête et la queue l'entraînent en douceur, le milieu suit « corps »."""
    y = points[:, 1]
    tete = K.lisse((-0.12 - y) / 0.12)
    queue = K.lisse((y - 0.16) / 0.14)
    return {"tete": tete, "queue": queue, "corps": 1.0 - tete - queue}


# les détails cousus sur le corps (joues, bouche, coutures) sont cuits dans sa texture : ils se rangent avec lui
PORTEURS = [("corps", _souple, "corps"), ("pied", _souple, "corps"), ("dos", _souple, "corps"), ("nuque", _souple, "corps"),
            ("joue", _souple, "corps"), ("bouche", _souple, "corps"),
            ("coquille", "coquille"), ("spire", "coquille"), ("bord", "coquille"),
            ("antenne", "antenne", True), ("oeil", "antenne", True), ("tentacule", "tete")]


def repos(t):
    """Il regarde autour de lui sans se presser ; une antenne se rétracte, hésite, ressort."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.25, 0.20), cloche(t, 0.72, 0.20)
    rentre = cloche(t, 0.48, 0.07)
    p.add("corps", ech=(1 + 0.012 * r, 1, 1 + 0.02 * r))
    p.add("coquille", rot=(1.5 * r, 0, 0), ech=(1, 1 + 0.008 * r, 1 + 0.008 * r))
    p.add("tete", rot=(-3 * g + 2 * d, 0, 12 * g - 10 * d))
    p.add("antenne_G", rot=(4 * onde(t, 1), -5 * g, 0), ech=(1, 1, 1 - 0.55 * rentre))
    p.add("antenne_D", rot=(4 * onde(t, 1, 0.15), 5 * d, 0))
    p.add("queue", rot=(0, 0, 4 * onde(t, 1)))
    p.ouvert = 1 - cloche(t, 0.10, 0.02) - cloche(t, 0.62, 0.02)
    return p


def avance(t):
    """Il rampe : la tête s'étire vers l'avant, le corps s'allonge, puis la queue rattrape. La coquille tangue."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    p.add("tete", pos=(0, -0.022 * (0.5 + 0.5 * s), 0.004 * c), rot=(3 * c, 0, 0))
    p.add("queue", pos=(0, 0.020 * (0.5 + 0.5 * c), 0))
    p.add("corps", ech=(1 - 0.02 * s, 1, 1 + 0.03 * c))
    p.add("coquille", rot=(5 * c, 2.5 * s, 0), pos=(0, 0, 0.004 * c))
    p.paire("antenne", rot=(7 * s, 3 * c, 0))
    return p


def mange(t):
    """La tête descend jusqu'au sol, râpe à petits coups, se relève pour avaler. Les antennes se couchent en arrière."""
    p = Pose()
    leve = cloche(t, 0.88, 0.12)
    coups = max(0.0, onde(t, 5)) ** 2 * (1 - leve)
    p.add("tete", rot=(34 - 30 * leve + 5 * coups, 0, 3 * onde(t, 2) * (1 - leve)), pos=(0, -0.006 * coups, -0.010 * (1 - leve)))
    p.paire("antenne", rot=(-22 + 18 * leve, 4, 0))
    p.add("coquille", rot=(4 - 3 * leve, 0, 0))
    p.add("queue", rot=(0, 0, 5 * onde(t, 1)))
    return p


def joie(t):
    """Les antennes se dressent et frétillent, la coquille tressaute, la tête se relève fièrement."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    bat = onde(t, 6) * env
    p.add("tete", rot=(-14 * env, 0, 7 * bat), pos=(0, 0, 0.012 * env))
    p.paire("antenne", rot=(-8 * env + 9 * bat, -10 * env, 0), ech=(1, 1, 1 + 0.18 * env))
    p.add("coquille", rot=(0, 9 * bat, 0), pos=(0, 0, 0.022 * abs(bat)), ech=(1, 1 + 0.03 * abs(bat), 1 - 0.03 * abs(bat)))
    p.add("queue", rot=(0, 0, 14 * bat))
    p.add("corps", ech=(1, 1, 1 + 0.04 * env))
    return p


def dort(t):
    """Rentré sous sa coquille : la tête reculée, les antennes rétractées, les yeux fermés ; la coquille respire."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("tete", pos=(0, 0.085, -0.015), rot=(8, 0, 0), ech=(0.86, 0.80, 0.86))
    p.paire("antenne", rot=(-35, 6, 0), ech=(0.42, 0.42, 0.42))
    p.add("queue", pos=(0, -0.05, 0))
    p.add("corps", ech=(1.04, 1, 0.96))
    p.add("coquille", pos=(0, -0.012, -0.012), rot=(6, 0, 0), ech=(1 + 0.012 * r, 1 + 0.015 * r, 1 + 0.015 * r))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (48, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
