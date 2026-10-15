"""La souris en peluche : tapie, le nez en l'air, de grandes oreilles et une chute de tissu rayé sur le flanc.

    python souris.py        fabrique la fiche art/apercus/animaux/souris.png
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

CORPS = Vector((0.0, 0.040, 0.068))
TETE = Vector((0.0, -0.062, 0.100))
LEVE = A.repere(TETE, (-14, 0, 0))            # la tête, le nez un peu levé : elle flaire


def construire():
    a = K.Animal("souris")
    a.taille = 0.34
    a.tete = TETE

    def surface(piece, centre, direction):
        """Le point de la surface visé depuis « centre », et la direction dans laquelle il regarde."""
        p0 = a.trace(piece, centre, [direction], 0.0)[0]
        p1 = a.trace(piece, centre, [direction], 0.01)[0]
        return p0, (p1 - p0).normalized()

    # ----- le corps : une poire couchée, la croupe large, deux cuisses rondes -----
    def coque(v):
        v = K.bosse(v, (0.75, 0.45, -0.35), 0.14, 0.18)
        v = K.bosse(v, (-0.75, 0.45, -0.35), 0.14, 0.18)
        arriere = K.lisse((v[:, 1] + 0.5) / 1.4)        # 0 au poitrail, 1 à la croupe
        s = v * [0.064, 0.088, 0.062]
        s[:, 0] *= 0.74 + 0.30 * arriere
        s[:, 2] *= np.where(v[:, 2] > 0, 0.80 + 0.24 * arriere, 1.0)    # le dos s'abaisse vers l'avant, le ventre reste au sol
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    G.sillons(corps, [14], 0.004, 1.1)                  # la couture du dos creuse un peu le tissu
    a.piece("corps", corps, K.GRIS, pos=CORPS)
    a.couture("dos", "corps", 14, 0.45, 0.99, fil=K.BLANC)
    # la pièce du flanc, taillée dans une chute de tissu rayé
    a.rustine("chute", "corps", CORPS, (0.80, 0.30, 0.52), 0.47, K.JAUNE, feston=18, fil=K.BLANC, motif=("rayures", K.BLANC))

    # ----- la tête : une goutte dont la pointe fait le museau -----
    def museau(v):
        avant = K.lisse(-v[:, 1])                       # 0 derrière, 1 au bout du nez
        s = v * [0.052, 0.048, 0.048]
        s[:, 1] -= 0.040 * avant ** 1.5
        s[:, 0] *= 1 - 0.50 * avant
        s[:, 2] = s[:, 2] * (1 - 0.50 * avant) + 0.010 * avant
        return s
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(museau), K.GRIS, mat=LEVE)
    a.couture("crane", "tete", 14, 0.55, 0.98, fil=K.BLANC)
    a.piece("nez", A.boule(0.011, 20, 10), K.ROSE, pos=LEVE @ Vector((0, -0.087, 0.010)), poil=False)
    oeil, vers = surface("tete", TETE, (0.70, -0.44, 0.56))
    a.bouton("oeil", oeil + vers * 0.003, vers, 0.018, paire=True)    # un peu décollé : le poil est long pour une si petite bête

    # ----- les moustaches : trois fils raides de chaque côté du museau, sous le regard -----
    depart = LEVE @ Vector((0.008, -0.074, 0.000))
    for i, leve in enumerate((0.012, -0.005, -0.021)):
        bout = depart + Vector((0.052, -0.012, leve))
        milieu = depart.lerp(bout, 0.5) + Vector((0, -0.003, 0.003))
        a.broderie("moustache%d" % i, A.courbe([depart, milieu, bout], 5), 0.0015, K.BRUN, paire=True)

    # ----- les grandes oreilles rondes, au dedans de feutrine rose tenu par un point avant -----
    pavillon = A.repere(TETE + Vector((0.052, 0.014, 0.060)), (-12, 24, 25))
    oreille = A.boule(1.0, 40, 20).etire(0.044, 0.044, 0.011).pose(rot=(90, 0, 0))    # les anneaux font le tour du pavillon
    a.piece("oreille", oreille, K.GRIS, mat=pavillon, paire=True)
    a.rustine("dedans", "oreille", pavillon.translation, pavillon.to_3x3() @ Vector((0, -1, 0)), 1.30, K.ROSE, 0.002, 0, paire=True)
    a.ourlet("dedans", "oreille", 0.80, fil=K.BLANC, paire=True)

    # ----- la longue queue de feutrine, qui fait le tour par la gauche et relève le bout -----
    queue = A.courbe([(0, 0.115, 0.045), (0.005, 0.150, 0.022), (0.030, 0.185, 0.012), (0.080, 0.200, 0.011), (0.130, 0.175, 0.011),
                      (0.155, 0.120, 0.012), (0.150, 0.065, 0.016), (0.128, 0.030, 0.030), (0.118, 0.018, 0.052)], 8)
    a.piece("queue", A.tube(queue, lambda t: 0.0075 - 0.0045 * t, 10), K.ROSE, poil=False)

    # ----- les pattes : quatre petits galets roses qui dépassent -----
    a.piece("pied", A.boule(1.0, 20, 10).etire(0.015, 0.032, 0.010), K.ROSE, pos=(0.050, 0.008, 0.011), rot=(0, 0, 16), poil=False, paire=True)
    a.piece("main", A.boule(1.0, 20, 10).etire(0.011, 0.022, 0.009), K.ROSE, pos=(0.022, -0.040, 0.010), rot=(0, 0, 10), poil=False, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py souris)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.07, 0.03)),             # les hanches : elle se dresse autour
    ("tete", "corps", (0, -0.035, 0.085)),            # la nuque
    ("oreille_G", "tete", (0.040, -0.050, 0.125)),    # le pied du pavillon
    ("main_G", "corps", (0.022, -0.040, 0.025)),
    ("pied_G", "racine", (0.050, 0.008, 0.025)),      # tenus par le sol : ils ne suivent pas le corps qui se dresse
    ("queue1", "racine", (0, 0.115, 0.04)),           # la queue traîne par terre, en trois os à la suite
    ("queue2", "queue1", (0.070, 0.197, 0.011)),
    ("queue3", "queue2", (0.155, 0.120, 0.012)),
]

# le chemin de la queue, tel qu'il est tracé dans construire()
TRACE = np.array([(0, 0.115, 0.045), (0.005, 0.150, 0.022), (0.030, 0.185, 0.012), (0.080, 0.200, 0.011), (0.130, 0.175, 0.011),
                  (0.155, 0.120, 0.012), (0.150, 0.065, 0.016), (0.128, 0.030, 0.030), (0.118, 0.018, 0.052)])


def fouet(points, cote):
    """La queue est souple : chaque point suit les os selon sa place le long du chemin, de la croupe (0) au bout (1)."""
    pas = np.linalg.norm(np.diff(TRACE, axis=0), axis=1)
    long = np.concatenate([[0.0], np.cumsum(pas)]) / pas.sum()
    place = np.linspace(0.0, 1.0, 97)
    chemin = np.stack([np.interp(place, long, TRACE[:, i]) for i in range(3)], axis=1)
    ici = place[np.argmin(np.linalg.norm(points[:, None, :] - chemin[None, :, :], axis=2), axis=1)]
    milieu, bout = K.lisse((ici - 0.22) / 0.22), K.lisse((ici - 0.56) / 0.22)
    return {"queue1": 1.0 - milieu, "queue2": milieu - bout, "queue3": bout}


PORTEURS = [("corps", "corps"), ("dos", "corps"), ("chute", "corps"), ("tete", "tete"), ("crane", "tete"), ("nez", "tete"),
            ("oeil", "tete"), ("moustache", "tete"), ("oreille", "oreille", True), ("dedans", "oreille", True),
            ("queue", fouet, "queue1"), ("pied", "pied", True), ("main", "main", True)]


def palier(t, centre, large):
    """Comme cloche, mais on y arrive d'un coup et on tient la pose : le geste vif d'un rongeur."""
    return borne(2.5 * cloche(t, centre, large))


def repos(t):
    """Tapie, le nez qui frétille ; d'un coup elle se dresse sur son derrière pour flairer l'air, regarde autour,
    retombe, tend une oreille puis l'autre."""
    p = Pose()
    r = onde(t, 3)                                       # un petit cœur qui bat vite
    dresse = palier(t, 0.40, 0.17)
    guet = palier(t, 0.80, 0.06)                         # un coup d'œil de côté, une fois retombée
    nez = onde(t, 18) * (0.5 + 0.5 * dresse)
    p.add("corps", rot=(-42 * dresse, 0, 0), ech=(1 + 0.012 * r, 1, 1 + 0.020 * r))
    p.add("tete", rot=(30 * dresse + 2.5 * nez, 0, 16 * onde(t, 3) * dresse + 26 * guet))
    p.paire("main", rot=(30 * dresse, 0, 0), pos=(0, -0.004 * dresse, 0.004 * dresse))
    p.paire("pied", pos=(0, 0.034 * dresse, 0))          # elle ramène ses pieds sous elle
    p.add("oreille_G", rot=(0, 0, 22 * cloche(t, 0.72, 0.05) - 10 * dresse))
    p.add("oreille_D", rot=(0, 0, -22 * cloche(t, 0.90, 0.05) + 10 * dresse))
    p.add("queue2", rot=(0, 0, 5 * onde(t, 1)))
    p.add("queue3", rot=(0, 0, 9 * onde(t, 1, -0.2) - 14 * dresse))
    p.ouvert = 1 - cloche(t, 0.08, 0.02) - cloche(t, 0.66, 0.02)
    return p


def avance(t):
    """Elle file ventre à terre : deux foulées menues par boucle, le nez tendu, les oreilles couchées,
    le corps qui s'allonge par à-coups, la queue décollée du sol qui serpente derrière elle."""
    p = Pose()
    c, s = math.cos(2 * math.tau * t), math.sin(2 * math.tau * t)
    elan = onde(t, 1)                                    # l'à-coup : elle s'étire, puis se ramasse
    p.add("corps", pos=(0, -0.005 * elan, 0.003 + 0.004 * abs(s)), rot=(3 + 2 * elan, 0, 3 * s),
          ech=(1, 1 + 0.05 * elan, 1 - 0.04 * elan))
    p.add("tete", rot=(11 - 5 * elan + 2 * onde(t, 4), 0, -3 * s), pos=(0, -0.004 * elan, 0))
    p.paire("oreille", rot=(-30 + 8 * elan, 0, 0))
    for nom, sens in (("pied_G", 1), ("main_D", 1), ("pied_D", -1), ("main_G", -1)):
        p.add(nom, pos=(0, 0.016 * sens * s, 0.010 * max(0.0, -sens * c)), rot=(-14 * max(0.0, -sens * c), 0, 0))
    p.add("queue1", rot=(9 + 3 * elan, 0, 26 + 6 * onde(t, 1, 0.10)))
    p.add("queue2", rot=(0, 0, 48 + 12 * onde(t, 1, -0.15)))
    p.add("queue3", rot=(0, 0, 52 + 18 * onde(t, 1, -0.40)))
    return p


def mange(t):
    """Le nez au sol, elle trouve une miette ; assise sur son derrière, elle la ronge à toute vitesse,
    se fige pour écouter, reprend, puis retombe sur ses pattes."""
    p = Pose()
    cherche = cloche(t, 0.10, 0.10)
    assise = palier(t, 0.58, 0.36)
    ecoute = palier(t, 0.60, 0.05)
    ronge = onde(t, 24) * assise * (1 - ecoute)
    p.add("corps", rot=(4 * cherche - 34 * assise, 0, 0))
    p.add("tete", rot=(32 * cherche + 58 * assise - 30 * ecoute + 2.5 * ronge, 0, 20 * ecoute))
    p.paire("main", rot=(40 * assise + 4 * ronge, 0, 0), pos=(0, -0.012 * assise, 0.006 * assise + 0.0015 * ronge))
    p.paire("pied", pos=(0, 0.030 * assise, 0))
    p.add("oreille_G", rot=(0, 0, 20 * ecoute))
    p.add("oreille_D", rot=(0, 0, -20 * ecoute))
    p.add("queue3", rot=(0, 0, 8 * onde(t, 2) * (1 - ecoute)))
    p.ouvert = 1 - cloche(t, 0.30, 0.02)
    return p


def joie(t):
    """Deux bonds de cabri, les quatre pattes décollées : le corps se tord en l'air d'un côté puis de l'autre,
    les oreilles battent, la queue claque."""
    p = Pose()
    u = borne(t / 0.9)
    env = math.sin(math.pi * u)
    saut = abs(math.sin(2 * math.pi * u)) * env ** 0.5
    tord = onde(u, 1) * env
    haut = 0.085 * saut
    p.add("corps", pos=(0, 0, haut), rot=(-16 * saut, 0, 12 * tord), ech=(1, 1 + 0.06 * saut, 1 - 0.03 * saut))
    p.add("tete", rot=(12 * saut, 8 * tord, 16 * tord))
    p.paire("oreille", rot=(-14 * saut, 22 * onde(u, 4) * env, 0))
    p.paire("main", rot=(-25 * saut, 0, 0), pos=(0, -0.008 * saut, 0))
    p.paire("pied", pos=(0, 0.014 * saut, haut * 0.8), rot=(30 * saut, 0, 0))
    p.add("queue1", pos=(0, 0, haut * 0.8), rot=(12 * saut, 0, 14 * onde(u, 2) * env))
    p.add("queue2", rot=(0, 0, 22 * onde(u, 2, -0.15) * env))
    p.add("queue3", rot=(0, 0, 30 * onde(u, 2, -0.35) * env))
    return p


def dort(t):
    """Roulée en boule : le nez rentré contre le flanc, les oreilles rabattues, la queue ramenée tout autour d'elle."""
    p = Pose()
    r = onde(t, 2)
    p.ouvert = 0.0
    p.add("corps", ech=(1.08 + 0.012 * r, 0.95, 0.96 + 0.030 * r))
    p.add("tete", rot=(38, 0, 34), pos=(0, 0.012, -0.022))
    p.paire("oreille", rot=(-38, 0, 0))
    p.paire("main", pos=(0, 0.012, 0.008), ech=(0.7, 0.7, 0.7))
    p.paire("pied", pos=(-0.006, 0.006, 0.004), ech=(0.8, 0.8, 0.8))
    p.add("queue1", rot=(0, 0, -6), ech=(0.80, 0.80, 1.0))
    p.add("queue3", rot=(0, 0, -18 + 2 * r))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (16, avance, True), "mange": (72, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
