"""Le hibou en peluche : perché debout, l'air sévère, deux grands disques crème autour des yeux.

    python hibou.py        fabrique la fiche art/apercus/animaux/hibou.png
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

CORPS = Vector((0.0, 0.01, 0.012))            # le pied du corps (une pièce tournée, debout)
VENTRE = Vector((0.0, 0.01, 0.170))           # son milieu, d'où l'on vise le ventre
TETE = Vector((0.0, -0.005, 0.385))
RAYONS = (0.150, 0.126, 0.118)                # la tête : large, un peu aplatie


def vise(tour, haut):
    """Une direction vers l'avant, décalée de « tour » radians vers la gauche et de « haut » vers le ciel."""
    return Vector((math.sin(tour) * math.cos(haut), -math.cos(tour) * math.cos(haut), math.sin(haut)))


def construire():
    a = K.Animal("hibou")
    a.taille = 0.62
    a.tete = TETE

    # ----- le corps : un œuf debout, large en bas -----
    corps = A.tour(A.profil([(0, 0), (0.088, 0.004), (0.130, 0.07), (0.138, 0.15), (0.118, 0.24), (0.07, 0.31), (0, 0.33)], 6), 48)
    corps.etire(1.0, 0.92, 1.0)
    G.sillons(corps, [12], 0.005, 1.1)                  # la couture du dos creuse un peu le tissu
    a.piece("corps", corps, K.CARAMEL, pos=CORPS)
    a.couture("dos", "corps", 12, 0.40, 0.92, fil=K.CHOCOLAT)
    a.rustine("ventre", "corps", VENTRE, (0, -0.95, -0.08), lambda th: 0.55 - 0.13 * math.cos(2 * th), K.CREME, feston=36)
    # le plumage du ventre : cinq petits « v » brodés
    for i, (tour, haut) in enumerate([(-0.17, 0.27), (0.17, 0.27), (0.0, 0.04), (-0.17, -0.19), (0.17, -0.19)]):
        plume = a.trace("corps", VENTRE, [vise(tour - 0.075, haut + 0.07), vise(tour, haut), vise(tour + 0.075, haut + 0.07)], 0.0048)
        a.broderie("plume%d" % i, plume, 0.0019, K.CHOCOLAT)

    # ----- la tête, large, posée sans cou -----
    a.piece("tete", A.boule(1.0, 56, 28).etire(*RAYONS), K.CARAMEL, pos=TETE)
    a.couture("crane", "tete", 14, 0.50, 0.99, fil=K.CHOCOLAT)
    a.couture("front", "tete", 42, 0.74, 0.99, fil=K.CHOCOLAT)

    # ----- les disques crème autour des yeux, et les yeux au milieu -----
    regard = Vector((0.50, -0.85, 0.10)).normalized()
    a.rustine("disque", "tete", TETE, regard, 0.47, K.CREME, 0.003, 22, paire=True)
    oeil = a.trace("tete", TETE, [regard], 0.003)[0]
    dehors = Vector([(oeil[i] - TETE[i]) / RAYONS[i] ** 2 for i in range(3)]).normalized()
    a.bouton("oeil", oeil, dehors, 0.031, paire=True)

    # ----- le bec en feutrine moutarde, pointé vers le bas -----
    bec = A.tour(A.profil([(0, 0), (0.024, 0.008), (0.017, 0.030), (0, 0.058)], 5), 24)
    a.piece("bec", bec, K.MOUTARDE, pos=TETE + Vector((0, -0.114, -0.010)), rot=A.viser((0, -0.50, -0.87)), poil=False)

    # ----- les aigrettes : deux boudins chocolat qui naissent au-dessus du bec, froncent le sourcil
    #       en travers des disques, puis quittent la tête en pointe -----
    def sur_tete(x, z):
        return TETE + Vector((x, -RAYONS[1] * math.sqrt(1 - (x / RAYONS[0]) ** 2 - (z / RAYONS[2]) ** 2), z))
    chemin = A.courbe([sur_tete(0.008, 0.025), sur_tete(0.034, 0.058), sur_tete(0.064, 0.088),
                       TETE + Vector((0.094, -0.058, 0.124)), TETE + Vector((0.114, -0.044, 0.168))], 6)
    aigrette = A.tube(chemin, lambda t: float(np.interp(t, [0, 0.25, 0.5, 0.75, 1], [0.008, 0.012, 0.022, 0.018, 0.003])), 12)
    a.piece("aigrette", aigrette, K.CHOCOLAT, paire=True)

    # ----- les ailes le long du corps : deux galets chocolat, cousus sur leur tranche -----
    def plume_d_aile(v):
        s = K.emousse(v, 0.85)
        bas = K.lisse((0.2 - v[:, 2]) / 1.2)            # 0 à l'épaule, 1 à la pointe
        s[:, 1] = s[:, 1] * (1 - 0.55 * bas) + 0.30 * bas   # la pointe s'affine et part vers l'arrière
        s[:, 0] -= 0.9 * v[:, 2] ** 2                   # l'aile épouse le rond du corps
        return s
    aile = A.boule(1.0, 40, 20).sculpte(plume_d_aile).etire(0.024, 0.078, 0.108)
    a.piece("aile", aile, K.CHOCOLAT, pos=(0.134, 0.015, 0.168), paire=True)
    for cote in (10, 30):
        a.couture("aile%d" % cote, "aile", cote, 0.12, 0.88, "droit", fil=K.MOUTARDE, paire=True)

    # ----- les pattes : trois doigts de feutrine qui dépassent sous le ventre -----
    def doigt(degres):
        t = math.radians(degres)
        return A.boule(1.0, 16, 8).etire(0.013, 0.038, 0.011).pose((0.030 * math.sin(t), -0.030 * math.cos(t), 0), (0, 0, degres))
    a.piece("patte", doigt(-28) + doigt(0) + doigt(28), K.MOUTARDE, pos=(0.055, -0.072, 0.011), poil=False, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py hibou)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.01, 0.03)),              # le pied de l'œuf : il bascule autour, comme un culbuto
    ("tronc", "corps", (0, 0.01, 0.10)),               # l'œuf seul : il respire, il se gonfle
    ("tete", "corps", (0, 0.0, 0.30)),                 # posée sans cou : elle pivote là, très loin de chaque côté
    ("aile_G", "corps", (0.125, 0.015, 0.255)),        # l'épaule
    ("patte_G", "racine", (0.055, -0.045, 0.02)),      # les pattes restent au sol quand le corps bascule
]
PORTEURS = [("aile", "aile", True), ("aigrette", "tete"), ("patte", "patte", True), ("tete", "tete"), ("crane", "tete"),
            ("front", "tete"), ("disque", "tete"), ("oeil", "tete"), ("bec", "tete"),
            ("corps", "tronc"), ("dos", "tronc"), ("ventre", "tronc"), ("plume", "tronc")]


def repos(t):
    """Immobile, il tourne la tête très loin à gauche, puis très loin à droite, la penche, et cligne lentement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.24, 0.17), cloche(t, 0.70, 0.17)
    p.add("tronc", ech=(1 + 0.012 * r, 1 + 0.012 * r, 1 + 0.015 * r))
    p.add("tete", rot=(0, 14 * cloche(t, 0.47, 0.06), 88 * g - 88 * d))
    p.paire("aile", rot=(0, -6 * cloche(t, 0.47, 0.05), 0))
    p.ouvert = 1 - cloche(t, 0.47, 0.05) - cloche(t, 0.93, 0.04)
    return p


def avance(t):
    """Il marche en se dandinant comme un culbuto, les ailes un peu écartées pour tenir debout ; la tête reste droite."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    saut = 0.012 * abs(s)
    p.add("corps", rot=(4, 10 * c, 5 * s), pos=(0, 0, saut))
    p.add("tete", rot=(-4, -10 * c, -5 * s))
    p.add("patte_G", rot=(18 * s, 0, 0), pos=(0, 0, 0.022 * max(0.0, -c)))
    p.add("patte_D", rot=(-18 * s, 0, 0), pos=(0, 0, 0.022 * max(0.0, c)))
    p.paire("aile", rot=(0, -10 - 6 * abs(c), 0))
    return p


def mange(t):
    """Trois coups de bec au sol : tout le corps plonge en avant, les ailes en balancier ; puis il se redresse et avale."""
    p = Pose()
    leve = cloche(t, 0.88, 0.11)
    coup = max(0.0, onde(t, 3)) ** 1.5 * (1 - leve)
    p.add("corps", rot=(18 * (1 - leve) + 46 * coup, 0, 0), pos=(0, 0, 0.035 * coup))        # il roule sur son ventre, comme un culbuto
    p.add("tete", rot=(18 * coup - 12 * leve, 0, 8 * leve))
    p.paire("aile", rot=(0, -8 - 22 * coup, 0))
    p.ouvert = 1 - 0.7 * coup
    return p


def joie(t):
    """Il se gonfle, bat des ailes à grands coups et sautille en hochant la tête."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    bat = onde(t, 6) * env
    saut = 0.045 * abs(onde(t, 3)) * env
    p.add("corps", pos=(0, 0, saut), rot=(-6 * env, 0, 5 * onde(t, 3) * env))
    p.paire("patte", pos=(0, 0, saut), rot=(12 * env, 0, 0))
    p.add("tronc", ech=(1 + 0.10 * env, 1 + 0.10 * env, 1 + 0.03 * env))
    p.add("tete", rot=(10 * onde(t, 6) * env, 0, 0))
    p.paire("aile", rot=(0, -50 * env - 28 * bat, 0))
    return p


def dort(t):
    """Debout, la tête rentrée dans les épaules, le plumage gonflé, les yeux fermés ; il respire à peine."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("tronc", ech=(1.08 + 0.012 * r, 1.08 + 0.012 * r, 0.97 + 0.015 * r))
    p.add("tete", pos=(0, 0.004, -0.045 + 0.003 * r), rot=(6, 0, 0))
    p.paire("aile", rot=(0, 3, 0), pos=(0.008, 0, -0.01))
    return p


ANIMATIONS = {"repos": (150, repos, True), "avance": (24, avance, True), "mange": (72, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
