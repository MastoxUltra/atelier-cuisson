"""Le paon en peluche : le poitrail turquoise bombé, le cou dressé, une aigrette sur la tête,
et derrière lui une grande roue de feutrine marine semée d'ocelles cousus.

    python paon.py        fabrique la fiche art/apercus/animaux/paon.png
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

CORPS = Vector((0.0, -0.030, 0.225))
TETE = Vector((0.0, -0.185, 0.560))
FIER = A.repere(CORPS, (-22, 0, 0))           # le corps : le poitrail haut, le croupion bas
HAUT = A.repere(TETE, (0, 0, 14))             # la tête, tournée d'un rien vers celui qui l'admire

# la roue : un éventail plat planté dans le croupion, un peu renversé en arrière
MOYEU = Vector((0.0, 0.100, 0.270))
RENVERSE = math.radians(10)
ROUE = A.cadre(MOYEU, (0, -math.cos(RENVERSE), math.sin(RENVERSE)))    # son X = la gauche, son Y monte, son Z regarde devant
RAYON, LOBES, OUVERT, EPAIS = 0.55, 9, math.radians(108), 0.026
RECUL = 0.12                                  # d'où l'on vise la roue pour y coudre un ocelle : de devant, à 12 cm


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du jardin."""
    return HAUT.to_3x3() @ Vector((x, y, z))


def eventail():
    """Le contour de la roue : neuf lobes ronds (un par grande plume), refermés par un petit arc sous le moyeu."""
    pts, n = [], LOBES * 12
    for i in range(n + 1):
        phi = -OUVERT + 2 * OUVERT * i / n
        r = RAYON * (1 - 0.085 * (1 - abs(math.sin(math.pi * i / 12)) ** 0.5))
        pts.append((r * math.sin(phi), r * math.cos(phi)))
    for i in range(1, 12):
        phi = OUVERT + (math.tau - 2 * OUVERT) * i / 12
        pts.append((0.10 * math.sin(phi), 0.10 * math.cos(phi)))
    return pts


def construire():
    a = K.Animal("paon")
    a.taille = 1.10
    a.tete = HAUT @ Vector((0, -0.050, 0.0))

    # ----- la roue, en feutrine marine : épaisse, les bords bien ronds, comme un coussin plat -----
    a.piece("roue", A.decoupe(eventail(), EPAIS, 0.010), K.MARINE, mat=ROUE, poil=False)

    # ----- les ocelles : trois ronds de feutrine l'un sur l'autre (moutarde, turquoise, marine),
    #       le plus grand tenu au point de feston. On vise la roue de devant, comme pour une rustine. -----
    vers_roue = -(ROUE.to_3x3() @ Vector((0, 0, 1)))

    def ocelle(nom, degres, rho, r, feston):
        phi = math.radians(degres)
        sortie = math.atan2(-math.cos(phi), math.sin(phi))       # l'ocelle est un peu allongé le long de sa plume
        centre = ROUE @ Vector((rho * math.sin(phi), rho * math.cos(phi), RECUL))
        for i, (part, couleur, epais) in enumerate(((1.0, K.MOUTARDE, 0.003), (0.64, K.TURQUOISE, 0.0055), (0.32, K.MARINE, 0.008))):
            angle = math.atan(part * r / (RECUL - EPAIS / 2))
            a.rustine("%s_%d" % (nom, i), "roue", centre, vers_roue,
                      lambda th, angle=angle: angle * (1 + 0.14 * math.cos(2 * (th - sortie))),
                      couleur, epais, feston if i == 0 else 0, paire=degres > 0)
    for degres in (0, 24, 48, 72, 96):                           # un grand ocelle au milieu de chaque lobe
        ocelle("ocelle%d" % degres, degres, 0.440, 0.066, 10)
    for degres in (12, 36, 60, 84):                              # un rang de petits, en quinconce
        ocelle("petit%d" % degres, degres, 0.262, 0.042, 0)
    # le dos de la roue : cinq nervures brodées
    for i, degres in enumerate((-72, -36, 0, 36, 72)):
        phi = math.radians(degres)
        a.broderie("nervure%d" % i, [ROUE @ Vector((r * math.sin(phi), r * math.cos(phi), -EPAIS / 2 - 0.002)) for r in (0.14, 0.44)], 0.003, K.MOUTARDE)

    # ----- le corps : un œuf dressé, le poitrail bombé -----
    def coque(v):
        v = K.bosse(v, (0, -0.75, 0.25), 0.10, 0.4)
        arriere = K.lisse((v[:, 1] - 0.1) / 0.9)
        s = v * [0.105, 0.150, 0.108]
        s[:, 0] *= 1 - 0.40 * arriere
        s[:, 2] *= 1 - 0.30 * arriere
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    G.sillons(corps, [42], 0.005, 1.1)                  # la couture du poitrail creuse un peu le tissu
    a.piece("corps", corps, K.TURQUOISE, mat=FIER)
    a.couture("poitrail", "corps", 42, 0.20, 0.47, fil=K.MOUTARDE)

    # ----- le cou, long et cambré, puis la petite tête -----
    cou = A.courbe([(0, -0.105, 0.290), (0, -0.152, 0.375), (0, -0.150, 0.455), (0, -0.172, 0.530)], 6)
    a.piece("cou", A.tube(cou, lambda t: 0.066 - 0.050 * t + 0.022 * t * t, 20), K.TURQUOISE)
    a.piece("tete", A.boule(1.0, 56, 28).etire(0.056, 0.063, 0.056), K.TURQUOISE, mat=HAUT)

    # ----- les yeux, entre deux traits de fil blanc (les marques du paon) : celui du haut, en biais, fait le regard hautain -----
    for nom, cote in (("g", 1), ("d", -1)):
        p, n = a.surface("tete", TETE, vers(0.80 * cote, -0.52, 0.22))
        a.bouton("oeil_" + nom, p + n * 0.004, n, 0.017)
        dessus = a.trace("tete", TETE, [vers(0.58 * cote, -0.76, 0.46), vers(0.74 * cote, -0.50, 0.66), vers(0.88 * cote, -0.24, 0.60)], 0.006)
        a.broderie("dessus_" + nom, A.courbe(dessus, 5), 0.0032, K.BLANC)
        dessous = a.trace("tete", TETE, [vers(0.64 * cote, -0.76, 0.0), vers(0.84 * cote, -0.50, -0.16), vers(0.96 * cote, -0.22, 0.02)], 0.006)
        a.broderie("dessous_" + nom, A.courbe(dessous, 5), 0.0032, K.BLANC)

    # ----- le bec en feutrine moutarde -----
    bec = A.tour(A.profil([(0, 0), (0.017, 0.004), (0.013, 0.018), (0.006, 0.038), (0, 0.048)], 5), 28)
    a.piece("bec", bec, K.MOUTARDE, pos=HAUT @ Vector((0, -0.052, -0.006)), rot=A.viser(vers(0, -1, -0.12)), poil=False)

    # ----- l'aigrette : cinq brins en éventail, chacun coiffé d'une petite boule -----
    pied = HAUT @ Vector((0, 0.012, 0.050))
    houppes = None
    for i, degres in enumerate((-44, -22, 0, 22, 44)):
        t = math.radians(degres)
        bout = pied + vers(math.sin(t), 0.22, math.cos(t)) * 0.090
        milieu = pied.lerp(bout, 0.5) + vers(0, 0.008, 0)
        a.broderie("brin%d" % i, A.courbe([pied, milieu, bout], 5), 0.003, K.MOUTARDE)
        boule = A.boule(0.013, 16, 8).pose(tuple(bout))
        houppes = boule if houppes is None else houppes + boule
    a.piece("houppes", houppes, K.TURQUOISE, poil=False)

    # ----- les ailes : deux galets marine plaqués sur les flancs, cousus sur leur tranche -----
    aile = A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.024, 0.112, 0.080)
    a.piece("aile", aile, K.MARINE, mat=FIER @ A.repere((0.098, 0.004, 0.022), (-6, 0, 8)), paire=True)
    for cote in (10, 30):
        a.couture("aile%d" % cote, "aile", cote, 0.12, 0.88, "droit", fil=K.MOUTARDE, paire=True)

    # ----- les pattes : deux tiges solides et trois doigts, en feutrine moutarde -----
    def doigt(degres):
        t = math.radians(degres)
        return A.boule(1.0, 16, 8).etire(0.011, 0.040, 0.009).pose((0.030 * math.sin(t), -0.030 * math.cos(t), 0), (0, 0, degres))
    patte = doigt(-30) + doigt(0) + doigt(30) + A.tube([(0, 0.008, 0.150), (0, 0.004, 0.0)], 0.011, 10)
    a.piece("patte", patte, K.MOUTARDE, pos=(0.048, -0.035, 0.009), poil=False, paire=True)
    return a

# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py paon). Les mesures sont celles du modèle (avant a.taille). Gardé par l'auteur (vague 2,
# 13/10). Sa pose de repos : la roue faite, le poitrail haut, le cou cambré.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, -0.030, 0.225)),         # le milieu du corps
    ("cou", "corps", (0.0, -0.105, 0.290)),            # le pied du cou, sur le poitrail
    ("tete", "cou", (0.0, -0.172, 0.530)),             # la nuque
    ("roue", "corps", (0.0, 0.100, 0.270)),            # le moyeu de la roue, au croupion
    ("aile_G", "corps", (0.090, -0.020, 0.250)),       # l'épaule de l'aile (la droite : son miroir)
    ("patte_G", "corps", (0.048, -0.035, 0.150)),      # le haut de la patte (la droite : son miroir)
]

PORTEURS = [("corps", "corps"), ("poitrail", "corps"),
            ("cou", "cou"),
            ("tete", "tete"), ("oeil", "tete"), ("dessus", "tete"), ("dessous", "tete"), ("bec", "tete"),
            ("brin", "tete"), ("houppes", "tete"),
            ("roue", "roue"), ("ocelle", "roue"), ("petit", "roue"), ("nervure", "roue"),
            ("aile", "aile", True),
            ("patte", "patte", True),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def repos(t):
    """Il fait la roue et s'admire : il respire, fait tourner lentement sa roue d'un côté puis de l'autre pour qu'on la
    voie bien, la fait frissonner une fois, hoche sa petite tête couronnée."""
    p = Pose()
    p.add("corps", ech=(1 + 0.010 * onde(t, 2), 1, 1 + 0.014 * onde(t, 2)))
    tourne = cloche(t, 0.30, 0.14) - cloche(t, 0.70, 0.14)
    frisson = cloche(t, 0.50, 0.04) * onde(t, 24)
    p.add("corps", rot=(0, 0, 8 * tourne))
    p.add("roue", rot=(2 * frisson, 0, 0))
    p.add("cou", rot=(0, 0, -4 * tourne))
    p.add("tete", rot=(5 * onde(t, 3), 0, -6 * tourne))
    p.ouvert = 1 - cloche(t, 0.15, 0.03) - cloche(t, 0.85, 0.03)
    return p


def avance(t):
    """Sa marche de parade : un pas lent et haut, la tête qui avance et recule à chaque pas, la roue qui balance."""
    p = Pose()
    for os_, phase in (("patte_G", 0.0), ("patte_D", 0.5)):
        a = math.tau * (t + phase)
        p.add(os_, rot=(-22 * math.sin(a), 0, 0), pos=(0, 0, 0.012 * max(0.0, -math.cos(a))))
    p.add("corps", pos=(0, 0, 0.006 * (0.5 - 0.5 * math.cos(2 * math.tau * t))), rot=(0, 3 * onde(t, 1), 0))
    p.add("cou", rot=(-8 * onde(t, 2), 0, 0))
    p.add("tete", rot=(6 * onde(t, 2), 0, 0))
    p.add("roue", rot=(0, 3 * onde(t, 1, 0.25), 0))
    return p


def mange(t):
    """Il baisse son long cou et picore deux fois, la roue toujours dressée, puis relève la tête, très digne."""
    p = Pose()
    bas = cloche(t, 0.30, 0.13) + cloche(t, 0.66, 0.13)
    pique = onde(t, 14) * bas
    p.add("cou", rot=(58 * bas, 0, 0))
    p.add("tete", rot=(22 * bas + 6 * pique, 0, 0))
    p.add("corps", rot=(10 * bas, 0, 0))
    p.add("roue", rot=(-10 * bas, 0, 0))
    return p


def joie(t):
    """Sa fête : la roue frissonne et cliquette, il se dresse sur ses pattes, déploie les ailes et lance un cri, la
    tête au ciel ; puis il reprend la pose."""
    p = Pose()
    haut = cloche(t, 0.45, 0.16)
    frisson = onde(t, 18) * cloche(t, 0.45, 0.22)
    p.add("corps", pos=(0, 0, 0.030 * haut), rot=(-6 * haut, 0, 0))
    p.add("roue", rot=(4 * frisson - 6 * haut, 0, 0), ech=(1 + 0.06 * haut, 1 + 0.06 * haut, 1))
    p.add("aile_G", rot=(0, 0, 30 * haut))
    p.add("cou", rot=(-14 * haut, 0, 0))
    p.add("tete", rot=(-24 * haut, 0, 0))
    return p


def dort(t):
    """Accroupi, la roue repliée et couchée derrière lui, le cou rentré, la tête posée sur le dos ; il respire
    lentement."""
    p = Pose()
    r = onde(t, 1)
    p.add("corps", pos=(0, 0, -0.110), rot=(18, 0, 0), ech=(1 + 0.012 * r, 1, 1 + 0.016 * r))
    p.add("patte_G", rot=(-80, 0, 0))
    p.add("patte_D", rot=(-80, 0, 0))
    p.add("roue", rot=(-62, 0, 0), ech=(0.55, 0.55, 1))
    p.add("cou", rot=(-30, 0, 0))
    p.add("tete", rot=(40, 0, 60))
    p.ouvert = 0.0
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Paon")
