"""Le lapin en peluche, le premier de tous : crème, le ventre et les joues roses, une fleur cousue sur la cuisse,
une oreille qui retombe. Ses formes viennent de la planche d'origine (planche_da.py), remises au format du kit.
Sans col ni nœud : aucun accessoire sur les modèles.

    python lapin.py        fabrique la fiche art/apercus/animaux/lapin.png
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
import lapinceau as L
import peluche as K
import planche_da as P

REP_OREILLE = A.repere((0.075, -0.215, 0.648), (-8, 14, 15))
MUSEAU = L.TETE + Vector((0, -0.135, -0.045))
CUISSE = Vector((0.195, 0.085, 0.165))


def construire():
    a = K.Animal("lapin")
    a.taille = 0.95
    a.tete = L.TETE

    # ----- les pièces de peluche -----
    f = P.formes(0.015)
    G.sillons(f["corps"][0], [0, 18, 36, 54], 0.008, 1.1)
    G.sillons(f["tete"][0], [0, 18, 36, 54], 0.006, 1.1)
    G.sillons(f["cuisse"][0], [14, 42], 0.004, 1.0)
    G.sillons(f["patte"][0], [0], 0.003, 0.8)
    for nom in ("corps", "tete", "museau"):
        a.piece(nom, f[nom][0], K.CREME, mat=f[nom][1])
    for nom in ("patte", "peton", "cuisse", "pied"):
        a.piece(nom, f[nom][0], K.CREME, mat=f[nom][1], paire=True)
    a.piece("queue", A.boule(0.06, 32, 16), K.BLANC, pos=(0, 0.285, 0.30))
    # le cou : sans le col, on voyait le jour entre la tête et le corps
    a.piece("cou", A.boule(1.0, 40, 20).etire(0.112, 0.105, 0.085), K.CREME, pos=(0, -0.150, 0.405), rot=(-33, 0, 0))

    # ----- les coutures d'assemblage : le dos, le crâne, les cuisses, le tour des pieds -----
    a.couture("dos", "corps", 18, 0.10, 0.90)
    a.couture("crane", "tete", 18, 0.30, 1.0)
    a.couture("crane2", "tete", 54, 0.63, 1.0)
    for cote in (14, 42):
        a.couture("cuisse%d" % cote, "cuisse", cote, 0.10, 0.90, paire=True)
    a.ourlet("pied", "pied", 0.42, paire=True)
    a.ourlet("peton", "peton", 0.45, paire=True)

    # ----- les oreilles, dressées toutes les deux : c'est le squelette qui en fait retomber une -----
    a.piece("oreille", A.boule(1.0, 40, 36).sculpte(P._oreille(0.015)), K.CREME, mat=REP_OREILLE, paire=True)
    dedans = A.boule(1.0, 40, 36).sculpte(P._oreille(0.006, 0.62)).etire(1, 1, 0.92).pose((0, -0.0125, 0.012))
    a.piece("dedans", dedans, K.ROSE, mat=REP_OREILLE, poil=False, paire=True)
    ourlet = A.boule(1.0, 40, 36).sculpte(P._oreille(0.006, 0.62)).etire(0.86, 1, 0.92).pose((0, -0.017, 0.012))
    bord = [r for r in ourlet.anneaux if len(r) > 1][3:-3]
    contour = [r[0] for r in bord] + [r[20] for r in reversed(bord)]
    face = [r[30] for r in bord] + [r[30] for r in reversed(bord)]       # la normale du milieu de la face avant, au même niveau
    points = P._vers_monde(ourlet.v[contour], REP_OREILLE)
    devant = P._vers_monde(ourlet.normales()[face], REP_OREILLE, True)
    a._poser(a._jouet(a._fils, K.JAUNE, "f"), "ourlet", G.couture(points, devant, 0.012, 0.007, 0.0013, 0.0015), "fil", None, True)

    # ----- les rapiéçages : le ventre, les joues, une fleur sur chaque cuisse -----
    a.rustine("ventre", "corps", P.CORPS, (0, -0.80, -0.22), lambda th: 0.60 - 0.16 * math.cos(2 * th), K.ROSE, feston=50)
    a.rustine("joue", "tete", L.TETE, (0.62, -0.55, -0.45), 0.27, K.ROSE, 0.0028, 20, paire=True)
    a.rustine("fleur", "cuisse", CUISSE, (1, 0, 0.08), lambda th: 0.58 * (0.68 + 0.32 * abs(math.cos(2.5 * th))), K.TURQUOISE, 0.003, 30, paire=True)
    a.rustine("coeur", "cuisse", CUISSE, (1, 0, 0.08), 0.21, K.JAUNE, 0.006, 0, paire=True)

    # ----- le visage : la truffe en feutrine, la bouche et les moustaches brodées, deux boutons noirs -----
    a.rustine("truffe", "museau", MUSEAU, (0, -1, 0.42), lambda th: 0.40 * (1 + 0.25 * math.cos(3 * (th - math.pi / 2))), K.CORAIL, 0.004, 0)
    a._poser(a._jouet(a._fils, K.BRUN, "f"), "bouche", P._bouche(a._arbres["museau"], MUSEAU, 0.0018), "fil", None, False)
    a._poser(a._jouet(a._fils, K.BLANC, "f"), "moustache", P._moustaches(0.0016), "fil", None, True)
    a.bouton("oeil", L.OEIL + L.REGARD * 0.008, L.REGARD, 0.037, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py lapin)

from poses import Pose, borne, cloche, onde

TAU = math.tau
OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.10, 0.18)),            # le bassin : tout le lapin bascule autour
    ("ventre", "corps", (0, 0.044, 0.212)),          # le tronc seul : il gonfle, s'écrase, s'étire
    ("tete", "corps", (0, -0.17, 0.42)),
    ("museau", "tete", (0, -0.36, 0.49)),
    ("oreille_G", "tete", tuple(REP_OREILLE @ Vector((0, 0, 0)))),
    ("oreille2_G", "oreille_G", tuple(REP_OREILLE @ Vector((0, 0, 0.14)))),
    ("patte_G", "corps", (0.105, -0.117, 0.25)),
    ("cuisse_G", "corps", (0.195, 0.095, 0.20)),
    ("pied_G", "cuisse_G", (0.205, 0.10, 0.045)),
    ("queue", "corps", (0, 0.255, 0.29)),
]
_VERS_OREILLE = np.array(REP_OREILLE.inverted())


def _cou(points, cote):
    """Le cou suit le corps et la tête à parts égales."""
    moitie = np.full(len(points), 0.5)
    return {"corps": moitie, "tete": moitie}


def _oreille(points, cote):
    """Les oreilles sont souples : le bas suit « oreille », le haut suit « oreille2 »."""
    z = (points @ _VERS_OREILLE[:3, :3].T + _VERS_OREILLE[:3, 3])[:, 2]
    haut = K.lisse((z - 0.10) / 0.08)
    return {"oreille" + cote: 1.0 - haut, "oreille2" + cote: haut}


PORTEURS = [("cou", _cou, "corps"), ("oreille", _oreille, "oreille*"), ("dedans", _oreille, "oreille*"), ("ourlet", _oreille, "oreille*"),
            ("patte", "patte", True), ("peton", "patte", True), ("cuisse", "cuisse", True), ("fleur", "cuisse", True),
            ("coeur", "cuisse", True), ("pied", "pied", True), ("corps", "ventre"), ("ventre", "ventre"), ("dos", "ventre"),
            ("queue", "queue"), ("tete", "tete"), ("crane", "tete"), ("joue", "tete"), ("oeil", "tete"),
            ("museau", "museau"), ("truffe", "museau"), ("bouche", "museau"), ("moustache", "museau")]


def tombante(p, combien=1.0):
    """Son allure : l'oreille droite retombe vers l'avant."""
    p.add("oreille_D", rot=(5 * combien, -5 * combien, 0))
    p.add("oreille2_D", rot=(54 * combien, -14 * combien, 0))


def repos(t):
    """Il respire, regarde à gauche puis à droite, remue le nez, une oreille tressaille, il cligne des yeux."""
    p = Pose()
    tombante(p)
    r = onde(t, 2)
    p.add("ventre", ech=(1 + 0.012 * r, 1 + 0.010 * r, 1 + 0.028 * r))
    p.add("corps", pos=(0, 0, 0.003 * r), rot=(0, 1.2 * onde(t, 1), 0))
    g, d = cloche(t, 0.25, 0.2), cloche(t, 0.70, 0.2)
    lacet = 17 * g - 15 * d
    p.add("tete", rot=(1.5 * r - 4 * g + 2 * d, 5 * d - 3 * g, lacet))
    vif = cloche(t, 0.43, 0.035) - 0.6 * cloche(t, 0.47, 0.03)
    p.add("oreille_G", rot=(-16 * vif, 10 * vif, 0))
    p.add("oreille2_G", rot=(-10 * vif + 2 * r, 0, 0))
    en_retard = 17 * cloche(t - 0.05, 0.25, 0.2) - 15 * cloche(t - 0.05, 0.70, 0.2)
    p.add("oreille2_D", rot=(3 * r, 0.9 * (en_retard - lacet), 0))
    nez = (cloche(t, 0.10, 0.07) + cloche(t, 0.56, 0.07) + cloche(t, 0.90, 0.05)) * onde(t, 14)
    p.add("museau", ech=(1 + 0.04 * nez, 1, 1 - 0.05 * nez), rot=(2.5 * nez, 0, 0))
    p.add("queue", rot=(0, 0, 22 * cloche(t, 0.84, 0.06) * onde(t, 12)))
    p.ouvert = 1 - cloche(t, 0.33, 0.02) - cloche(t, 0.78, 0.02)
    return p


def avance(t):
    """Un bond sur place : il se tasse, pousse des pattes arrière, s'étire en l'air, se reçoit sur l'avant."""
    p = Pose()
    tombante(p, 0.6)
    s = borne((t - 0.2) / 0.5)
    haut = 0.15 * 4 * s * (1 - s)
    tasse, amorti, etire = cloche(t, 0.08, 0.12), cloche(t, 0.86, 0.12), cloche(t, 0.34, 0.18)
    tangage = -15 * cloche(t, 0.27, 0.17) + 13 * cloche(t, 0.72, 0.15)
    au_sol = 0.03 * tasse + 0.035 * amorti
    p.add("corps", pos=(0, 0, haut - au_sol), rot=(tangage, 0, 0))
    p.add("ventre", ech=(1 - 0.05 * etire + 0.07 * amorti + 0.04 * tasse, 1 + 0.12 * etire - 0.03 * amorti,
                         1 - 0.05 * etire - 0.11 * amorti - 0.06 * tasse))
    pousse, replie = cloche(t, 0.27, 0.13), cloche(t, 0.52, 0.2)
    p.paire("cuisse", rot=(40 * pousse - 24 * replie, 0, 0), pos=(0, 0, au_sol))
    p.paire("pied", rot=(32 * pousse - 16 * replie + 8 * amorti, 0, 0))
    p.paire("patte", rot=(22 * cloche(t, 0.30, 0.14) - 34 * cloche(t, 0.62, 0.16) + 10 * cloche(t, 0.80, 0.1), 0, 0), pos=(0, 0, au_sol))
    p.add("tete", rot=(-0.6 * tangage + 7 * cloche(t, 0.82, 0.1), 0, 0))
    p.paire("oreille", rot=(-26 * cloche(t, 0.30, 0.16) + 15 * cloche(t, 0.82, 0.12), 0, 0))
    p.paire("oreille2", rot=(-34 * cloche(t, 0.37, 0.17) + 26 * cloche(t, 0.88, 0.12), 0, 0))
    p.add("queue", rot=(-16 * cloche(t, 0.3, 0.15) + 20 * cloche(t, 0.84, 0.12), 0, 0))
    return p


def mange(t):
    """Le nez au sol, il mâchonne ; de temps en temps il relève la tête sans s'arrêter de mâcher."""
    p = Pose()
    tombante(p, 0.8)
    leve = cloche(t, 0.82, 0.12)
    m = onde(t, 8)
    pique = 7 - 4 * leve
    p.add("corps", pos=(0, 0, -0.008), rot=(pique, 0, 0))
    p.add("tete", pos=(0, -0.012, -0.02), rot=(27 - 22 * leve + 2.5 * onde(t, 2), 2.2 * onde(t, 4), 4 * leve))
    p.add("museau", ech=(1 + 0.05 * m, 1, 1 - 0.07 * m), rot=(3 * m, 0, 0))
    p.paire("oreille", rot=(-20 + 8 * leve + 1.2 * m, 0, 0))
    p.paire("oreille2", rot=(-10 + 6 * leve, 0, 0))
    p.paire("patte", pos=(0, 0, 0.008 + 0.0048 * pique), rot=(-5 - pique, 0, 0))
    p.paire("cuisse", pos=(0, 0, 0.008))
    p.add("ventre", ech=(1 + 0.01 * onde(t, 1), 1, 1 + 0.02 * onde(t, 1)))
    p.add("queue", rot=(0, 0, 8 * onde(t, 2)))
    p.ouvert = 1 - cloche(t, 0.40, 0.025)
    return p


def joie(t):
    """Le saut de joie du lapin : il bondit haut en se tortillant, retombe, et se secoue."""
    p = Pose()
    tombante(p)
    prep = cloche(t, 0.08, 0.10, False)
    s = borne((t - 0.15) / 0.5)
    haut = 0.30 * 4 * s * (1 - s)
    vol = math.sin(math.pi * s)
    recu = cloche(t, 0.70, 0.08, False)
    fin = borne((t - 0.72) / 0.28)
    secoue = (1 - fin) * math.sin(TAU * 3 * fin) if t > 0.72 else 0.0
    au_sol = 0.04 * prep + 0.045 * recu
    p.add("corps", pos=(0, 0, haut - au_sol),
          rot=(-10 * cloche(t, 0.2, 0.1, False) + 8 * cloche(t, 0.62, 0.08, False), 12 * math.sin(TAU * s) * vol, 30 * math.sin(TAU * s) + 6 * secoue))
    p.add("ventre", ech=(1 + 0.06 * prep + 0.09 * recu - 0.04 * vol, 1 + 0.08 * vol, 1 - 0.08 * prep - 0.14 * recu + 0.03 * vol))
    p.add("tete", rot=(-8 * vol + 10 * recu, -8 * math.sin(TAU * s) * vol, -20 * math.sin(TAU * s - 0.7) * vol))
    p.add("cuisse_G", rot=(48 * cloche(t, 0.36, 0.12, False) - 15 * cloche(t, 0.55, 0.1, False), 0, 0))
    p.add("cuisse_D", rot=(44 * cloche(t, 0.42, 0.12, False) - 15 * cloche(t, 0.58, 0.1, False), 0, 0))
    p.paire("cuisse", pos=(0, 0, au_sol))
    p.paire("pied", rot=(30 * cloche(t, 0.38, 0.14, False), 0, 0))
    p.paire("patte", rot=(-30 * vol, -24 * vol, 0), pos=(0, 0, au_sol))
    p.paire("oreille", rot=(-36 * cloche(t, 0.25, 0.12, False) + 22 * cloche(t, 0.70, 0.1, False) - 6 * secoue, 0, 0))
    p.paire("oreille2", rot=(-40 * cloche(t, 0.30, 0.13, False) + 34 * cloche(t, 0.75, 0.1, False) - 10 * secoue, 0, 0))
    p.add("queue", rot=(0, 0, 25 * secoue + 20 * math.sin(TAU * 4 * s) * vol))
    p.ouvert = 1 - 0.85 * recu                        # il plisse les yeux en se recevant
    return p


def dort(t):
    """En boule, le menton posé, les oreilles couchées, les yeux fermés. Il respire lentement ; une oreille tressaille."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.045), rot=(4, 0, 0))
    p.add("ventre", ech=(1.11 + 0.014 * r, 1.04, 0.85 + 0.032 * r))
    p.add("tete", pos=(0, -0.02, -0.115 + 0.006 * r), rot=(30 + 1.5 * r, 12, -8))
    p.add("museau", ech=(1, 1, 1 + 0.04 * onde(t, 10) * cloche(t, 0.3, 0.06)))
    tic = cloche(t, 0.62, 0.035)
    p.add("oreille_G", rot=(-96 + 18 * tic, 8, 0))
    p.add("oreille2_G", rot=(-16 + 8 * tic, 0, 0))
    p.add("oreille_D", rot=(-90, -10, 0))
    p.add("oreille2_D", rot=(-22, -8, 0))
    p.paire("patte", pos=(0, 0, 0.044), rot=(32, 0, 0))
    p.paire("cuisse", pos=(0, 0, 0.043), rot=(-6, 0, 0))
    p.add("queue", rot=(8, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (18, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
