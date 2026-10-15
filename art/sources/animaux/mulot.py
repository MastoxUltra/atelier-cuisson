"""Le mulot en peluche : le dos miel doré, le devant blanc, une ligne franche entre les deux. Assis sur son derrière,
les mains ramenées contre lui, il lève le nez et penche la tête : des yeux énormes, de grandes oreilles rondes
et fines, et une queue interminable qui serpente dans l'herbe.

    python mulot.py        fabrique la fiche art/apercus/animaux/mulot.png
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

MIEL = M.hexa("#eabe67")                    # le dos (le poil le fonce et le dore)
TETE = Vector((0.0, -0.015, 0.250))


def construire():
    a = K.Animal("mulot")
    a.taille = 0.30

    # ----- le corps : une poire assise bien à plat, un peu renversée en arrière ; le dos miel, le devant blanc -----
    def assis(v):
        s = v.copy()
        s[:, 1] += 0.06 * v[:, 2]
        return s
    corps = A.tour(A.profil([(0, 0), (0.062, 0.003), (0.086, 0.030), (0.090, 0.075), (0.078, 0.125), (0.060, 0.165),
                             (0.046, 0.190), (0, 0.205)], 6), 48)
    G.sillons(corps, [12], 0.004, 1.1)
    robe = np.tile(np.asarray(MIEL, float), (len(corps.v), 1))
    for anneau in corps.anneaux:                          # le côté 36 est le devant : la limite suit les mailles, elle sort nette dans le poil
        if len(anneau) > 1:
            robe[anneau[27:45]] = K.BLANC
    corps.teinte = robe
    a.piece("corps", corps.sculpte(assis), None, pos=(0, 0.01, 0))
    a.couture("dos", "corps", 12, 0.35, 0.95)

    # ----- la tête : une boule qui s'étire en museau pointu, le nez en l'air, penchée par curiosité -----
    H = A.repere(TETE, (-18, 12, 12))                     # le nez levé, la tête de travers, un peu tournée vers sa gauche (vers nous)
    H3 = H.to_3x3()
    a.tete = H @ Vector((0, -0.090, 0.005))

    def museau(v):                                        # sur la boule : l'avant s'étire en cône, un peu vers le bas
        s = v.copy()
        avant = K.lisse((-v[:, 1] - 0.15) / 0.85)
        s[:, 1] -= 0.55 * avant ** 1.5
        s[:, 0] *= 1 - 0.50 * avant
        s[:, 2] = v[:, 2] * (1 - 0.50 * avant) - 0.10 * avant
        return s * [0.070, 0.072, 0.064]
    tete = K.bandes(A.boule(1.0, 56, 28), [(-0.38, K.BLANC), (9, MIEL)]).sculpte(museau)   # le dessous blanc : menton, bas des joues, gorge
    a.piece("tete", tete, None, mat=H)
    a.couture("crane", "tete", 14, 0.58, 0.98)
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.012, 0.010, 0.010), K.FRAMBOISE, mat=H @ A.repere((0, -0.113, -0.005)), poil=False)

    # ----- les yeux énormes, et deux longues moustaches blanches de chaque côté du nez -----
    for nom, c in (("G", 1), ("D", -1)):
        pos, vers = a.surface("tete", TETE, H3 @ Vector((c * 0.69, -0.54, 0.34)))
        vers = (vers + H3 @ Vector((0, -0.22, -0.06))).normalized()      # le bouton regarde un peu plus vers l'avant que le tissu
        a.bouton("oeil_" + nom, pos - vers * 0.003, vers, 0.026)
        for k, dz in enumerate((0.024, -0.010)):
            a.broderie("moustache_%s%d" % (nom, k), [H @ Vector((c * 0.014, -0.096, -0.008)), H @ Vector((c * 0.050, -0.112, -0.004 + dz * 0.5)),
                                                     H @ Vector((c * 0.088, -0.118, -0.004 + dz))], 0.0010, K.BLANC)

    # ----- les grandes oreilles : deux disques de feutrine fine, creusés en coupe, un point avant près du bord -----
    def coupe(v):                                         # le bord du pavillon revient vers l'avant
        s = v.copy()
        s[:, 2] += 2.2 * (v[:, 0] ** 2 + v[:, 1] ** 2)
        return s * [0.050, 0.056, 0.0045]
    for nom, c in (("G", 1), ("D", -1)):
        E = H @ A.cadre((c * 0.062, 0.022, 0.085), (c * 0.30, -0.92, 0.25), (c * 0.35, 0.0, 1.0))   # Z regarde vers l'avant, Y monte
        a.piece("oreille_" + nom, A.boule(1.0, 32, 16).sculpte(coupe), K.PECHE, mat=E, poil=False)
        a.ourlet("ourlet_" + nom, "oreille_" + nom, 0.63, haut=0.0015, pas=0.010)

    # ----- les bras courts, les deux mains de feutrine jointes sur la poitrine -----
    bras = A.courbe([(0.050, -0.020, 0.150), (0.062, -0.048, 0.120), (0.036, -0.066, 0.115), (0.018, -0.070, 0.124)], 6)
    a.piece("bras", A.tube(bras, lambda t: 0.017 - 0.004 * t, 12), MIEL, paire=True)
    a.piece("main", A.boule(1.0, 16, 8).etire(0.012, 0.013, 0.015), K.PECHE, pos=(0.013, -0.075, 0.130), poil=False, paire=True)

    # ----- les cuisses rondes, cousues sur leur tranche, et les longs pieds de feutrine qui dépassent devant -----
    cuisse = A.boule(1.0, 32, 16).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.026, 0.058, 0.050)
    a.piece("cuisse", cuisse, MIEL, pos=(0.082, 0.005, 0.052), rot=(12, 0, 10), paire=True)
    a.couture("cuisse", "cuisse", 8, 0.15, 0.85, "droit", paire=True)
    pied = A.boule(1.0, 24, 12).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.017, 0.046, 0.010)
    a.piece("pied", pied, K.PECHE, pos=(0.052, -0.088, 0.010), rot=(0, 0, 18), poil=False, paire=True)

    # ----- la queue interminable : elle fait le tour par sa gauche et finit en S devant lui, le bout relevé -----
    queue = A.courbe([(0, 0.075, 0.020), (0.030, 0.125, 0.012), (0.100, 0.140, 0.011), (0.155, 0.095, 0.010), (0.172, 0.015, 0.009),
                      (0.150, -0.075, 0.008), (0.135, -0.140, 0.008), (0.165, -0.185, 0.012), (0.205, -0.172, 0.034)], 8)
    a.piece("queue", A.tube(queue, lambda t: 0.0105 - 0.0065 * t, 12), K.PECHE, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py mulot)

from poses import Pose, borne, cloche, onde

# Les bras, les cuisses et les pieds sont de vraies paires (un os à gauche, recopié à droite) ; les pieds pendent à la
# racine : posés à plat, ils ne bougent pas quand il se penche. La tête est penchée et tournée : les deux oreilles
# n'ont rien de symétrique, leurs os sont nommés à la main (oreille_g, oreille_d). La queue interminable, couchée
# dans l'herbe, est une pièce souple que trois os se partagent le long de son chemin, de la croupe au bout relevé.
_QUEUE = A.courbe([(0, 0.075, 0.020), (0.030, 0.125, 0.012), (0.100, 0.140, 0.011), (0.155, 0.095, 0.010), (0.172, 0.015, 0.009),
                   (0.150, -0.075, 0.008), (0.135, -0.140, 0.008), (0.165, -0.185, 0.012), (0.205, -0.172, 0.034)], 8)
_FAIT = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(_QUEUE, axis=0), axis=1))])
_JALONS = (("queue1", 0.0), ("queue2", 0.35), ("queue3", 0.68))


def _au_fil(f):
    """Le point du chemin de la queue à la fraction f de sa longueur : le pivot d'un os."""
    i = int(np.searchsorted(_FAIT, f * _FAIT[-1]))
    return tuple(round(float(x), 3) for x in _QUEUE[min(i, len(_QUEUE) - 1)])


def _abscisse(points):
    """Pour chaque point : sa place le long de la queue (de 0 à 1), au pied de la perpendiculaire sur le tronçon le plus proche."""
    a, ab = _QUEUE[:-1], np.diff(_QUEUE, axis=0)
    l2 = np.maximum((ab * ab).sum(axis=1), 1e-12)
    ap = points[:, None, :] - a[None, :, :]
    u = np.clip((ap * ab[None]).sum(axis=2) / l2, 0.0, 1.0)
    j = np.linalg.norm(ap - u[..., None] * ab[None], axis=2).argmin(axis=1)
    return (_FAIT[j] + u[np.arange(len(points)), j] * np.sqrt(l2[j])) / _FAIT[-1]


def _relais(f, jalons, large):
    """Des os qui se passent la main le long d'un fil : chacun porte le tronçon qui suit son pivot, et cède au suivant
    en douceur sur ± large autour du pivot de celui-ci."""
    def marche(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3 - 2 * x)
    montees = [np.ones_like(f)] + [marche((f - f0 + large) / (2 * large)) for _o, f0 in jalons[1:]] + [np.zeros_like(f)]
    return {o: montees[i] - montees[i + 1] for i, (o, _f0) in enumerate(jalons)}


def _queue(points, cote):
    return _relais(_abscisse(points), _JALONS, 0.08)


def _oreille(points, cote):
    return {"oreille_g" if cote == "_G" else "oreille_d": np.ones(len(points))}


OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.010, 0.050)),            # le derrière sur lequel il est assis : il se penche et se dresse autour
    ("tete", "corps", (-0.005, -0.010, 0.195)),          # la nuque, sur le haut de la poire
    ("oreille_g", "tete", (0.045, 0.020, 0.290)),        # la base de chaque oreille, contre le crâne
    ("oreille_d", "tete", (-0.035, 0.005, 0.305)),
    ("bras_G", "corps", (0.050, -0.020, 0.150)),         # l'épaule
    ("cuisse_G", "corps", (0.082, 0.005, 0.060)),        # la hanche, au cœur de la cuisse
    ("pied_G", "racine", (0.052, -0.050, 0.010)),        # le talon
    ("queue1", "corps", _au_fil(0.0)),                   # la queue : trois os, de la croupe au bout
    ("queue2", "queue1", _au_fil(0.35)),
    ("queue3", "queue2", _au_fil(0.68)),
]
PORTEURS = [("corps", "corps"), ("dos", "corps"),
            ("tete", "tete"), ("crane", "tete"), ("truffe", "tete"), ("oeil", "tete"), ("moustache", "tete"),
            ("oreille", _oreille, "oreille_g"), ("ourlet", _oreille, "oreille_g"),
            ("bras", "bras", True), ("main", "bras", True), ("cuisse", "cuisse", True), ("pied", "pied", True),
            ("queue", _queue, "queue1"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


BASCULE = 30.0                 # penché pour bondir, de tant de degrés
TETE_TOILETTE, BRAS_TOILETTE = 25.0, -70.0      # pour la toilette : le nez baissé, les mains montées contre les joues


def _penche(p, k):
    """Penché en avant pour bondir, à la fraction k (0 : assis, 1 : penché) : les mains repliées contre la poitrine,
    la tête relevée pour regarder devant, la queue gardée à plat dans l'herbe."""
    p.add("corps", rot=(BASCULE * k, 0, 0), pos=(0, 0, 0.020 * k))      # le bas du ventre, devant, ne s'enfonce pas
    p.add("tete", rot=(-0.75 * BASCULE * k, 0, 0))
    p.paire("bras", rot=(-BASCULE * k, 0, 0))
    p.paire("cuisse", rot=(-0.6 * BASCULE * k, 0, 0))
    p.add("queue1", rot=(-BASCULE * k, 0, 0), pos=(0, 0, -0.040 * k))


def repos(t):
    """Assis sur son derrière, il vit vite : il respire en hâte, flaire (le nez frémit), penche la tête d'un côté puis
    de l'autre par curiosité, tourne une oreille ; puis il fait sa toilette : les deux mains montent frotter le museau,
    trois fois ; le bout de la queue frétille ; il cligne."""
    p = Pose()
    r = onde(t, 4)
    toilette = _plateau(t, 0.66, 0.09, 0.05)
    frotte = onde(t, 24) * _plateau(t, 0.66, 0.07, 0.03)
    p.add("corps", ech=(1 + 0.015 * r, 1 + 0.015 * r, 1 + 0.010 * r))
    flaire = cloche(t, 0.08, 0.05) * onde(t, 30)
    incline = 14 * cloche(t, 0.24, 0.07) - 16 * cloche(t, 0.42, 0.07)
    p.add("tete", rot=(2.5 * flaire + TETE_TOILETTE * toilette + 3 * frotte, incline, 0))
    p.paire("bras", rot=(BRAS_TOILETTE * toilette + 6 * frotte, 0, 0))
    p.add("oreille_g", rot=(0, 0, 25 * cloche(t, 0.32, 0.05)))
    p.add("oreille_d", rot=(0, 0, -20 * cloche(t, 0.86, 0.04)))
    p.add("queue3", rot=(0, 0, 25 * cloche(t, 0.90, 0.05) * onde(t, 12)))
    p.ouvert = borne(1 - cloche(t, 0.16, 0.02) - cloche(t, 0.52, 0.02) - 0.4 * toilette)
    return p


def avance(t):
    """Il file comme les mulots, en petit kangourou : penché en avant, les mains repliées contre lui, il pousse des deux
    longs pieds ensemble, passe en l'air le nez d'abord levé puis plongeant, se reçoit sur ses pieds en se tassant, et
    ses pieds posés glissent vers l'arrière jusqu'au bond suivant ; les oreilles se couchent, la queue ondule derrière."""
    p = Pose()
    _penche(p, 1.0)
    vol = max(0.0, onde(t, 1))                                 # en l'air de 0 à 0,5, au sol de 0,5 à 1
    sol = max(0.0, -onde(t, 1))
    p.add("corps", rot=(-8 * onde(t, 2) * vol, 0, 0), pos=(0, 0, 0.035 * vol), ech=(1 + 0.02 * sol, 1, 1 - 0.05 * sol))
    p.add("tete", rot=(5 * onde(t, 2) * vol, 0, 0))
    p.paire("pied", rot=(12 * vol, 0, 0), pos=(0, 0.012 * math.cos(math.tau * t), 0.030 * vol))
    p.paire("cuisse", rot=(-10 * vol, 0, 0))
    p.add("oreille_g", rot=(-15, 0, 0))
    p.add("oreille_d", rot=(-15, 0, 0))
    p.add("queue1", rot=(0, 0, 8 * onde(t, 1, -0.1)))
    p.add("queue2", rot=(0, 0, 12 * onde(t, 1, -0.25)))
    p.add("queue3", rot=(0, 0, 16 * onde(t, 1, -0.4)))
    return p


def mange(t):
    """Il se penche, ramasse une graine du bout des mains, se rassoit et la grignote à toute vitesse, les mains contre
    le museau, puis relève le nez et regarde autour."""
    p = Pose()
    ramasse = cloche(t, 0.10, 0.10)
    grignote = _plateau(t, 0.52, 0.26, 0.08)
    dents = onde(t, 36) * _plateau(t, 0.52, 0.24, 0.03)
    p.add("corps", rot=(45 * ramasse, 0, 0), pos=(0, 0, 0.030 * ramasse))         # le nez jusqu'à l'herbe
    p.add("tete", rot=(50 * ramasse, 0, 0))
    p.paire("bras", rot=(10 * ramasse, 0, 0))
    p.paire("cuisse", rot=(-27 * ramasse, 0, 0))
    p.add("queue1", rot=(-45 * ramasse, 0, 0), pos=(0, 0, -0.110 * ramasse))   # la queue reste couchée dans l'herbe
    p.add("tete", rot=(TETE_TOILETTE * grignote + 3 * dents, 0, -12 * cloche(t, 0.88, 0.06)))
    p.paire("bras", rot=(BRAS_TOILETTE * grignote + 2 * dents, 0, 0))
    p.add("oreille_g", rot=(0, 0, 15 * cloche(t, 0.88, 0.06)))
    p.add("queue3", rot=(0, 0, 10 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.80, 0.02))
    return p


def joie(t):
    """Sa fête : il se ramasse et bondit tout droit, très haut pour sa taille, en se tordant d'un demi-tour, les mains
    ouvertes, la queue qui fouette l'air ; il retombe assis, le nez levé, curieux comme avant."""
    p = repos(0.0)
    tasse = cloche(t, 0.10, 0.10, False)
    saut = math.sin(math.pi * borne((t - 0.16) / 0.48))          # en l'air de 0,16 à 0,64
    p.add("corps", rot=(10 * tasse - 8 * saut, 10 * saut, 50 * saut), pos=(0, 0, -0.006 * tasse + 0.090 * saut))
    p.paire("pied", rot=(25 * saut, 0, 0), pos=(0, 0.010 * saut, 0.092 * saut))
    p.paire("cuisse", rot=(20 * saut, 0, 0))
    p.paire("bras", rot=(-35 * saut, 0, 0))
    p.add("tete", rot=(-12 * saut, 0, -15 * saut))
    p.add("oreille_g", rot=(0, 25 * saut, 0))
    p.add("oreille_d", rot=(0, -25 * saut, 0))
    fouet = onde(t, 3) * math.sin(math.pi * borne(t / 0.8))
    p.add("queue1", rot=(0, 0, 20 * fouet))
    p.add("queue2", rot=(0, 0, 25 * fouet))
    p.add("queue3", rot=(0, 0, 30 * onde(t, 3, -0.1) * math.sin(math.pi * borne(t / 0.8))))
    return p


def dort(t):
    """Roulé en boule : penché tout en avant sur ses pieds, la tête rentrée entre les mains, le nez sous lui, les
    oreilles couchées, la queue ramenée autour de lui, les yeux fermés ; il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", rot=(34, 0, 0), pos=(0, 0, 0.024), ech=(1.04 + 0.018 * r, 1.04 + 0.018 * r, 0.96))
    p.add("tete", rot=(18, 0, 0))
    p.paire("bras", rot=(10, 0, 0))
    p.paire("cuisse", rot=(-20, 0, 0))
    p.add("oreille_g", rot=(-30, 0, 0))
    p.add("oreille_d", rot=(-30, 0, 0))
    p.add("queue1", rot=(-34, 0, -10), pos=(0, 0, -0.050))        # à plat dans l'herbe, ramenée autour de lui
    p.add("queue2", rot=(0, 0, -25))
    p.add("queue3", rot=(0, 0, -30))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Mulot")
