"""L'écureuil en peluche : assis, la queue en panache dans le dos, il serre son gland et s'inquiète qu'on le lui prenne.

    python ecureuil.py        fabrique la fiche art/apercus/animaux/ecureuil.png
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

CORPS = Vector((0.0, 0.02, 0.122))
TETE = Vector((0.0, -0.03, 0.305))


def sur(a, piece, centre, vers):
    """Le point de la surface visé depuis « centre », et la normale à cet endroit."""
    p = a.trace(piece, centre, [vers], 0.0)[0]
    return p, a.trace(piece, centre, [vers], 1.0)[0] - p


def construire():
    a = K.Animal("ecureuil")
    a.taille = 0.58
    a.tete = Vector((0, -0.06, 0.32))

    # ----- le corps : une poire assise sur son derrière, le ventre rapiécé de crème -----
    def poire(v):
        s = v * [0.098, 0.098, 0.130]
        s[:, :2] *= (1 - 0.24 * v[:, 2])[:, None]         # plus large en bas
        s[:, 2] = np.maximum(s[:, 2], -0.118)             # le dessous à plat
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(poire), K.CARAMEL, pos=CORPS)
    a.rustine("ventre", "corps", CORPS, (0, -0.95, 0.12), lambda th: 0.60 - 0.14 * math.cos(2 * th), K.CREME, feston=32)

    # ----- la tête : de bonnes joues, et la gauche encore plus pleine (il y cache déjà une noisette) -----
    def crane(v):
        v = K.bosse(v, (0.95, -0.25, -0.45), 0.34, 0.25)
        v = K.bosse(v, (-0.95, -0.25, -0.45), 0.12, 0.25)
        return v * [0.095, 0.090, 0.082]
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(crane), K.CARAMEL, pos=TETE)
    a.couture("crane", "tete", 14, 0.55, 0.98)

    # ----- le museau crème, la truffe, et deux dents de rongeur en feutrine blanche -----
    a.piece("museau", A.boule(1.0, 32, 16).etire(0.040, 0.034, 0.030), K.CREME, pos=TETE + Vector((0, -0.072, -0.022)))
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.012, 0.009, 0.009), K.NOIR, pos=TETE + Vector((0, -0.104, -0.006)), poil=False)
    dents = A.boule(1.0, 16, 8).sculpte(lambda v: K.emousse(v, 0.5)).etire(0.011, 0.0045, 0.012)
    a.piece("dents", dents, K.BLANC, pos=TETE + Vector((0, -0.102, -0.046)), poil=False)
    a.broderie("dents", [TETE + Vector((0, -0.107, -0.036)), TETE + Vector((0, -0.107, -0.057))], 0.0009)

    # ----- les yeux, et des sourcils qui remontent au milieu : il s'inquiète pour son gland -----
    p, n = sur(a, "tete", TETE, (0.50, -0.74, 0.36))
    a.bouton("oeil", p, n, 0.022, paire=True)
    inquiet = [Vector((0.14 + 0.50 * t, -0.76 + 0.24 * t, 0.78 - 0.20 * t)) for t in np.linspace(0, 1, 6)]
    a.broderie("sourcil", a.trace("tete", TETE, inquiet), 0.0024, paire=True)

    # ----- les oreilles pointues, doublées de feutrine chocolat -----
    oreille = A.tour(A.profil([(0, 0), (0.030, 0.012), (0.025, 0.04), (0.012, 0.072), (0, 0.090)], 6), 32).etire(1.0, 0.42, 1.0)
    E = A.repere(TETE + Vector((0.055, 0.012, 0.050)), (-4, 16, 12))
    a.piece("oreille", oreille, K.CARAMEL, mat=E, paire=True)
    a.rustine("pavillon", "oreille", E @ Vector((0, 0, 0.042)), E.to_3x3() @ Vector((0, -1, 0)),
              lambda th: 1.15 + 0.20 * max(0.0, -math.sin(th)), K.CHOCOLAT, 0.002, 0, paire=True)

    # ----- les bras, refermés sur le gland : la noix moutarde, la cupule chocolat et sa petite tige -----
    bras = A.tube(A.courbe([(0.052, 0.0, 0.215), (0.085, -0.045, 0.178), (0.066, -0.092, 0.162), (0.036, -0.108, 0.170)], 6),
                  lambda t: 0.027 - 0.006 * t, 12)
    a.piece("bras", bras, K.CARAMEL, paire=True)

    # ----- les cuisses, cousues sur leur tranche, et les grands pieds posés devant -----
    cuisse = A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.030, 0.078, 0.070)
    a.piece("cuisse", cuisse, K.CARAMEL, pos=(0.092, 0.0, 0.078), rot=(10, 0, 8), paire=True)
    for cote in (10, 30):
        a.couture("cuisse%d" % cote, "cuisse", cote, 0.12, 0.88, "droit", paire=True)
    pied = A.boule(1.0, 32, 16).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.032, 0.062, 0.022)
    a.piece("pied", pied, K.CARAMEL, pos=(0.072, -0.085, 0.022), rot=(0, 0, -12), paire=True)

    # ----- la queue : un grand panache qui monte derrière le dos et se recourbe vers l'arrière -----
    def panache(v):
        long = np.linspace(0.0, 0.48, 200)                # le long de la pièce, le cap de la queue au-dessus de l'horizontale
        cap = np.radians(np.interp(long, [0, 0.10, 0.20, 0.30, 0.40, 0.48], [20, 70, 88, 84, 40, -20]))
        y = np.concatenate([[0.0], np.cumsum(np.cos(cap[:-1]) * np.diff(long))])
        z = np.concatenate([[0.0], np.cumsum(np.sin(cap[:-1]) * np.diff(long))])
        ici = np.interp(v[:, 2], long, cap)
        s = v.copy()
        s[:, 1] = np.interp(v[:, 2], long, y) + v[:, 1] * np.sin(ici)
        s[:, 2] = np.interp(v[:, 2], long, z) - v[:, 1] * np.cos(ici)
        return s
    queue = A.tour(A.profil([(0, 0), (0.030, 0.012), (0.036, 0.07), (0.060, 0.19), (0.084, 0.31), (0.080, 0.39), (0.048, 0.455), (0, 0.48)], 6), 48)
    G.sillons(queue, [12], 0.005, 1.1)
    a.piece("queue", queue.etire(0.82, 1.0, 1.0).sculpte(panache), K.CARAMEL, pos=(0, 0.085, 0.055))
    a.couture("queue", "queue", 12, 0.12, 0.92)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py ecureuil)

from poses import Pose, borne, cloche, onde

BASSIN = (0, 0.02, 0.05)
OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", BASSIN),
    ("tete", "corps", (0, -0.01, 0.235)),             # la nuque
    ("oreille_G", "tete", (0.055, -0.018, 0.355)),
    ("bras_G", "corps", (0.052, 0.0, 0.215)),         # l'épaule
    ("patte_G", "corps", (0.088, 0.0, 0.085)),        # la hanche : elle porte la cuisse
    ("pied_G", "patte_G", (0.072, -0.045, 0.025)),    # le talon
    ("queue1", "corps", (0, 0.085, 0.06)),            # la queue, en trois os l'un sur l'autre
    ("queue2", "queue1", (0, 0.163, 0.16)),
    ("queue3", "queue2", (0, 0.182, 0.32)),
]


def panache(points, cote):
    """La queue est souple : elle passe d'un os au suivant en montant, du croupion à la pointe."""
    milieu = K.lisse((points[:, 2] - 0.10) / 0.12)
    haut = K.lisse((points[:, 2] - 0.26) / 0.12)
    return {"queue1": 1.0 - milieu, "queue2": milieu - haut, "queue3": haut}


PORTEURS = [("corps", "corps"), ("ventre", "corps"), ("tete", "tete"), ("crane", "tete"), ("museau", "tete"), ("truffe", "tete"),
            ("dents", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("oreille", "oreille", True), ("pavillon", "oreille", True),
            ("bras", "bras", True), ("cuisse", "patte", True), ("pied", "pied", True), ("queue", panache, "queue1")]


def palier(t, centre, large):
    """Comme cloche, mais on y arrive d'un coup et on tient la pose : le geste vif d'un rongeur."""
    return borne(2.5 * cloche(t, centre, large))


def penche(p, angle, appui=(-0.05, 0.0)):
    """Bascule le corps vers l'avant autour du bord de son assise (y, z), et non du bassin : rien ne s'enfonce dans le sol."""
    a = math.radians(angle)
    dy, dz = appui[0] - BASSIN[1], appui[1] - BASSIN[2]
    p.add("corps", rot=(angle, 0, 0), pos=(0, dy - (dy * math.cos(a) - dz * math.sin(a)), dz - (dy * math.sin(a) + dz * math.cos(a))))


def repos(t):
    """Assis, il surveille : un regard vif à gauche, un autre à droite, la queue qui ondule sans cesse, une oreille qui tressaille."""
    p = Pose()
    r = onde(t, 2)
    g, d = palier(t, 0.24, 0.12), palier(t, 0.64, 0.12)
    sursaut = cloche(t, 0.84, 0.03) + cloche(t, 0.90, 0.03)
    p.add("corps", ech=(1 + 0.010 * r, 1 + 0.010 * r, 1 + 0.016 * r))
    p.add("tete", rot=(1.5 * r - 5 * (g + d), 6 * d - 6 * g, 34 * g - 32 * d))
    p.paire("bras", rot=(-3 * r - 7 * (g + d), 0, 0))
    p.add("queue1", rot=(4 * onde(t, 2), 4 * onde(t, 2, 0.05), 6 * onde(t, 1)))
    p.add("queue2", rot=(8 * onde(t, 2, -0.12), 13 * onde(t, 2, -0.10), 0))
    p.add("queue3", rot=(14 * onde(t, 2, -0.26) + 18 * sursaut, 20 * onde(t, 2, -0.24), 0))
    p.add("oreille_D", rot=(0, -26 * sursaut, 0))
    p.paire("oreille", rot=(-8 * (g + d), 0, 0))
    p.ouvert = 1 - cloche(t, 0.45, 0.02) - cloche(t, 0.95, 0.02)
    return p


def avance(t):
    """Un bond par boucle : il se ramasse, s'élance le corps tendu, les bras en avant et les pieds derrière,
    le panache qui suit avec un temps de retard, puis retombe assis et la queue lui passe par-dessus."""
    p = Pose()

    def vol(retard=0.0):                                 # 0 au sol, 1 au sommet du bond
        return math.sin(math.pi * borne((t - 0.14 - retard) / 0.62))
    v = vol()
    ramasse = cloche(t, 0.96, 0.20)                      # replié à la réception, puis juste avant l'élan
    p.add("corps", pos=(0, 0, 0.115 * v), rot=(30 * v - 5 * ramasse, 0, 0),
          ech=(1 + 0.05 * ramasse - 0.02 * v, 1 + 0.05 * ramasse - 0.02 * v, 1 - 0.10 * ramasse + 0.05 * v))
    p.add("tete", rot=(-22 * v + 7 * ramasse, 0, 0))
    p.paire("oreille", rot=(-26 * v, 0, 0))
    p.paire("bras", rot=(-38 * v + 12 * ramasse, 0, 0))
    p.paire("patte", rot=(25 * v - 6 * ramasse, 0, 0))
    p.paire("pied", rot=(-15 * v + 11 * ramasse, 0, 0))
    p.add("queue1", rot=(-34 * v + 6 * ramasse, 0, 0))
    p.add("queue2", rot=(-20 * vol(0.10) + 12 * cloche(t, 0.88, 0.13), 0, 0))
    p.add("queue3", rot=(-30 * vol(0.20) + 20 * cloche(t, 0.93, 0.12), 0, 0))
    return p


def mange(t):
    """Assis, les pattes à la bouche, il grignote à toute vitesse ; il se fige, un coup d'œil inquiet de chaque côté, et reprend."""
    p = Pose()
    tient = palier(t, 0.50, 0.46)                        # les pattes portées à la bouche
    g, d = palier(t, 0.47, 0.06), palier(t, 0.60, 0.06)  # il guette : à gauche, puis à droite
    guet = borne(g + d)
    ronge = onde(t, 18) * tient * (1 - guet)
    p.add("corps", rot=(3 * tient, 0, 0), ech=(1, 1, 1 + 0.01 * ronge))
    p.add("tete", rot=(13 * tient - 9 * guet + 2.5 * ronge, 0, 30 * g - 30 * d))
    p.paire("bras", rot=(-40 * tient + 3 * ronge + 6 * guet, 0, -7 * tient))
    p.paire("oreille", rot=(6 * tient - 14 * guet, 0, 0))
    p.add("queue2", rot=(7 * onde(t, 2) * (1 - guet), 9 * onde(t, 2, 0.1) * (1 - guet), 0))
    p.add("queue3", rot=(12 * onde(t, 2, -0.15) * (1 - guet) - 12 * guet, 14 * onde(t, 2, -0.05) * (1 - guet), 0))
    p.ouvert = 1 - cloche(t, 0.80, 0.025)
    return p


def joie(t):
    """Deux sauts sur place, les bras jetés en l'air, le nez au ciel, la queue qui fouette de bas en haut."""
    p = Pose()
    u = borne(t / 0.92)
    env = math.sin(math.pi * u)
    saut = abs(math.sin(2 * math.pi * u)) * env ** 0.5
    fouet = onde(u, 4) * env
    p.add("corps", pos=(0, 0, 0.11 * saut), rot=(-7 * env, 0, 8 * onde(u, 2) * env), ech=(1 - 0.03 * saut, 1 - 0.03 * saut, 1 + 0.06 * saut))
    p.add("tete", rot=(-16 * env, 6 * onde(u, 2) * env, 0))
    p.paire("oreille", rot=(0, 12 * fouet, 0))
    p.paire("bras", rot=(-75 * env - 10 * saut, 0, 70 * env))
    p.paire("patte", rot=(18 * saut, 0, 0))
    p.paire("pied", rot=(10 * saut, 0, 0))
    p.add("queue1", rot=(-8 * env + 6 * fouet, 0, 0))
    p.add("queue2", rot=(18 * onde(u, 4, -0.12) * env, 0, 0))
    p.add("queue3", rot=(28 * onde(u, 4, -0.26) * env, 0, 0))
    return p


def dort(t):
    """Tassé sur lui-même, le nez sur le ventre, et le panache rabattu par-dessus la tête comme une couverture."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    penche(p, 10)
    p.add("corps", ech=(1.05 + 0.010 * r, 1.04 + 0.010 * r, 0.92 + 0.025 * r))
    p.add("tete", rot=(34, 5, 10), pos=(0, 0, -0.012))
    p.paire("oreille", rot=(-22, 0, 0))
    p.paire("bras", rot=(8, 0, -5))
    p.paire("pied", rot=(-10, 0, 0))
    p.add("queue1", rot=(10, 0, 0))
    p.add("queue2", rot=(30 + 2 * r, 0, 0))
    p.add("queue3", rot=(46 + 3 * r, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (72, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
