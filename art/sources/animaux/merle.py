"""(Quatrième dessin, 15/10 au soir, d'après le contrôleur : le troisième faisait poussin à lunettes ; le corps
plus long, la tête plus petite, un cerne fin au lieu d'un disque, le bec en vrai cône, plus de rond cousu au flanc.
Le troisième, l'auteur, 15/10 : « ça fait pas trop corbeau ? » ; le deuxième : merle_ancien2.py.)
Le merle en peluche, deuxième dessin : l'écouteur de pelouse. Un long fuseau noir suie penché en avant, le poitrail
vers l'herbe, la longue queue dans l'axe, à peine relevée ; une patte avancée, arrêté net en pleine
course. La tête basse, couchée sur le côté : il tend l'œil gauche vers le sol, il écoute le ver. Le bec orange vif
pointé vers la terre, un fin cerne orange autour de l'œil.

    python merle.py        fabrique la fiche art/apercus/animaux/merle.png
    (le premier dessin, jamais gardé : merle_ancien.py)
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

SUIE = M.hexa("#302d35")                      # un noir de suie, pas un noir pur : le relief doit se lire
PLUME = M.hexa("#3d3a4a")                     # les ailes et la queue, un rien plus bleutées
FUMEE = M.hexa("#8c8796")                     # le fil des coutures
ORANGE = M.hexa("#ff8a1a")                    # l'accent : le bec et le cerne de l'œil
PATTE = M.hexa("#4b3a30")                     # les pattes, en feutrine brun sombre
CORPS = Vector((0.0, 0.020, 0.128))
TETE = Vector((0.004, -0.096, 0.158))
RAYON = 0.034                                  # une petite tête : la grosse tête faisait poussin
PENCHE = A.repere(CORPS, (5, 0, 0))          # le corps : le poitrail vers le sol, le croupion en l'air
ECOUTE = A.repere(TETE, (2, 30, -14))        # la tête : le bec vers la terre, couchée sur le côté pour tendre l'œil gauche


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du jardin."""
    return ECOUTE.to_3x3() @ Vector((x, y, z))


def construire():
    a = K.Animal("merle")
    a.taille = 0.31
    a.tete = ECOUTE @ Vector((0.010, -0.032, -0.004))

    # ----- le corps : un long fuseau, le poitrail plein, des épaules, et qui s'effile vers la queue -----
    def coque(v):
        v = K.bosse(v, (0, -0.70, -0.45), 0.12, 0.30)       # le poitrail
        v = K.bosse(v, (0, -0.30, 0.90), 0.05, 0.30)        # les épaules
        arriere = K.lisse(v[:, 1])
        s = v * [0.054, 0.108, 0.058]                # un fuseau, pas une boule
        s[:, 0] *= 1 - 0.50 * arriere
        s[:, 2] *= 1 - 0.45 * arriere
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    G.sillons(corps, [14], 0.004, 1.1)
    a.piece("corps", corps, SUIE, mat=PENCHE)
    a.couture("dos", "corps", 14, 0.55, 0.95, fil=FUMEE)

    # ----- la tête, basse et emmanchée sur le bout du corps, le front un peu bombé -----
    tete = A.boule(1.0, 56, 28).sculpte(lambda v: K.bosse(v, (0, -0.6, 0.6), 0.08, 0.3)).etire(RAYON, RAYON * 1.08, RAYON * 0.96)
    a.piece("tete", tete, SUIE, mat=ECOUTE)
    a.couture("crane", "tete", 14, 0.50, 0.97, fil=FUMEE, large=0.007, haut=0.0035, pas=0.012)

    # ----- les yeux : un œil vivant dans un fin cerne orange, posés un par un (la tête est couchée) -----
    for nom, cote in (("g", 1), ("d", -1)):
        regard = vers(0.86 * cote, -0.42, 0.20)
        a.rustine("cerne_" + nom, "tete", TETE, regard, 0.30, ORANGE, 0.003, 0)     # un fin cerne, pas des lunettes
        p, n = a.surface("tete", TETE, regard)
        a.oeil("oeil_" + nom, p + n * 0.0035, n, 0.0100)

    # ----- le bec : un cône rond et fin de feutrine orange vif, pointé vers la terre -----
    bec = A.tour(A.profil([(0, 0), (0.0095, 0.004), (0.0085, 0.012), (0.0040, 0.027), (0, 0.035)], 5), 28)
    a.piece("bec", bec, ORANGE, pos=ECOUTE @ Vector((0, -0.030, -0.005)), rot=A.viser(vers(0, -1, -0.10)), poil=False)

    # ----- les ailes : deux longs galets serrés au corps, la pointe qui croise sur la queue -----
    def galet(v):
        s = K.emousse(v, 0.85)
        pointe = K.lisse((v[:, 1] + 0.1) / 1.1)
        s[:, 0] *= 1 - 0.35 * pointe
        s[:, 2] *= 1 - 0.35 * pointe
        return s
    aile = A.boule(1.0, 40, 20).sculpte(galet).etire(0.017, 0.094, 0.030)       # épaisse et à moitié dans le corps : pas une moufle posée
    a.piece("aile", aile, PLUME, mat=PENCHE @ A.repere((0.038, 0.040, 0.004), (-9, 0, 3)), paire=True)
    a.couture("aile_bord", "aile", 10, 0.12, 0.88, "droit", fil=FUMEE, paire=True)

    # ----- la queue : dans l'axe du corps, à peine relevée (dressée, elle faisait troglodyte), le bout arrondi -----
    def palette(v):
        s = K.emousse(v, 0.8)
        s[:, 0] *= 0.70 + 0.40 * K.lisse((v[:, 1] + 1) / 2)     # plus large au bout
        return s
    racine = PENCHE @ Vector((0, 0.070, 0.012))
    leve = math.radians(7)
    queue = A.boule(1.0, 32, 16).sculpte(palette).etire(0.022, 0.068, 0.009)
    a.piece("queue", queue, PLUME, pos=racine + Vector((0, math.cos(leve), math.sin(leve))) * 0.060, rot=(7, 0, 0))

    # ----- les pattes : longues, arrêtées en pleine course ; la gauche en avant, la droite qui pousse derrière -----
    def doigt(degres, long):
        t = math.radians(degres)
        return A.boule(1.0, 16, 8).etire(0.0055, long, 0.0050).pose((0.75 * long * math.sin(t), -0.75 * long * math.cos(t), 0), (0, 0, degres))
    for nom, cote, pas_ in (("patte_g", 1, -0.030), ("patte_d", -1, 0.034)):
        haut_ = (0.020 * cote, 0.010, 0.094)
        genou = (0.023 * cote, 0.018 + 0.4 * pas_, 0.050)
        bas_ = (0.025 * cote, pas_, 0.0055)
        tige = A.tube(A.courbe([haut_, genou, bas_], 5), 0.0050, 12)
        pied = (doigt(-28, 0.022) + doigt(0, 0.027) + doigt(28, 0.022) + doigt(180, 0.016)).pose(bas_, (0, 0, -8 * cote))
        a.piece(nom, tige + pied, PATTE, poil=False)
    return a

# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py merle). Les mesures sont celles du modèle (avant a.taille). Gardé par l'auteur le
# 15/10 (4e dessin). Sa pose de repos : penché vers la pelouse, la tête couchée, il écoute le ver.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.020, 0.128)),          # le milieu du fuseau
    ("tete", "corps", (0.003, -0.072, 0.150)),         # la nuque, où la tête s'emmanche sur le corps
    ("aile_G", "corps", (0.036, -0.010, 0.142)),       # l'épaule de l'aile (la droite : son miroir)
    ("queue", "corps", (0.0, 0.088, 0.140)),           # le croupion
    ("patte_g", "corps", (0.020, 0.010, 0.094)),       # la hanche ; les pattes, l'une en avant, l'autre derrière :
    ("patte_d", "corps", (-0.020, 0.010, 0.094)),      #   chacune son os nommé à la main
]

PORTEURS = [("corps", "corps"), ("dos", "corps"),
            ("tete", "tete"), ("crane", "tete"), ("cerne", "tete"), ("oeil", "tete"), ("bec", "tete"),
            ("aile", "aile", True), ("aile_bord", "aile", True),
            ("queue", "queue"), ("patte_g", "patte_g"), ("patte_d", "patte_d"),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def repos(t):
    """Il écoute la pelouse : il respire vite, penche la tête d'un côté puis de l'autre, la queue qui tressaute à
    chaque arrêt ; il cligne."""
    p = Pose()
    p.add("corps", ech=(1 + 0.015 * onde(t, 6), 1, 1 + 0.020 * onde(t, 6)))
    ecoute = cloche(t, 0.30, 0.12) - cloche(t, 0.72, 0.12)
    p.add("tete", rot=(4 * cloche(t, 0.30, 0.12), 14 * ecoute, 6 * ecoute))
    p.add("queue", rot=(-14 * (cloche(t, 0.50, 0.03) + cloche(t, 0.92, 0.03)), 0, 0))
    p.ouvert = 1 - cloche(t, 0.12, 0.03) - cloche(t, 0.60, 0.03)
    return p


def avance(t):
    """Sa course sautillée sur l'herbe : deux petits bonds par boucle, les deux pattes ensemble, la queue qui balance
    à chaque réception, la tête qui reste en avant."""
    p = Pose()
    bond = max(0.0, math.sin(2 * math.tau * t))
    p.add("corps", pos=(0, 0, 0.018 * bond), rot=(-6 * bond, 0, 0))
    for os_ in ("patte_g", "patte_d"):
        p.add(os_, rot=(-26 * bond, 0, 0))
    p.add("tete", rot=(5 * bond, 0, 0))
    p.add("queue", rot=(18 * bond - 6, 0, 0))
    p.add("aile_G", rot=(0, 0, 6 * bond))
    return p


def mange(t):
    """Il plonge le bec dans la pelouse, tire le ver d'un coup sec, se redresse et l'avale."""
    p = Pose()
    bas = cloche(t, 0.30, 0.10) + cloche(t, 0.62, 0.10)
    tire = cloche(t, 0.40, 0.03) + cloche(t, 0.72, 0.03)
    p.add("corps", rot=(16 * bas, 0, 0))
    p.add("tete", rot=(30 * bas - 12 * tire, 0, 0))
    p.add("queue", rot=(-18 * bas, 0, 0))
    p.ouvert = 1 - cloche(t, 0.88, 0.03)
    return p


def joie(t):
    """Sa fête : il gonfle le jabot, bat des ailes deux fois en sautant sur place, la queue en éventail, et retombe à
    l'écoute."""
    p = Pose()
    saut = cloche(t, 0.45, 0.16)
    bat = onde(t, 4) * cloche(t, 0.45, 0.20)
    p.add("corps", pos=(0, 0, 0.040 * saut), rot=(-14 * saut, 0, 0), ech=(1 + 0.06 * saut, 1, 1 + 0.06 * saut))
    p.add("aile_G", rot=(0, 0, 55 * bat * bat + 10 * saut))
    p.add("tete", rot=(-18 * saut, 0, 0))
    p.add("queue", rot=(-20 * saut, 0, 0), ech=(1 + 0.4 * saut, 1, 1))
    for os_ in ("patte_g", "patte_d"):
        p.add(os_, rot=(-20 * saut, 0, 0))
    return p


def dort(t):
    """En boule, gonflé contre le froid, les pattes cachées sous lui, la tête rentrée dans les épaules, le bec dans
    les plumes du dos ; il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.add("corps", pos=(0, 0, -0.060), rot=(-10, 0, 0), ech=(1.10 + 0.015 * r, 1, 1.10 + 0.020 * r))
    p.add("tete", rot=(-20, 0, 70), pos=(0, 0.012, -0.012))
    p.add("patte_g", rot=(-70, 0, 0))
    p.add("patte_d", rot=(-70, 0, 0))
    p.add("queue", rot=(10, 0, 0))
    p.ouvert = 0.0
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Merle")
