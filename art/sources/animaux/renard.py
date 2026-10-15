"""Le renard en peluche : il avance tête basse, le regard par en dessous, la queue en point d'interrogation.

    python renard.py        fabrique la fiche art/apercus/animaux/renard.png
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

CORPS = Vector((0.0, 0.03, 0.175))
TETE = Vector((0.0, -0.23, 0.30))


def sur(a, piece, centre, vers):
    """Le point de la surface visé depuis « centre », et la normale à cet endroit."""
    p = a.trace(piece, centre, [vers], 0.0)[0]
    return p, a.trace(piece, centre, [vers], 1.0)[0] - p


def construire():
    a = K.Animal("renard")
    a.taille = 1.30
    a.tete = TETE + Vector((0, -0.03, 0.04))

    # ----- le corps : un œuf couché, le poitrail plus profond que la croupe -----
    def coque(v):
        avant = K.lisse((-v[:, 1] - 0.1) / 0.8)
        arriere = K.lisse((v[:, 1] - 0.3) / 0.7)
        s = v * [0.115, 0.200, 0.108]
        s[:, 0] *= 1 + 0.08 * avant - 0.12 * arriere
        s[:, 2] = s[:, 2] * (1 + 0.12 * avant) + 0.025 * avant + 0.02 * arriere
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    G.sillons(corps, [14, 42], 0.005, 1.1)
    a.piece("corps", corps, K.ROUX, pos=CORPS)
    a.couture("dos", "corps", 14, 0.52, 0.98)
    a.couture("echine", "corps", 42, 0.72, 0.98)
    a.rustine("jabot", "corps", CORPS + Vector((0, -0.08, 0.01)), (0, -0.80, -0.60),
              lambda th: 0.50 - 0.12 * math.cos(2 * th), K.CREME, feston=30)

    # ----- le cou, puis la tête : elle penche du nez, tout ce qu'elle porte penche avec elle -----
    cou = A.tour(A.profil([(0, 0), (0.086, 0.012), (0.078, 0.08), (0.068, 0.15), (0, 0.175)], 5), 32)
    a.piece("cou", cou, K.ROUX, pos=(0, -0.085, 0.20), rot=A.viser((0, -0.83, 0.55)))
    H = A.repere(TETE, (10, 0, 0))
    H3 = H.to_3x3()

    def crane(v):
        for cote in (1, -1):                              # les bajoues
            v = K.bosse(v, (cote * 0.9, -0.15, -0.4), 0.20, 0.25)
        return v * [0.121, 0.112, 0.102]
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(crane), K.ROUX, mat=H)
    a.couture("crane", "tete", 14, 0.55, 0.98)
    a.rustine("joue", "tete", TETE, H3 @ Vector((0.80, -0.42, -0.42)), lambda th: 0.42 + 0.08 * math.cos(2 * th),
              K.CREME, 0.0025, 16, paire=True)

    # ----- le museau pointu : la base rousse, le bout crème, la truffe en feutrine noire -----
    pm = A.profil([(0.068, 0.0), (0.058, 0.036), (0.042, 0.078), (0.028, 0.114), (0.017, 0.137), (0, 0.146)], 6)
    M = H @ A.repere((0, -0.064, -0.024), (92, 0, 0))    # dans ce repère : X la gauche, Y le haut, Z vers la truffe
    M3 = M.to_3x3()
    a.piece("museau", A.tour(pm[:13], 40).etire(1.0, 0.82, 1.0), K.ROUX, mat=M)
    a.piece("bout", A.tour(pm[12:], 40).etire(1.0, 0.82, 1.0), K.CREME, mat=M)
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.019, 0.015, 0.014), K.NOIR, mat=M @ A.repere((0, 0.004, 0.142)), poil=False)
    # le sourire en coin : il part de sous la truffe, longe le museau et remonte vers la joue
    sourire = [("bout", 0.134, -80), ("bout", 0.125, -60), ("bout", 0.114, -42), ("bout", 0.104, -30), ("bout", 0.094, -22),
               ("bout", 0.086, -14), ("museau", 0.074, -6), ("museau", 0.064, 6), ("museau", 0.056, 22), ("museau", 0.052, 40)]
    points = [a.trace(piece, M @ Vector((0, 0, z)), [M3 @ Vector((math.cos(math.radians(d)), math.sin(math.radians(d)), 0))])[0]
              for piece, z, d in sourire]
    a.broderie("sourire", A.courbe(points, 4), 0.0022, paire=True)

    # ----- les yeux, et deux sourcils qui ne sont pas d'accord : l'air de mijoter quelque chose -----
    p, n = sur(a, "tete", TETE, H3 @ Vector((0.42, -0.80, 0.40)))
    a.bouton("oeil", p, n, 0.023, paire=True)
    fronce = [H3 @ Vector((0.019 + 0.052 * t, -0.093 + 0.037 * t, 0.068 + 0.017 * t)) for t in np.linspace(0, 1, 6)]
    leve = [H3 @ Vector((-0.022 - 0.052 * t, -0.090 + 0.040 * t, 0.076 + 0.012 * t + 0.016 * math.sin(math.pi * t))) for t in np.linspace(0, 1, 7)]
    a.broderie("sourcil_fronce", a.trace("tete", TETE, fronce), 0.0024)       # à gauche il plisse l'œil,
    a.broderie("sourcil_leve", a.trace("tete", TETE, leve), 0.0024)           # à droite il hausse le sourcil

    # ----- les grandes oreilles triangulaires, doublées de feutrine chocolat -----
    oreille = A.tour(A.profil([(0, 0), (0.062, 0.020), (0.047, 0.067), (0.028, 0.119), (0.010, 0.160), (0, 0.176)], 6), 40)
    E = H @ A.repere((0.070, 0.012, 0.045), (-6, 14, 14))
    a.piece("oreille", oreille.etire(1.0, 0.32, 1.0), K.ROUX, mat=E, paire=True)
    a.rustine("pavillon", "oreille", E @ Vector((0, 0, 0.07)), E.to_3x3() @ Vector((0, -1, 0)),
              lambda th: 1.22 + 0.20 * max(0.0, -math.sin(th)), K.CHOCOLAT, 0.002, 0, paire=True)

    # ----- les pattes : le haut roux, la chaussette chocolat, un point avant à la limite -----
    pp = A.profil([(0, 0), (0.042, 0.004), (0.046, 0.028), (0.037, 0.062), (0.037, 0.11), (0.043, 0.15), (0, 0.175)], 6)

    def pied(v):                                          # le bas de la patte avance un peu : un pied
        s = v.copy()
        s[:, 1] -= 0.014 * K.lisse((0.05 - v[:, 2]) / 0.05)
        return s
    for nom, pos in (("avant", (0.064, -0.10, 0.0)), ("arriere", (0.068, 0.15, 0.0))):
        a.piece("patte_" + nom, A.tour(pp[18:], 32), K.ROUX, pos=pos, paire=True)
        a.piece("chaussette_" + nom, A.tour(pp[:19], 32).sculpte(pied), K.CHOCOLAT, pos=pos, paire=True)
        a.ourlet("revers_" + nom, "chaussette_" + nom, 1.0, paire=True)

    # ----- la queue : un gros panache qui remonte, le bout crème -----
    pq = A.profil([(0, 0), (0.036, 0.012), (0.050, 0.07), (0.078, 0.17), (0.092, 0.255), (0.076, 0.33), (0.038, 0.385), (0, 0.41)], 6)

    def panache(v):                                       # la pièce (axe Z) s'enroule vers -Y, sur un cercle de 0,40 m
        angle = 2.5 * v[:, 2]
        s = v.copy()
        s[:, 1] = -0.4 + (0.4 + v[:, 1]) * np.cos(angle)
        s[:, 2] = (0.4 + v[:, 1]) * np.sin(angle)
        return s
    a.piece("queue", A.tour(pq[:27], 40).sculpte(panache), K.ROUX, pos=(0, 0.19, 0.195), rot=(-68, 0, 0))
    a.piece("bout_queue", A.tour(pq[26:], 40).sculpte(panache), K.CREME, pos=(0, 0.19, 0.195), rot=(-68, 0, 0))
    a.ourlet("queue", "bout_queue", 0.0)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py renard)

from poses import Pose, borne, cloche, onde

JAMBE = 0.165                                        # de l'épaule (ou de la hanche) au sol
ECHINE = 0.25                                        # des hanches aux épaules

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.15, 0.165)),           # les hanches : il s'incline, se cabre et se couche autour
    ("cou", "corps", (0, -0.09, 0.205)),
    ("tete", "cou", (0, -0.185, 0.27)),              # la nuque
    ("oreille_G", "tete", (0.076, -0.226, 0.375)),
    ("patte_avant_G", "corps", (0.064, -0.10, 0.165)),      # l'épaule
    ("patte_arriere_G", "corps", (0.068, 0.15, 0.165)),     # la hanche
    ("queue1", "corps", (0, 0.20, 0.20)),            # le panache : trois os, du croupion au bout crème
    ("queue2", "queue1", (0, 0.305, 0.266)),
    ("queue3", "queue2", (0, 0.39, 0.372)),
]


def queue_souple(points, cote):
    """Le panache est souple : trois os se le partagent. On retrouve la place de chaque point le long de l'arc
    (0 au croupion, 1 au bout) en défaisant la pose de la pièce : voir « panache » dans construire."""
    c, s = math.cos(math.radians(68)), math.sin(math.radians(68))
    y, z = points[:, 1] - 0.19, points[:, 2] - 0.195
    u = np.arctan2(y * s + z * c, y * c - z * s + 0.4) / 1.025

    def doux(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3 - 2 * x)
    milieu, bout = doux((u - 0.18) / 0.30), doux((u - 0.50) / 0.30)
    return {"queue1": 1 - milieu, "queue2": milieu * (1 - bout), "queue3": milieu * bout}


PORTEURS = [("corps", "corps"), ("dos", "corps"), ("echine", "corps"), ("jabot", "corps"), ("cou", "cou"),
            ("tete", "tete"), ("crane", "tete"), ("joue", "tete"), ("museau", "tete"), ("bout_queue", queue_souple, "queue1"),
            ("bout", "tete"), ("truffe", "tete"), ("sourire", "tete"), ("oeil", "tete"), ("sourcil", "tete"),
            ("oreille", "oreille", True), ("pavillon", "oreille", True),
            ("patte_avant", "patte_avant", True), ("chaussette_avant", "patte_avant", True), ("revers_avant", "patte_avant", True),
            ("patte_arriere", "patte_arriere", True), ("chaussette_arriere", "patte_arriere", True),
            ("revers_arriere", "patte_arriere", True), ("queue", queue_souple, "queue1")]      # le panache se range sous son premier os


def pattes(p, dz, rx, avant, arriere):
    """Les quatre pattes quand le corps monte de dz et pique du nez de rx degrés autour des hanches : chaque paire fait
    l'angle voulu avec la verticale (> 0 : le pied part en arrière) et se tasse juste assez pour ne pas entrer dans le sol."""
    for nom, angle, haut in (("patte_avant", avant, JAMBE + dz - ECHINE * math.sin(math.radians(rx))), ("patte_arriere", arriere, JAMBE + dz)):
        e = max(0.5, min(1.0, haut / (JAMBE * math.cos(math.radians(angle)))))
        p.paire(nom, rot=(angle - rx, 0, 0), ech=(1 + 0.4 * (1 - e), 1 + 0.4 * (1 - e), e))


def repos(t):
    """Il respire et guette de côté, par en dessous, l'œil mi-clos ; une oreille pivote, puis l'autre ; le panache balance."""
    p = Pose()
    r, b = onde(t, 2), onde(t, 1)
    g, d = cloche(t, 0.26, 0.17), cloche(t, 0.72, 0.13)         # un long regard à gauche, un coup d'œil à droite
    p.add("corps", ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add("cou", rot=(5 * g, 0, 12 * g - 9 * d))
    p.add("tete", rot=(2 * r + 4 * g, -9 * g + 5 * d, 22 * g - 16 * d))
    p.add("oreille_G", rot=(0, 0, 30 * cloche(t, 0.50, 0.05) - 12 * g))
    p.add("oreille_D", rot=(0, 0, -30 * cloche(t, 0.90, 0.05)))
    p.add("queue1", rot=(0, 0, -6 * b))
    p.add("queue2", rot=(3 * r, 8 * onde(t, 1, -0.10), 0))
    p.add("queue3", rot=(4 * r, 11 * onde(t, 1, -0.20), 0))
    p.ouvert = borne(1 - 0.42 * g - cloche(t, 0.06, 0.02) - cloche(t, 0.58, 0.02))
    return p


def avance(t):
    """Le trot souple : les pattes vont par diagonales, l'échine ondule à peine, la tête reste basse, le panache traîne en retard."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 27.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s)))        # les pattes sont raides : le corps descend quand elles s'écartent
    p.add("corps", pos=(0, 0, -creux), rot=(1.2 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in (("patte_avant_G", 1), ("patte_arriere_D", 1), ("patte_avant_D", -1), ("patte_arriere_G", -1)):
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.032 * max(0.0, -sens * c)))
    p.add("cou", rot=(14 + 3 * onde(t, 2, -0.10), 0, -1.5 * s))
    p.add("tete", rot=(-8 - 2 * onde(t, 2, -0.20), -3 * c, -1 * s))
    p.paire("oreille", rot=(-10 + 5 * onde(t, 2, -0.25), 0, 0))
    p.add("queue1", rot=(-14 + 4 * onde(t, 2, -0.15), 0, -6 * onde(t, 1, -0.12)))
    p.add("queue2", rot=(-14 + 5 * onde(t, 2, -0.28), 0, -8 * onde(t, 1, -0.24)))
    p.add("queue3", rot=(-12 + 6 * onde(t, 2, -0.40), 0, -10 * onde(t, 1, -0.36)))
    return p


def mange(t):
    """Le poitrail baissé, il flaire, donne trois coups de dents au ras du sol, puis relève la tête pour mâcher en surveillant les alentours."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add("corps", rot=(5 * bas, 0, 0))
    pattes(p, 0.0, 5 * bas, -14 * bas, 0.0)
    p.add("cou", rot=(30 * bas - 6 * leve + 3 * coups, 0, 8 * leve))
    p.add("tete", rot=(-10 * bas + 7 * coups + 3 * leve * onde(t, 12), -5 * leve, 20 * leve))
    p.paire("oreille", rot=(-6 * bas + 6 * leve, 0, 0))
    p.add("queue1", rot=(-12 * bas, 0, -5 * onde(t, 2)))
    p.add("queue2", rot=(-6 * bas, 6 * onde(t, 2, -0.12), 0))
    p.add("queue3", rot=(0, 8 * onde(t, 2, -0.24), 0))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Le bond du mulot : il se tasse, s'élance en se cabrant, s'étire de tout son long au sommet, pique du museau,
    retombe sur les pattes avant, le nez dans l'herbe et la croupe en l'air, le panache qui fouette."""
    p = Pose()
    tasse = cloche(t, 0.11, 0.11, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.38))           # en l'air de 0,18 à 0,56
    cabre, pique = cloche(t, 0.25, 0.14, False), cloche(t, 0.49, 0.14, False)
    sommet = cloche(t, 0.37, 0.14, False)
    salut = cloche(t, 0.69, 0.19, False)                         # la révérence de l'atterrissage
    fouet = onde(t, 6) * cloche(t, 0.76, 0.22, False)
    dz = -0.035 * tasse + 0.21 * vol
    rx = -24 * cabre + 20 * pique + 11 * salut
    p.add("corps", pos=(0, 0, dz), rot=(rx, 0, 0), ech=(1, 1 + 0.05 * sommet, 1))
    pattes(p, dz, rx, 25 * cabre - 30 * sommet - 30 * pique - 32 * salut, 28 * cabre + 34 * sommet + 30 * pique)
    p.add("cou", rot=(10 * tasse + 8 * cabre + 10 * pique + 20 * salut, 0, 0))
    p.add("tete", rot=(14 * cabre + 8 * pique, 0, 0))
    p.paire("oreille", rot=(-24 * vol + 8 * salut, 0, 0))
    p.add("queue1", rot=(-12 * tasse - 14 * vol + 22 * salut, 0, -14 * fouet))
    p.add("queue2", rot=(-16 * vol + 8 * salut, 16 * fouet, 0))
    p.add("queue3", rot=(-14 * vol + 6 * salut, 20 * fouet, 0))
    return p


def dort(t):
    """Roulé en boule sur le flanc gauche : le ventre au sol, les pattes ramenées sous le menton, la tête couchée
    contre le flanc et le bout du panache posé sur le museau. Une oreille tressaille."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.066), rot=(0, 7, 0), ech=(1 + 0.012 * r, 1, 1 + 0.03 * r))
    p.add("patte_avant_G", rot=(-69, 0, 35))
    p.add("patte_avant_D", rot=(-69, 0, 50))
    p.paire("patte_arriere", rot=(-74, 0, 8))
    p.add("cou", rot=(32, 0, 72))
    p.add("tete", rot=(-4, 6, 46))
    p.add("oreille_D", rot=(0, 0, -22 * cloche(t, 0.55, 0.04)))
    p.add("queue1", rot=(50, 91, 0))                             # le panache, d'abord ramené vers l'avant, se couche sur le côté gauche
    p.add("queue2", rot=(31 + 2 * r, 0, 0))
    p.add("queue3", rot=(6 + 3 * r, 0, 0))
    return p


# C'est l'Épinglé du bois (voir epingle.py) : huit épingles sur le dos, la croupe et le crâne, une couture qui lâche au flanc.
EPINGLE = dict(
    epingles=[("corps", CORPS, (0.25, -0.30, 1.0), (0.10, -0.25)), ("corps", CORPS, (-0.35, 0.05, 1.0), (-0.30, 0.10)),
              ("corps", CORPS, (0.10, 0.50, 1.0), (0.15, 0.30)), ("corps", CORPS, (0.95, 0.30, 0.55), (0.20, 0.25)),
              ("corps", CORPS, (-0.85, -0.15, 0.60), (-0.25, -0.10)), ("corps", CORPS, (-0.30, 0.65, 0.75), (-0.10, 0.35)),
              ("tete", TETE, (-0.30, 0.45, 1.0), (-0.20, 0.30)), ("tete", TETE, (0.55, 0.50, 0.65), (0.30, 0.20))],
    couture=("corps", CORPS, (1.0, -0.20, 0.10), (0.0, 1.0, 0.25)))

ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
