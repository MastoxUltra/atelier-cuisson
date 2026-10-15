"""La mésange en peluche, deuxième dessin : la sentinelle du jardin. Fine et dressée presque à la verticale sur
de longues pattes, le poids sur la patte gauche, la droite avancée prête à repartir ; la longue queue étroite
qui prolonge la diagonale du dos. La petite tête marine tournée d'un coup sec vers ce qui a bougé, le bec en l'air ;
les grandes joues blanches où l'œil mord, une tache blanche sur la nuque. Le ventre citron barré d'une cravate
marine qui s'élargit vers le bas, le manteau bleu ardoise, l'aile barrée de blanc.

    python mesange.py        fabrique la fiche art/apercus/animaux/mesange.png
    (le premier dessin, jamais gardé : mesange_ancien.py)
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

CITRON = M.hexa("#fff06a")                    # le ventre : un jaune froid et clair (le poil le fonce)
MARINE = M.hexa("#26305e")                    # la tête, la cravate, la queue
ARDOISE = M.hexa("#6c7fae")                   # le manteau et les ailes : un bleu ardoise clair
NEIGE = M.hexa("#fbfaf4")                     # les joues, la nuque, la barre de l'aile
PATTE = M.hexa("#5d6680")                     # les pattes et le bec, en feutrine
CORPS = Vector((0.0, 0.010, 0.112))
TETE = Vector((0.0, -0.040, 0.205))
RAYON = 0.037
DRESSE = A.repere(CORPS, (-50, 0, 4))         # le corps : presque debout, la poitrine haute
VIF = A.repere(TETE, (-14, -8, -38))          # la tête : tournée d'un coup sec vers sa droite, le bec en l'air


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du jardin."""
    return VIF.to_3x3() @ Vector((x, y, z))


def construire():
    a = K.Animal("mesange")
    a.taille = 0.27
    a.tete = VIF @ Vector((0.0, -0.040, 0.0))

    # ----- le corps : un œuf fin et long, la poitrine bombée ; le manteau ardoise du dos et le ventre citron
    #       sont peints sur la même pièce -----
    def coque(v):
        v = K.bosse(v, (0, -0.85, -0.25), 0.12, 0.32)       # la poitrine
        arriere = K.lisse((v[:, 1] - 0.05) / 0.95)
        s = v * [0.045, 0.084, 0.048]
        s[:, 0] *= 1 - 0.45 * arriere
        s[:, 2] *= 1 - 0.42 * arriere
        return s
    corps = A.boule(1.0, 56, 28)
    manteau = corps.v[:, 2] > 0.30 - 0.25 * corps.v[:, 1]
    corps.sculpte(coque)
    corps.teinte = np.where(manteau[:, None], ARDOISE, CITRON)
    G.sillons(corps, [14], 0.003, 1.1)
    a.piece("corps", corps, None, mat=DRESSE)
    a.couture("dos", "corps", 14, 0.55, 0.95, fil=NEIGE, large=0.006, haut=0.0032, pas=0.011)

    # ----- la cravate marine : étroite sous le menton, elle s'élargit en descendant vers le ventre -----
    def cravate(th):
        haut_ = math.sin(th)
        long = 0.55 if haut_ > 0 else 0.95
        large = 0.11 if haut_ > 0 else 0.20
        return large * long / math.hypot(long * math.cos(th), large * math.sin(th))
    a.rustine("cravate", "corps", CORPS, DRESSE.to_3x3() @ Vector((0, -0.70, -0.72)), cravate, MARINE, 0.003, 0)

    # ----- la tête marine, petite et ronde, le crâne un peu haut -----
    tete = A.boule(1.0, 56, 28).sculpte(lambda v: K.bosse(v, (0, 0.2, 1), 0.06, 0.4)).etire(RAYON, RAYON * 1.04, RAYON)
    a.piece("tete", tete, MARINE, mat=VIF)
    a.couture("crane", "tete", 14, 0.55, 0.97, fil=ARDOISE, large=0.006, haut=0.003, pas=0.010)
    a.rustine("nuque", "tete", TETE, vers(0, 0.88, 0.25), 0.24, NEIGE, 0.003, 10, fil=MARINE)

    # ----- les grandes joues blanches ; l'œil mord sur leur bord haut -----
    def joue(th):                                         # un triangle aux coins ronds, la pointe vers le bec
        return 0.66 + 0.10 * math.cos(3 * th + 0.6)
    for nom, cote in (("g", 1), ("d", -1)):
        a.rustine("joue_" + nom, "tete", TETE, vers(0.84 * cote, -0.34, -0.16), joue, NEIGE, 0.003, 16, fil=MARINE)
        p, n = a.surface("tete", TETE, vers(0.58 * cote, -0.74, 0.12))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0098)

    # ----- le bec : une pointe courte et fine -----
    bec = A.tour(A.profil([(0, 0), (0.0085, 0.003), (0.0065, 0.010), (0.003, 0.020), (0, 0.027)], 5), 24)
    a.piece("bec", bec, PATTE, pos=VIF @ Vector((0, -0.034, -0.004)), rot=A.viser(vers(0, -1, -0.10)), poil=False)

    # ----- les ailes : deux longs galets ardoise serrés au corps, barrés de blanc, la pointe sur la queue -----
    def galet(v):
        s = K.emousse(v, 0.85)
        pointe = K.lisse((v[:, 1] + 0.1) / 1.1)
        s[:, 0] *= 1 - 0.30 * pointe
        return s
    aile = A.boule(1.0, 40, 20).sculpte(galet).etire(0.011, 0.066, 0.034)
    K.bandes(aile, [(-0.024, ARDOISE), (-0.010, NEIGE), (9, MARINE)], axe=1)
    a.piece("aile", aile, None, mat=DRESSE @ A.repere((0.036, 0.022, 0.012), (-2, 0, 4)), paire=True)
    a.couture("aile_bord", "aile", 10, 0.12, 0.88, "droit", fil=NEIGE, paire=True, large=0.006, haut=0.003, pas=0.010)

    # ----- la queue : une longue palette étroite qui prolonge la diagonale du dos -----
    def palette(v):
        s = K.emousse(v, 0.8)
        s[:, 0] *= 0.80 + 0.30 * K.lisse((v[:, 1] + 1) / 2)
        return s
    racine = DRESSE @ Vector((0, 0.070, 0.004))
    pente = math.radians(-12)
    queue = A.boule(1.0, 32, 16).sculpte(palette).etire(0.017, 0.064, 0.006)
    a.piece("queue", queue, MARINE, pos=racine + Vector((0, math.cos(pente), math.sin(pente))) * 0.058, rot=(-12, 0, 0))

    # ----- les pattes : longues et fines ; la gauche porte le poids, la droite avance d'un pas -----
    def doigt(degres, long):
        t = math.radians(degres)
        return A.boule(1.0, 16, 8).etire(0.0042, long, 0.0040).pose((0.75 * long * math.sin(t), -0.75 * long * math.cos(t), 0), (0, 0, degres))
    for nom, cote, avance in (("patte_g", 1, 0.0), ("patte_d", -1, -0.026)):
        haut_ = (0.016 * cote, 0.000, 0.084)
        genou = (0.020 * cote, 0.004 + avance * 0.5, 0.044)
        bas_ = (0.022 * cote, avance, 0.0045)
        tige = A.tube(A.courbe([haut_, genou, bas_], 5), 0.0036, 12)
        pied = (doigt(-30, 0.017) + doigt(0, 0.021) + doigt(30, 0.017) + doigt(180, 0.012)).pose(bas_, (0, 0, -10 * cote))
        a.piece(nom, tige + pied, PATTE, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py mesange). Les mesures sont celles du modèle, avant a.taille.
# Les pattes pendent à la racine, pas au corps : posées, elles ne bougent pas quand le corps bascule au-dessus d'elles.
# La droite est avancée d'un pas : chacune a son os, nommé à la main.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.000, 0.084)),          # les hanches, en haut des pattes
    ("tete", "corps", (0.0, -0.030, 0.176)),           # le dessous de la petite tête, sur la poitrine
    ("aile_G", "corps", (0.034, -0.003, 0.150)),       # l'épaule (la droite est son miroir)
    ("queue", "corps", (0.0, 0.058, 0.061)),           # le croupion, d'où part la longue queue
    ("patte_g", "racine", (0.016, 0.000, 0.084)),      # le haut de chaque patte
    ("patte_d", "racine", (-0.016, 0.000, 0.084)),
]
PORTEURS = [("corps", "corps"), ("dos", "corps"), ("cravate", "corps"),
            ("tete", "tete"), ("crane", "tete"), ("nuque", "tete"), ("joue", "tete"), ("oeil", "tete"), ("bec", "tete"),
            ("aile", "aile", True), ("queue", "queue"), ("patte_g", "patte_g"), ("patte_d", "patte_d"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]

PENCHE_MANGE = (52.0, 47.0, 0.032)            # mange : de combien le corps (autour des hanches) et la tête plongent,
                                              # et de combien elle s'accroupit (les pattes rentrent sous le ventre)


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _sec(t, centre, large):
    """Un geste d'oiseau : vite parti, tenu, vite revenu (une cloche aplatie au sommet)."""
    return borne(1.6 * cloche(t, centre, large))


def _ailes(p, leve, ouvre=0.0):
    """Les ailes se décollent du corps (leve, en degrés) et s'ouvrent vers l'extérieur autour de l'épaule (ouvre)."""
    p.paire("aile", rot=(0.4 * leve, -0.5 * leve - 0.6 * ouvre, -0.4 * leve - 0.3 * ouvre))


def repos(t):
    """La sentinelle : elle respire vite, la tête claque d'un point à l'autre (là-bas, ici, en l'air, puis de nouveau
    vers ce qui a bougé), la longue queue bat de haut en bas par petits coups, le poids passe d'une patte à l'autre ;
    un clignement vif."""
    p = Pose()
    r = onde(t, 6)
    p.add("corps", ech=(1 + 0.012 * r, 1 + 0.010 * r, 1 + 0.010 * r))
    ici = _sec(t, 0.20, 0.07)
    ciel = _sec(t, 0.42, 0.06)
    la = _sec(t, 0.64, 0.07)
    p.add("tete", rot=(-6 * ici - 14 * ciel + 4 * la, 0, 30 * ici + 12 * ciel + 46 * la))
    p.add("queue", rot=(10 * max(0.0, onde(t, 12)) * cloche(t, 0.86, 0.10), 0, 0))
    p.add("corps", rot=(0, 3 * cloche(t, 0.55, 0.15), 0))
    _ailes(p, 4 * cloche(t, 0.86, 0.06))
    p.ouvert = 1 - cloche(t, 0.10, 0.015) - cloche(t, 0.76, 0.015)
    return p


def avance(t):
    """Elle sautille, pieds joints, nerveuse : un petit bond rapide, les ailes qui frémissent en l'air, la queue qui
    bat pour l'équilibre ; elle se reçoit droite, la tête toujours aux aguets."""
    p = Pose()
    air = math.sin(math.pi * borne((t - 0.18) / 0.60))
    tasse = cloche(t, 0.08, 0.09) + cloche(t, 0.88, 0.10)
    p.add("corps", pos=(0, 0, 0.034 * air - 0.005 * tasse), rot=(8 * tasse - 6 * air, 0, 0))
    for c in ("patte_g", "patte_d"):
        p.add(c, pos=(0, 0.004 * air, 0.030 * air), rot=(-22 * air, 0, 0))
    p.add("tete", rot=(5 * air - 6 * tasse, 0, 0))
    p.add("queue", rot=(14 * air - 10 * tasse, 0, 0))
    _ailes(p, 10 * air + 8 * air * onde(t, 4))
    return p


def mange(t):
    """Elle se penche sur sa graine et la martèle du bec à grands coups secs, quatre fois, la queue relevée à chaque
    coup ; puis elle se redresse d'un coup et jette un œil à droite, à gauche."""
    p = Pose()
    bas = _plateau(t, 0.36, 0.22, 0.10)
    coups = max(0.0, onde(t, 11, 0.0)) ** 2 * _plateau(t, 0.36, 0.18, 0.05)
    p.add("corps", rot=(PENCHE_MANGE[0] * bas + 5 * coups, 0, 0), pos=(0, 0, -PENCHE_MANGE[2] * bas))
    p.add("tete", rot=(PENCHE_MANGE[1] * bas + 16 * coups, 0, 34 * bas + 22 * _sec(t, 0.76, 0.05) - 20 * _sec(t, 0.90, 0.04)))
    p.add("queue", rot=(-0.5 * PENCHE_MANGE[0] * bas - 8 * coups, 0, 0))
    _ailes(p, 3 * bas)
    p.ouvert = 1 - cloche(t, 0.68, 0.02)
    return p


def joie(t):
    """Sa fête d'acrobate : elle bondit en voletant, les ailes grandes ouvertes qui battent à toute vitesse, se tourne
    d'un quart en l'air d'un côté puis de l'autre, la queue en éventail, et chante son « titu-titu » le bec au ciel ;
    elle se repose sur ses pattes, droite comme avant."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85)) if t < 0.85 else 0.0
    vol = math.sin(math.pi * borne((t - 0.10) / 0.65))
    tourne = 40 * (cloche(t, 0.32, 0.12, False) - cloche(t, 0.58, 0.12, False))
    p.add("corps", pos=(0, 0, 0.050 * vol), rot=(-6 * env, 0, tourne))
    for c in ("patte_g", "patte_d"):
        p.add(c, pos=(0, 0, 0.050 * vol), rot=(-20 * vol, 0, tourne))
    p.add("tete", rot=(-20 * env + 6 * abs(onde(t, 6)) * env, 0, -0.5 * tourne))
    _ailes(p, 50 * vol + 30 * onde(t, 10) * vol, 14 * vol)
    p.add("queue", rot=(-14 * env, 0, 0), ech=(1 + 0.4 * env, 1, 1))
    return p


def dort(t):
    """Elle se gonfle en boule, accroupie sur ses pattes, la tête retournée sur le dos et le bec glissé dans les plumes
    de l'épaule, les yeux fermés ; elle respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.010), rot=(-8, 0, 0), ech=(1.10 + 0.015 * r, 1.05 + 0.01 * r, 1.0 + 0.02 * r))
    p.add("tete", pos=(0, 0.004, -0.008), rot=(18, 0, 142))
    _ailes(p, -2)
    p.add("queue", rot=(8, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Mésange")
