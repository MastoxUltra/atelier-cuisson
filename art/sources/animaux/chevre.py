"""La chèvre en peluche, troisième dessin : une alpine chamoisée, la chèvre qu'on connaît, effrontée et maligne. Une robe
noisette chaude, la raie de mulet charbon de la nuque à la queue, les chaussettes charbon, le museau et le ventre crème.
Campée sur trois pattes, la quatrième levée, la tête penchée vers vous, deux petits yeux vifs sous un seul sourcil
brodé, le sourire en coin, la barbiche en avant, et deux cornes en arc, courtes et annelées, couleur de corne.
(l'auteur, 15/10 : la poitevine noire était « trop bizarre » : chevre_ancien2.py ; le premier dessin : chevre_ancien.py)

    python chevre.py        fabrique la fiche art/apercus/animaux/chevre.png
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

CROUPE = Vector((0.0, 0.26, 0.385))           # le bout arrière du corps (une pièce tournée, couchée vers l'avant)
MILIEU = Vector((0.0, 0.0, 0.385))            # le milieu du corps, d'où l'on vise ses rapiéçages
TETE = Vector((0.01, -0.36, 0.625))
NARGUE = A.repere(TETE, (-6, 8, 12))          # la tête : le menton levé, penchée sur l'épaule et tournée vers celui qu'elle nargue
PERLE = M.hexa("#c08a5e")                     # la robe : un noisette chaud (le nom est resté du premier dessin)
ARDOISE = M.hexa("#3a3236")                   # la raie, les chaussettes et le bout de la queue : charbon (idem)
CORNE = M.hexa("#8f8478")                     # les cornes : la couleur de la corne, grise et chaude


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du jardin."""
    return NARGUE.to_3x3() @ Vector((x, y, z))


def construire():
    a = K.Animal("chevre")
    a.taille = 1.00
    a.tete = NARGUE @ Vector((0, -0.11, 0.0))

    # ----- le corps : un tonneau tourné de la croupe au poitrail, puis couché ; dans la pièce, X est la gauche,
    #       Y le dos, Z l'avant. Le poitrail est profond, le ventre remonte vers l'arrière. -----
    corps = A.tour(A.profil([(0, 0), (0.075, 0.012), (0.108, 0.07), (0.112, 0.16), (0.108, 0.26), (0.122, 0.37), (0.110, 0.45),
                             (0.06, 0.495), (0, 0.505)], 6), 48)
    echine = (np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1])) < 0.34) & (corps.v[:, 2] > 0.02) & (corps.v[:, 2] < 0.43)
    corps.teinte = np.where(echine[:, None], ARDOISE, PERLE)     # la raie de mulet : trois méridiens peints, de la queue au garrot

    def tonneau(v):
        s = v.copy()
        s[:, 0] *= 0.84
        dessous = v[:, 1] < 0
        s[dessous, 1] *= (1 - 0.20 * K.lisse((0.30 - v[:, 2]) / 0.22) + 0.10 * K.lisse((v[:, 2] - 0.30) / 0.14))[dessous]
        return s
    corps.sculpte(tonneau)
    G.sillons(corps, [12], 0.004, 1.1)                  # la couture du dos creuse un peu le tissu
    a.piece("corps", corps, None, pos=CROUPE, rot=(90, 0, 0))
    a.couture("dos", "corps", 12, 0.08, 0.84, fil=PERLE)
    # le dessous crème : il court sous le ventre, remonte à mi-flanc (vu d'en haut, on doit le voir) et grimpe devant jusqu'au cou
    a.rustine("ventre", "corps", MILIEU + Vector((0, -0.03, 0)), (0, -0.25, -0.97),
              lambda th: 1.21 - 0.09 * math.cos(2 * th) - 0.10 * math.sin(th), K.CREME, feston=52, fil=M.hexa("#8a7a6e"))

    # ----- la petite queue retroussée, le bout ardoise -----
    queue = K.bandes(A.tour(A.profil([(0, 0), (0.026, 0.010), (0.024, 0.050), (0.012, 0.090), (0, 0.100)], 5), 24), [(0.045, PERLE), (9, ARDOISE)])
    a.piece("queue", queue, None, pos=(0, 0.245, 0.455), rot=A.viser((0, 0.55, 0.83)))

    # ----- le cou, porté vers l'avant -----
    cou = A.tour(A.profil([(0, 0), (0.090, 0.012), (0.082, 0.08), (0.068, 0.16), (0.062, 0.22), (0, 0.245)], 5), 32)
    a.piece("cou", cou, PERLE, pos=(0, -0.185, 0.40), rot=A.viser((0.02, -0.58, 0.81)))

    # ----- la tête : un crâne à bajoues, et un long museau crème qui descend en coin -----
    H3 = NARGUE.to_3x3()

    def crane(v):
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.9, -0.2, -0.4), 0.12, 0.25)
        return v * [0.078, 0.088, 0.076]
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(crane), PERLE, mat=NARGUE)
    a.couture("crane", "tete", 14, 0.58, 0.97, fil=K.CREME)
    pm = A.profil([(0.060, 0.0), (0.056, 0.03), (0.047, 0.07), (0.040, 0.105), (0.034, 0.125), (0, 0.140)], 6)
    Mu = NARGUE @ A.repere((0, -0.040, -0.020), (118, 0, 0))     # dans ce repère : X la gauche, Y le dessus du nez, Z vers le bout
    Mu3 = Mu.to_3x3()
    a.piece("museau", A.tour(pm, 40).etire(1.0, 0.85, 1.0), K.CREME, mat=Mu)
    a.piece("nez", A.boule(1.0, 24, 12).etire(0.021, 0.012, 0.013), M.hexa("#5a4446"), mat=Mu @ A.repere((0, 0.010, 0.131)), poil=False)
    # le sourire en coin, d'un seul côté : il part de sous le nez et remonte le long du museau
    sourire = [a.trace("museau", Mu @ Vector((0, 0, z)), [Mu3 @ Vector((math.cos(math.radians(d)), math.sin(math.radians(d)), 0))])[0]
               for z, d in ((0.128, -80), (0.118, -60), (0.105, -42), (0.092, -28), (0.080, -16), (0.068, -4), (0.058, 10))]
    a.broderie("sourire", A.courbe(sourire, 4), 0.0030, M.hexa("#5a4446"))

    # ----- les yeux rapprochés, et par-dessus un seul sourcil brodé : haussé à gauche, froncé à droite -----
    for nom, cote in (("g", 1), ("d", -1)):
        p, n = a.surface("tete", TETE, vers(0.34 * cote, -0.84, 0.46))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0150)
    sourcil = a.trace("tete", TETE, [vers(*d) for d in ((0.62, -0.52, 0.98), (0.32, -0.72, 0.90), (0.02, -0.84, 0.64), (-0.28, -0.78, 0.72), (-0.56, -0.68, 0.60))], 0.005)
    a.broderie("sourcil", A.courbe(sourcil, 5), 0.0034, ARDOISE)

    # ----- la barbiche crème, pointée en avant sous le menton -----
    barbiche = A.tour(A.profil([(0, 0), (0.020, 0.008), (0.021, 0.045), (0.012, 0.105), (0, 0.130)], 5), 24)
    a.piece("barbiche", barbiche, K.CREME, pos=Mu @ Vector((0, -0.025, 0.080)), rot=A.viser(vers(0, -0.22, -1)))

    # ----- les cornes : deux arcs courts de feutrine couleur de corne, annelés, qui montent et partent en arrière -----
    arc = ((0.040, 0.000, 0.045), (0.044, 0.018, 0.105), (0.056, 0.060, 0.150), (0.072, 0.110, 0.160), (0.084, 0.150, 0.135))
    for nom, cote in (("g", 1), ("d", -1)):
        fil = A.courbe([tuple(NARGUE @ Vector((x * cote, y, z))) for x, y, z in arc], 12)
        a.piece("corne_" + nom, A.tube(fil, lambda t: (0.034 - 0.028 * t) * (1 + 0.08 * math.cos(math.tau * 7 * t)), 16), CORNE, poil=False)

    # ----- les oreilles tombantes : une feuille gris perle, son dedans rose -----
    def feuille(v):                                       # étroite à l'attache, large au milieu
        s = v.copy()
        s[:, 0] *= 1 - 0.45 * K.lisse((v[:, 2] + 0.2) / 1.2)
        return s
    for nom, cote in (("g", 1), ("d", -1)):
        tombe = Vector((0.72 * cote, 0.10, -0.68)).normalized()
        racine = Vector((0.072 * cote, 0.020, 0.020))
        a.piece("oreille_" + nom, A.boule(1.0, 28, 14).sculpte(feuille).etire(0.040, 0.012, 0.085), PERLE,
                mat=NARGUE @ A.repere(racine + tombe * 0.070, A.viser(tombe)))
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).sculpte(feuille).etire(0.026, 0.007, 0.060), M.hexa("#c9a3a0"),
                mat=NARGUE @ A.repere(racine + tombe * 0.074 + Vector((0, -0.008, 0)), A.viser(tombe)), poil=False)

    # ----- trois pattes plantées, en bas ardoise : l'avant droite arc-boutée, les deux arrière campées loin derrière -----
    canon = [(0, 0), (0.036, 0.004), (0.040, 0.030), (0.030, 0.070), (0.029, 0.130), (0.033, 0.165), (0.031, 0.200)]
    devant = A.profil(canon + [(0.036, 0.250), (0.044, 0.300), (0, 0.335)], 6)                       # une épaule
    derriere = A.profil(canon + [(0.046, 0.270), (0.058, 0.330), (0.050, 0.375), (0, 0.395)], 6)     # un gigot

    def sabot(v):                                         # le bas de la patte avance un peu : un sabot
        s = v.copy()
        s[:, 1] -= 0.012 * K.lisse((0.05 - v[:, 2]) / 0.05)
        return s
    for nom, profil, pos, rot in (("avant_d", devant, (-0.062, -0.190, 0.0), (-5, 0, 0)), ("arriere_g", derriere, (0.072, 0.215, 0.005), (7, -3, 0)),
                                  ("arriere_d", derriere, (-0.072, 0.215, 0.005), (7, 3, 0))):      # l'arrière un rien relevé : penché, son bord passerait sous le sol
        a.piece("patte_" + nom, K.bandes(A.tour(profil, 32).sculpte(sabot), [(0.078, ARDOISE), (9, PERLE)]), None, pos=pos, rot=rot)

    # ----- la quatrième, l'avant gauche : levée haut, l'avant-bras à l'horizontale, le sabot replié qui pend -----
    fil = A.courbe([(0.066, -0.150, 0.330), (0.074, -0.240, 0.305), (0.080, -0.292, 0.280), (0.081, -0.285, 0.235), (0.080, -0.262, 0.180)], 6)
    levee = A.tube(fil, lambda t: float(np.interp(t, [0, 0.45, 0.80, 0.93, 1], [0.044, 0.033, 0.029, 0.037, 0.037])), 20)
    a.piece("patte_avant_g", K.bandes(levee, [(0.240, ARDOISE), (9, PERLE)]), None)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py chevre). Les mesures sont celles du modèle, avant a.taille.
# Les pattes pendent à la racine, pas au corps : un sabot posé ne bouge pas quand le corps penche. Chacune a son os à
# elle, nommé à la main (le modèle n'est pas symétrique). Les trois pattes plantées sont d'une pièce, un os à l'épaule
# ou à la hanche ; la patte levée a deux os, l'épaule et le genou, et sa pièce passe de l'un à l'autre au genou, en
# fondu, comme celles du cheval. Pliée, elle est plus courte que les autres : pour la poser, on la déplie sous l'épaule
# et on la descend de 5 cm (son haut reste caché dans le poitrail). La tête est penchée et tournée : les oreilles ont
# chacune leur os.

from poses import Pose, borne, cloche, onde

# chaque patte plantée : son pivot (l'épaule ou la hanche) et le bas de son sabot
JAMBES = {"av_d": ((-0.062, -0.164, 0.305), (-0.062, -0.199, 0.006)),
          "ar_g": ((0.054, 0.172, 0.365), (0.071, 0.201, 0.008)),
          "ar_d": ((-0.054, 0.172, 0.365), (-0.071, 0.201, 0.008)),
          "av_g": ((0.066, -0.150, 0.330), (0.066, -0.150, 0.006))}       # la patte levée, une fois posée (voir _pose)
GENOU = ((0.080, -0.292, 0.280), (0.074, -0.240, 0.305), (0.081, -0.285, 0.235))     # le genou levé, et les points qui l'encadrent

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.170, 0.370)),            # au-dessus des hanches : elle se penche et se cabre autour
    ("cou", "corps", (0.0, -0.185, 0.400)),              # le pied du cou, dans le poitrail
    ("tete", "cou", (0.002, -0.320, 0.595)),             # la nuque, là où le cou entre sous le crâne
    ("oreille_g", "tete", (0.078, -0.323, 0.633)),       # l'attache de chaque oreille tombante
    ("oreille_d", "tete", (-0.062, -0.353, 0.653)),
    ("queue", "corps", (0.0, 0.245, 0.455)),             # l'attache de la queue retroussée
    ("av_g", "racine", (0.066, -0.150, 0.330)),          # l'épaule de la patte levée
    ("av_g2", "av_g", GENOU[0]),                         # son genou
    ("av_d", "racine", JAMBES["av_d"][0]),
    ("ar_g", "racine", JAMBES["ar_g"][0]),
    ("ar_d", "racine", JAMBES["ar_d"][0]),
]


def _levee(points, cote):
    """La patte levée : l'épaule au-dessus du genou, le genou en dessous, avec un fondu de 4 cm."""
    g, u, v = (np.array(q) for q in GENOU)
    sens = (g - u) / np.linalg.norm(g - u) + (v - g) / np.linalg.norm(v - g)
    w = K.lisse((points - g) @ (sens / np.linalg.norm(sens)) / 0.04 + 0.5)
    return {"av_g": 1 - w, "av_g2": w}


PORTEURS = [("corps", "corps"), ("ventre", "corps"), ("dos", "corps"), ("queue", "queue"), ("cou", "cou"),
            ("tete", "tete"), ("crane", "tete"), ("museau", "tete"), ("nez", "tete"), ("sourire", "tete"),
            ("oeil", "tete"), ("sourcil", "tete"), ("barbiche", "tete"), ("corne", "tete"),
            ("oreille_g", "oreille_g"), ("dedans_g", "oreille_g"), ("oreille_d", "oreille_d"), ("dedans_d", "oreille_d"),
            ("patte_avant_g", _levee, "av_g"), ("patte_avant_d", "av_d"), ("patte_arriere_g", "ar_g"), ("patte_arriere_d", "ar_d"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _pose(p, x):
    """La patte levée : en l'air comme sur le modèle (x = 0), ou posée d'aplomb sous l'épaule (x = 1)."""
    p.add("av_g", rot=(71 * x, 0, 0), pos=(0, 0, -0.046 * x))
    p.add("av_g2", rot=(-88 * x, 0, 0))


def _jambe(p, nom, angle, leve=0.0):
    """Tourne une patte posée de « angle » degrés autour de son haut (> 0 : le sabot part vers l'arrière) en gardant le
    sabot au ras du sol ; « leve » le soulève. (Pour av_g, la patte doit être posée : _pose(p, 1).)"""
    h, b = JAMBES[nom]
    dy, dz = b[1] - h[1], b[2] - h[2]
    a = math.radians(angle)
    p.add(nom, rot=(angle, 0, 0), pos=(0, 0, dz - (dy * math.sin(a) + dz * math.cos(a)) + 0.030 * abs(math.sin(a)) + leve))


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def repos(t):
    """L'effrontée : campée sur trois pattes, la quatrième en l'air, elle respire, frappe deux fois le sol du sabot
    (elle réclame), secoue la tête d'un air de défi en penchant le menton, remue la queue à toute vitesse, une oreille
    qui bat ; elle cligne, et nous regarde en coin."""
    p = Pose()
    r = onde(t, 2)
    frappe = cloche(t, 0.30, 0.045) + cloche(t, 0.42, 0.045)
    defi = cloche(t, 0.62, 0.10)
    coin = cloche(t, 0.84, 0.10)
    p.add("corps", ech=(1 + 0.012 * r, 1, 1 + 0.018 * r))
    _pose(p, 0.92 * frappe)
    p.add("cou", rot=(1.5 * r - 4 * defi, 0, 4 * coin))
    p.add("tete", rot=(-8 * defi, 10 * defi * onde(t, 10), 12 * coin))
    p.add("oreille_g", rot=(0, 26 * cloche(t, 0.16, 0.03), 0))
    p.add("oreille_d", rot=(0, -20 * cloche(t, 0.64, 0.05), 0))
    p.add("queue", rot=(-10 * cloche(t, 0.06, 0.05), 0, 20 * cloche(t, 0.06, 0.05) * onde(t, 24)))
    p.ouvert = 1 - cloche(t, 0.20, 0.02) - cloche(t, 0.76, 0.02)
    return p


def avance(t):
    """Un petit pas vif et décidé, une patte après l'autre (arrière gauche, avant gauche, arrière droite, avant droite),
    la tête haute qui hoche à chaque pas, les oreilles qui ballottent et la queue en l'air qui frétille. Un sabot posé
    glisse vers l'arrière pendant qu'il porte : elle avance."""
    p = Pose()
    _pose(p, 1.0)
    for nom, phase in (("ar_g", 0.0), ("av_g", 0.25), ("ar_d", 0.5), ("av_d", 0.75)):
        u = t - phase
        en_l_air = max(0.0, -math.sin(math.tau * u))
        _jambe(p, nom, -12 * math.cos(math.tau * u) - 10 * en_l_air, 0.045 * en_l_air)
    p.add("corps", rot=(0, 2 * onde(t, 1), 2 * onde(t, 1, 0.1)), pos=(0, 0, 0.006 * onde(t, 2, 0.25)))
    p.add("cou", rot=(-3 + 4 * onde(t, 2), 0, 0))
    p.add("tete", rot=(-3 * onde(t, 2, -0.1), 0, 3 * onde(t, 1)))
    p.add("oreille_g", rot=(0, 10 * onde(t, 2, -0.2), 0))
    p.add("oreille_d", rot=(0, -10 * onde(t, 2, -0.2), 0))
    p.add("queue", rot=(-12, 0, 14 * onde(t, 4)))
    return p


def mange(t):
    """Elle pose sa patte, baisse le cou jusqu'à l'herbe, arrache trois touffes d'un coup de tête de côté, puis relève la
    tête et mâche de travers, la barbiche qui va et vient, en nous regardant en coin."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    arrache = max(0.0, onde(t, 3)) ** 2 * bas
    _pose(p, 1.0)
    p.add("corps", rot=(8 * bas, 0, 0))
    p.add("cou", rot=(66 * bas - 4 * arrache, 0, -6 * bas), pos=(0, -0.040 * bas, 0))
    p.add("tete", rot=(-36 * bas - 8 * arrache, 0, 14 * arrache))
    p.add("tete", rot=(-3 * leve * abs(onde(t, 8)), 4 * leve * onde(t, 8), 12 * leve))      # elle mâche, elle nous regarde
    p.add("oreille_g", rot=(0, 14 * bas, 0))
    p.add("oreille_d", rot=(0, -14 * bas, 0))
    p.add("queue", rot=(0, 0, 10 * onde(t, 3)))
    p.ouvert = borne(1 - cloche(t, 0.92, 0.03))
    return p


def _avec_corps(p, nom, angle):
    """Une patte de devant qui suit le corps quand il se cabre de « angle » degrés autour de son pivot (elles pendent
    à la racine : sans cela, elles resteraient plantées au sol)."""
    pivot = np.array(OS[1][2])
    h = np.array(JAMBES[nom][0] if nom != "av_g" else OS[7][2])
    a = math.radians(angle)
    d = h - pivot
    y, z = d[1] * math.cos(a) - d[2] * math.sin(a), d[1] * math.sin(a) + d[2] * math.cos(a)
    p.add(nom, rot=(angle, 0, 0), pos=(0, y - d[1], z - d[2]))


def joie(t):
    """Sa fête à elle : elle se cabre sur ses pattes arrière, les pattes de devant repliées, la tête penchée de côté
    d'un air de défi ; elle retombe et donne un grand coup de tête dans le vide, les oreilles qui volent ; puis elle
    reprend sa pose, la patte en l'air."""
    p = repos(0.0)
    cabre = math.sin(math.pi * borne((t - 0.05) / 0.50))         # cabrée de 0,05 à 0,55
    coup = cloche(t, 0.64, 0.10, False)                           # le coup de tête, en retombant
    p.add("corps", rot=(-34 * cabre, 0, 0))
    _avec_corps(p, "av_g", -34 * cabre)
    p.add("av_g2", rot=(30 * cabre, 0, 0))
    _avec_corps(p, "av_d", -34 * cabre)
    p.add("av_d", rot=(70 * cabre, 0, 0))
    p.add("ar_g", rot=(-8 * cabre, 0, 0))
    p.add("ar_d", rot=(-8 * cabre, 0, 0))
    p.add("cou", rot=(-6 * cabre + 34 * coup, 0, 0))
    p.add("tete", rot=(10 * cabre - 10 * coup, -18 * cabre, 10 * cabre))
    p.add("oreille_g", rot=(0, 30 * cabre + 20 * coup, 0))
    p.add("oreille_d", rot=(0, -30 * cabre - 20 * coup, 0))
    p.add("queue", rot=(-20 * cabre, 0, 16 * onde(t, 8) * cabre))
    return p


def dort(t):
    """Couchée sur le ventre, la patte de devant gauche repliée sous le poitrail, le genou en avant, les autres rentrées
    sous elle ; la tête tournée et posée sur son flanc gauche, les oreilles tombées, les yeux fermés ; elle respire
    lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.225), ech=(1.04 + 0.012 * r, 1.0, 0.97 + 0.020 * r))
    p.add("av_g", pos=(0, 0, -0.225))
    p.add("av_g2", rot=(84, 0, 0))
    for nom in ("av_d", "ar_g", "ar_d"):
        p.add(nom, pos=(0, 0, -0.225), ech=(1, 1, 0.22))
    p.add("cou", rot=(30, 0, 62))
    p.add("tete", rot=(22, 12, 84))
    p.add("oreille_g", rot=(0, -12, 0))
    p.add("oreille_d", rot=(0, 18, 0))
    p.add("queue", rot=(12, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Chèvre")
