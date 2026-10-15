"""La courtilière en peluche, deuxième dessin : la taupe-grillon, un petit bulldozer. Un corps long et bas de velours ocre
cuivré, l'abdomen bagué de châtaigne qui file de travers derrière elle ; un énorme corselet de feutrine brun bitume, carré,
qui avance en visière au-dessus des yeux ; deux pattes avant démesurées, en pelles de bitume à quatre dents griffées
d'ivoire, plantées devant elle comme une lame de chantier. Les ailes trop courtes, en cuir, et dessous deux longues
pointes rouge coquelicot qui dépassent : son seul éclat. Une terrassière bourrue : le nez au ras du sol, l'épaule en
avant, une pelle plantée, l'autre levée en plein coup de rame, l'œil petit et noir sous la visière.

    python courtiliere.py        fabrique la fiche art/apercus/animaux/courtiliere.png
    (le premier dessin, refusé le 14/10 : courtiliere_ancien.py)
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

OCRE = M.hexa("#e6a46a")                      # le velours : un ocre cuivré (le poil le fonce en mordoré)
BAGUE = M.hexa("#c47c45")                     # les anneaux de l'abdomen, le fil des coutures
BITUME = M.hexa("#4e2f1f")                    # le corselet et les pelles, en feutrine rase
CUIR = M.hexa("#8a5232")                      # les ailes courtes
COQUELICOT = M.hexa("#e5482f")                # l'accent : les deux pointes des ailes de dessous
LEVE = 0.016                                  # tout le corps monte d'un cran sur ses pattes : l'herbe ne l'avale pas
CORSELET = A.repere((0, -0.050, 0.070 + LEVE), (8, 0, 0))     # basculé vers l'avant : elle charge
TETE = Vector((0.0, -0.114, 0.046 + LEVE))
PORT = A.repere(TETE, (6, 0, 16))             # la tête basse, tournée vers celui qui approche
DOS = K.Fil([(0, -0.020, 0.050 + LEVE), (0, 0.050, 0.053 + LEVE), (0, 0.120, 0.059 + LEVE), (0, 0.188, 0.073 + LEVE)], flanc=(1, 0, 0))


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête, rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def de_travers(s):
    """L'abdomen file de travers vers sa droite (-X) en s'éloignant : la ligne du corps n'est pas droite."""
    s = s.copy()
    s[:, 0] -= 0.030 * K.lisse((s[:, 1] - 0.03) / 0.17) ** 2
    return s


def pelle(poignet, face, doigts):
    """La pelle d'une patte fouisseuse : un large coussin de feutrine bitume, épais au milieu, creusé en godet, tout le
    haut taillé en quatre grosses dents en éventail dont les pointes sont griffées d'ivoire. face : là où regarde la
    paume ; doigts : là où pointent les dents. (Une boule à 64 côtés tombe juste : une dent tous les 8 côtés.)"""
    m = A.boule(1.0, 64, 20)
    tour = np.arctan2(m.v[:, 1], m.v[:, 0])
    scie = np.where(m.v[:, 1] > 1e-9, 1.0 - np.abs(2.0 * ((tour / (math.pi / 4)) % 1.0) - 1.0), 0.0)

    unite = m.v.copy()
    rho = np.hypot(unite[:, 0], unite[:, 1])

    def lame(v):
        r = 0.036 + 0.004 * np.sin(tour) + 0.017 * scie
        s = np.stack([v[:, 0] * r * 0.95, v[:, 1] * r * np.where(v[:, 1] > 0, 1.08, 1.0),
                      np.sign(v[:, 2]) * np.abs(v[:, 2]) ** 0.6 * 0.013], axis=1)
        s[:, 2] += 0.012 * (s[:, 0] ** 2 + s[:, 1] ** 2) / 0.05 ** 2
        s[:, 1] += 0.030
        return s
    m.sculpte(lame)
    griffe = (scie > 0.40) & (rho > 0.88) & (unite[:, 1] > 0.10)          # le bout de chaque dent, au bord du coussin
    m.teinte = np.where(griffe[:, None], np.asarray(K.CREME), np.asarray(BITUME))
    rep = np.array(A.cadre(poignet, face, doigts))
    m.v = m.v @ rep[:3, :3].T + rep[:3, 3]
    return m


def bras(epaule, coude, poignet, face, doigts):
    """Le bras qui porte la pelle : un gros boudin de velours, renflé au milieu, qui s'arrête au dos de la pelle."""
    main = Vector(poignet) + Vector(doigts).normalized() * 0.010 - Vector(face).normalized() * 0.012
    return A.tube(A.conges([epaule, coude, tuple(main)], 0.016, 5), lambda t: 0.021 + 0.007 * math.sin(math.pi * t), 14)


def pointe(longueur, largeur):
    """Le contour d'une aile en lame : étroite, pointue au bout, arrondie à la racine."""
    return A.courbe([(0.0, 0.0), (largeur * 0.5, 0.010), (largeur * 0.55, longueur * 0.45), (largeur * 0.30, longueur * 0.85),
                     (0.0, longueur), (-largeur * 0.30, longueur * 0.85), (-largeur * 0.55, longueur * 0.45), (-largeur * 0.5, 0.010)],
                    5, fermee=True)


def construire():
    a = K.Animal("courtiliere")
    a.taille = 0.44
    a.tete = PORT @ Vector((0, -0.036, 0.004))

    # ----- l'abdomen : un long boudin de velours bagué de châtaigne, plus large que haut, couché le long du dos -----
    profil = A.profil([(0, 0), (0.030, 0.006), (0.046, 0.030), (0.052, 0.075), (0.049, 0.120), (0.040, 0.160), (0.028, 0.190),
                       (0.016, 0.208), (0, 0.216)], 6)
    anneaux = [palier for z in (0.112, 0.138, 0.164, 0.188) for palier in ((z - 0.006, OCRE), (z + 0.005, BAGUE))] + [(9, OCRE)]
    ventre = K.bandes(A.tour(profil, 56), anneaux).sculpte(lambda v: v * [1.08, 0.82, 1.0]).sculpte(DOS.couche).sculpte(de_travers)
    a.piece("abdomen", ventre, None)
    a.couture("flanc", "abdomen", 0, 0.30, 0.92, "droit", fil=BAGUE, large=0.010, haut=0.003, pas=0.014)

    # ----- le corselet : une cuirasse de feutrine carrée, plus large que le corps, qui avance en visière au-dessus des
    #       yeux ; un sillon la fend du front à la nuque, tenu par des points ton sur ton -----
    def cuirasse(v):
        s = K.emousse(v, 0.78) * [0.064, 0.066, 0.050]
        s[:, 1] -= 0.020 * K.lisse((-v[:, 1] - 0.2) / 0.8) * K.lisse((v[:, 2] + 0.1) / 0.9)
        return s
    corselet = A.boule(1.0, 56, 28).sculpte(cuirasse)
    G.sillons(corselet, [14, 42], 0.005, 1.3)
    a.piece("corselet", corselet, BITUME, mat=CORSELET, poil=False)
    a.couture("suture_nuque", "corselet", 14, 0.58, 0.99, "droit", fil=BAGUE, large=0.011, haut=0.002, pas=0.015)
    a.couture("suture_front", "corselet", 42, 0.62, 0.99, "droit", fil=BAGUE, large=0.011, haut=0.002, pas=0.015)

    # ----- la tête : une petite boule de velours aux bajoues lourdes, à moitié rentrée sous la visière -----
    def caboche(v):
        v = K.bosse(K.bosse(v, (0.70, -0.45, -0.40), 0.10, 0.25), (-0.70, -0.45, -0.40), 0.10, 0.25)
        return K.emousse(v, 0.90) * [0.042, 0.038, 0.034]
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(caboche), OCRE, mat=PORT)
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, vers(0.30 * cote, -0.88, 0.34))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0100)
        # une lourde paupière châtaigne, qui lui tombe sur l'œil : l'air bourru
        a.piece("lourde_" + nom, K.paupiere(0.0100, 0.22), BAGUE, mat=A.cadre(p + n * 0.003, n, vers(0, 0.15, 1)), poil=False)
        # les antennes : courtes, couchées vers l'avant et vers le dehors
        p, n = a.surface("tete", TETE, vers(0.55 * cote, -0.70, 0.45))
        fil = A.courbe([p - n * 0.004, p + vers(0.012 * cote, -0.016, 0.010), p + vers(0.030 * cote, -0.034, 0.012),
                        p + vers(0.048 * cote, -0.044, 0.004)], 6)
        a.piece("antenne_" + nom, K.tube_peint(fil, lambda t: 0.0050 - 0.0018 * t, [(0.75, BITUME), (9, BAGUE)]), None, poil=False)
    # la bouche : un trait court qui tombe d'un côté
    bouche = a.trace("tete", TETE, [vers(x, -0.90, z) for x, z in ((0.26, -0.30), (0.08, -0.36), (-0.10, -0.38), (-0.22, -0.46))], 0.003)
    a.broderie("bouche", A.courbe(bouche, 4), 0.0024, BITUME)

    # ----- les pattes fouisseuses : la gauche tendue devant elle, la paume vers la terre, les dents en éventail prêtes à
    #       mordre ; la droite levée en plein coup de rame -----
    for nom, epaule, coude, poignet, face, doigts in (
            ("G", (0.046, -0.090, 0.042 + LEVE), (0.076, -0.110, 0.044 + LEVE), (0.086, -0.140, 0.040 + LEVE), (-0.09, 0.23, -0.97), (0.35, -0.90, -0.25)),
            ("D", (-0.046, -0.090, 0.046 + LEVE), (-0.076, -0.108, 0.058 + LEVE), (-0.088, -0.132, 0.074 + LEVE), (-0.80, -0.20, 0.40), (-0.35, -0.80, 0.45))):
        a.piece("bras_" + nom, bras(epaule, coude, poignet, face, doigts), OCRE)
        a.piece("pelle_" + nom, pelle(poignet, face, doigts), None, poil=False)

    # ----- les ailes : deux courtes en cuir posées en toit sur l'avant du dos, et dessous, les deux longues pointes
    #       coquelicot qui dépassent jusqu'au bout de l'abdomen -----
    for nom, cote in (("G", 1), ("D", -1)):
        rep = A.cadre((0.016 * cote, 0.004, 0.094 + LEVE), (0.30 * cote, 0.02, 0.95), (0.10 * cote, 1.0, -0.06))
        a.piece("aile_" + nom, A.decoupe(pointe(0.100, 0.040), 0.005, 0.002), CUIR, mat=rep, poil=False)
        for k, x in enumerate((-0.007, 0.008)):
            a.broderie("nervure%d_%s" % (k, nom), [rep @ Vector((x * 0.5, 0.012, 0.0042)), rep @ Vector((x, 0.050, 0.0042)),
                                                   rep @ Vector((x * 0.6, 0.082, 0.0042))], 0.0017, BITUME)
        rep = A.cadre((0.006 * cote, 0.070, 0.101 + LEVE), (0.12 * cote, 0.06, 0.99), (0.10 * cote - 0.02, 1.0, -0.06))
        a.piece("pointe_" + nom, A.decoupe(pointe(0.130, 0.016), 0.004, 0.0015), COQUELICOT, mat=rep, poil=False)

    # ----- les deux cerques : deux longues queues fines au bout de l'abdomen, en V, la pointe claire -----
    bout = Vector((-0.029, 0.200, 0.074 + LEVE))
    for nom, fin in (("G", (0.028, 0.062, 0.020)), ("D", (-0.034, 0.052, 0.008))):
        chemin = A.courbe([bout - Vector((0, 0.010, 0)), bout + Vector(fin) * 0.5 + Vector((0, 0, 0.006)), bout + Vector(fin)], 6)
        a.piece("cerque_" + nom, K.tube_peint(chemin, lambda t: 0.0060 - 0.0030 * t, [(0.70, BITUME), (9, K.CREME)]), None, poil=False)

    # ----- les quatre pattes de marche, courtes et trapues, la chaussette sombre ; aucune n'est posée comme sa voisine -----
    for cote, nom in ((1, "pattes_G"), (-1, "pattes_D")):
        milieu = [(0.040 * cote, -0.010, 0.030 + LEVE), (0.070 * cote, -0.020, 0.034 + LEVE), (0.080 * cote, 0.000 + 0.006 * cote, 0.008),
                  (0.090 * cote, 0.006 + 0.006 * cote, 0.004)]
        arriere = [(0.036 * cote, 0.060, 0.034 + LEVE), (0.070 * cote, 0.098, 0.058 + LEVE), (0.078 * cote, 0.082 + 0.008 * cote, 0.010),
                   (0.084 * cote, 0.072 + 0.008 * cote, 0.004)]
        pattes = None
        for chemin, gros in ((milieu, 0.0135), (arriere, 0.0170)):
            une = K.tube_peint(A.conges(chemin, 0.012, 5), lambda u, g=gros: g * (1 - 0.40 * u), [(0.55, OCRE), (9, BITUME)])
            pattes = une if pattes is None else pattes + une
        a.piece(nom, pattes, None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py courtiliere). Les mesures sont celles du modèle, avant a.taille.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.020, 0.070)),                  # le milieu du dos : elle roule et tangue autour
    ("queue", "corps", (-0.010, 0.120, 0.074)),                 # le bout de l'abdomen, qui fouette de côté
    ("tete", "corps", (0.0, -0.092, 0.066)),                   # la nuque, sous la visière
    ("bras_G", "corps", (0.046, -0.090, 0.060)),               # l'épaule de la pelle gauche (la droite est son miroir)
    ("ailes_G", "corps", (0.016, 0.004, 0.110)),               # la racine des ailes
    ("pattes_G", "racine", (0.040, 0.020, 0.046)),             # les pattes de marche : à la racine, elles restent au sol
]


def souple(points, cote):
    """L'abdomen : l'avant suit le corps, l'arrière la queue, en douceur entre les deux."""
    w = K.lisse((points[:, 1] - 0.050) / 0.120)
    return {"corps": 1 - w, "queue": w}


PORTEURS = [("abdomen", souple, "corps"), ("flanc", souple, "corps"), ("cerque", "queue"),
            ("corselet", "corps"), ("suture", "corps"),
            ("tete", "tete"), ("oeil", "tete"), ("lourde", "tete"), ("antenne", "tete"), ("bouche", "tete"),
            ("bras", "bras", True), ("pelle", "bras", True),
            ("aile", "ailes", True), ("nervure", "ailes", True), ("pointe", "ailes", True),
            ("pattes", "pattes", True),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def pelles(p, g, d):
    """Les deux pelles : (lève, tire en arrière) en degrés pour la gauche et pour la droite."""
    p.add("bras_G", rot=(0, -g[0], g[1]))
    p.add("bras_D", rot=(0, d[0], -d[1]))


def repos(t):
    """Elle respire, gratte l'air de sa pelle levée (deux coups de rame), tourne la tête vers ce qui bouge, fouette de
    l'abdomen, cligne d'un œil lourd."""
    p = Pose()
    r = onde(t, 2)
    rame = cloche(t, 0.30, 0.05) + cloche(t, 0.42, 0.05)
    p.add("corps", ech=(1 + 0.012 * r, 1, 1 + 0.020 * r))
    p.add("tete", rot=(2 * r, 0, 14 * cloche(t, 0.68, 0.12) - 6 * cloche(t, 0.15, 0.08)))
    pelles(p, (0, 0), (-10 * rame, 30 * rame))
    p.add("queue", rot=(0, 0, 9 * cloche(t, 0.80, 0.06) * onde(t, 8)))
    p.ouvert = 1 - cloche(t, 0.55, 0.02)
    return p


def avance(t):
    """Elle rame dans l'herbe comme dans la terre : une pelle tire pendant que l'autre revient, le corps roule à chaque
    coup, l'abdomen balance à contre-sens, les pattes trottinent."""
    p = Pose()
    s = onde(t, 1)
    p.add("corps", rot=(0, 5 * s, 4 * s), pos=(0, 0, 0.003 * abs(onde(t, 2))))
    pelles(p, (8 * max(0.0, -s), 28 * s), (8 * max(0.0, s), -28 * s))
    p.add("queue", rot=(0, 0, -8 * s))
    p.add("tete", rot=(0, -3 * s, -4 * s))
    p.add("pattes_G", rot=(0, 0, 10 * onde(t, 2)))
    p.add("pattes_D", rot=(0, 0, 10 * onde(t, 2, 0.25)))
    return p


def mange(t):
    """Elle pique du nez, creuse quatre coups de pelle à tour de rôle, mâche, puis relève la tête."""
    p = Pose()
    bas = 1 - cloche(t, 0.88, 0.12)
    creuse = onde(t, 4) * bas
    p.add("corps", rot=(10 * bas, 0, 0))
    p.add("tete", rot=(14 * bas + 4 * abs(onde(t, 8)) * bas, 0, 0))
    pelles(p, (-6 * bas, 26 * max(0.0, creuse)), (-6 * bas, 26 * max(0.0, -creuse)))
    p.add("queue", rot=(-6 * bas, 0, 0))
    p.ouvert = 1 - cloche(t, 0.92, 0.02)
    return p


def joie(t):
    """Elle se cabre sur l'abdomen, les deux pelles brandies au-dessus de la tête qu'elle tape l'une contre l'autre,
    les ailes qui frémissent ; puis elle retombe sur ses pattes."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.9)) if t < 0.9 else 0.0
    tape = abs(onde(t, 4)) * env
    p.add("corps", rot=(-24 * env, 0, 0), pos=(0, 0, 0.012 * env))
    p.add("tete", rot=(-10 * env, 0, 0))
    pelles(p, (50 * env + 12 * tape, -10 * env), (50 * env + 12 * tape, -10 * env))
    p.paire("ailes", rot=(0, -14 * env * abs(onde(t, 10)), 0))
    p.add("queue", rot=(10 * env, 0, 6 * onde(t, 6) * env))
    return p


def dort(t):
    """Tassée sur le ventre, les pelles ramenées sous le menton, les yeux fermés ; elle respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.010), rot=(3, 0, 0), ech=(1.02 + 0.010 * r, 1.0, 0.97 + 0.022 * r))
    p.add("tete", rot=(10, 0, 0))
    pelles(p, (-14, -18), (-14, -18))
    p.add("queue", rot=(0, 0, 6))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Courtilière")
