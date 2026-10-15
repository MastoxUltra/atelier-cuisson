"""Le crapaud en peluche, deuxième dessin : le vieux grognon du potager. Un pavé de peluche bronze, mou, plus large que
long, qui s'affaisse sur le sol comme un coussin trop rempli ; le dessus plat, les flancs qui coulent, le ventre sable qui
déborde par-devant. Deux grosses glandes en haricot derrière les yeux, couvertes de feutrine moutarde, et des pustules
moutarde semées en relief sur le dos et les cuisses. La bouche est un pli creusé d'une joue à l'autre, qui tombe aux deux
coins (plus bas d'un côté) ; les yeux, petits et cuivrés, sont écrasés sous deux paupières lourdes. Il s'est tourné de
trois quarts pour ne pas vous faire face, il vous regarde quand même, de côté, accoudé sur un bras, l'autre main à plat.

    python crapaud.py        fabrique la fiche art/apercus/animaux/crapaud.png
    (le premier dessin, jamais gardé : crapaud_ancien.py)
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

BRONZE = M.hexa("#b88248")                    # le corps : un bronze chaud (le poil le fonce en vieux bronze)
PATINE = M.hexa("#6e4526")                    # le bronze sombre : les paupières, les tourelles, le rapiéçage, le fil
SABLE = M.hexa("#f0d6a8")                     # le ventre qui déborde, les mains et les pieds
MOUTARDE = M.hexa("#e8ac2a")                  # l'accent : les glandes, les pustules, le cerne des yeux
TOURNE = 0                                    # tout l'animal tourne autour de Z (degrés) ; 0 pour le jeu
TOUR = A.repere((0, 0, 0), (0, 0, TOURNE))     # (s'appelait CAP : verif_os.py lit CAP comme une constante de pose)
CORPS = A.repere((0.0, 0.004, 0.084), (-5, 0, -14))   # le pavé : il s'est détourné vers sa droite, le nez un peu bas
CENTRE = TOUR @ CORPS.to_translation()
DEMI = (0.152, 0.120, 0.076)                  # ses demi-mesures : large, long, haut


def ici(x, y, z):
    """Un point du jardin, avant que tout l'animal ne tourne de TOURNE."""
    return TOUR @ Vector((x, y, z))


# les pustules en relief : (direction dans le corps, hauteur de la bosse, ouverture de la feutrine)
PUSTULES = [((0.52, 0.28, 0.80), 0.050, 0.12), ((-0.40, 0.42, 0.81), 0.055, 0.13), ((0.10, 0.70, 0.70), 0.040, 0.10),
            ((0.84, 0.22, 0.48), 0.045, 0.11), ((-0.80, 0.30, 0.52), 0.040, 0.10), ((0.30, 0.86, 0.40), 0.035, 0.09),
            ((-0.20, 0.10, 0.97), 0.030, 0.08), ((0.66, -0.20, 0.72), 0.030, 0.07), ((-0.62, 0.70, 0.35), 0.035, 0.09),
            ((0.93, -0.12, 0.30), 0.035, 0.09), ((0.74, 0.02, 0.62), 0.030, 0.07)]
GLANDES = [((0.50, -0.02, 0.86), 1), ((-0.50, -0.02, 0.86), -1)]       # les parotoïdes, juste derrière les yeux


def bouche_haut(az):
    """La hauteur (sur la boule unité) du pli de la bouche selon l'angle autour du museau : il tombe aux deux coins,
    plus bas du côté droit (az < 0) : la moue."""
    return -0.06 - 0.36 * (abs(az) / 1.35) ** 2.2 * (1.25 if az < 0 else 1.0)


def coque(v):
    """La boule unité devient le pavé mou : carré, plat dessus, les flancs qui coulent, le ventre qui déborde devant,
    la bouche creusée, les glandes et les pustules gonflées."""
    u = v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)
    w = K.emousse(v, 0.74)
    for d, haut, _o in PUSTULES:
        w = K.bosse(w, d, haut, 0.010)
    for d, _c in GLANDES:
        w = K.bosse(w, d, 0.16, 0.030)
    w = K.bosse(w, (0, -0.85, -0.45), 0.12, 0.25)            # le ventre qui déborde par-devant
    w = K.bosse(w, (0, -0.95, 0.05), 0.05, 0.10)             # la lippe du haut, qui avance au-dessus du pli
    for cote, haut in ((1, 0.07), (-1, 0.10)):              # les bajoues qui pendent sous les coins de la bouche
        w = K.bosse(w, (0.80 * cote, -0.50, -0.42), haut, 0.035)
    # la bouche : un pli creusé tout autour du museau
    az = np.arctan2(u[:, 0], -u[:, 1])
    bas = np.array([bouche_haut(a) for a in az])
    pli = np.exp(-((u[:, 2] - bas) / 0.075) ** 2) * K.lisse((1.40 - np.abs(az)) / 0.18)
    w = w * (1 - 0.085 * pli)[:, None]
    s = w * DEMI
    coule = K.lisse((0.2 - v[:, 2]) / 1.0)                   # le bas s'étale : il s'affaisse
    s[:, 0] *= 1 + 0.16 * coule
    s[:, 1] *= 1 + 0.08 * coule
    s[:, 2] -= 0.010 * v[:, 1]                               # la croupe un peu plus basse que la tête
    return s


def sur_corps(d):
    """Le point de la peau visé dans la direction d (repère de la boule unité), et la direction depuis le centre du corps."""
    p = TOUR @ (CORPS @ Vector(coque(np.array([d], float) / np.linalg.norm(d))[0]))
    return p, p - CENTRE


def doigts(depart, bouts, fil):
    """Une main ou un pied : de gros doigts courts et mous, le bout rond, sans ventouse."""
    m = None
    for bout in bouts:
        doigt = A.tube([depart, bout], fil, 12) + A.boule(1.0, 16, 8).etire(fil * 1.2, fil * 1.2, fil * 0.85).pose(bout)
        m = doigt if m is None else m + doigt
    return m


def construire():
    a = K.Animal("crapaud")
    a.taille = 0.40

    # ----- le pavé : une seule grosse pièce de peluche bronze, cousue le long du dos -----
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    G.sillons(corps, [14], 0.005, 1.1)
    a.piece("corps", corps, BRONZE, mat=TOUR @ CORPS)
    a.couture("dos", "corps", 14, 0.50, 0.94, fil=PATINE)
    # le ventre sable, qui déborde sous la bouche, tenu au point de feston
    _p, axe = sur_corps((0, -0.75, -0.66))
    a.rustine("ventre", "corps", CENTRE, axe, lambda th: 0.46 + 0.20 * math.cos(2 * th), SABLE, 0.003, 0)

    # ----- les glandes en haricot et les pustules : de la feutrine moutarde sur les bosses -----
    for d, cote in GLANDES:
        _p, axe = sur_corps(d)
        a.rustine("glande_" + ("G" if cote > 0 else "D"), "corps", CENTRE, axe,
                  lambda th: 0.25 + 0.10 * math.cos(2 * th - 0.9 * cote), MOUTARDE, 0.004, 16 if cote > 0 else 0, fil=PATINE)
    for i, (d, _h, ouverture) in enumerate(PUSTULES):
        _p, axe = sur_corps(d)
        a.rustine("pustule%d" % i, "corps", CENTRE, axe, ouverture, MOUTARDE, 0.004, 0)
    # un rapiéçage de bronze sombre sur la croupe
    _p, axe = sur_corps((-0.55, 0.78, 0.30))
    a.rustine("rapiecage", "corps", CENTRE, axe, 0.26, PATINE, 0.003, 14, fil=MOUTARDE)

    # ----- la bouche : un fil sombre au fond du pli, qui tombe aux deux coins -----
    pli = [sur_corps((math.sin(az), -math.cos(az), bouche_haut(az)))[1] for az in np.linspace(-1.36, 1.36, 15)]
    a.broderie("bouche", A.courbe(a.trace("corps", CENTRE, pli, 0.0045), 3), 0.0036, PATINE)

    # ----- les yeux : deux petites tourelles sur le front ; l'œil cuivré, à demi écrasé sous la paupière -----
    regard = (TOUR.to_3x3() @ Vector((0.62, -0.78, 0.10))).normalized()     # il nous regarde de côté
    a.tete = None
    for nom, cote in (("G", 1), ("D", -1)):
        p, _d = sur_corps((0.42 * cote, -0.60, 0.68))
        normale = (p - CENTRE).normalized()
        globe = p + normale * 0.006
        a.piece("tourelle_" + nom, A.boule(1.0, 40, 20).etire(0.030, 0.030, 0.026), BRONZE, pos=globe)
        n = (regard + normale * 0.55 + Vector((0.20 * cote, 0, 0))).normalized()
        q = globe + n * 0.027
        a.rustine("cerne_" + nom, "tourelle_" + nom, globe, n, 0.52, MOUTARDE, 0.0025, 0)
        a.oeil("oeil_" + nom, q + n * 0.003, n, 0.0115)
        a.piece("lourde_" + nom, K.paupiere(0.0115, 0.02 if cote > 0 else -0.10), PATINE,
                mat=A.cadre(q + n * 0.004, n, Vector((-0.25 * cote, 0, 1))), poil=False)
        if cote > 0:
            a.tete = q + Vector((-0.040, -0.020, -0.020))
    # un sourcil brodé : un seul trait, tombant, au-dessus de l'œil gauche
    p, _d = sur_corps((0.42, -0.60, 0.68))
    sourcil = [p + Vector((0.030 - 0.026 * u, -0.012 - 0.010 * u, 0.034 - 0.010 * u)) for u in np.linspace(0, 1, 5)]
    a.broderie("sourcil", A.courbe(sourcil, 3), 0.0030, PATINE)

    # ----- les cuisses repliées : deux gros galets bronze contre la croupe, cousus sur leur tranche, une pustule chacune -----
    for nom, cote, pos, rot in (("G", 1, (0.142, 0.058, 0.058), (-14, 0, 22)), ("D", -1, (-0.136, 0.072, 0.054), (-14, 0, -30))):
        pos = ici(*pos)
        cuisse = A.boule(1.0, 40, 20).sculpte(lambda v: K.bosse(K.emousse(v, 0.84), (0.6, -0.2, 0.75), 0.10, 0.04)).etire(0.050, 0.092, 0.050)
        a.piece("cuisse_" + nom, cuisse, BRONZE, pos=pos, rot=(rot[0], 0, rot[2] * 1.0 + TOURNE))
        a.couture("cuisse_" + nom, "cuisse_" + nom, 10 if cote > 0 else 30, 0.18, 0.82, "droit", fil=PATINE)
        a.rustine("pustule_cuisse_" + nom, "cuisse_" + nom, pos, Vector((0.55 * cote, -0.20, 0.80)), 0.24, MOUTARDE, 0.004, 0)
        pied = doigts(ici(0.150 * cote, 0.006, 0.011), [ici(0.168 * cote, -0.050, 0.010), ici(0.192 * cote, -0.032, 0.010),
                                                        ici(0.204 * cote, -0.004, 0.010)], 0.0105)
        a.piece("pied_" + nom, pied, SABLE, poil=False)

    # ----- les bras : le gauche accoudé, le coude loin dehors, la main tournée en dedans ; le droit, plus droit,
    #       la main à plat, les doigts écartés -----
    for nom, chemin, main, bouts in (
            ("G", [(0.092, -0.072, 0.066), (0.150, -0.106, 0.050), (0.118, -0.150, 0.016)], (0.116, -0.150, 0.011),
             [(0.074, -0.166, 0.010), (0.088, -0.188, 0.010), (0.112, -0.196, 0.010)]),
            ("D", [(-0.090, -0.064, 0.064), (-0.124, -0.104, 0.044), (-0.112, -0.146, 0.016)], (-0.110, -0.146, 0.011),
             [(-0.080, -0.176, 0.010), (-0.104, -0.192, 0.010), (-0.132, -0.184, 0.010), (-0.146, -0.162, 0.010)])):
        bras = A.tube(A.courbe([ici(*p) for p in chemin], 6), lambda t: 0.030 - 0.009 * t, 14)
        a.piece("bras_" + nom, bras, BRONZE)
        a.piece("main_" + nom, doigts(ici(*main), [ici(*b) for b in bouts], 0.0100), SABLE, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py crapaud). Les mesures sont celles du modèle de jeu (TOURNE = 0), avant a.taille.
# Le pavé est une seule pièce : on le rend souple, le devant (le museau, les tourelles) suit « tete », le dessous du
# museau suit « gorge », qui se gonfle. Il est assis de travers, les deux côtés ne sont pas à la même place : chaque
# membre a son os nommé à la main (cuisse_g, cuisse_d...). Les mains et les pieds pendent à la racine, pas au corps :
# posés à plat, ils ne bougent pas quand le pavé se balance au-dessus d'eux ; les bras s'étirent entre l'épaule et la main.

from poses import Pose, borne, cloche, onde


def _ou(v):
    return tuple(round(float(x), 4) for x in v)


OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", _ou(TOUR @ CORPS @ Vector((0, 0.0, -0.070)))),      # le dessous du pavé, sur l'herbe
    ("tete", "corps", _ou(TOUR @ CORPS @ Vector((0, -0.040, 0.0)))),        # au milieu du pavé, là où le devant plie
    ("gorge", "tete", _ou(TOUR @ CORPS @ Vector((0, -0.090, -0.045)))),     # sous la bouche
    ("cuisse_g", "corps", _ou(ici(0.118, 0.050, 0.058))),                 # la hanche, contre le flanc
    ("cuisse_d", "corps", _ou(ici(-0.112, 0.064, 0.054))),
    ("pied_g", "racine", _ou(ici(0.150, 0.006, 0.011))),                  # le talon
    ("pied_d", "racine", _ou(ici(-0.150, 0.006, 0.011))),
    ("main_g", "racine", _ou(ici(0.116, -0.150, 0.011))),                 # le poignet
    ("main_d", "racine", _ou(ici(-0.110, -0.146, 0.011))),
]

_DANS = np.linalg.inv(np.array(TOUR @ CORPS))                               # du jardin vers le repère du pavé
_EPAULE = {"_G": np.array(ici(0.092, -0.072, 0.066)), "_D": np.array(ici(-0.090, -0.064, 0.064))}
_POIGNET = {"_G": np.array(ici(0.116, -0.150, 0.011)), "_D": np.array(ici(-0.110, -0.146, 0.011))}


def _vrais(points, cote):
    """L'usine retourne en miroir les pièces de droite avant de les donner : on les remet à leur place."""
    return points * ([-1, 1, 1] if cote == "_D" else [1, 1, 1])


def souple(points, cote):
    """Le pavé et ce qui y est cousu : le devant plie avec « tete », le dessous du museau gonfle avec « gorge »."""
    q = _vrais(points, cote) @ _DANS[:3, :3].T + _DANS[:3, 3]
    u = q / np.array(DEMI)
    avant = K.lisse((-u[:, 1] - 0.10) / 0.50)
    gorge = avant * K.lisse((-u[:, 2] - 0.05) / 0.45) * K.lisse((-u[:, 1] - 0.35) / 0.35)
    return {"corps": 1 - avant, "tete": avant - gorge, "gorge": gorge}


def bras(points, cote):
    """Un bras : le haut suit le pavé, le bas suit la main posée ; il s'étire entre les deux."""
    q = _vrais(points, cote)
    e, m = _EPAULE[cote], _POIGNET[cote]
    f = np.clip((q - e) @ (m - e) / float((m - e) @ (m - e)), 0.0, 1.0)
    w = K.lisse((f - 0.30) / 0.55)
    return {"corps": 1 - w, ("main_g" if cote == "_G" else "main_d"): w}


def membre(base):
    """Une pièce tout entière sur l'os de son côté, nommé à la main (base_g ou base_d)."""
    return lambda points, cote: {base + ("_g" if cote == "_G" else "_d"): np.ones(len(points))}


# « pustule_cuisse » avant « pustule » : le premier qui correspond gagne
PORTEURS = [("corps", souple, "corps"), ("dos", souple, "corps"), ("ventre", souple, "corps"), ("glande", souple, "corps"),
            ("pustule_cuisse", membre("cuisse")), ("pustule", souple, "corps"), ("rapiecage", souple, "corps"),
            ("bouche", souple, "corps"), ("sourcil", souple, "corps"),
            ("tourelle", "tete"), ("cerne", "tete"), ("oeil", "tete"), ("lourde", "tete"),
            ("cuisse", membre("cuisse")), ("pied", membre("pied")), ("bras", bras), ("main", membre("main")),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _bascule(p, degres, cote=0.0):
    """Le pavé bascule sur le bord de son assise : vers l'avant (degrés > 0) ou en arrière, et de côté (cote, en degrés) ;
    il se soulève d'autant, pour que le bord qui descend reste posé sur l'herbe au lieu d'y entrer."""
    leve = 0.13 * math.sin(math.radians(abs(degres))) + 0.16 * math.sin(math.radians(abs(cote)))
    p.add("corps", rot=(degres, cote, 0), pos=(0, 0, leve))


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _gorge(p, g):
    """La gorge se gonfle de g (0 : au repos ; 1 : le grand ballon du chant)."""
    p.add("gorge", ech=(1 + 0.22 * g, 1 + 0.32 * g, 1 + 0.10 * g))


def repos(t):
    """Le vieux grognon boude : il respire lentement, la gorge palpite sans arrêt, il se détourne encore un peu plus en
    levant le menton, puis nous coule un regard de côté ; il tapote l'herbe du plat de la main droite, agacé, et cligne
    lourdement, comme si ça lui coûtait."""
    p = Pose()
    r = onde(t, 2)
    p.add("corps", ech=(1 + 0.015 * r, 1 + 0.010 * r, 1 + 0.025 * r))
    _gorge(p, 0.12 * (0.5 - 0.5 * math.cos(math.tau * 14 * t)) + 0.25 * cloche(t, 0.32, 0.06))
    boude = cloche(t, 0.55, 0.16)
    p.add("tete", rot=(-4 * boude, 0, -12 * boude + 5 * cloche(t, 0.85, 0.08)))
    tape = max(0.0, onde(t, 16)) * cloche(t, 0.78, 0.09)
    p.add("main_d", rot=(-14 * tape, 0, 0), pos=(0, 0, 0.004 * tape))
    p.ouvert = 1 - cloche(t, 0.14, 0.06) - cloche(t, 0.66, 0.06)
    return p


def avance(t):
    """Il avance d'un bond lourd, sans enthousiasme : il se tasse, pousse des cuisses en levant le museau, décolle à
    peine, les mains d'abord, puis les pieds ; il retombe sur les mains en s'écrasant comme un coussin, et se rassoit."""
    p = Pose()
    air = cloche(t, 0.46, 0.20)
    tasse = cloche(t, 0.14, 0.12) + cloche(t, 0.76, 0.10)
    _bascule(p, -9 * cloche(t, 0.36, 0.13) + 7 * cloche(t, 0.62, 0.10))
    p.add("corps", pos=(0, 0, 0.028 * air - 0.004 * tasse), ech=(1 + 0.05 * tasse, 1 + 0.02 * tasse, 1 - 0.07 * tasse))
    p.add("tete", rot=(4 * cloche(t, 0.62, 0.10) - 3 * cloche(t, 0.36, 0.13), 0, 0))
    for c in ("g", "d"):
        p.add("cuisse_" + c, rot=(14 * cloche(t, 0.40, 0.12), 0, 0))
        p.add("pied_" + c, pos=(0, 0, 0.022 * cloche(t, 0.48, 0.15)), rot=(-18 * cloche(t, 0.42, 0.10), 0, 0))
        p.add("main_" + c, pos=(0, -0.012 * cloche(t, 0.44, 0.15), 0.030 * cloche(t, 0.44, 0.15)), rot=(-12 * cloche(t, 0.44, 0.15), 0, 0))
    _gorge(p, 0.10 * tasse)
    return p


def mange(t):
    """Il guette, se hausse sur les mains et happe deux fois d'un coup sec vers l'herbe devant lui ; puis il avale :
    les yeux rentrent et se ferment (un crapaud avale avec les yeux), la gorge se gonfle, il se rassoit content."""
    p = Pose()
    guette = _plateau(t, 0.34, 0.20, 0.12)
    happe = cloche(t, 0.24, 0.05) + cloche(t, 0.44, 0.05)
    avale = cloche(t, 0.68, 0.08)
    _bascule(p, 5 * guette + 6 * happe)
    p.add("corps", pos=(0, -0.010 * happe, 0.004 * guette))
    p.add("tete", rot=(4 * happe, 0, 0), pos=(0, 0, -0.004 * avale))
    _gorge(p, 0.35 * avale + 0.15 * happe)
    p.ouvert = 1 - 0.95 * avale - cloche(t, 0.90, 0.03)
    return p


def joie(t):
    """Sa joie, bougonne et brève : il se redresse sur ses mains, gonfle la gorge en grand ballon et coasse deux fois,
    tambourine l'herbe des deux mains, lâche un petit bond lourd, et se laisse retomber dans sa pose de boudeur."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85)) if t < 0.85 else 0.0
    croa = cloche(t, 0.24, 0.08, False) + cloche(t, 0.42, 0.08, False)
    saut = cloche(t, 0.66, 0.08, False)
    _bascule(p, -7 * env)
    p.add("corps", pos=(0, 0, 0.032 * saut), ech=(1, 1, 1 + 0.04 * env))
    p.add("tete", rot=(-6 * env, 0, 6 * env))
    _gorge(p, croa)
    for c, phase in (("g", 0.0), ("d", 0.5)):
        tambour = max(0.0, onde(t, 4, phase)) * env
        p.add("main_" + c, pos=(0, 0, 0.012 * tambour + 0.020 * saut), rot=(-10 * tambour, 0, 0))
        p.add("pied_" + c, pos=(0, 0, 0.018 * cloche(t, 0.68, 0.07, False)))
    p.ouvert = 1 - 0.6 * croa
    return p


def dort(t):
    """Il s'affaisse tout à fait, aplati comme un coussin, le menton posé dans l'herbe entre les mains, les yeux
    fermés ; il respire lentement, et la gorge se gonfle doucement à chaque souffle."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", ech=(1.05 + 0.012 * r, 1.03, 0.90 + 0.025 * r))
    p.add("tete", rot=(5, 0, 6), pos=(0, 0, -0.006))
    _gorge(p, 0.10 + 0.08 * r)
    p.add("cuisse_g", rot=(0, 0, 4))
    p.add("cuisse_d", rot=(0, 0, -4))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Crapaud")
