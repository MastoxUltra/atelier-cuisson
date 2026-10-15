"""La poule en peluche, deuxième dessin : une andalouse bleue, la commère de la basse-cour. Un gros œuf de peluche
bleu lavande, le jabot bombé en avant comme une poitrine de cantatrice, tout le corps semé de pastilles de feutrine marine
cousues au point de feston ; une collerette marine festonnée sur les épaules, comme une pèlerine ; une queue de quatre
larges plumes marine dressées en éventail. La tête tendue vers la nouvelle du jour, penchée pour vous fixer d'un œil
rond sous un sourcil levé, le bec entrouvert (elle a toujours quelque chose à dire), une grande crête rouge coquelicot
qui lui retombe sur l'œil d'en face, une patte levée en plein pas.

    python poule.py        fabrique la fiche art/apercus/animaux/poule.png
    (le premier dessin, refusé : poule_ancien.py)
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

LAVANDE = M.hexa("#b3bde6")                   # le plumage : un bleu lavande (le poil le fonce en bleu ardoise doux)
MARINE = M.hexa("#36406e")                    # les écailles, la collerette, la queue, les ailes
COQUELICOT = M.hexa("#e2402e")                # l'accent : la crête et les barbillons
CORNE = M.hexa("#e6b04a")                     # le bec et les pattes
CORPS = Vector((0.0, 0.03, 0.262))
TETE = Vector((-0.014, -0.262, 0.482))
GUETTE = A.repere(TETE, (6, -16, -22), (1.1, 1.1, 1.1))   # la tête : tournée vers sa droite et penchée, pour ne regarder que d'un œil
FIL_DU_COU = [(0, -0.070, 0.330), (0, -0.112, 0.400), (-0.006, -0.172, 0.448), (-0.012, -0.236, 0.470)]   # court et épais : une poule, pas une oie


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du jardin."""
    return GUETTE.to_3x3() @ Vector((x, y, z))


def pied():
    """Un pied à plat : trois doigts devant (vers -Y), un ergot derrière."""
    def doigt(degres, long):
        t = math.radians(degres)
        return A.boule(1.0, 16, 8).etire(0.011, long, 0.009).pose((0.8 * long * math.sin(t), -0.8 * long * math.cos(t), 0), (0, 0, degres))
    return doigt(-32, 0.040) + doigt(0, 0.048) + doigt(32, 0.040) + doigt(180, 0.022)


def pelerine():
    """La collerette : un anneau épais de feutrine marine posé sur les épaules autour du pied du cou, évasé vers le bas
    comme une pèlerine, dont le bord est découpé en dix festons ronds. Dans son repère, Z monte le long du cou."""
    prof = A.profil([(0.112, -0.050), (0.104, -0.020), (0.086, 0.012), (0.066, 0.038), (0.058, 0.046),
                     (0.052, 0.030), (0.066, 0.004), (0.086, -0.026), (0.100, -0.050)], 4)
    m = A.tour(prof, 64).etire(0.74, 0.74, 0.80)
    tour = np.arctan2(m.v[:, 1], m.v[:, 0])
    bas = K.lisse((-0.010 - m.v[:, 2]) / 0.040)
    m.v[:, 2] -= 0.026 * np.abs(np.sin(tour * 5)) * bas         # les festons
    return m


def construire():
    a = K.Animal("poule")
    a.taille = 0.52
    a.tete = GUETTE @ Vector((0.02, -0.05, 0.0))

    # ----- le corps : un gros œuf, le jabot bombé très en avant et haut, le croupion qui remonte vers la queue -----
    def coque(v):
        v = K.bosse(v, (0, -0.75, -0.10), 0.26, 0.30)       # le jabot de cantatrice
        v = K.bosse(v, (0, -0.30, -0.85), 0.08, 0.40)       # le ventre plein
        arriere = K.lisse((v[:, 1] - 0.15) / 0.85)
        s = v * [0.128, 0.162, 0.134]
        s[:, 0] *= 1 - 0.38 * arriere
        s[:, 2] = s[:, 2] * (1 - 0.40 * arriere) + 0.090 * arriere
        return s
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    G.sillons(corps, [14], 0.005, 1.1)
    a.piece("corps", corps, LAVANDE, pos=CORPS)
    a.couture("dos", "corps", 14, 0.62, 0.98, fil=MARINE)

    # ----- les écailles : des demi-lunes de feutrine marine semées en quinconce sur les flancs et le jabot, de plus en
    #       plus petites vers le ventre ; chacune tenue au point de feston -----
    for i in range(64):
        z = 1 - 2 * (i + 0.5) / 64
        d = Vector((math.sqrt(1 - z * z) * math.cos(2.39996 * i), math.sqrt(1 - z * z) * math.sin(2.39996 * i), z))
        if d.x > 0.12 and -0.60 < z < 0.50 and d.angle(Vector((0, 0.9, 0.45))) > 0.55 and d.angle(Vector((0, -0.75, 0.66))) > 0.50:
            a.rustine("ecaille%d" % i, "corps", CORPS, d, 0.17 if z > 0 else 0.14, MARINE, 0.003, 12, fil=LAVANDE, paire=True)

    # ----- la queue : quatre larges plumes marine dressées en éventail, la pointe recourbée vers l'arrière -----
    pq = A.profil([(0, 0), (0.024, 0.012), (0.046, 0.080), (0.054, 0.160), (0.040, 0.235), (0, 0.270)], 6)

    def plume(long):
        m = A.tour(pq, 32).etire(1.0, 0.34, long)
        return m.sculpte(lambda v: v + np.outer((v[:, 2] / 0.270) ** 2, [0, 0.090, 0]))
    croupion = a.trace("corps", CORPS, [(0, 0.80, 0.60)], -0.03)[0]
    a.piece("plume", plume(1.05), MARINE, pos=croupion, rot=(-4, 0, 0))
    a.piece("plume_moyenne", plume(0.96), MARINE, pos=croupion + Vector((0.014, 0.010, -0.004)), rot=(-22, 16, 0), paire=True)
    a.piece("plume_basse", plume(0.82), MARINE, pos=croupion + Vector((0.026, 0.022, -0.014)), rot=(-44, 26, 0), paire=True)

    # ----- le cou tendu en avant, et la pèlerine marine sur les épaules -----
    fil = A.courbe(FIL_DU_COU, 6)
    a.piece("cou", A.tube(fil, lambda t: 0.070 - 0.040 * t + 0.016 * t * t, 20), LAVANDE)
    pied_cou = Vector(fil[len(fil) * 2 // 5])
    sens = (Vector(fil[8]) - Vector(fil[0])).normalized()
    a.piece("pelerine", pelerine(), MARINE, mat=A.cadre(pied_cou, sens, (0, 1, 0)), poil=False)

    # ----- la tête : une petite boule ; un grand œil vivant du côté qu'elle nous tend, sous un sourcil levé -----
    a.piece("tete", A.boule(1.0, 56, 28).etire(0.056, 0.062, 0.055), LAVANDE, mat=GUETTE)
    for nom, cote in (("g", 1), ("d", -1)):
        p, n = a.surface("tete", TETE, vers(0.86 * cote, -0.42, 0.22))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0155)
    sourcil = a.trace("tete", TETE, [vers(0.70, -0.30 + 0.30 * u, 0.62 + 0.10 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 6)])
    a.broderie("sourcil", A.courbe(sourcil, 4), 0.0030, MARINE)

    # ----- le bec entrouvert, en feutrine corne -----
    dessus_ = A.tour(A.profil([(0, 0), (0.021, 0.004), (0.017, 0.020), (0.008, 0.044), (0, 0.056)], 5), 28).etire(1.0, 0.80, 1.0)
    a.piece("bec", dessus_, CORNE, pos=GUETTE @ Vector((0, -0.050, 0.0)), rot=A.viser(vers(0, -1, -0.04)), poil=False)
    dessous_ = A.tour(A.profil([(0, 0), (0.017, 0.004), (0.013, 0.016), (0.006, 0.032), (0, 0.040)], 5), 28).etire(1.0, 0.60, 1.0)
    a.piece("bec_bas", dessous_, CORNE, pos=GUETTE @ Vector((0, -0.048, -0.010)), rot=A.viser(vers(0, -1, -0.52)), poil=False)

    # ----- la crête : une grande crête simple à cinq dents, qui part droite puis retombe sur l'œil d'en face -----
    def lame(v):
        s = v.copy()
        dents = 0.30 * np.abs(np.sin(5 * math.pi * (v[:, 1] + 1) / 2)) * K.lisse(v[:, 2])
        s[:, 2] = v[:, 2] * (1 + dents)
        return s
    def retombe(v):                                       # au-dessus de sa base, elle se couche vers sa droite (-X)
        s = v.copy()
        h = np.maximum(v[:, 2] - 0.004, 0.0)
        s[:, 0] -= 9.0 * h ** 2
        s[:, 2] -= 3.0 * h ** 2
        return s
    crete = A.boule(1.0, 40, 20).sculpte(lame).etire(0.010, 0.058, 0.036).sculpte(retombe)
    a.piece("crete", crete, COQUELICOT, mat=GUETTE @ A.repere((0, -0.004, 0.050)), poil=False)

    # ----- les barbillons : deux gouttes coquelicot qui pendent sous le bec -----
    def goutte(v):
        s = v.copy()
        k = 0.50 + 0.50 * K.lisse((0.5 - v[:, 2]) / 1.3)
        s[:, 0] *= k
        s[:, 1] *= k
        return s
    for nom, cote in (("g", 1), ("d", -1)):
        a.piece("barbillon_" + nom, A.boule(1.0, 24, 12).sculpte(goutte).etire(0.017, 0.018, 0.040), COQUELICOT,
                mat=GUETTE @ A.repere((0.016 * cote, -0.040, -0.064), (0, -12 * cote, 0)), poil=False)

    # ----- les ailes : deux galets marine serrés sur les flancs, la pointe relevée, la tranche soulignée d'un fil -----
    def galet(v):
        s = K.emousse(v, 0.85)
        pointe = K.lisse((v[:, 1] + 0.2) / 1.2)
        s[:, 2] = s[:, 2] * (1 - 0.45 * pointe) + 0.22 * pointe
        return s
    AILE = A.repere((0.118, 0.034, 0.276), (6, 0, 8))
    a.piece("aile", A.boule(1.0, 40, 20).sculpte(galet).etire(0.022, 0.098, 0.068), MARINE, mat=AILE, paire=True)
    a.couture("aile_bord", "aile", 10, 0.12, 0.88, "droit", fil=LAVANDE, paire=True)

    # ----- les culottes : deux cuisses de peluche ; celle de droite part en avant avec la patte levée -----
    a.piece("cuisse_g", A.boule(1.0, 32, 16).etire(0.044, 0.052, 0.062), LAVANDE, pos=(0.060, 0.045, 0.186))
    a.piece("cuisse_d", A.boule(1.0, 32, 16).etire(0.044, 0.052, 0.066), LAVANDE, pos=(-0.062, -0.022, 0.186), rot=(-38, 0, 0))

    # ----- les pattes en feutrine corne : la gauche pousse au sol, la droite est levée, les doigts pendants -----
    appui = A.tube(A.courbe([(0.058, 0.045, 0.19), (0.058, 0.062, 0.10), (0.058, 0.070, 0.010)], 5), 0.013, 12)
    a.piece("patte_g", appui + pied().pose((0.058, 0.070, 0.009), (0, 0, 8)), CORNE, poil=False)
    levee = A.tube(A.courbe([(-0.060, -0.010, 0.19), (-0.062, -0.098, 0.142), (-0.062, -0.102, 0.085)], 5), 0.013, 12)
    a.piece("patte_d", levee + pied().pose((-0.062, -0.102, 0.085), (32, 0, -8)), CORNE, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py poule). Les mesures sont celles du modèle, avant a.taille.
# Le modèle est saisi en plein pas : la patte droite levée devant, les doigts pendants, la tête tournée vers sa droite.
# Chaque patte a son os à elle (pas de miroir) et pend à la racine, comme celles du canard : un pied posé ne bouge pas
# quand le corps roule. Chaque patte a deux os : la cuisse (à la hanche) et le pied (à la cheville) ; la pièce passe de
# l'un à l'autre juste au-dessus du pied. La patte levée est plus courte que l'autre (elle est pliée) : pour la poser,
# on la redresse sous la hanche et on la descend de 4 cm, la culotte de plumes la cache.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.020, 0.200)),            # entre les deux hanches : elle roule et se penche autour
    ("cou", "corps", (0.0, -0.070, 0.330)),              # le pied du cou, enfoui dans le jabot
    ("tete", "cou", (0.010, -0.216, 0.466)),             # la nuque
    ("bec_bas", "tete", (-0.029, -0.311, 0.466)),        # la charnière du bec
    ("queue", "corps", (-0.006, 0.155, 0.358)),          # le croupion, d'où partent les quatre plumes
    ("aile_G", "corps", (0.117, -0.040, 0.305)),         # l'épaule : l'aile part de là vers l'arrière
    ("patte_g", "racine", (0.058, 0.045, 0.190)),        # la hanche de la patte d'appui
    ("pied_g", "patte_g", (0.058, 0.070, 0.012)),        # sa cheville, au ras du sol
    ("patte_d", "racine", (-0.060, -0.010, 0.190)),      # la hanche de la patte levée
    ("pied_d", "patte_d", (-0.062, -0.102, 0.085)),      # sa cheville, en l'air
]


def _patte(os_haut, os_bas, cheville_z):
    """Une patte : la cuisse jusqu'au-dessus de la cheville, puis le pied (les doigts et l'ergot), en fondu sur 2 cm."""
    def poids(points, cote):
        w = K.lisse((cheville_z + 0.016 - points[:, 2]) / 0.020)
        return {os_haut: 1 - w, os_bas: w}
    return poids


def _pelerine(points, cote):
    """La pèlerine est cousue sur les épaules, autour du cou : elle suit le cou, mais à moitié seulement."""
    return {"cou": np.full(len(points), 0.6), "corps": np.full(len(points), 0.4)}


PORTEURS = [("corps", "corps"), ("dos", "corps"), ("ecaille", "corps"), ("cuisse", "corps"),
            ("plume", "queue"), ("pelerine", _pelerine, "cou"), ("cou", "cou"),
            ("tete", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("crete", "tete"), ("barbillon", "tete"),
            ("bec_bas", "bec_bas"), ("bec", "tete"),
            ("aile", "aile", True),
            ("patte_g", _patte("patte_g", "pied_g", 0.012), "patte_g"), ("patte_d", _patte("patte_d", "pied_d", 0.085), "patte_d"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _douce(x):
    x = borne(x)
    return x * x * (3 - 2 * x)


def _pose_d(p, x):
    """La patte droite : levée comme sur le modèle (x = 0), ou posée à plat sous la hanche (x = 1) : la cuisse se
    redresse, la patte descend de 4 cm, le pied se remet à plat."""
    p.add("patte_d", rot=(41 * x, 0, 0), pos=(0, 0.020 * x, -0.041 * x))
    p.add("pied_d", rot=(-73 * x, 0, 0))


def _leve_g(p, x):
    """La patte gauche : posée comme sur le modèle (x = 0), ou levée devant, les doigts qui pendent (x = 1)."""
    p.add("patte_g", rot=(-28 * x, 0, 0), pos=(0, 0, 0.030 * x))
    p.add("pied_g", rot=(40 * x, 0, 0))


def _ailes(p, leve):
    """Les deux ailes se décollent de « leve » degrés autour de l'épaule : le bout monte et s'écarte du corps."""
    p.paire("aile", rot=(0.55 * leve, -0.4 * leve, -0.6 * leve))


def _campe(p):
    """La pose d'attente : les deux pieds au sol, la patte droite un peu devant."""
    _pose_d(p, 1.0)
    return p


def repos(t):
    """La commère aux aguets : elle respire, tourne la tête par à-coups pour fixer d'un œil, puis de l'autre ;
    elle hésite, lève la patte droite et la garde en l'air (la pose du modèle), la repose ; puis elle caquette, le bec
    qui claque, la tête tendue vers la nouvelle du jour ; elle cligne."""
    p = _campe(Pose())
    r = onde(t, 2)
    droite = _plateau(t, 0.20, 0.07, 0.025)              # des à-coups : la tête se pose, reste, repart
    gauche = _plateau(t, 0.38, 0.06, 0.025)
    hesite = _plateau(t, 0.64, 0.08, 0.05)
    caquet = cloche(t, 0.88, 0.07)
    p.add("corps", ech=(1 + 0.012 * r, 1 + 0.008 * r, 1 + 0.018 * r))
    p.add("cou", rot=(5 * caquet + 3 * hesite, 0, -6 * droite + 6 * gauche))
    p.add("tete", rot=(-4 * caquet, -10 * droite + 12 * gauche, -26 * droite + 30 * gauche))
    _pose_d(p, -hesite)                                  # la patte remonte : la pose du modèle
    p.add("bec_bas", rot=(14 * caquet * abs(onde(t, 16)), 0, 0))
    _ailes(p, 5 * cloche(t, 0.52, 0.04))
    p.add("queue", rot=(0, 0, 10 * cloche(t, 0.06, 0.05) * onde(t, 12)))
    p.ouvert = 1 - cloche(t, 0.10, 0.02) - cloche(t, 0.47, 0.02)
    return p


def _pas(u):
    """Une patte à la phase u de son pas : posée de 0 à 0,6 (elle glisse de l'avant vers l'arrière pendant qu'elle porte :
    la poule avance), levée de 0,6 à 1 (elle revient devant). Rend (combien elle est levée, où elle en est : -1 devant,
    1 derrière)."""
    u %= 1.0
    if u < 0.6:
        return 0.0, -1 + 2 * u / 0.6
    x = (u - 0.6) / 0.4
    return math.sin(math.pi * x), 1 - 2 * _douce(x)


def avance(t):
    """Sa marche : de grands pas posés, le pied levé haut et les doigts qui pendent, le corps qui roule sur la patte qui
    porte ; et la tête qui pique en avant à chaque pas : elle reste sur place pendant que le corps passe, puis repart d'un
    coup. À t = 0, c'est la pose du modèle (la patte droite levée devant)."""
    p = Pose()
    leve_d, glisse_d = _pas(t + 0.8)
    leve_g, glisse_g = _pas(t + 0.3)
    _pose_d(p, 1 - leve_d)
    p.add("patte_d", pos=(0, 0.030 * glisse_d, 0))
    _leve_g(p, leve_g)
    p.add("patte_g", pos=(0, 0.030 * glisse_g, 0))
    p.add("corps", rot=(0, 4 * math.cos(math.tau * t), 3 * math.cos(math.tau * t)),
          pos=(0, 0, 0.006 * (1 - math.cos(2 * math.tau * t)) / 2))
    v = (2 * t) % 1.0                                    # deux pas, deux coups de tête
    pique = 1 - 2 * v / 0.7 if v < 0.7 else -1 + 2 * _douce((v - 0.7) / 0.3)
    p.add("cou", rot=(7 * pique, 0, 0))
    p.add("tete", rot=(-7 * pique, 0, 0))
    _ailes(p, 3)
    p.add("queue", rot=(0, 0, 5 * math.cos(math.tau * t)))
    return p


def mange(t):
    """Elle gratte deux fois la terre de la patte droite, recule d'un pas pour voir, puis pique du bec, quatre coups secs
    (le bec s'ouvre entre deux), et relève la tête pour avaler."""
    p = _campe(Pose())
    gratte = cloche(t, 0.10, 0.05) + cloche(t, 0.21, 0.05)
    bas = _plateau(t, 0.60, 0.15, 0.13)
    coups = max(0.0, onde(t, 12)) ** 2 * _plateau(t, 0.60, 0.13, 0.04)
    avale = cloche(t, 0.93, 0.05)
    p.add("patte_d", rot=(24 * gratte, 0, 0), pos=(0, 0, 0.012 * gratte))
    p.add("corps", rot=(28 * bas, 0, 0))
    p.add("cou", rot=(52 * bas + 8 * coups - 6 * avale, 0, -6 * bas))
    p.add("tete", rot=(20 * bas + 8 * coups - 12 * avale, 0, 0))
    p.add("bec_bas", rot=(10 * max(0.0, -onde(t, 12)) * bas + 8 * avale, 0, 0))
    _ailes(p, 4 * bas)
    p.add("queue", rot=(8 * bas, 0, 0))
    p.ouvert = 1 - cloche(t, 0.30, 0.02) - cloche(t, 0.97, 0.02)
    return p


def joie(t):
    """Sa fête à elle : elle saute sur place en battant des ailes à grands coups, la tête au ciel, le bec grand ouvert
    (elle caquette à tue-tête), la queue qui frétille ; puis elle retombe, se lisse et reprend sa pose d'attente."""
    p = repos(0.0)
    env = math.sin(math.pi * borne(t / 0.85)) if t < 0.85 else 0.0
    saut = abs(onde(t, 3)) * env
    bat = onde(t, 8) * env
    p.add("corps", pos=(0, 0, 0.050 * saut + 0.010 * env), rot=(-10 * env, 0, 0))
    for nom in ("patte_g", "patte_d"):
        p.add(nom, pos=(0, 0, 0.050 * saut + 0.010 * env))
    p.add("pied_g", rot=(25 * saut, 0, 0))
    p.add("pied_d", rot=(25 * saut, 0, 0))
    p.add("cou", rot=(-10 * env, 0, 0))
    p.add("tete", rot=(-18 * env, 0, 8 * onde(t, 3) * env))
    p.add("bec_bas", rot=(22 * env * (0.5 + 0.5 * abs(onde(t, 8))), 0, 0))
    _ailes(p, 45 * env + 30 * bat)
    p.add("queue", rot=(10 * env, 0, 15 * onde(t, 6) * env))
    return p


def dort(t):
    """Elle couve : posée à plat sur le ventre, gonflée en boule, les pattes rentrées sous les plumes, la tête rentrée
    dans les épaules et le bec sur le jabot, les yeux fermés ; elle respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.105), ech=(1.06 + 0.012 * r, 1.02, 0.95 + 0.022 * r))
    p.add("patte_d", rot=(41, 0, 0))                     # la patte droite repliée sous la hanche, sans descendre
    p.add("pied_d", rot=(-73, 0, 0))
    for nom in ("patte_g", "patte_d"):
        p.add(nom, ech=(1, 1, 0.35))
    p.add("cou", rot=(18, 0, -8), pos=(0, 0.035, -0.030))
    p.add("tete", rot=(24, 6, 14))
    _ailes(p, 1 + 1.5 * r)
    p.add("queue", rot=(-6, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Poule")
