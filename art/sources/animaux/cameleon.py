"""Le caméléon en peluche, cousu main : un rose vif zébré de bandes turquoise, un corps haut et aplati comme une feuille,
la crête du dos en dents de scie, la queue enroulée en escargot, et surtout ses yeux : deux tourelles coniques qui
tournent chacune de leur côté. Il avance au ralenti, une patte levée au-dessus du vide, un œil rivé sur nous et l'autre
qui regarde très haut, derrière lui, quelque chose que nous ne verrons jamais.

    python cameleon.py        fabrique la fiche art/apercus/animaux/cameleon.png (cousu main, palier 2)
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


def propres(points, eps=2e-4):
    """Les points d'un tracé sans doublons consécutifs (un tube dont deux points se suivent à l'identique se déforme en NaN) ;
    au moins deux points, écartés d'un millimètre au pire."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie

ROSE = M.hexa("#ff8db4")                      # la dominante : rose vif (le poil la fonce un peu)
TURQUOISE = M.hexa("#3fdcd0")                 # l'accent : les bandes, l'iris
CITRON = M.hexa("#fff27a")                    # la crête, le dessous
CHARBON = M.hexa("#3a3236")                   # les griffes, le bout de la queue
CORPS = Vector((0.0, 0.020, 0.190))


def construire():
    a = K.Animal("cameleon")
    a.taille = 0.55

    # ----- le corps : haut, aplati de côté, le dos voûté ; peint de bandes turquoise en travers (avant d'être sculpté) -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(ROSE, float), (len(v), 1))
    bande = (np.floor((v[:, 1] + 1.0) / 0.28) % 2 == 1)
    t[bande] = TURQUOISE
    t[(v[:, 2] < -0.55)] = CITRON                                                  # le ventre
    corps.teinte = t

    def feuille(v):
        s = v * [0.062, 0.175, 0.125]
        s[:, 2] += 0.030 * np.cos(v[:, 1] * 1.4)                                    # le dos voûté
        return s
    G.sillons(corps, [14], 0.004, 1.1)
    a.piece("corps", corps.sculpte(feuille), None, pos=CORPS, rot=(-6, 0, 0))

    # ----- la crête : de petites dents de scie citron le long de l'échine -----
    dents = None
    for i, y in enumerate(np.linspace(-0.130, 0.140, 8)):
        d = A.tour(A.profil([(0, 0), (0.016, 0.004), (0.012, 0.022), (0, 0.040)], 4), 14).etire(0.55, 1.0, 1.0)
        d = d.pose((0, CORPS.y + y, CORPS.z + 0.120 + 0.025 * math.cos(y * 1.4 * 1.0)), (-4, 0, 0))
        dents = d if dents is None else dents + d
    a.piece("crete", dents, CITRON, poil=False)

    # ----- la tête : un coin, le casque pointu vers l'arrière, le menton fin ; tournée vers nous -----
    T = A.repere(Vector((0.0, -0.200, 0.250)), (8, 0, 20))
    T3 = T.to_3x3()

    def casque(v):
        s = v.copy()
        s[:, 2] += 0.060 * K.lisse((v[:, 1] - 0.2) / 0.8) * (1 - v[:, 0] ** 2)       # le casque se relève derrière
        s[:, 0] *= 0.60 + 0.30 * K.lisse((v[:, 1] + 0.3) / 1.0)
        return s * [0.064, 0.100, 0.060]
    a.piece("tete", K.bandes(A.boule(1.0, 40, 20), [(-0.55, CITRON), (9, ROSE)], axe=1).sculpte(casque), None, mat=T)
    a.tete = T @ Vector((0, -0.100, 0.0))
    a.piece("nez", A.boule(1.0, 16, 8).etire(0.012, 0.012, 0.010), CHARBON, mat=T @ A.repere((0, -0.098, 0.004)), poil=False)
    bouche = [T3 @ Vector(d) for d in ((-0.30, -0.78, -0.30), (0.0, -0.98, -0.34), (0.32, -0.76, -0.30))]
    a.broderie("sourire", A.courbe(propres(a.trace("tete", T.to_translation(), bouche, 0.004)), 4), 0.0022, CHARBON)

    # ----- les yeux en tourelle : deux petits cônes de la couleur de la peau, un iris turquoise, une pupille : celui qui
    #       nous regarde droit, l'autre tourné très haut -----
    for nom, c, regard in (("G", 1, (0.40, -0.90, 0.12)), ("D", -1, (-0.80, 0.30, 0.50))):
        place = T @ Vector((c * 0.060, -0.018, 0.034))
        cone = A.boule(1.0, 28, 14).etire(0.040, 0.040, 0.036)
        a.piece("tourelle_" + nom, cone, ROSE, mat=A.repere(place))
        vers = T3 @ Vector(regard)
        vers.normalize()
        p, n = a.surface("tourelle_" + nom, place, vers)
        a.rustine("iris_" + nom, "tourelle_" + nom, place, vers, 0.62, TURQUOISE, 0.003, 14)
        a.oeil("oeil_" + nom, p + n * 0.006, n, 0.0135)

    # ----- les pattes : quatre pattes fines, coudées, aux doigts en pince ; l'avant gauche levée dans le vide -----
    def patte(points, r=0.019):
        return A.tube(A.courbe(points, 6), lambda t: r - 0.006 * t, 12)
    pattes = (("av_D", [(-0.040, -0.110, 0.230), (-0.085, -0.120, 0.130), (-0.060, -0.135, 0.030)]),
              ("ar_G", [(0.040, 0.130, 0.220), (0.085, 0.145, 0.120), (0.060, 0.130, 0.030)]),
              ("ar_D", [(-0.040, 0.130, 0.220), (-0.085, 0.145, 0.120), (-0.060, 0.130, 0.030)]),
              ("av_G", [(0.040, -0.110, 0.230), (0.090, -0.150, 0.190), (0.075, -0.210, 0.175)]))
    for nom, pts in pattes:
        a.piece("patte_" + nom, patte(pts), ROSE)
        x, y, z = pts[-1]
        a.piece("pince_" + nom, A.boule(1.0, 20, 10).etire(0.026, 0.032, 0.015), CHARBON, pos=(x, y - 0.010, z - 0.004 if z < 0.1 else z), poil=False)

    # ----- la queue : un long fouet qui s'enroule en escargot dans son dos, le bout charbon -----
    chemin = [(0.0, 0.160, 0.170)]
    for k in range(1, 15):
        ang = 0.55 * k
        r = 0.150 - 0.0075 * k
        chemin.append((0.0, 0.330 + r * math.sin(ang - 1.0), 0.190 + r * math.cos(ang - 1.0)))
    queue = K.tube_peint(A.courbe(chemin, 4), lambda t: 0.034 - 0.024 * t, [(0.55, ROSE), (0.70, TURQUOISE), (0.88, ROSE), (1.0, CHARBON)], 14)
    a.piece("queue", queue, None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("cameleon", styles.style_de("cameleon"), sys.modules[__name__]), "Caméléon")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py cameleon). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.227                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.075, 0.219)),
    ('tete', 'corps', (-0.013, -0.114, 0.248)),
    ('patte_av_D', 'corps', (-0.045, -0.111, 0.228)),
    ('patte_ar_G', 'corps', (0.045, 0.132, 0.218)),
    ('patte_av_G', 'corps', (0.052, -0.117, 0.235)),
    ('queue', 'corps', (-0.000, 0.159, 0.208)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('pince_av', 'patte_av', True), ('pince_ar', 'patte_ar', True), ('tourelle', 'corps'),
    ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('sourire', 'tete'), ('corps', 'corps'),
    ('queue', 'queue'), ('crete', 'tete'), ('tete', 'tete'), ('iris', 'tete'), ('oeil', 'tete'), ('nez', 'tete'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add('queue', rot=(0, 0, 10 * onde(t, 1)))
    p.ouvert = borne(1 - 0.3 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.62, 0.02))
    return p


def avance(t):
    """Sa marche : les pattes alternent, le corps oscille, la tête dodeline."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 26.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('queue', rot=(-6, 0, -10 * s))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.add('queue', rot=(0, 0, -7 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.068 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.125), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
