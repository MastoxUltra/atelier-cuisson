"""Le chat en peluche : assis, gris ardoise, la queue dressée et l'air hautain.

    python chat.py        fabrique la fiche art/apercus/animaux/chat.png
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

ROBE = M.hexa("#aab3ce")                            # le poil fonce la teinte : ce gris-bleu clair sort ardoise
SUIE = M.hexa("#2b2e38")                            # les rayures de la queue et les traits brodés
TETE = Vector((0.0, -0.045, 0.420))
AVANT = Vector((0.0, -0.978, 0.208))                # le menton levé de 12 degrés : tout l'air hautain est là
HAUT = Vector((0.0, 0.208, 0.978))
COTE = Vector((1.0, 0.0, 0.0))


def vers(a, c, h):
    """Une direction dans le repère de la tête penchée : tant vers l'avant, tant de côté, tant vers le haut."""
    return AVANT * a + COTE * c + HAUT * h


def construire():
    a = K.Animal("chat")
    a.taille = 0.85
    a.tete = TETE + AVANT * 0.08

    # ----- le corps assis : une poire dont le bas part vers l'arrière, le poitrail bien droit -----
    def assis(v):
        s = v.copy()
        s[:, 1] = v[:, 1] * (1.05 - 0.05 * K.lisse(v[:, 2] / 0.22)) + 0.05 - 0.06 * K.lisse(v[:, 2] / 0.32)
        return s
    corps = A.tour(A.profil([(0, 0), (0.125, 0.006), (0.158, 0.07), (0.152, 0.16), (0.128, 0.25), (0.100, 0.32), (0, 0.36)], 6), 48).sculpte(assis)
    G.sillons(corps, [12], 0.005, 1.1)
    a.piece("corps", corps, ROBE)
    a.couture("dos", "corps", 12, 0.30, 0.90)

    # ----- les cuisses : deux galets cousus sur leur tranche, les pieds qui dépassent devant -----
    cuisse = A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.050, 0.105, 0.088)
    a.piece("cuisse", cuisse, ROBE, pos=(0.140, 0.045, 0.090), rot=(8, 0, -6), paire=True)
    for cote in (10, 30):
        a.couture("cuisse%d" % cote, "cuisse", cote, 0.15, 0.88, "droit", paire=True)
    a.piece("pied", A.boule(1.0, 28, 14).etire(0.038, 0.060, 0.028), ROBE, pos=(0.112, -0.098, 0.028), paire=True)

    # ----- les pattes avant, serrées l'une contre l'autre, qui remontent dans le poitrail -----
    patte = A.tour(A.profil([(0, 0), (0.040, 0.004), (0.044, 0.030), (0.037, 0.075), (0.036, 0.18), (0.032, 0.25), (0, 0.27)], 5), 28)
    patte.sculpte(lambda v: v + np.outer(v[:, 2], [0, 0.12, 0]))
    a.piece("patte", patte, ROBE, pos=(0.050, -0.142, 0.0), paire=True)
    a.ourlet("poignet", "patte", 0.42, paire=True)

    # ----- la tête, large des joues, le museau en feutrine crème -----
    def minois(v):
        s = K.bosse(v, (0.75, -0.30, -0.45), 0.10, 0.25)
        return K.bosse(s, (-0.75, -0.30, -0.45), 0.10, 0.25) * [0.135, 0.113, 0.108]
    tete = A.boule(1.0, 56, 28).sculpte(minois)
    G.sillons(tete, [14], 0.004, 1.1)
    a.piece("tete", tete, ROBE, pos=TETE, rot=(-12, 0, 0))
    a.couture("crane", "tete", 14, 0.60, 0.97)
    a.rustine("museau", "tete", TETE, vers(1, 0, -0.30), lambda th: 0.36 + 0.10 * math.cos(2 * th), K.CREME, 0.003, 22)
    truffe = A.boule(1.0, 20, 10).sculpte(lambda v: v * np.stack([0.78 + 0.22 * v[:, 2], np.ones(len(v)), np.ones(len(v))], axis=1))
    a.piece("truffe", truffe.etire(0.019, 0.010, 0.013), K.ROSE, pos=a.trace("tete", TETE, [vers(1, 0, -0.16)], 0.004)[0], rot=(-12, 0, 0), poil=False)

    # ----- les yeux, et au-dessus une paupière brodée qui descend vers le nez : il vous toise -----
    regard = vers(0.80, 0.50, 0.22).normalized()
    oeil = a.trace("tete", TETE, [regard], 0.0)[0]
    a.bouton("oeil", oeil, a.trace("tete", TETE, [regard], 1.0)[0] - oeil, 0.026, paire=True)
    a.broderie("sourcil", a.trace("tete", TETE, [vers(0.80, c, 0.40 + 0.22 * (c - 0.26)) for c in np.linspace(0.26, 0.76, 6)], 0.006), 0.0034, SUIE, paire=True)

    # ----- la bouche et les moustaches brodées, trois marques de tigré sur le front -----
    a.broderie("babine", a.trace("tete", TETE, [vers(1, 0, h) for h in (-0.20, -0.25, -0.30)], 0.004), 0.002, SUIE)
    a.broderie("bouche", a.trace("tete", TETE, [vers(1, x, -0.30 - 0.06 * math.sin(math.pi * abs(x) / 0.20) - 0.02 * abs(x) / 0.20)
                                                for x in np.linspace(-0.20, 0.20, 13)], 0.004), 0.002, SUIE)
    for k, (h0, h1) in enumerate(((-0.20, -0.08), (-0.30, -0.28), (-0.40, -0.50))):
        a.broderie("moustache%d" % k, a.trace("tete", TETE, [vers(math.cos(f), math.sin(f), h0 + (h1 - h0) * t)
                                                             for t, f in zip(np.linspace(0, 1, 7), np.linspace(0.40, 1.05, 7))], 0.004), 0.0018, K.BLANC, paire=True)
    for k, x in enumerate((-0.16, 0.0, 0.16)):
        a.broderie("front%d" % k, a.trace("tete", TETE, [vers(0.80 - 0.50 * t, x * (1 + 0.3 * t), 0.62 + 0.45 * t) for t in np.linspace(0, 1, 5)], 0.006), 0.0032, SUIE)

    # ----- les oreilles pointues, le dedans en feutrine rose -----
    def pointe(v):
        s = v.copy()
        s[:, 0] *= 1 - 0.9 * np.clip((v[:, 2] + 0.8) / 1.8, 0, 1)
        return s
    pose = dict(pos=TETE + vers(-0.01, 0.082, 0.120), rot=(-12, 16, 14), paire=True)
    a.piece("oreille", A.boule(1.0, 32, 16).sculpte(pointe).etire(0.064, 0.014, 0.078), ROBE, **pose)
    a.piece("dedans", A.boule(1.0, 24, 12).sculpte(pointe).etire(0.043, 0.007, 0.056).pose((0, -0.009, -0.006)), K.ROSE, poil=False, **pose)


    # ----- la queue dressée le long du dos, le bout en crosse, cerclée de trois rayures de feutrine -----
    chemin = A.courbe([(0.02, 0.13, 0.07), (0.04, 0.215, 0.085), (0.05, 0.245, 0.18), (0.058, 0.222, 0.30), (0.068, 0.194, 0.42),
                       (0.080, 0.177, 0.52), (0.090, 0.170, 0.595), (0.106, 0.168, 0.645), (0.136, 0.168, 0.666), (0.164, 0.170, 0.648),
                       (0.176, 0.171, 0.618)], 6)
    gros = lambda t: 0.029 - 0.009 * t
    a.piece("queue", A.tube(chemin, gros, 12), ROBE)
    rayures = None
    for i in (25, 33, 41):
        anneau = A.tore(gros(i / (len(chemin) - 1)) + 0.003, 0.008, 24, 8).pose(chemin[i], A.viser(chemin[i + 1] - chemin[i - 1]))
        rayures = anneau if rayures is None else rayures + anneau
    a.piece("rayures", rayures, SUIE, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py chat)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.05, 0.04)),              # il est assis dessus : tout le chat bascule autour
    ("ventre", "corps", (0, 0.05, 0.10)),              # la poire du corps seule : elle respire, elle se tasse
    ("tete", "corps", (0, -0.02, 0.33)),               # la nuque
    ("oreille_G", "tete", (0.078, -0.012, 0.468)),
    ("patte_G", "corps", (0.050, -0.110, 0.250)),      # l'épaule, dans le poitrail
    ("cuisse_G", "corps", (0.140, 0.070, 0.090)),
    ("queue", "corps", (0.04, 0.215, 0.085)),          # le pied de la queue, au bas du dos
    ("queue2", "queue", (0.066, 0.200, 0.40)),         # sa moitié haute, et la crosse
]


def _queue(points, cote):
    """La queue est souple : le bas suit « queue », le haut et la crosse suivent « queue2 »."""
    haut = K.lisse((points[:, 2] - 0.34) / 0.12)
    return {"queue": 1.0 - haut, "queue2": haut}


PORTEURS = [("cuisse", "cuisse", True), ("pied", "cuisse", True), ("patte", "patte", True), ("poignet", "patte", True),
            ("tete", "tete"), ("crane", "tete"), ("museau", "tete"), ("truffe", "tete"), ("oeil", "tete"), ("sourcil", "tete"),
            ("babine", "tete"), ("bouche", "tete"), ("moustache", "tete"), ("front", "tete"),
            ("oreille", "oreille", True), ("dedans", "oreille", True),
            ("queue", _queue, "queue"), ("rayures", _queue, "queue"), ("corps", "ventre"), ("dos", "ventre")]


def repos(t):
    """Assis, il toise le jardin, cligne lentement, puis se lèche une patte ; le bout de sa queue bat la mesure."""
    p = Pose()
    r = onde(t, 2)
    leche = cloche(t, 0.68, 0.16)
    coups = onde(t, 8) * leche
    regard = cloche(t, 0.22, 0.14)
    p.add("ventre", ech=(1 + 0.010 * r, 1 + 0.008 * r, 1 + 0.018 * r))
    p.add("tete", rot=(26 * leche + 4 * coups, -8 * leche, 16 * regard - 8 * leche), pos=(0, -0.010 * leche, -0.020 * leche))
    p.add("patte_G", rot=(-105 * leche, 0, -10 * leche), ech=(1, 1, 1 - 0.35 * leche))
    p.add("oreille_D", rot=(0, 0, -14 * cloche(t, 0.40, 0.03)))
    p.add("queue2", rot=(0, 16 * onde(t, 1), 12 * onde(t, 1, 0.25)))
    p.ouvert = 1 - cloche(t, 0.08, 0.035) - 0.6 * leche
    return p


def avance(t):
    """Un trot menu et silencieux : la tête reste haute et droite, la queue en chandelle se balance."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    p.add("corps", rot=(9, 3 * c, 4 * s), pos=(0, 0, 0.014 + 0.006 * abs(c)))
    p.add("patte_G", rot=(24 * s - 9, 0, 0), pos=(0, 0, 0.018 * max(0.0, c)), ech=(1, 1, 0.93))
    p.add("patte_D", rot=(-24 * s - 9, 0, 0), pos=(0, 0, 0.018 * max(0.0, -c)), ech=(1, 1, 0.93))
    p.add("cuisse_G", rot=(-16 * s, 0, 0), pos=(0, 0, 0.012 * max(0.0, -c)))
    p.add("cuisse_D", rot=(16 * s, 0, 0), pos=(0, 0, 0.012 * max(0.0, c)))
    p.add("tete", rot=(-9, -3 * c, -4 * s))
    p.add("queue", rot=(0, 5 * s, 0))
    p.add("queue2", rot=(0, 10 * s, 8 * c))
    return p


def mange(t):
    """Accroupi sur ses pattes avant, il mange du bout des dents ; il relève la tête et se pourlèche."""
    p = Pose()
    leve = cloche(t, 0.86, 0.12)
    bas = 1 - leve
    bouchee = max(0.0, onde(t, 5)) ** 2 * bas
    p.add("corps", rot=(24 * bas, 0, 0), pos=(0, 0, 0.004))
    p.paire("patte", rot=(-24 * bas, 0, 0), ech=(1, 1, 1 - 0.28 * bas))
    p.add("tete", rot=(40 * bas + 5 * bouchee, 0, 6 * leve), pos=(0, -0.01 * bas, -0.07 * bas))
    p.paire("oreille", rot=(-8 * bas, 0, 0))
    p.add("queue2", rot=(0, 12 * onde(t, 2), 0))
    p.ouvert = 1 - 0.5 * bouchee - 0.5 * leve
    return p


def joie(t):
    """Sa joie est retenue : il ferme les yeux de plaisir, penche la tête, pétrit des pattes, et sa queue frémit."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    petrit = onde(t, 5) * env
    p.add("corps", rot=(-4 * env, 0, 0))
    p.add("ventre", ech=(1, 1, 1 + 0.04 * env))
    p.add("tete", rot=(-10 * env, 14 * onde(t, 1.5) * env, 0))
    p.add("patte_G", pos=(0, 0, 0.022 * max(0.0, petrit)))
    p.add("patte_D", pos=(0, 0, 0.022 * max(0.0, -petrit)))
    p.add("queue", rot=(-6 * env, 0, 0))
    p.add("queue2", rot=(0, 10 * onde(t, 9) * env, 10 * onde(t, 9, 0.25) * env))
    p.paire("oreille", rot=(10 * env, 0, 0))
    p.ouvert = 1 - 0.85 * env
    return p


def dort(t):
    """Couché en rond : le corps tassé, la tête posée sur ses pattes allongées, la queue ramenée devant lui, les yeux fermés."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("ventre", ech=(1.14 + 0.012 * r, 1.06, 0.74 + 0.025 * r))
    p.add("tete", pos=(0, -0.050, -0.150 + 0.004 * r), rot=(30, 10, 18))
    p.paire("patte", rot=(-70, 0, 0), pos=(0, 0, -0.170))
    p.paire("oreille", rot=(0, 12, 0))
    p.add("queue", rot=(0, 78, -72))
    p.add("queue2", rot=(0, 0, -45))
    return p


ANIMATIONS = {"repos": (150, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (54, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
