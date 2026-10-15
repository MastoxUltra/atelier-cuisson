"""Le paresseux en peluche de velours ras : un beige lichen tout hirsute, des mèches qui lui pendent du corps comme de
la mousse, la face crème et ronde sous deux grands masques chocolat qui lui font un sourire permanent, et des bras
démesurés aux trois longues griffes crème. Le roi de la lenteur : assis en tas, la tête penchée de côté sur l'épaule,
les yeux presque fermés, les bras qui pendent jusqu'au sol, un bout de sourire : il n'a pas encore fini d'y penser.

    python paresseux.py        fabrique la fiche art/apercus/animaux/paresseux.png (velours ras, palier 3)
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

LICHEN = M.hexa("#e4d9b4")                    # la dominante : beige lichen (le poil le dore : on le prend clair)
MOUSSE = M.hexa("#d0c898")                    # les mèches, un ton plus bas, un rien verdi
CREME = M.hexa("#fffbe8")                     # la face
CHOCOLAT = M.hexa("#5a4030")                  # l'accent : les masques d'œil, le nez
GRIFFE = M.hexa("#f2e4c0")                    # les griffes
CORPS = Vector((0.0, 0.040, 0.250))
TETE = Vector((0.0, -0.100, 0.455))
LACET, PENCHE = 18.0, 14.0                    # la tête tournée vers nous, penchée sur l'épaule


def meche(chemin, large, face, plat=0.40, cotes=14):
    """Une mèche plate (le geste des mèches du cheval) couchée le long d'un chemin."""
    p = A.courbe(chemin, 8)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    n0 = np.asarray(face, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.linalg.norm(t, axis=1, keepdims=True)
        x = np.cross(n0, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.60 * large, 0.05 * L), (0.95 * large, 0.22 * L), (large, 0.42 * L), (0.72 * large, 0.70 * L),
                     (0.30 * large, 0.93 * L), (0.06 * large, 0.985 * L), (0, L)], 5)
    return A.tour(prof, cotes).etire(1.0, plat, 1.0).sculpte(couche)


def construire():
    a = K.Animal("paresseux")
    a.taille = 0.80

    # ----- le corps : un gros tas rond, le dos voûté, le ventre qui s'étale sur le sol -----
    def tas(v):
        v = K.bosse(v, (0, -0.8, 0.2), 0.10, 0.5)
        s = v * [0.185, 0.175, 0.200]
        s[:, 2] = np.where(s[:, 2] < 0, s[:, 2] * 0.85, s[:, 2])
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(tas), LICHEN, pos=CORPS)

    # ----- des mèches de mousse : des longues mèches plates qui pendent des flancs et du dos, comme du lichen -----
    rng = np.random.default_rng(11)
    meches = None
    for i in range(22):
        t = 2 * math.pi * (i + rng.uniform(-0.3, 0.3)) / 22
        base = np.array([0.168 * math.cos(t), CORPS.y + 0.160 * math.sin(t)])
        radial = np.array([math.cos(t), math.sin(t)])
        hz = CORPS.z + rng.uniform(-0.01, 0.07)
        k = 0.8 + 0.5 * rng.random()
        chemin = [(base[0] * 0.92, base[1] * 0.92 + CORPS.y * 0.08, hz + 0.04), (base[0], base[1], hz - 0.04),
                  (base[0] + radial[0] * 0.035, base[1] + radial[1] * 0.035, hz - 0.10 * k),
                  (base[0] + radial[0] * 0.050, base[1] + radial[1] * 0.050, hz - 0.165 * k)]
        m = meche(chemin, 0.042 + 0.012 * rng.random(), (radial[0], radial[1], 0.0))
        meches = m if meches is None else meches + m
    a.piece("meches", meches, MOUSSE)

    # ----- la tête : ronde et petite, les joues molles ; penchée sur l'épaule, tournée vers nous -----
    H = A.repere(TETE, (0, PENCHE, LACET))
    H3 = H.to_3x3()

    def tete_f(v):
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.9, -0.2, -0.35), 0.14, 0.30)
        return v * [0.112, 0.100, 0.098]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(tete_f), LICHEN, mat=H)
    a.tete = H @ Vector((0, -0.100, -0.005))
    # la face : un grand disque crème ; les masques chocolat en virgules qui descendent de chaque œil vers la joue
    a.rustine("face", "tete", TETE, H3 @ Vector((0, -1.0, 0.0)), lambda th: 0.62 + 0.06 * math.cos(2 * th), CREME, 0.003, 0)
    for nom, c in (("G", 1), ("D", -1)):
        masque = H3 @ Vector((c * 0.46, -0.84, 0.0))
        a.rustine("masque_" + nom, "tete", TETE, masque, lambda th: 0.26 + 0.20 * max(0.0, -math.sin(th)) ** 1.2, CHOCOLAT, 0.004, 0)
        p, n = a.surface("tete", TETE, H3 @ Vector((c * 0.46, -0.84, 0.10)))
        a.oeil("oeil_" + nom, p + n * 0.005, n, 0.0135)
        a.piece("lourde_" + nom, K.paupiere(0.0165, 0.02), LICHEN, mat=A.cadre(p + n * 0.006, n, H3 @ Vector((0, 0, 1))), poil=False)
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.022, 0.014, 0.014), CHOCOLAT, mat=H @ A.repere((0, -0.102, -0.014)), poil=False)
    sourire = [H3 @ Vector(d) for d in ((-0.38, -0.84, -0.42), (-0.16, -0.92, -0.52), (0.16, -0.92, -0.52), (0.40, -0.80, -0.42))]
    a.broderie("sourire", A.courbe(propres(a.trace("tete", TETE, sourire, 0.004)), 4), 0.0030, CHOCOLAT)

    # ----- les bras : démesurés, ils pendent devant jusqu'au sol, les trois griffes crème qui griffent l'herbe -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.150, -0.040, 0.350), (c * 0.205, -0.110, 0.250), (c * 0.215, -0.185, 0.120), (c * 0.205, -0.235, 0.040)]
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.050 - 0.012 * t, 16), LICHEN)
        griffes = None
        for k in (-1, 0, 1):
            g = A.tour(A.profil([(0, 0), (0.014, 0.004), (0.011, 0.040), (0.005, 0.075), (0, 0.095)], 5), 14)
            g = g.etire(1.5, 1.5, 1.7).pose((0, 0, 0), (-80, 0, 0)).pose((k * 0.026, -0.015, 0.0), (0, 0, k * 10))
            griffes = g if griffes is None else griffes + g
        a.piece("griffes_" + nom, griffes, GRIFFE, pos=(chemin[-1][0], chemin[-1][1], 0.026), poil=False)
        a.piece("main_" + nom, A.boule(1.0, 24, 12).etire(0.046, 0.054, 0.038), LICHEN, pos=(chemin[-1][0], chemin[-1][1] - 0.010, 0.050))

    # ----- les jambes : deux petits genoux repliés sous le tas, les pieds à plat -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.boule(1.0, 28, 14).etire(0.060, 0.090, 0.062), LICHEN, pos=(c * 0.100, 0.020, 0.062))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("paresseux", styles.style_de("paresseux"), sys.modules[__name__]), "Paresseux")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py paresseux). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.224                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.138, 0.274)),
    ('tete', 'corps', (0.004, -0.058, 0.368)),
    ('patte_av_G', 'corps', (0.171, -0.065, 0.324)),
    ('patte_ar_G', 'corps', (0.103, 0.024, 0.123)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('griffes', 'patte_av', True), ('sourire', 'tete'), ('lourde', 'tete'),
    ('cuisse', 'patte_ar', True), ('meches', 'corps'), ('masque', 'tete'), ('corps', 'corps'), ('tete', 'tete'),
    ('bras', 'patte_av', True), ('main', 'patte_av', True), ('face', 'corps'), ('oeil', 'tete'), ('nez', 'tete'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
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
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.067 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.123), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
