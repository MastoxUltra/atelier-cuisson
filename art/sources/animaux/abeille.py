"""L'abeille en peluche : un boudin dodu à bandes cousues, des ailes de feutrine pâle, un sourire en coin.

    python abeille.py        fabrique la fiche art/apercus/animaux/abeille.png
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

SUIE = M.hexa("#2b2725")                      # le noir des rayures : un charbon, pour que le poil se lise encore
GIVRE = M.hexa("#d3e9fa")                     # le bleu ciel très pâle des ailes
DARD = Vector((0.0, 0.160, 0.103))            # le bout arrière du corps ; le corps file vers l'avant (-Y)
LONG, GROS = 0.240, 0.088                     # la longueur du corps et son plus gros rayon
BORDS = [0.0, 0.14, 0.30, 0.46, 0.62, 0.78, 1.0]    # les coutures entre les bandes, du dard (0) au cou (1)
TETE = Vector((0.0, -0.090, 0.112))


def rayon(t):
    """Le rayon du corps à la fraction t de sa longueur : un œuf, que chaque couture serre un peu."""
    r = GROS * math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2)) * (0.82 + 0.18 * float(K.lisse(t / 0.6)))
    return r * (1 - 0.06 * sum(math.exp(-((t - b) / 0.035) ** 2) for b in BORDS[1:-1]))


def vise(tour, haut):
    """Une direction vers l'avant, décalée de « tour » radians vers la gauche et de « haut » vers le ciel."""
    return Vector((math.sin(tour) * math.cos(haut), -math.cos(tour) * math.cos(haut), math.sin(haut)))


def construire():
    a = K.Animal("abeille")
    a.taille = 0.32
    a.tete = TETE

    # ----- le corps : six bandes tournées bout à bout, jaune et charbon, et la couture du dos -----
    for i in range(6):
        t0, t1 = BORDS[i], BORDS[i + 1]
        pas = np.linspace(0, 1, 10)
        if i == 0:
            pas = pas ** 2                              # plus de points près du bout, pour qu'il soit rond
        if i == 5:
            pas = 1 - (1 - pas) ** 2
        bande = A.tour([(rayon(t0 + (t1 - t0) * s), (t0 + (t1 - t0) * s) * LONG) for s in pas], 48)
        G.sillons(bande, [12], 0.004, 1.1)
        a.piece("bande%d" % i, bande, K.JAUNE if i % 2 == 0 else SUIE, pos=DARD, rot=(90, 0, 0))
        a.couture("dos%d" % i, "bande%d" % i, 12, 0.0, 0.6 if i == 5 else 1.0)

    # ----- le dard, un petit cône de feutrine -----
    dard = A.tour(A.profil([(0, 0), (0.017, 0.004), (0.010, 0.020), (0, 0.042)], 5), 16)
    a.piece("dard", dard, SUIE, pos=DARD + Vector((0, -0.008, 0)), rot=A.viser((0, 1, 0.15)), poil=False)

    # ----- la tête, ses joues, ses yeux -----
    a.piece("tete", A.boule(1.0, 56, 28).etire(0.068, 0.064, 0.064), K.JAUNE, pos=TETE)
    a.couture("crane", "tete", 14, 0.62, 0.99)
    a.rustine("joue", "tete", TETE, (0.72, -0.55, -0.32), 0.26, K.ROSE, 0.0025, 14, paire=True)
    regard = vise(0.80, 0.33)
    oeil = a.trace("tete", TETE, [regard], 0.0)[0]
    a.bouton("oeil", oeil + regard * 0.002, regard, 0.021, paire=True)

    # ----- le caractère : un sourire en coin, brodé par-dessus le poil -----
    sourire = [vise(-0.16 + 0.54 * s, -0.36 + 0.14 * s - 0.09 * math.sin(math.pi * s)) for s in np.linspace(0, 1, 9)]
    a.broderie("sourire", a.trace("tete", TETE, sourire, 0.0055), 0.0021, K.BRUN)

    # ----- les antennes : un fil de feutrine coudé vers l'avant, une boule au bout -----
    fil = A.courbe([TETE + Vector(p) for p in ((0.024, -0.012, 0.052), (0.032, -0.024, 0.098), (0.044, -0.052, 0.130), (0.050, -0.082, 0.138))], 6)
    antenne = A.tube(fil, 0.0042, 8) + A.boule(0.011, 16, 8).pose(tuple(fil[-1]))
    a.piece("antenne", antenne, SUIE, poil=False, paire=True)

    # ----- les ailes : deux gouttes de feutrine pâle, relevées en V, le plat tourné vers l'avant ;
    #       un point avant en fait le tour, en retrait du bord (au bord, il ferait des dents de scie) -----
    def goutte(v):
        s = v.copy()
        s[:, 0] *= 0.62 + 0.38 * v[:, 1]                # étroite à l'attache, large vers le bout
        s[:, 2] = np.sign(v[:, 2]) * np.abs(v[:, 2]) ** 0.6     # une plaque, pas une lentille
        return s
    aile = A.boule(1.0, 40, 20).sculpte(goutte).etire(0.058, 0.075, 0.004)    # les anneaux font le tour de l'aile
    attache, elan, plat = Vector((0.018, -0.010, 0.180)), Vector((0.599, 0.431, 0.674)), Vector((-0.25, -0.70, 0.67))
    a.piece("aile", aile, GIVRE, mat=A.cadre(attache + elan * 0.068, plat, elan), poil=False, paire=True)
    a.ourlet("aile", "aile", 0.75, fil=K.CIEL, paire=True)

    # ----- les pattes : trois petits fils coudés de chaque côté -----
    pattes = None
    for y in (-0.020, 0.030, 0.080):
        patte = A.tube(A.courbe([(0.045, y, 0.050), (0.086, y, 0.042), (0.100, y - 0.004, 0.008)], 5), 0.006, 8)
        pattes = patte if pattes is None else pattes + patte
    a.piece("pattes", pattes, SUIE, poil=False, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py abeille)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.03, 0.10)),            # le milieu du boudin : il tangue autour
    ("tete", "corps", (0, -0.06, 0.110)),            # la nuque, cachée dans la première bande
    ("antenne_G", "tete", (0.024, -0.102, 0.162)),
    ("aile_G", "corps", (0.018, -0.010, 0.178)),     # l'attache, sur le dos
    ("patte1_G", "corps", (0.050, -0.020, 0.050)),   # les hanches, de l'avant vers l'arrière
    ("patte2_G", "corps", (0.050, 0.030, 0.050)),
    ("patte3_G", "corps", (0.050, 0.080, 0.050)),
]


def pattes(points, cote):
    """Les trois pattes d'un côté sont une seule pièce, trois fils de même longueur mis bout à bout : un os par tiers."""
    tiers = np.arange(len(points)) * 3 // len(points)
    return {"patte%d%s" % (i + 1, cote): (tiers == i).astype(float) for i in range(3)}


PORTEURS = [("bande", "corps"), ("dos", "corps"), ("dard", "corps"), ("tete", "tete"), ("crane", "tete"), ("joue", "tete"),
            ("oeil", "tete"), ("sourire", "tete"), ("antenne", "antenne", True), ("aile", "aile", True),
            ("pattes", pattes, "patte1*")]


def doux(x):
    """De 0 à 1 en douceur, pour un geste qui part et s'arrête sans à-coup."""
    x = borne(x)
    return x * x * (3 - 2 * x)


def en_vol(p, air, bat, remous):
    """Ce que tous ses vols ont en commun : les ailes qui battent autour de l'horizontale, les pattes qui pendent
    en traînant un peu, les antennes couchées par le vent. air : 0 posée, 1 en plein vol."""
    p.paire("aile", rot=(0, (16 + 42 * bat) * air, 0))
    for i, traine in enumerate((8, 14, 20)):
        p.paire("patte%d" % (i + 1), rot=((traine + 5 * remous) * air, 20 * air, 0))
    p.paire("antenne", rot=((-14 + 4 * remous) * air, 0, 0))


def repos(t):
    """Posée, elle respire et tâte l'air de ses antennes ; elle se redresse sur ses pattes arrière pour se frotter
    les pattes avant sous le menton (elle mijote quelque chose), puis lance un regard en coin et fait vibrer ses ailes."""
    p = Pose()
    r = onde(t, 2)
    frotte = doux((t - 0.18) / 0.10) * (1 - doux((t - 0.52) / 0.10))
    va = onde(t, 15) * frotte
    coin = cloche(t, 0.78, 0.14)
    p.add("corps", ech=(1 + 0.012 * r, 1, 1 + 0.02 * r), rot=(-12 * frotte, 0, 0), pos=(0, 0, 0.010 * frotte))
    p.add("tete", rot=(7 * frotte - 3 * coin, 8 * coin, 16 * coin))
    p.add("patte1_G", rot=(0, -6 * frotte + 9 * va, -136 * frotte + 7 * va))     # les deux pieds se rejoignent devant le poitrail
    p.add("patte1_D", rot=(0, 6 * frotte + 9 * va, 136 * frotte + 7 * va))
    p.paire("patte2", rot=(0, 12 * frotte, 0))
    p.add("antenne_G", rot=(8 * onde(t, 3) + 4 * onde(t, 5), 0, 6 * onde(t, 2)))
    p.add("antenne_D", rot=(-8 * onde(t, 3) + 4 * onde(t, 4), 0, 6 * onde(t, 2)))
    p.paire("aile", rot=(0, 3 * r + 9 * cloche(t, 0.92, 0.05) * onde(t, 30), 0))
    p.ouvert = 1 - cloche(t, 0.30, 0.02) - cloche(t, 0.66, 0.02)
    return p


def avance(t):
    """Elle vole : le corps en l'air, penché vers l'avant, les ailes qui battent huit fois par cycle, les pattes qui pendent."""
    p = Pose()
    h = onde(t, 1)
    p.add("corps", pos=(0, 0, 0.18 + 0.014 * h), rot=(12 + 2.5 * onde(t, 1, 0.25), 3 * onde(t, 2), 2 * h))
    p.add("tete", rot=(-8 - 2 * onde(t, 1, 0.25), -2 * onde(t, 2), -2 * h))
    en_vol(p, 1.0, onde(t, 8), onde(t, 2, 0.3))
    return p


def mange(t):
    """Elle butine : la tête plongée vers le sol, l'arrière-train en l'air, elle lape à petits coups, les antennes
    tapotent, les ailes frémissent d'aise ; puis elle relève la tête pour savourer."""
    p = Pose()
    leve = cloche(t, 0.86, 0.13)
    bas = 1 - leve
    coups = max(0.0, onde(t, 5)) ** 2 * bas
    p.add("corps", rot=(15 * bas + 2 * coups, 0, 0), pos=(0, 0, 0.008 * bas))
    p.add("tete", rot=(9 * bas + 7 * coups - 6 * leve, 6 * leve, 8 * leve))
    p.add("antenne_G", rot=(20 * bas + 14 * coups, 0, 0))
    p.add("antenne_D", rot=(20 * bas + 14 * max(0.0, onde(t, 5, 0.5)) ** 2 * bas, 0, 0))
    p.paire("aile", rot=(0, (6 + 5 * onde(t, 15)) * bas, 0))
    p.paire("patte1", rot=(-15 * bas, -6 * bas, 0))          # les pattes restent d'aplomb sous le corps qui bascule
    p.paire("patte2", rot=(-15 * bas, 10 * bas, 0))
    p.paire("patte3", rot=(-15 * bas, 22 * bas, 0))
    return p


def joie(t):
    """Elle décolle, fait un tour complet sur elle-même en frétillant de l'arrière-train (sa danse), et se repose."""
    p = Pose()
    air = doux(t / 0.18) * (1 - doux((t - 0.70) / 0.20))
    tour = doux((t - 0.14) / 0.60)
    fretille = onde(t, 8) * air
    p.add("corps", pos=(0, 0, 0.14 * air + 0.012 * abs(fretille)), rot=(-6 * air, 9 * fretille, 360 * tour + 12 * fretille))
    p.add("tete", rot=(-10 * air, -6 * fretille, -8 * fretille))
    en_vol(p, air, onde(t, 16), fretille)
    return p


def dort(t):
    """Posée sur le ventre, les pattes écartées, les ailes couchées sur le dos l'une sur l'autre, la tête qui penche,
    une antenne tombée devant, l'autre couchée en arrière, les yeux fermés."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.014), ech=(1 + 0.012 * r, 1, 1 + 0.03 * r))
    p.add("tete", rot=(10 + 1.5 * r, 9, 5), pos=(0, 0, -0.004))
    p.add("antenne_G", rot=(-95 - 3 * r, 12, 0))             # celle du côté où la tête penche ne barre pas le visage
    p.add("antenne_D", rot=(30 + 3 * r, -22, 0))
    p.add("aile_G", rot=(-38, 32 + 2 * r, 26), pos=(0, 0, 0.008))
    p.add("aile_D", rot=(-36, -30 - 2 * r, -24), pos=(0, 0, 0.011))
    for i in (1, 2, 3):
        p.paire("patte%d" % i, rot=(0, -16, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
