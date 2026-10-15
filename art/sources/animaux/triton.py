"""Le triton en peluche : un petit dragon de mare. Le dos charbon ardoise, le ventre orange feu semé de pois noirs, une
crête de feutrine en dents de scie cousue au fil orange de la nuque au bout de la queue, la queue en lame avec son
reflet nacré. Le corps en S, dressé sur ses pattes avant, la tête haute, l'œil sévère : il est très fier de sa crête.

    python triton.py        fabrique la fiche art/apercus/animaux/triton.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K

CHARBON = np.array(M.hexa("#535a6c"))         # le dos : un charbon qui tire sur l'ardoise (le poil le fonce beaucoup)
FEU = np.array(M.hexa("#ff7a1a"))             # le ventre orange feu
NACRE = np.array(M.hexa("#c9d3e0"))           # le reflet nacré le long de la queue
ARDOISE = M.hexa("#5f6b82")                   # la feutrine de la crête
NUIT = M.hexa("#26242b")                      # les pois du ventre
COTES = 48

# Le fil du corps, du bout de la queue au bout du nez : la queue part sur sa gauche en arc et se relève
# (sa lame se montre de profil), le corps file un peu de biais, puis le poitrail se dresse, le cou monte en col de cygne
# et la tête, bien à plat tout en haut, se tourne vers celui qui la regarde.
CHEMIN = [(0.218, 0.150, 0.088), (0.188, 0.192, 0.052), (0.135, 0.215, 0.032), (0.075, 0.205, 0.028), (0.030, 0.160, 0.029),
          (0.015, 0.100, 0.034), (0.000, 0.035, 0.040), (-0.030, -0.025, 0.060), (-0.040, -0.070, 0.105), (-0.040, -0.100, 0.148),
          (-0.028, -0.135, 0.166), (-0.008, -0.165, 0.170)]
FIL = A.courbe(CHEMIN, 16)
FAIT = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(FIL, axis=0), axis=1))])     # la distance parcourue jusqu'à chaque point
SENS = np.gradient(FIL, FAIT, axis=0)
LONG = float(FAIT[-1])
BASSIN, EPAULES = 0.50 * LONG, 0.70 * LONG    # là où s'attachent les pattes, le long du fil
# le rayon du boudin le long du fil (en fraction de la longueur) : queue effilée, corps dodu, cou fin, tête ronde
PROFIL = A.profil([(0, 0)] + [(r, f * LONG) for f, r in ((0.04, 0.006), (0.15, 0.012), (0.30, 0.018), (0.42, 0.025), (0.50, 0.034), (0.60, 0.038),
                                                        (0.70, 0.035), (0.80, 0.026), (0.87, 0.025), (0.93, 0.032), (0.985, 0.023))] + [(0, LONG)], 12)


def rayon(s):
    return np.interp(s, PROFIL[:, 1], PROFIL[:, 0])


def large(s):
    """Le boudin est écrasé en lame le long de la queue, élargi et aplati à la tête : ce par quoi multiplier sa largeur."""
    return 0.50 + 0.55 * K.lisse((s / LONG - 0.25) / 0.22) + 0.22 * K.lisse((s / LONG - 0.86) / 0.06)


def haut(s):
    """... et ce par quoi multiplier sa hauteur."""
    return 1.50 - 0.52 * K.lisse((s / LONG - 0.25) / 0.22) - 0.10 * K.lisse((s / LONG - 0.86) / 0.06)


def repere(s):
    """En un point du fil : le centre du boudin, la direction où il va, son dos (vers le ciel) et son flanc gauche."""
    centre = np.stack([np.interp(s, FAIT, FIL[:, k]) for k in range(3)], axis=-1)
    avant = np.stack([np.interp(s, FAIT, SENS[:, k]) for k in range(3)], axis=-1)
    avant = avant / np.linalg.norm(avant, axis=-1, keepdims=True)
    dos = np.array([0.0, 0.0, 1.0]) - avant[..., 2:3] * avant
    dos = dos / np.linalg.norm(dos, axis=-1, keepdims=True)
    return centre, avant, dos, np.cross(dos, avant)


def couche(v):
    """Couche le boudin droit le long du fil : le dos de la pièce (son +Y) reste tourné vers le ciel."""
    s = np.clip(v[:, 2], 0.0, LONG)
    centre, _avant, dos, flanc = repere(s)
    return centre + (v[:, 0] * large(s))[:, None] * flanc + (v[:, 1] * haut(s))[:, None] * dos


def crete(debut, fin, hauteur, dent=0.034, epais=0.005, pas=0.002):
    """La crête : un ruban de feutrine planté debout dans la couture du dos, de « debut » à « fin » le long du fil,
    découpé en dents couchées vers l'arrière. hauteur(s) donne sa hauteur à chaque endroit."""
    s = np.arange(debut, fin, pas)
    centre, _avant, dos, flanc = repere(s)
    pied = centre + dos * (rayon(s) * haut(s) - 0.005)[:, None]
    scie = 0.30 + 0.70 * (1.0 - ((s - debut) / dent) % 1.0) ** 0.8
    cime = pied + dos * (0.005 + hauteur(s) * scie)[:, None]
    n = len(s)
    points = np.concatenate([pied - flanc * epais * 0.5, pied + flanc * epais * 0.5, cime - flanc * epais * 0.22, cime + flanc * epais * 0.22])
    faces = []
    for k in range(n - 1):
        g0, d0, g1, d1 = k, n + k, 2 * n + k, 3 * n + k
        faces += [(g0 + 1, g0, g1, g1 + 1), (d0, d0 + 1, d1 + 1, d1), (g1, d1, d1 + 1, g1 + 1)]
    faces += [(0, n, 3 * n, 2 * n), (2 * n - 1, n - 1, 3 * n - 1, 4 * n - 1)]
    return A.Maille(points, faces)


def boudin(points, rayons, cotes=14):
    """Un membre : un boudin lisse qui passe par les points, avec le rayon voulu à chacun."""
    n = len(points) - 1
    return A.tube(A.courbe(points, 8), lambda t: float(np.interp(t * n, range(n + 1), rayons)), cotes)


def construire():
    a = K.Animal("triton")
    a.taille = 0.40

    # ----- le corps : un boudin tourné tout droit, peint par quartiers (le ventre feu, le reflet de la queue),
    #       puis couché le long de son fil -----
    corps = A.tour(PROFIL, COTES)
    corps.teinte = np.tile(CHARBON, (len(corps.v), 1))
    for anneau in corps.anneaux:
        for j, i in enumerate(anneau if len(anneau) > 1 else []):
            c = 360.0 * (j + 0.5) / COTES                              # le milieu de la case que ce point colore
            angle = c if c <= 90 else 180 - c if c <= 270 else c - 360
            f = corps.v[i, 2] / LONG
            ventre = 8 - 26 * float(K.lisse((f - 0.84) / 0.07))                # sous la tête, le feu ne garde que le menton
            corps.teinte[i] = FEU if angle <= ventre else NACRE if angle <= 24 and 0.05 < f < 0.40 else CHARBON
    a.piece("corps", corps.sculpte(couche), None)
    a.couture("echine", "corps", 12, 0.09, 0.74, style="droit", fil=tuple(FEU), large=0.017, haut=0.004, pas=0.020)   # la crête est cousue au fil orange

    # ----- la crête : haute sur le dos, un creux au bassin, puis elle repart le long de la queue -----
    def hauteur(s):
        return np.interp(s / LONG, [0.02, 0.06, 0.20, 0.38, 0.49, 0.60, 0.74, 0.84, 0.885], [0.0, 0.014, 0.026, 0.026, 0.012, 0.040, 0.044, 0.024, 0.0])
    a.piece("crete", crete(0.02 * LONG, 0.885 * LONG, hauteur), ARDOISE, poil=False)

    # ----- les pois noirs du ventre : sur le poitrail dressé et le long des flancs -----
    for k, (f, cote, bas, ouvert) in enumerate(((0.83, 0.25, -0.95, 0.30), (0.79, -0.55, -0.80, 0.24), (0.76, 0.85, -0.50, 0.34), (0.71, 0.30, -0.95, 0.26),
                                                (0.66, 0.90, -0.42, 0.27), (0.60, 0.80, -0.58, 0.34), (0.54, 0.92, -0.38, 0.24), (0.905, 0.45, -0.88, 0.22),
                                                (0.63, -0.85, -0.50, 0.30), (0.74, -0.90, -0.40, 0.26), (0.47, 0.90, -0.40, 0.26))):
        centre, _avant, dos, flanc = (Vector(q) for q in repere(f * LONG))
        a.rustine("pois%d" % k, "corps", centre, flanc * cote + dos * bas, ouvert, NUIT, 0.0022, 0)

    # ----- le visage : deux boutons sur un cerne nacré, coupé droit en haut comme une paupière sévère -----
    centre, avant, dos, flanc = (Vector(q) for q in repere(0.94 * LONG))
    a.tete = centre + avant * 0.030 + dos * 0.006
    for nom, cote, coupe in (("_G", 1, 315), ("_D", -1, 225)):
        vers = flanc * (0.86 * cote) + dos * 0.36 + avant * 0.36
        a.rustine("cerne" + nom, "corps", centre, vers, lambda th: 0.50 * (1 - 0.42 * max(0.0, math.cos(th - math.radians(coupe))) ** 2),
                  tuple(NACRE), 0.0022, 0)
        p, n = a.surface("corps", centre, vers)
        a.bouton("oeil" + nom, p + n * 0.0025, n, 0.0125)

    # ----- les pattes : courtes, le coude sorti ; celles de devant tendues, pour porter le poitrail -----
    for nom, s, coude, pied, rayons in (("avant", EPAULES, (0.056, -0.004, -0.012), (0.066, 0.030), (0.016, 0.013, 0.010)),
                                        ("arriere", BASSIN, (0.056, 0.018, 0.004), (0.072, -0.004), (0.017, 0.013, 0.010))):
        centre, avant, dos, flanc = (Vector(q) for q in repere(s))
        a_plat = Vector((avant.x, avant.y, 0)).normalized()
        for cote, lettre in ((1, "_G"), (-1, "_D")):
            lat = flanc * cote
            sol = centre + lat * pied[0] + a_plat * pied[1]
            sol.z = 0.010
            a.piece("patte_%s%s" % (nom, lettre), boudin([centre + lat * 0.012, centre + lat * coude[0] + a_plat * coude[1] + Vector((0, 0, coude[2])), sol], rayons), tuple(CHARBON))
            vers = (a_plat + lat * 0.45).normalized()
            doigts = A.boule(1.0, 16, 8).etire(0.013, 0.013, 0.007).pose(sol + vers * 0.004 - Vector((0, 0, 0.003)))
            for angle, long in ((-48, 0.026), (-16, 0.034), (16, 0.034), (48, 0.026)):
                d = A.tourne((0, 0, 1), angle, vers)
                doigts = doigts + A.tube([sol - Vector((0, 0, 0.002)), sol + d * long - Vector((0, 0, 0.004))], lambda t: 0.0056 - 0.0020 * t, 10)
            a.piece("pied_%s%s" % (nom, lettre), doigts, tuple(FEU), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py triton). Les mesures sont celles du modèle, avant a.taille.

from poses import Pose, borne, cloche, onde

# Le corps, la crête et la queue sont un seul boudin couché le long du fil : sept os se le partagent, chacun son tronçon.
# Le corps tient le bassin ; de là, une chaîne file vers le bout de la queue (queue1, queue2, queue3), l'autre vers le nez
# (poitrail, cou, tete). Le fil n'est pas symétrique (la queue part sur sa gauche, la tête est tournée) : les pattes ont
# chacune leur os, nommé à la main en minuscules, posé au départ de son boudin.
# Les pivots de la queue sont du côté du corps : chaque os de la queue porte le tronçon qui va vers le bout.
TRONCONS = [("queue3", 0.00, 0.15), ("queue2", 0.15, 0.29), ("queue1", 0.29, 0.43), ("corps", 0.43, 0.60),
            ("poitrail", 0.60, 0.76), ("cou", 0.76, 0.86), ("tete", 0.86, 1.00)]     # (os, du, au) en part de la longueur
PIVOTS = {"queue3": 0.15, "queue2": 0.29, "queue1": 0.43, "corps": 0.50, "poitrail": 0.60, "cou": 0.76, "tete": 0.86}


def _au_fil(f):
    """Le centre du boudin à la part f de sa longueur : le pivot d'un os."""
    return tuple(round(float(x), 4) for x in repere(f * LONG)[0])


def _depart(s, cote):
    """Le départ du boudin d'une patte, là où il entre dans le corps : son pivot."""
    centre, _avant, _dos, flanc = repere(s)
    return tuple(round(float(x), 4) for x in centre + flanc * (0.012 * cote))


def souple(points, cote):
    """Chaque point du boudin suit le tronçon où il tombe sur le fil ; deux tronçons voisins se passent la main en douceur."""
    if cote == "_D":
        points = points * [-1, 1, 1]                  # l'usine passe les pièces de droite en miroir : on les remet à leur place
    f = FAIT[np.linalg.norm(points[:, None, :] - FIL[None, :, :], axis=2).argmin(axis=1)] / LONG
    montees = [np.ones(len(points))] + [K.lisse((f - du + 0.03) / 0.06) for _o, du, _au in TRONCONS[1:]] + [np.zeros(len(points))]
    return {o: montees[i] - montees[i + 1] for i, (o, _du, _au) in enumerate(TRONCONS)}


def _cote(os_):
    """Une pièce d'un côté (patte_avant_G, pied_arriere_D...) portée tout entière par l'os de son côté."""
    return lambda points, cote: {os_ + "_" + cote[1:].lower(): np.ones(len(points))}


OS = [("racine", None, (0, 0, 0)), ("corps", "racine", _au_fil(PIVOTS["corps"]))]
OS += [(o, parent, _au_fil(PIVOTS[o])) for o, parent in (("queue1", "corps"), ("queue2", "queue1"), ("queue3", "queue2"),
                                                          ("poitrail", "corps"), ("cou", "poitrail"), ("tete", "cou"))]
OS += [("patte_avant_g", "poitrail", _depart(EPAULES, 1)), ("patte_avant_d", "poitrail", _depart(EPAULES, -1)),   # les épaules
       ("patte_arriere_g", "corps", _depart(BASSIN, 1)), ("patte_arriere_d", "corps", _depart(BASSIN, -1))]      # les hanches
# Tout ce qui est sur le boudin est rangé avec la tête : les yeux sont cousus sur lui, et leurs paupières prennent
# pour parent l'os où est rangée la pièce voisine ; rangées avec « corps », elles resteraient au bassin quand il tourne la tête.
PORTEURS = [("corps", souple, "tete"), ("crete", souple, "tete"), ("echine", souple, "tete"), ("pois", souple, "tete"),
            ("cerne", souple, "tete"), ("oeil", "tete"),
            ("patte_avant", _cote("patte_avant")), ("pied_avant", _cote("patte_avant")),
            ("patte_arriere", _cote("patte_arriere")), ("pied_arriere", _cote("patte_arriere")),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def pas(p, t, avance, leve, retard=0.0):
    """La marche en diagonale : l'avant gauche et l'arrière droite ensemble, puis les deux autres. Chaque patte tourne
    autour de son épaule (« avance » degrés de part et d'autre) et décolle son pied quand elle revient vers l'avant."""
    for o, cote, phase in (("patte_avant_g", 1, 0.0), ("patte_arriere_d", -1, retard), ("patte_avant_d", -1, 0.5), ("patte_arriere_g", 1, 0.5 + retard)):
        u = math.tau * (t - phase)
        p.add(o, rot=(0, -cote * leve * max(0.0, math.sin(u)), cote * avance * math.cos(u)))


def fouette(p, t, force, tours=1, phase=0.0):
    """Une vague qui court le long de la queue, de plus en plus large vers le bout."""
    for i, o in enumerate(("queue1", "queue2", "queue3")):
        p.add(o, rot=(0, 0, force * (0.5 + 0.45 * i) * onde(t, tours, phase - 0.12 * (i + 1))))


def repos(t):
    """Dressé sur ses pattes de devant, il toise : il respire, tourne lentement la tête vers sa droite puis revient,
    cligne d'un air sévère ; puis il fait la roue : la queue se plaque en arc sur son flanc et vibre, pour montrer sa crête."""
    p = Pose()
    r = onde(t, 2)
    toise = cloche(t, 0.22, 0.14)
    roue = cloche(t, 0.68, 0.18)
    vibre = roue * onde(t, 24)
    p.add("corps", ech=(1 + 0.014 * r, 1 + 0.014 * r, 1 + 0.010 * r))
    p.add("poitrail", rot=(-2 * r - 4 * roue, 0, 0))
    p.add("cou", rot=(0, 0, -8 * toise + 4 * roue))
    p.add("tete", rot=(2 * r, 0, -16 * toise + 6 * roue))
    p.add("queue1", rot=(4 * roue, 0, -14 * roue))                 # la queue se replie vers sa gauche et se lève en lame
    p.add("queue2", rot=(6 * roue, 0, -22 * roue + 6 * vibre))
    p.add("queue3", rot=(8 * roue, 0, -24 * roue + 12 * vibre))
    fouette(p, t, 4 * (1 - roue), 1)
    p.ouvert = borne(1 - cloche(t, 0.40, 0.02) - cloche(t, 0.90, 0.02))
    return p


def avance(t):
    """Il se tortille : l'échine ondule en S, les pattes marchent en diagonale, la queue serpente derrière lui ;
    la tête, elle, garde son cap, très digne."""
    p = Pose()
    s = onde(t, 1)
    p.add("corps", rot=(0, 0, 10 * s))
    p.add("poitrail", rot=(0, 0, -18 * s))
    p.add("cou", rot=(0, 0, 4 * s))
    p.add("tete", rot=(0, 0, 4 * s))
    pas(p, t, 24, 22)
    fouette(p, t, 22, 1, 0.0)
    return p


def mange(t):
    """Il repère un ver, baisse le nez, le happe d'un coup sec et l'avale en trois coups de gorge, la tête qui tressaute."""
    p = Pose()
    baisse = cloche(t, 0.45, 0.32)
    happe = cloche(t, 0.30, 0.05)
    gobe = (cloche(t, 0.50, 0.04) + cloche(t, 0.60, 0.04) + cloche(t, 0.70, 0.04)) * baisse
    p.add("poitrail", rot=(14 * baisse + 6 * happe, 0, 0))
    for o in ("patte_avant_g", "patte_avant_d"):                   # les coudes plient : les pieds restent dans l'herbe
        p.add(o, rot=(-14 * baisse - 6 * happe, 0, 0), ech=(1, 1, 1 - 0.30 * baisse - 0.10 * happe))
    p.add("cou", rot=(22 * baisse + 10 * happe, 0, 0))
    p.add("tete", rot=(18 * baisse + 12 * happe - 10 * gobe, 0, 0))
    fouette(p, t, 6, 2)
    p.ouvert = borne(1 - 0.6 * gobe - cloche(t, 0.88, 0.025))
    return p


def joie(t):
    """Sa parade : il se hausse tout droit sur ses pattes de devant, le menton levé, la crête au ciel, se balance pour
    qu'on l'admire de chaque côté, et la queue fouette à grands coups ; puis il retombe, très content de lui, dans sa pose."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.85))
    haut = env * env
    p.add("poitrail", rot=(-18 * haut, 0, 0))
    for o in ("patte_avant_g", "patte_avant_d"):                   # les pattes de devant se tendent sous le poitrail
        p.add(o, rot=(18 * haut, 0, 0), ech=(1, 1, 1 + 0.25 * haut))
    p.add("cou", rot=(-6 * haut, 0, 10 * env * onde(t, 2)))
    p.add("tete", rot=(-8 * haut, 0, -6 * env * onde(t, 2)))
    fouette(p, t, 34 * env, 4)
    p.ouvert = borne(1 - 0.5 * cloche(t, 0.45, 0.10, False))
    return p


def dort(t):
    """Couché à plat, le menton dans l'herbe, les pattes étalées sur les côtés, la queue ramenée contre son flanc ;
    les yeux fermés, il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", ech=(1 + 0.012 * r, 1, 1 + 0.018 * r))
    p.add("poitrail", rot=(22, 0, 0))
    p.add("cou", rot=(26, 0, 0))
    p.add("tete", rot=(-8, 0, 10))
    for o, cote, rx in (("patte_avant_g", 1, -28), ("patte_avant_d", -1, -6)):     # le corps n'est pas droit : chacune à sa mesure
        p.add(o, rot=(rx, -cote * 30, 0))
    for o, cote in (("patte_arriere_g", 1), ("patte_arriere_d", -1)):
        p.add(o, rot=(0, -cote * 20, 0))
    p.add("queue1", rot=(0, 0, -12))                               # la queue s'enroule vers sa gauche
    p.add("queue2", rot=(0, 0, -24))
    p.add("queue3", rot=(0, 0, -26 - 3 * r))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Triton")
