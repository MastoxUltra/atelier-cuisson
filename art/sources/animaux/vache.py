"""La vache en peluche, troisième dessin : une frisonne bonne pâte, placide et contente de son sort. Un énorme tonneau
blanc cassé sur quatre pattes fines, rapiécé de grandes taches charbon ; un mufle de velours taupe, large et doux, deux
petits yeux vivants grands ouverts, et deux cornes en lyre, crème à la pointe charbon. La tête tournée vers nous, le
menton à hauteur du dos, la mâchoire de travers : elle rumine en vous regardant, un sourire en coin.
(l'auteur, 15/10 : la vache aux paupières lourdes était « trop dépressive » : vache_ancien2.py ; le premier : vache_ancien.py)

    python vache.py        fabrique la fiche art/apercus/animaux/vache.png
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

CHARBON = M.hexa("#3b3c43")                 # les taches, les oreilles, le toupet, les sabots
TAUPE = M.hexa("#9c8a86")                   # le mufle : un velours taupe, doux (plus de rose de bébé)
VIEUX_ROSE = M.hexa("#d6aaa4")              # le dedans des oreilles, le pis
CORPS = Vector((0.0, 0.06, 0.365))
LARGE, LONG, HAUT = 0.180, 0.280, 0.165     # les demi-mesures du tonneau
NUQUE = Vector((-0.020, -0.300, 0.455))     # l'arrière du crâne : à hauteur du dos, elle porte la tête haute
LACET, PIQUE, PENCHE = 30.0, 6.0, -9.0      # la tête : tournée vers sa gauche (vers nous), à l'horizontale, un rien penchée


def tache(rayon, a2, p2, a3, p3):
    """Le contour d'une tache : un rond cabossé (l'ouverture de la rustine dans chaque direction)."""
    return lambda th: rayon * (1 + a2 * math.cos(2 * th + p2) + a3 * math.cos(3 * th + p3))


def meche(pos, tourne):
    """Une mèche du toupet, couchée sur le front (dans le repère de la tête), tournée de quelques degrés."""
    return A.boule(1.0, 20, 10).etire(0.019, 0.017, 0.034).pose(pos, (0, tourne, 0))


def paupiere(r, coupe):
    """Une lourde paupière : un demi-dôme de feutrine qui coiffe le haut d'un bouton de rayon r.
    coupe : la hauteur de son bord au-dessus du milieu du bouton, en rayons (0 = l'œil à moitié fermé)."""
    def f(v):
        s = v * [1.30 * r, 1.30 * r, 0.62 * r]
        s[:, 1] = np.maximum(s[:, 1], coupe * r)
        return s
    return A.boule(1.0, 32, 16).sculpte(f)


def construire():
    a = K.Animal("vache")
    a.taille = 1.80

    # ----- le corps : un tonneau presque carré, la panse qui pend, les os des hanches qui pointent -----
    def tonneau(v):
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.55, 0.60, 0.58), 0.13, 0.07)         # les deux os des hanches
        v = K.bosse(v, (0, -0.66, 0.75), 0.06, 0.15)                      # le garrot
        y = np.clip(v[:, 1], -1.0, 1.0)
        rond = np.sqrt(np.maximum(1 - y * y, 1e-9))
        k = np.maximum(1 - np.abs(y) ** 3.0, 0.0) ** (1 / 3.0) / rond     # des flancs droits, deux bouts francs
        h = np.maximum(np.hypot(v[:, 0], v[:, 2]), 1e-9)
        k = k * (np.abs(v[:, 0] / h) ** 3.0 + np.abs(v[:, 2] / h) ** 3.0) ** (-1 / 3.0)   # la section : un carré aux coins ronds
        s = np.stack([v[:, 0] * k * LARGE, y * LONG, v[:, 2] * k * HAUT], axis=1)
        panse = np.exp(-((y - 0.10) / 0.60) ** 2)
        s[:, 2] *= np.where(v[:, 2] < 0, 1 + 0.20 * panse, 1.0)           # la panse pend au milieu
        s[:, 0] *= 1 + 0.06 * panse                                       # ... et déborde sur les côtés
        return s
    corps = A.boule(1.0, 56, 28).sculpte(tonneau)
    G.sillons(corps, [14], 0.005, 1.1)
    a.piece("corps", corps, K.BLANC, pos=CORPS)
    a.couture("dos", "corps", 14, 0.52, 0.72)

    # ----- les grandes taches : cinq rustines charbon aux contours francs, tenues au point de feston crème -----
    # (toutes visées depuis le milieu du corps : deux taches ne se chevauchent pas si leurs axes s'écartent assez)
    for nom, axe, forme, epais, points in (("selle", (0.48, 0.10, 0.86), tache(0.60, 0.20, 0.6, 0.13, 1.9), 0.006, 44),
                                           ("epaule", (0.80, -0.62, -0.15), tache(0.36, 0.24, 2.2, 0.12, 0.4), 0.004, 26),
                                           ("cuisse", (0.75, 0.62, -0.30), tache(0.28, 0.20, 1.0, 0.14, 2.5), 0.004, 20),
                                           ("croupe", (-0.62, 0.74, 0.12), tache(0.45, 0.20, 0.3, 0.12, 1.2), 0.004, 30),
                                           ("flanc", (-0.85, -0.50, 0.15), tache(0.44, 0.22, 1.5, 0.12, 0.2), 0.004, 30)):
        a.rustine(nom, "corps", CORPS, axe, forme, CHARBON, epais, points, fil=K.CREME)

    # ----- la tête : un bloc court et large ; dans son repère, X la gauche, Y le front, Z vers le mufle -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre(NUQUE, nez) @ Matrix.Rotation(math.radians(PENCHE), 4, "Z")
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.06, 0.150))
    tete = A.tour(A.profil([(0, 0), (0.072, 0.012), (0.100, 0.050), (0.104, 0.090), (0.092, 0.135), (0.082, 0.170),
                            (0.080, 0.200), (0, 0.216)], 6), 48).etire(1.0, 0.80, 1.0)
    G.sillons(tete, [12], 0.004, 1.1)
    a.piece("tete", tete, K.BLANC, mat=T)
    a.couture("chanfrein", "tete", 12, 0.44, 0.70)                       # le côté 12 de la pièce est le milieu du front

    # ----- le cou : un gros boudin court qui descend du garrot jusque derrière le crâne -----
    cou = A.courbe([CORPS + Vector((0, -0.150, 0.030)), CORPS + Vector((-0.005, -0.265, -0.025)), T @ Vector((0, -0.030, 0.035))], 8)
    a.piece("cou", A.tube(cou, lambda t: 0.105 - 0.027 * t, 20), K.BLANC)

    # ----- le mufle : un large tambour de feutrine rose, deux gros naseaux, et la mâchoire qui part de côté (elle rumine) -----
    mufle = T @ Vector((0, -0.004, 0.203))
    a.piece("mufle", A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.75)).etire(0.090, 0.060, 0.044), TAUPE,
            mat=T @ A.repere((0, -0.004, 0.203)))
    a.piece("machoire", A.boule(1.0, 32, 16).etire(0.070, 0.040, 0.058), K.BLANC, mat=T @ A.repere((0.050, -0.052, 0.200)))
    for nom, c in (("naseau_G", 1), ("naseau_D", -1)):
        a.rustine(nom, "mufle", mufle, T3 @ Vector((c * 0.40, 0.55, 0.73)), lambda th: 0.24 * (1 + 0.28 * math.cos(2 * th)),
                  CHARBON, 0.0025, 0)
    bouche = [T3 @ Vector((0.9 * x, -0.50 + 0.10 * x * x - 0.06 * x, 0.78)) for x in np.linspace(-0.85, 0.85, 9)]    # un sourire, plus haut d'un côté
    a.broderie("bouche", a.trace("mufle", mufle, bouche, 0.004), 0.0026, CHARBON)

    # ----- une tache sur l'œil droit, puis les yeux : petits, vivants, grands ouverts ; un sourcil en accent circonflexe, l'air content -----
    a.rustine("bandeau", "tete", T @ Vector((0, 0, 0.080)), T3 @ Vector((-0.80, 0.56, -0.12)), tache(0.52, 0.16, 0.8, 0.10, 2.0),
              CHARBON, 0.003, 18, fil=K.CREME)
    for nom, c, coupe, cale in (("G", 1, 0.22, 0.0), ("D", -1, 0.40, 0.003)):
        pos, vers = a.surface("tete", T @ Vector((0, 0, 0.080)), T3 @ Vector((c * 0.70, 0.66, 0.18)))
        pos = pos + vers * cale                                           # à droite, le bouton se pose sur la tache
        a.oeil("oeil_" + nom, pos + vers * 0.002, vers, 0.021)
        haut = [T3 @ Vector((c * (0.62 + 0.16 * u), 0.88 - 0.10 * abs(u), -0.05 + 0.30 * u)) for u in np.linspace(-1, 1, 5)]
        a.broderie("sourcil_" + nom, A.courbe(a.trace("tete", T @ Vector((0, 0, 0.080)), haut, 0.004), 4), 0.0030, CHARBON if nom == "G" else K.BLANC)

    # ----- les petites cornes crème, les oreilles charbon doublées de rose, et le toupet qui retombe sur le front -----
    def feuille(v):                                       # une oreille : ronde à l'attache, plus étroite au bout
        s = v.copy()
        s[:, 0] *= 1 - 0.40 * K.lisse((v[:, 2] - 0.1) / 0.9)
        return s
    for nom, c in (("G", 1), ("D", -1)):
        # une corne en lyre : elle part de côté, monte, et sa pointe se retourne vers l'avant ; crème, le bout charbon
        corne = A.courbe([T @ Vector((c * x, y, z)) for x, y, z in ((0.058, 0.020, 0.028), (0.100, 0.034, 0.016),
                                                                     (0.140, 0.080, 0.000), (0.150, 0.140, 0.010), (0.132, 0.180, 0.040))], 6)
        a.piece("corne_" + nom, K.tube_peint(corne, lambda t: 0.019 * (1 - t) ** 0.7 + 0.004, [(0.78, K.CREME), (9, CHARBON)], 14), None, poil=False)
        tombe = (T3 @ Vector((c * 0.93, -0.20, 0.30))).normalized()
        E = A.cadre(T @ Vector((c * 0.088, -0.012, 0.048)) + tombe * 0.058, tombe, T3 @ Vector((0, 0.75, 0.65)))
        a.piece("oreille_" + nom, A.boule(1.0, 32, 16).sculpte(feuille).etire(0.034, 0.011, 0.066), CHARBON, mat=E)
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).sculpte(feuille).etire(0.022, 0.006, 0.048).pose((0, 0.0075, 0.002)),
                VIEUX_ROSE, mat=E, poil=False)
    toupet = A.boule(0.036, 24, 12).pose((0, 0.046, 0.006)) + meche((0.002, 0.076, 0.046), 4) \
        + meche((0.030, 0.068, 0.036), 24) + meche((-0.028, 0.068, 0.036), -22)
    a.piece("toupet", toupet, CHARBON, mat=T)

    # ----- quatre pattes fines, le genou noueux, le sabot en feutrine charbon ; elles sont posées en quinconce
    #       (une vache au repos ne se tient jamais d'équerre, et vues de trois quarts elles ne se cachent pas l'une l'autre) -----
    pp = A.profil([(0.026, 0.040), (0.024, 0.085), (0.031, 0.120), (0.025, 0.155), (0.030, 0.21), (0.036, 0.26), (0, 0.29)], 6)
    ps = A.profil([(0, 0), (0.035, 0.004), (0.039, 0.024), (0.030, 0.050), (0, 0.054)], 5)
    for nom, x, y, rot in (("avant_G", 0.094, -0.160, (-6, -4, 0)), ("avant_D", -0.094, -0.105, (-2, 4, 0)),
                           ("arriere_G", 0.085, 0.215, (4, -4, 0)), ("arriere_D", -0.085, 0.275, (-3, 4, 0))):
        a.piece("patte_" + nom, A.tour(pp, 28), K.BLANC, pos=(x, y, 0.0), rot=rot)
        a.piece("sabot_" + nom, A.tour(ps, 28), CHARBON, pos=(x, y, 0.0), rot=rot, poil=False)

    # ----- le pis en feutrine rose, entre les pattes arrière -----
    pis = A.boule(1.0, 32, 16).etire(0.058, 0.078, 0.055)
    for x, y in ((0.026, -0.035), (-0.026, -0.035), (0.026, 0.035), (-0.026, 0.035)):
        pis = pis + A.boule(1.0, 12, 8).etire(0.012, 0.012, 0.018).pose((x, y, -0.052))
    a.piece("pis", pis, VIEUX_ROSE, pos=(0, 0.215, 0.205), poil=False)

    # ----- la queue : une cordelette qui chasse les mouches vers sa gauche, un gros pompon charbon au bout -----
    queue = A.courbe([(0, 0.29, 0.45), (0, 0.345, 0.455), (0.02, 0.38, 0.41), (0.07, 0.39, 0.33), (0.14, 0.365, 0.28),
                      (0.195, 0.32, 0.275)], 8)
    a.piece("queue", A.tube(queue, 0.014, 12), K.BLANC)
    a.piece("pompon", A.boule(1.0, 28, 14).etire(0.042, 0.042, 0.048), CHARBON, pos=(0.214, 0.302, 0.282), rot=A.viser((0.6, -0.6, 0.3)))
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py vache). Les mesures sont celles du modèle, avant a.taille.
# Les quatre pattes sont posées en quinconce, pas en miroir : chacune a son os à elle, nommé à la main en minuscules
# (av_g, av_d, ar_g, ar_d), et pend à la racine, pas au corps : ses sabots restent plantés quand le corps se balance.
# Une patte et son sabot suivent le même os. La tête est tournée vers nous et de travers : les oreilles ont chacune leur
# os ; la mâchoire, cousue de côté, a le sien : elle rumine.

from poses import Pose, borne, cloche, onde

# chaque patte : son pivot (le haut, dans le corps) et le bas de son sabot
JAMBES = {"av_g": ((0.076, -0.133, 0.265), (0.092, -0.157, 0.005)),
          "av_d": ((-0.077, -0.096, 0.265), (-0.092, -0.104, 0.006)),
          "ar_g": ((0.067, 0.197, 0.265), (0.083, 0.213, 0.005)),
          "ar_d": ((-0.067, 0.288, 0.265), (-0.083, 0.277, 0.006))}

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.150, 0.380)),            # au-dessus des hanches : elle se balance et se penche autour
    ("cou", "corps", (0.0, -0.090, 0.395)),              # le pied du cou, au garrot
    ("tete", "cou", (-0.015, -0.315, 0.440)),            # la nuque, derrière le crâne
    ("machoire", "tete", (0.089, -0.403, 0.392)),        # le fond de la mâchoire, cousue de côté
    ("oreille_g", "tete", (0.076, -0.297, 0.425)),       # l'attache de chaque oreille
    ("oreille_d", "tete", (-0.073, -0.386, 0.452)),
    ("queue", "corps", (0.0, 0.290, 0.450)),             # l'attache de la queue
] + [(nom, "racine", JAMBES[nom][0]) for nom in ("av_g", "av_d", "ar_g", "ar_d")]


def _cote(rang):
    """Une patte ou un sabot : tout sur l'os de sa patte (av_g, av_d, ar_g ou ar_d), selon son côté."""
    return lambda points, cote: {rang + ("_g" if cote == "_G" else "_d"): np.ones(len(points))}


def _oreille(points, cote):
    return {"oreille_g" if cote == "_G" else "oreille_d": np.ones(len(points))}


PORTEURS = [("corps", "corps"), ("dos", "corps"), ("selle", "corps"), ("epaule", "corps"), ("cuisse", "corps"),
            ("croupe", "corps"), ("flanc", "corps"), ("pis", "corps"), ("cou", "cou"),
            ("tete", "tete"), ("chanfrein", "tete"), ("mufle", "tete"), ("naseau", "tete"), ("bouche", "tete"),
            ("bandeau", "tete"), ("oeil", "tete"), ("sourcil", "tete"), ("corne", "tete"), ("toupet", "tete"),
            ("machoire", "machoire"), ("oreille", _oreille, "oreille_g"), ("dedans", _oreille, "oreille_g"),
            ("patte_avant", _cote("av"), "av_g"), ("sabot_avant", _cote("av"), "av_g"),
            ("patte_arriere", _cote("ar"), "ar_g"), ("sabot_arriere", _cote("ar"), "ar_g"),
            ("queue", "queue"), ("pompon", "queue"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _jambe(p, nom, angle, leve=0.0):
    """Tourne une patte de « angle » degrés autour de son haut (> 0 : le sabot part vers l'arrière) en gardant le sabot
    au ras du sol (le sabot penche avec la patte : son bord piquerait) ; « leve » le soulève."""
    h, b = JAMBES[nom]
    dy, dz = b[1] - h[1], b[2] - h[2]
    a = math.radians(angle)
    p.add(nom, rot=(angle, 0, 0), pos=(0, 0, dz - (dy * math.sin(a) + dz * math.cos(a)) + 0.035 * abs(math.sin(a)) + leve))


def _rumine(p, t, tours, k=1.0):
    """La mâchoire qui broie en rond, de côté : « tours » coups de mâchoire dans l'animation."""
    p.add("machoire", rot=(4 * k * (0.5 + 0.5 * onde(t, tours, 0.25)), 0, 9 * k * onde(t, tours)))


def repos(t):
    """Placide et contente : elle rumine sans s'arrêter en nous regardant, respire à grands coups lents, pousse un gros
    soupir d'aise, bat d'une oreille, chasse une mouche d'un coup de queue sur le flanc ; elle cligne, tranquille."""
    p = Pose()
    r = onde(t, 2)
    soupir = cloche(t, 0.48, 0.12)
    mouche = cloche(t, 0.78, 0.09)
    p.add("corps", ech=(1 + 0.012 * r + 0.025 * soupir, 1, 1 + 0.016 * r + 0.020 * soupir))
    p.add("cou", rot=(1.5 * r + 3 * soupir, 0, 0))
    p.add("tete", rot=(-4 * soupir, 3 * onde(t, 1), 4 * cloche(t, 0.20, 0.15)))
    _rumine(p, t, 10, 1 - 0.7 * soupir)
    p.add("oreille_g", rot=(0, 24 * cloche(t, 0.30, 0.03), 0))
    p.add("oreille_d", rot=(0, -18 * cloche(t, 0.64, 0.03), 0))
    p.add("queue", rot=(-8 * mouche, 0, 26 * mouche * onde(t, 5)))
    p.ouvert = borne(1 - cloche(t, 0.12, 0.025) - cloche(t, 0.56, 0.025) - 0.25 * soupir)
    return p


def avance(t):
    """Elle va son train, lourde et tranquille, une patte après l'autre (arrière gauche, avant gauche, arrière droit,
    avant droit) : les hanches roulent, la tête hoche bas à chaque pas, la queue balance, et elle rumine en marchant.
    Un sabot posé glisse vers l'arrière pendant qu'il porte : elle avance."""
    p = Pose()
    for nom, phase in (("ar_g", 0.0), ("av_g", 0.25), ("ar_d", 0.5), ("av_d", 0.75)):
        u = t - phase
        en_l_air = max(0.0, -math.sin(math.tau * u))
        _jambe(p, nom, -10 * math.cos(math.tau * u) - 8 * en_l_air, 0.035 * en_l_air)
    p.add("corps", rot=(0, 2.5 * onde(t, 1), 2 * onde(t, 1, 0.1)), pos=(0, 0, 0.006 * onde(t, 2, 0.25)))
    p.add("cou", rot=(5 + 3 * onde(t, 2), 0, 0))
    p.add("tete", rot=(-2 * onde(t, 2, -0.1), 0, 2 * onde(t, 1)))
    _rumine(p, t, 2, 0.6)
    p.add("oreille_g", rot=(0, 6 * onde(t, 2, -0.2), 0))
    p.add("oreille_d", rot=(0, -6 * onde(t, 2, -0.2), 0))
    p.add("queue", rot=(0, 0, 10 * onde(t, 1, -0.2)))
    return p


def mange(t):
    """Elle broute : le cou plonge jusqu'à l'herbe, elle arrache trois touffes d'un coup de tête de côté, puis relève la
    tête et mâche de travers en nous regardant, contente ; la queue balance."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    arrache = max(0.0, onde(t, 3)) ** 2 * bas
    p.add("corps", rot=(8 * bas, 0, 0))
    p.add("cou", rot=(35 * bas - 3 * arrache, 0, -8 * bas), pos=(0, -0.030 * bas, -0.020 * bas))
    p.add("tete", rot=(20 * bas - 6 * arrache, 0, -16 * bas + 10 * arrache))
    _rumine(p, t, 6, 0.4 + 0.6 * leve)
    p.add("oreille_g", rot=(0, 10 * bas, 0))
    p.add("oreille_d", rot=(0, -10 * bas, 0))
    p.add("queue", rot=(0, 0, 8 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.93, 0.03))
    return p


def joie(t):
    """Sa fête à elle, une vache au printemps : une gambade lourde. Elle se ramasse, saute des quatre pattes, rue en
    l'air des postérieurs, la queue dressée, en secouant la tête, les oreilles qui volent ; elle retombe, souffle, et
    se remet à ruminer, contente."""
    p = repos(0.0)
    saut = math.sin(math.pi * borne((t - 0.10) / 0.30))           # en l'air de 0,10 à 0,40
    rue = math.sin(math.pi * borne((t - 0.36) / 0.34))            # la ruade, de 0,36 à 0,70
    tasse = cloche(t, 0.08, 0.07, False) + cloche(t, 0.44, 0.06, False)
    bascule = 12 * rue
    monte = 0.30 * math.sin(math.radians(bascule))                # la croupe monte, le poitrail reste à sa hauteur
    p.add("corps", rot=(-6 * saut + bascule, 0, 4 * saut), pos=(0, 0, 0.090 * saut - 0.012 * tasse + monte))
    for nom in ("av_g", "av_d"):
        p.add(nom, rot=(-18 * saut, 0, 0), pos=(0, 0, 0.090 * saut - 0.012 * tasse))
    for nom in ("ar_g", "ar_d"):
        p.add(nom, rot=(16 * saut + bascule + 40 * rue ** 2, 0, 0), pos=(0, 0, 0.090 * saut - 0.012 * tasse + 1.15 * monte))
    p.add("cou", rot=(-8 * saut + 10 * rue, 0, 0))
    p.add("tete", rot=(-6 * saut, 0, 14 * onde(t, 3) * borne(saut + rue)))
    p.add("oreille_g", rot=(0, 30 * saut, 0))
    p.add("oreille_d", rot=(0, -30 * saut, 0))
    p.add("queue", rot=(-50 * borne(saut + rue), 0, 12 * onde(t, 6) * rue))
    return p


def dort(t):
    """Couchée sur le ventre, les pattes repliées sous elle, la tête tournée et posée contre son flanc gauche, les yeux
    fermés ; elle respire lentement, à grands coups, et la mâchoire bouge encore un peu (elle rumine en dormant)."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.135), ech=(1.04 + 0.014 * r, 1.0, 0.97 + 0.022 * r))
    for nom in JAMBES:
        p.add(nom, pos=(0, 0, -0.135), ech=(1, 1, 0.30))
    p.add("cou", rot=(14, 0, 40))
    p.add("tete", rot=(16, 10, 46))
    _rumine(p, t, 3, 0.25)
    p.add("oreille_g", rot=(0, -14, 0))
    p.add("oreille_d", rot=(0, 14, 0))
    p.add("queue", rot=(0, 0, 10 * cloche(t, 0.6, 0.05) * onde(t, 8)))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Vache")
