"""L'âne en peluche : gris tourterelle, le ventre et le museau crème, la croix chocolat sur le dos et les épaules.
Il a planté ses quatre fers et ne bougera pas : le corps tiré en arrière, la tête de travers, une oreille
immense dressée vers l'avant et l'autre couchée à l'horizontale.

    python ane.py        fabrique la fiche art/apercus/animaux/ane.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import garnitures as G
import matieres as M
import peluche as K

TOURTERELLE = M.hexa("#b9aaa0")             # le gris chaud de la robe
CROUPE = Vector((0.0, 0.30, 0.305))         # le bout de la croupe : le corps, une pièce tournée, part de là vers le poitrail
CABRE = 8.0                                 # le poitrail plus haut que la croupe : il tire en arrière
NUQUE = Vector((0.0, -0.200, 0.625))        # l'arrière du crâne, au bout du cou
LACET, PIQUE, PENCHE = 24.0, 44.0, 8.0      # la tête : tournée vers sa gauche (vers nous), le nez vers le sol, de travers


def robe(corps):
    """Peint le corps point par point : le dessous crème, la raie chocolat le long du dos, la barre des épaules.
    Les limites suivent les mailles de la pièce tournée (64 côtés) : elles sortent nettes dans le poil."""
    t = np.tile(np.asarray(TOURTERELLE, float), (len(corps.v), 1))
    for anneau in corps.anneaux:
        if len(anneau) < 2:
            continue
        z = corps.v[anneau[0], 2]                         # de 0 (la croupe) à 0,45 (le poitrail)
        for j, k in enumerate(anneau):                    # le côté 16 est le dessus, le 48 le dessous
            if 36 <= j <= 59:
                t[k] = K.CREME
            if (14 <= j <= 17 and 0.02 < z < 0.302) or (6 <= j <= 25 and 0.262 <= z < 0.302):
                t[k] = K.CHOCOLAT
    corps.teinte = t
    return corps


def oreille(profil):
    """Une oreille d'âne : une longue feuille grise, le bout et le liseré des deux bords en chocolat."""
    m = A.tour(profil, 40).etire(1.0, 0.34, 1.0)
    t = np.tile(np.asarray(TOURTERELLE, float), (len(m.v), 1))
    for anneau in m.anneaux:
        for j, k in enumerate(anneau):                    # les côtés 0 et 20 sont les deux bords de la feuille
            if m.v[k, 2] > 0.240 or (len(anneau) > 1 and j in (39, 0, 19, 20) and m.v[k, 2] > 0.035):
                t[k] = K.CHOCOLAT
    m.teinte = t
    return m


def construire():
    a = K.Animal("ane")
    a.taille = 1.50

    # ----- le corps : un baril à la panse ronde, tourné de la croupe au poitrail, peint de sa croix -----
    def baril(v):
        s = v.copy()
        panse = np.exp(-((v[:, 2] - 0.20) / 0.14) ** 2)
        s[:, 1] *= np.where(v[:, 1] < 0, 1 + 0.18 * panse, 1.0)           # la panse d'âne
        s[:, 0] *= 1 - 0.12 * K.lisse(v[:, 1] / 0.13)                     # le dos plus étroit que le ventre
        return s
    corps = A.tour(A.profil([(0, 0), (0.085, 0.012), (0.125, 0.07), (0.136, 0.16), (0.140, 0.25), (0.128, 0.34),
                             (0.095, 0.415), (0, 0.45)], 6), 64).sculpte(baril)
    G.sillons(corps, [36, 60], 0.004, 1.1)
    a.piece("corps", robe(corps), None, pos=CROUPE, rot=(90 - CABRE, 0, 0))
    a.couture("flanc_G", "corps", 60, 0.14, 0.80)                         # la couture suit la limite du gris et du crème
    a.couture("flanc_D", "corps", 36, 0.14, 0.80)

    # ----- la tête : longue, la ganache ronde, le museau crème ; dans son repère, X la gauche, Y le front, Z vers le nez -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre(NUQUE, nez) @ Matrix.Rotation(math.radians(PENCHE), 4, "Z")
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.07, 0.09))

    def ganache(v):                                       # la joue ronde sous l'œil
        s = v.copy()
        s[:, 1] *= np.where(v[:, 1] < 0, 1 + 0.22 * np.exp(-((v[:, 2] - 0.08) / 0.05) ** 2), 1.0)
        return s
    tete = A.tour(A.profil([(0, 0), (0.060, 0.012), (0.085, 0.06), (0.082, 0.11), (0.066, 0.17), (0.064, 0.215),
                            (0.071, 0.25), (0.055, 0.277), (0, 0.288)], 6), 48).sculpte(ganache).etire(0.88, 1.0, 1.0)
    a.piece("tete", K.bandes(tete, [(0.168, TOURTERELLE), (9, K.CREME)]), None, mat=T)
    a.ourlet("museau", "tete", 0.495)                                     # un point avant là où le gris passe au crème
    for nom, c in (("G", 1), ("D", -1)):
        a.rustine("naseau_" + nom, "tete", T @ Vector((0, 0, 0.245)), T3 @ Vector((c * 0.55, 0.38, 0.74)), 0.20, K.CHOCOLAT, 0.0025, 0)
    moue = [T3 @ Vector((0.95 * x, -0.62 - 0.18 * x * x, 0.55)) for x in np.linspace(-0.85, 0.85, 11)]
    a.broderie("moue", a.trace("tete", T @ Vector((0, 0, 0.235)), moue), 0.0024)

    # ----- les yeux : cerclés de crème, sous deux sourcils qui plongent vers le nez (il a dit non) -----
    for nom, c in (("G", 1), ("D", -1)):
        axe = T3 @ Vector((c * 0.55, 0.84, 0.0))
        a.rustine("lunette_" + nom, "tete", T @ Vector((0, 0, 0.075)), axe, 0.36, K.CREME, 0.0025, 0)
        pos, vers = a.surface("tete", T @ Vector((0, 0, 0.075)), axe)
        a.bouton("oeil_" + nom, pos + vers * 0.0025, vers, 0.024)
        arc = []
        for t in np.linspace(0, 1, 6):                    # du coin extérieur, côté nuque, au coin intérieur, côté nez
            tour_ = math.radians(34 + 44 * t)
            arc += a.trace("tete", T @ Vector((0, 0, 0.034 + 0.030 * t)), [T3 @ Vector((c * math.cos(tour_), math.sin(tour_), 0))], 0.0045)
        a.broderie("sourcil_" + nom, A.courbe(arc, 4), 0.0032)

    # ----- le cou, raide, et la crinière en brosse : une rangée de mèches dressées, du garrot à la nuque -----
    cou = A.courbe([(0, -0.075, 0.375), (0, -0.150, 0.470), T @ Vector((0, -0.030, 0.060))], 8)
    a.piece("cou", A.tube(cou, lambda t: 0.090 - 0.024 * t, 20), TOURTERELLE)
    pm = A.profil([(0, 0), (0.026, 0.008), (0.022, 0.038), (0.011, 0.068), (0, 0.078)], 5)
    dresse = Vector((0, 0.45, 0.89)).normalized()
    brosse = None
    for s in np.linspace(0, 1, 7):
        pied = Vector((0, -0.028, 0.458)).lerp(Vector((0.005, -0.165, 0.598)), s) - dresse * 0.014
        meche = A.tour(pm, 16).etire(0.75 * (1 + 0.2 * s), 1 + 0.2 * s, 1 + 0.2 * s).pose(pied, A.viser(dresse))
        brosse = meche if brosse is None else brosse + meche
    a.piece("criniere", brosse, K.CHOCOLAT)
    a.piece("toupet", A.tour(pm, 16), K.CHOCOLAT, mat=T @ A.repere((0, 0.030, 0.020), A.viser((0, 0.80, 0.60))))

    # ----- les oreilles immenses, doublées de corail : la gauche dressée vers l'avant, la droite couchée à l'horizontale -----
    po = A.profil([(0, 0), (0.034, 0.020), (0.050, 0.090), (0.047, 0.170), (0.031, 0.250), (0.012, 0.296), (0, 0.306)], 6)
    for nom, c, vers, face in (("G", 1, (0.12, -0.50, 0.86), (0.20, -0.90, -0.35)), ("D", -1, (-0.93, -0.10, -0.22), (0.10, -0.95, -0.20))):
        vers = Vector(vers).normalized()
        E = A.cadre(T @ Vector((c * 0.045, 0.030, 0.014)) - vers * 0.022, vers, face)   # Z le long de l'oreille, Y son dedans
        a.piece("oreille_" + nom, oreille(po), None, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 32).etire(0.62, 0.34, 0.84).pose((0, 0.0075, 0.022)), K.CORAIL, mat=E, poil=False)

    # ----- les quatre fers plantés : les pattes partent toutes vers l'avant, zébrées au genou, le sabot bien à plat -----
    pp = A.profil([(0.031, 0.030), (0.029, 0.08), (0.036, 0.125), (0.031, 0.17), (0.040, 0.24), (0.046, 0.30), (0, 0.335)], 6)
    ps = A.profil([(0, 0), (0.038, 0.004), (0.043, 0.026), (0.034, 0.056), (0, 0.060)], 5)
    for nom, pos, penche in (("avant", (0.095, -0.190, 0.0), -16), ("arriere", (0.100, 0.172, 0.0), -10)):
        patte = K.bandes(A.tour(pp, 28), [(0.100, TOURTERELLE), (0.118, K.CHOCOLAT), (0.146, TOURTERELLE), (0.164, K.CHOCOLAT), (9, TOURTERELLE)])
        a.piece("patte_" + nom, patte, None, pos=pos, rot=(penche, -4, 0), paire=True)
        a.piece("sabot_" + nom, A.tour(ps, 28), K.CHOCOLAT, pos=pos, poil=False, paire=True)

    # ----- la queue : une cordelette serrée contre la croupe, sa mèche chocolat au bout -----
    queue = A.courbe([(0, 0.25, 0.385), (0, 0.30, 0.385), (0.012, 0.335, 0.34), (0.03, 0.345, 0.26), (0.045, 0.34, 0.19)], 8)
    a.piece("queue", A.tube(queue, 0.013, 12), TOURTERELLE)
    a.piece("meche", A.boule(1.0, 24, 12).etire(0.027, 0.027, 0.055), K.CHOCOLAT, pos=(0.048, 0.338, 0.150))
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py ane)

from poses import Pose, borne, cloche, onde

# Les quatre jambes pendent à la racine, pas au corps : ses fers restent plantés quand il tire en arrière, et le haut
# de chaque jambe, enfoui dans le corps, n'en sort pas pour de petits gestes. Elles sont posées en miroir (paire=True) :
# un os à gauche, recopié à droite. La tête est tournée et de travers, les deux oreilles n'ont rien de symétrique :
# leurs os sont nommés à la main, en minuscules (oreille_g, oreille_d), et une fonction les distribue.
_JAMBES = {"patte_avant": (0.333, 16.0), "patte_arriere": (0.333, 10.0)}     # longueur de l'épaule au fer, inclinaison au repos


def _oreille(points, cote):
    return {"oreille_g" if cote == "_G" else "oreille_d": np.ones(len(points))}


OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.180, 0.320)),            # au-dessus des hanches : il tire en arrière, se cabre et rue autour
    ("cou", "corps", (0.0, -0.090, 0.400)),              # le pied du cou, dans le poitrail
    ("tete", "cou", (0.006, -0.200, 0.590)),             # la nuque, là où le cou entre sous le crâne
    ("oreille_g", "tete", (0.051, -0.216, 0.641)),       # la base de chaque oreille
    ("oreille_d", "tete", (-0.034, -0.244, 0.632)),
    ("queue", "corps", (0.0, 0.265, 0.385)),             # l'attache de la queue
    ("patte_avant_G", "racine", (0.073, -0.100, 0.320)), # l'épaule, au haut de la jambe
    ("patte_arriere_G", "racine", (0.077, 0.230, 0.325)),# la hanche
]
PORTEURS = [("corps", "corps"), ("flanc", "corps"), ("cou", "cou"), ("criniere", "cou"),
            ("tete", "tete"), ("museau", "tete"), ("naseau", "tete"), ("moue", "tete"), ("lunette", "tete"), ("oeil", "tete"),
            ("sourcil", "tete"), ("toupet", "tete"),
            ("oreille", _oreille, "oreille_g"), ("pavillon", _oreille, "oreille_g"),
            ("patte_avant", "patte_avant", True), ("sabot_avant", "patte_avant", True),
            ("patte_arriere", "patte_arriere", True), ("sabot_arriere", "patte_arriere", True),
            ("queue", "queue"), ("meche", "queue"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _plateau(t, centre, demi, pente):
    """1 autour de « centre » sur une demi-largeur « demi », 0 au-delà de demi + pente, en douceur entre les deux (en boucle)."""
    d = abs(((t - centre + 0.5) % 1.0) - 0.5)
    x = borne((demi + pente - d) / pente)
    return x * x * (3 - 2 * x)


def _jambe(p, jambe, angle, leve=0.0, cote="_G"):
    """Tourne une jambe de « angle » degrés autour de son épaule (> 0 : le fer part vers l'arrière) en gardant le fer au
    ras du sol : la jambe, inclinée vers l'avant au repos, descendrait sinon en se redressant. « leve » le soulève."""
    long, incline = _JAMBES[jambe]
    dz = long * (math.cos(math.radians(incline - angle)) - math.cos(math.radians(incline)))
    dz += 0.040 * abs(math.sin(math.radians(angle)))              # le sabot penche avec la jambe : sa pince ou son talon piquerait
    p.add(jambe + cote, rot=(angle, 0, 0), pos=(0, 0, dz + leve))


def _non(t, centre, large):
    """Il secoue la tête : non, non. Deux allers-retours autour de « centre »."""
    return cloche(t, centre, large) * math.sin(math.tau * 2 * (t - centre + large) / (2 * large))


def repos(t):
    """Planté sur ses quatre fers, le corps tiré en arrière : il respire, tourne l'oreille dressée vers un bruit, relève
    un instant l'oreille couchée et la laisse retomber, puis il secoue la tête (non, non) en tirant encore plus fort ;
    la queue chasse une mouche ; il cligne."""
    p = Pose()
    r = onde(t, 2)
    tire = cloche(t, 0.62, 0.16)
    p.add("corps", rot=(-3 * tire, 0, 0), pos=(0, 0.012 * tire, 0), ech=(1 + 0.012 * r, 1, 1 + 0.016 * r))
    for nom in ("patte_avant_G", "patte_avant_D"):           # les fers ne bougent pas : les jambes se tendent davantage
        _jambe(p, nom[:-2], -2 * tire, cote=nom[-2:])
    p.add("cou", rot=(1.5 * r - 4 * tire, 0, 0))
    p.add("tete", rot=(2 * tire, 0, 16 * _non(t, 0.62, 0.10)))
    p.add("oreille_g", rot=(0, 0, 35 * cloche(t, 0.20, 0.07)))
    p.add("oreille_d", rot=(0, 40 * cloche(t, 0.38, 0.03) + 10 * cloche(t, 0.43, 0.04), 0))
    p.add("queue", rot=(0, 0, 18 * cloche(t, 0.88, 0.07) * onde(t, 8)))
    p.ouvert = borne(1 - cloche(t, 0.10, 0.02) - cloche(t, 0.48, 0.02) - 0.3 * tire)
    return p


def avance(t):
    """Il y va, mais à son pas : un pas court et têtu, une jambe après l'autre (arrière gauche, avant gauche, arrière
    droit, avant droit), les jambes ramenées sous lui ; la tête hoche à chaque pas, bas et en avant, l'oreille couchée
    ballotte, la queue balance. Un fer posé glisse vers l'arrière pendant qu'il porte : il avance."""
    p = Pose()
    for nom, phase, sous in (("patte_arriere_G", 0.0, 7), ("patte_avant_G", 0.25, 13), ("patte_arriere_D", 0.5, 7), ("patte_avant_D", 0.75, 13)):
        u = t - phase
        en_l_air = max(0.0, -math.sin(math.tau * u))
        _jambe(p, nom[:-2], sous - 11 * math.cos(math.tau * u) - 8 * en_l_air, 0.040 * en_l_air, nom[-2:])
    p.add("corps", rot=(0, 2.5 * onde(t, 1), 2 * onde(t, 1, 0.1)), pos=(0, 0, 0.006 * onde(t, 2, 0.25)))
    p.add("cou", rot=(6 + 4 * onde(t, 2), 0, 0))
    p.add("tete", rot=(-3 * onde(t, 2, -0.1), 0, 3 * onde(t, 1)))
    p.add("oreille_g", rot=(-8 * onde(t, 2, -0.2), 0, 0))
    p.add("oreille_d", rot=(0, 10 * onde(t, 2, -0.25), 0))
    p.add("queue", rot=(0, 0, 9 * onde(t, 1, -0.2)))
    return p


def mange(t):
    """Il baisse le cou jusqu'à l'herbe, arrache trois touffes d'un coup de tête de côté, puis relève la tête en
    mâchant, les oreilles qui se détendent, et nous jette un regard en coin."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    arrache = max(0.0, onde(t, 3)) ** 2 * bas
    p.add("corps", rot=(10 * bas, 0, 0))
    p.add("cou", rot=(70 * bas - 4 * arrache, 0, -6 * bas), pos=(0, -0.05 * bas, 0))      # le cou sort un peu du poitrail pour aller plus loin
    p.add("tete", rot=(-50 * bas - 8 * arrache, 0, 14 * arrache))
    p.add("tete", rot=(-3 * leve * abs(onde(t, 8)), 0, -10 * cloche(t, 0.88, 0.06)))      # il mâche, il nous regarde
    p.add("oreille_g", rot=(0, 18 * bas, 0))
    p.add("oreille_d", rot=(0, -8 * bas, 0))
    p.add("queue", rot=(0, 0, 8 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.92, 0.03))
    return p


def joie(t):
    """Sa fête à lui : une ruade. Il baisse le nez, la croupe monte, les deux postérieurs détendent un grand coup de pied
    en arrière, la queue en fouet ; il retombe, relève la tête pour un hi-han, le nez au ciel, puis se replante,
    têtu comme avant."""
    p = repos(0.0)
    rue = math.sin(math.pi * borne((t - 0.08) / 0.40))           # la ruade, de 0,08 à 0,48
    hihan = math.sin(math.pi * borne((t - 0.50) / 0.42))          # le hi-han, de 0,50 à 0,92
    bascule = 18 * rue
    monte = 0.27 * math.sin(math.radians(bascule))                # le poitrail reste à sa hauteur, la croupe monte
    p.add("corps", rot=(bascule, 0, 0), pos=(0, 0, monte))
    for nom in ("patte_arriere_G", "patte_arriere_D"):
        p.add(nom, rot=(bascule + 55 * rue ** 2, 0, 0), pos=(0, 0, 1.18 * monte))      # la hanche monte avec la croupe
    p.add("cou", rot=(14 * rue - 18 * hihan, 0, 0))
    p.add("tete", rot=(10 * rue - 30 * hihan + 4 * onde(t, 9) * hihan, 0, 0))
    p.add("oreille_g", rot=(-20 * rue, 0, 0))
    p.add("oreille_d", rot=(0, 30 * hihan, 0))
    p.add("queue", rot=(-40 * rue, 0, 15 * onde(t, 5) * rue))
    return p


def dort(t):
    """Il dort debout, en âne qui ne se couchera pas devant nous : l'encolure basse, la tête qui pend, les deux oreilles
    tombées de côté, un postérieur au repos sur la pince, les yeux fermés ; il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", ech=(1 + 0.012 * r, 1, 1 + 0.018 * r))
    p.add("cou", rot=(24 + 1.5 * r, 0, 0))
    p.add("tete", rot=(12, 0, -6))
    p.add("oreille_g", rot=(0, 45, 0))
    p.add("oreille_d", rot=(0, -18, 0))
    _jambe(p, "patte_arriere", -6, 0.030, "_D")
    p.add("queue", rot=(4, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Âne")
