"""Le moineau en peluche, deuxième dessin : le titi du jardin. Une boule trapue plantée sur ses deux pattes écartées,
le jabot bombé comme un torse de petit dur, les ailes rejetées en arrière, la queue courte dressée d'un coup sec.
La grosse tête posée sans cou, penchée sur l'épaule pour vous jauger, coiffée d'une calotte chocolat taillée de
travers comme une casquette de gavroche : elle descend sur l'œil droit et laisse l'œil gauche, sous son sourcil
levé, vous toiser. Une bavette charbon sous le bec, les épaulettes brique : l'accent qui claque.

    python moineau.py        fabrique la fiche art/apercus/animaux/moineau.png
    (le premier dessin, jamais gardé : moineau_ancien.py)
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

SABLE = M.hexa("#f9dcae")                     # le corps : un sable chaud et clair (le poil le dore)
CARAMEL = M.hexa("#c98b52")                   # le manteau du dos et la barre de l'aile
CHOCOLAT = M.hexa("#5a3524")                  # la calotte, les ailes, la queue
CHARBON = M.hexa("#2e2a2b")                   # la bavette
BRIQUE = M.hexa("#d4502c")                    # l'accent : les épaulettes
ARDOISE = M.hexa("#4b4650")                   # le bec, gros et court
CHAIR = M.hexa("#e2a993")                     # les pattes
CORPS = Vector((0.0, 0.020, 0.104))
TETE = Vector((0.006, -0.032, 0.204))
RAYON = 0.060                                 # la tête : grosse, posée sans cou
PENCHE = A.repere(TETE, (-8, 18, -16))         # le menton levé, penchée sur l'épaule : il vous toise de l'œil gauche


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du jardin."""
    return PENCHE.to_3x3() @ Vector((x, y, z))


def construire():
    a = K.Animal("moineau")
    a.taille = 0.27
    a.tete = PENCHE @ Vector((0.0, -0.056, -0.004))

    # ----- le corps : une boule trapue, le jabot très bombé et haut, la croupe qui remonte vers la queue ;
    #       le manteau caramel du dos et le ventre sable sont peints sur la même pièce -----
    def coque(v):
        v = K.bosse(v, (0, -0.92, 0.05), 0.30, 0.30)        # le torse de petit dur
        v = K.bosse(v, (0, -0.20, -0.90), 0.06, 0.40)       # le ventre plein
        arriere = K.lisse((v[:, 1] - 0.15) / 0.85)
        s = v * [0.084, 0.094, 0.082]
        s[:, 0] *= 1 - 0.30 * arriere
        s[:, 2] = s[:, 2] * (1 - 0.30 * arriere) + 0.020 * arriere
        s[:, 2] = np.maximum(s[:, 2], -0.068)               # un fond aplati : il est posé, lourd, sur ses pattes
        return s
    corps = A.boule(1.0, 56, 28)
    manteau = (corps.v[:, 1] > 0.10) & (corps.v[:, 2] > 0.05)
    corps.sculpte(coque)
    corps.teinte = np.where(manteau[:, None], CARAMEL, SABLE)
    G.sillons(corps, [14], 0.004, 1.1)
    a.piece("corps", corps, None, pos=CORPS)
    a.couture("dos", "corps", 14, 0.55, 0.95, fil=CHOCOLAT, large=0.007, haut=0.0035, pas=0.012)

    # ----- la bavette charbon : une goutte qui part du menton et tombe sur le jabot -----
    def bavette(th):
        return 0.24 + 0.14 * max(0.0, math.sin(th))
    a.rustine("bavette", "corps", CORPS, (0, -0.90, 0.42), bavette, CHARBON, 0.003, 16, fil=CHOCOLAT)

    # ----- la tête : une grosse boule aux joues pleines, le front bas -----
    def joues(v):
        for cote in (1, -1):
            v = K.bosse(v, (0.70 * cote, -0.45, -0.40), 0.09, 0.22)
        v = K.bosse(v, (0, -0.75, 0.55), 0.05, 0.25)        # le front
        return v
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(joues).etire(RAYON), SABLE, mat=PENCHE)

    # ----- la barbiche : un petit triangle charbon sous le bec, la pointe vers le jabot (la bavette du moineau, en bouc) -----
    def barbiche(th):
        return 0.20 + 0.16 * max(0.0, math.sin(th)) ** 2
    a.rustine("barbiche", "tete", TETE, vers(0, -0.62, -0.78), barbiche, CHARBON, 0.003, 0)

    # ----- la calotte : une pièce de peluche chocolat qui coiffe le crâne, coupée de travers comme une casquette
    #       de gavroche : haute sur l'œil gauche, basse sur le droit, et qui descend sur la nuque -----
    def casquette(v):
        s = v * 1.07
        bord = 0.36 + 0.13 * s[:, 0] - 0.40 * np.maximum(s[:, 1], 0) + 0.10 * np.maximum(-s[:, 1], 0)
        s[:, 2] = np.maximum(s[:, 2], bord)
        return s * RAYON
    calotte = A.boule(1.0, 56, 28).sculpte(joues).sculpte(casquette)
    a.piece("calotte", calotte, CHOCOLAT, mat=PENCHE)
    a.couture("crane", "calotte", 14, 0.60, 0.97, fil=SABLE, large=0.006, haut=0.003, pas=0.011)

    # ----- les yeux, petits et vifs, posés un par un ; un seul sourcil, levé, sur l'œil gauche -----
    for nom, cote in (("oeil_g", 1), ("oeil_d", -1)):
        p, n = a.surface("tete", TETE, vers(0.64 * cote, -0.70, 0.14))
        a.oeil(nom, p + n * 0.002, n, 0.0125)
    leve = a.trace("tete", TETE, [vers(0.40 + 0.34 * u, -0.80 + 0.40 * u, 0.30 + 0.12 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 6)])
    a.broderie("sourcil", A.courbe(leve, 4), 0.0024, CHOCOLAT)

    # ----- le bec : un cône de granivore, court et épais, en feutrine ardoise -----
    bec = A.tour(A.profil([(0, 0), (0.019, 0.004), (0.016, 0.014), (0.008, 0.030), (0, 0.040)], 5), 28).etire(1.0, 0.92, 1.0)
    a.piece("bec", bec, ARDOISE, pos=PENCHE @ Vector((0, -0.054, -0.006)), rot=A.viser(vers(0, -1, -0.12)), poil=False)

    # ----- les ailes : deux galets rejetés en arrière, l'épaulette brique, le reste chocolat barré de caramel -----
    def galet(v):
        s = K.emousse(v, 0.85)
        pointe = K.lisse((v[:, 1] + 0.1) / 1.1)
        s[:, 2] = s[:, 2] * (1 - 0.40 * pointe) + 0.18 * pointe
        return s
    aile = A.boule(1.0, 40, 20).sculpte(galet).etire(0.017, 0.070, 0.048)
    K.bandes(aile, [(-0.046, BRIQUE), (-0.010, CHOCOLAT), (0.004, CARAMEL), (9, CHOCOLAT)], axe=1)
    a.piece("aile", aile, None, pos=(0.068, 0.050, 0.124), rot=(18, 0, 7), paire=True)
    a.couture("aile_bord", "aile", 10, 0.12, 0.88, "droit", fil=SABLE, paire=True, large=0.007, haut=0.0035, pas=0.012)

    # ----- la queue : une courte palette échancrée, dressée d'un coup sec -----
    def palette(v):
        s = K.emousse(v, 0.8)
        s[:, 0] *= 0.85 + 0.25 * K.lisse((v[:, 1] + 1) / 2)
        s[:, 1] -= 0.22 * np.exp(-(v[:, 0] / 0.35) ** 2) * K.lisse((v[:, 1] - 0.4) / 0.6)   # l'échancrure du bout
        return s
    queue = A.boule(1.0, 32, 16).sculpte(palette).etire(0.030, 0.066, 0.009)
    a.piece("queue", queue, CHOCOLAT, pos=(0, 0.118, 0.166), rot=(64, 0, 0))

    # ----- les pattes : de courtes tiges chair, plantées écartées, les doigts ouverts en éventail -----
    def doigt(degres, long):
        t = math.radians(degres)
        return A.boule(1.0, 16, 8).etire(0.0065, long, 0.0055).pose((0.75 * long * math.sin(t), -0.75 * long * math.cos(t), 0), (0, 0, degres))
    for nom, cote in (("patte_g", 1), ("patte_d", -1)):
        haut_ = Vector((0.034 * cote, 0.004, 0.052))
        bas_ = Vector((0.046 * cote, -0.004, 0.006))
        tige = A.tube(A.courbe([haut_, (haut_ + bas_) * 0.5 + Vector((0, -0.004, 0)), bas_], 4), 0.0055, 12)
        pied = (doigt(-34, 0.022) + doigt(0, 0.027) + doigt(34, 0.022) + doigt(180, 0.014)).pose(bas_, (0, 0, -18 * cote))
        a.piece(nom, tige + pied, CHAIR, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py moineau). Les mesures sont celles du modèle, avant a.taille.
# Les pattes pendent à la racine, pas au corps : posées, elles ne bougent pas quand la boule se penche au-dessus d'elles.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.004, 0.054)),          # les hanches, en haut des pattes : la boule bascule autour
    ("tete", "corps", (0.006, -0.025, 0.158)),         # le dessous de la tête, posée sans cou sur le jabot
    ("aile_G", "corps", (0.064, -0.010, 0.108)),       # l'épaule (la droite est son miroir)
    ("queue", "corps", (0.0, 0.090, 0.110)),           # le croupion, d'où la queue se dresse
    ("patte_g", "racine", (0.034, 0.004, 0.052)),      # le haut de chaque tige
    ("patte_d", "racine", (-0.034, 0.004, 0.052)),
]
PORTEURS = [("corps", "corps"), ("dos", "corps"), ("bavette", "corps"),
            ("tete", "tete"), ("barbiche", "tete"), ("calotte", "tete"), ("crane", "tete"), ("oeil", "tete"),
            ("sourcil", "tete"), ("bec", "tete"),
            ("aile", "aile", True), ("queue", "queue"), ("patte_g", "patte_g"), ("patte_d", "patte_d"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


PENCHE_MANGE = (42.0, 36.0)                   # mange : de combien le corps (autour des hanches) et la tête plongent


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _sec(t, centre, large=0.025):
    """Un geste d'oiseau : vite parti, tenu, vite revenu (une cloche aplatie au sommet)."""
    return borne(1.6 * cloche(t, centre, large))


def _ailes(p, leve, ouvre=0.0):
    """Les ailes se décollent du corps (leve, en degrés : le bout monte et s'écarte) et s'ouvrent (ouvre : elles
    pivotent vers l'extérieur autour de l'épaule)."""
    p.paire("aile", rot=(0.5 * leve, -0.4 * leve - 0.6 * ouvre, -0.5 * leve - 0.3 * ouvre))


def repos(t):
    """Le titi monte la garde : il respire vite en bombant le jabot, la tête claque d'un côté à l'autre par petits
    coups secs (il jauge, il penche la tête encore plus pour mieux vous toiser), la queue se redresse d'un coup sec
    deux fois, il cligne vite."""
    p = Pose()
    r = onde(t, 6)
    p.add("corps", ech=(1 + 0.015 * r, 1 + 0.010 * r, 1 + 0.012 * r))
    gauche = _sec(t, 0.18, 0.07)
    droite = _sec(t, 0.40, 0.07)
    jauge = _sec(t, 0.62, 0.06)
    p.add("tete", rot=(-4 * jauge, 14 * jauge - 4 * gauche, 22 * gauche - 26 * droite))
    for c in (0.80, 0.88):
        p.add("queue", rot=(-16 * cloche(t, c, 0.025), 0, 0))
    _ailes(p, 3 * cloche(t, 0.80, 0.06))
    p.ouvert = 1 - cloche(t, 0.08, 0.015) - cloche(t, 0.52, 0.015)
    return p


def avance(t):
    """Il sautille pieds joints, comme tous les moineaux : il se tasse, bondit, les pattes se replient sous lui en
    l'air, il se reçoit en se tassant ; la queue bat pour l'équilibre, les ailes se décollent un peu, la tête reste à
    l'affût."""
    p = Pose()
    air = math.sin(math.pi * borne((t - 0.15) / 0.65))
    tasse = cloche(t, 0.08, 0.08) + cloche(t, 0.88, 0.10)
    p.add("corps", pos=(0, 0, 0.040 * air - 0.006 * tasse), rot=(-6 * air + 6 * tasse, 0, 0),
          ech=(1 + 0.03 * tasse, 1, 1 - 0.04 * tasse))
    for c in ("patte_g", "patte_d"):
        p.add(c, pos=(0, 0.004 * air, 0.034 * air), rot=(-26 * air, 0, 0))
    p.add("tete", rot=(4 * air - 5 * tasse, 0, 0))
    p.add("queue", rot=(12 * air - 10 * tasse, 0, 0))
    _ailes(p, 12 * air)
    return p


def mange(t):
    """Il bascule en avant, pique le sol trois fois d'un coup de bec rapide (la queue se relève à chaque coup), puis se
    redresse d'un coup, mâche sa graine et regarde à droite, à gauche, au cas où."""
    p = Pose()
    bas = _plateau(t, 0.36, 0.22, 0.10)
    coups = max(0.0, onde(t, 9, 0.0)) ** 2 * _plateau(t, 0.36, 0.17, 0.05)
    p.add("corps", rot=(PENCHE_MANGE[0] * bas + 6 * coups, 0, 0))
    p.add("tete", rot=(PENCHE_MANGE[1] * bas + 14 * coups, 0, 18 * _sec(t, 0.78, 0.05) - 18 * _sec(t, 0.90, 0.04)))
    p.add("queue", rot=(-PENCHE_MANGE[0] * 0.6 * bas - 8 * coups, 0, 0))
    _ailes(p, 4 * bas)
    p.ouvert = 1 - cloche(t, 0.70, 0.02)
    return p


def joie(t):
    """Sa fête de petit dur : il se gonfle comme un coq, bat des ailes à toute vitesse, piaille le bec au ciel en
    deux salves, et saute deux fois sur place ; puis il retombe et se rengorge."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85)) if t < 0.85 else 0.0
    saut = abs(onde(borne(t / 0.85), 2)) * env
    piaille = abs(onde(t, 8)) * env
    p.add("corps", pos=(0, 0, 0.035 * saut), rot=(-10 * env, 0, 0), ech=(1 + 0.06 * env, 1 + 0.04 * env, 1 + 0.05 * env))
    for c in ("patte_g", "patte_d"):
        p.add(c, pos=(0, 0, 0.035 * saut), rot=(-18 * saut, 0, 0))
    p.add("tete", rot=(-18 * env - 6 * piaille, 6 * onde(t, 3) * env, 0))
    _ailes(p, 40 * env + 26 * onde(t, 9) * env, 10 * env)
    p.add("queue", rot=(-20 * env + 8 * onde(t, 6) * env, 0, 0))
    return p


def dort(t):
    """Il se met en boule, gonflé comme un pompon, accroupi sur ses pattes ; la tête rentrée dans les épaules, le bec
    enfoui dans la bavette, les yeux fermés ; la boule respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.012), ech=(1.08 + 0.015 * r, 1.04 + 0.01 * r, 1.0 + 0.02 * r))
    p.add("tete", pos=(0, 0.006, -0.016), rot=(22, 0, 6))
    p.add("queue", rot=(10, 0, 0))
    _ailes(p, -2)
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Moineau")
