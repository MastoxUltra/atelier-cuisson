"""L'aye-aye en peluche de velours ras : un taupe sombre tout hirsute, une crinière de longs poils sur le dos, de grandes
oreilles rondes et minces comme des disques de papier, des yeux d'ambre immenses, la face rose sale, et surtout cette
longue main au doigt du milieu démesuré, crème, fin comme une baguette. Le tapoteur de la nuit : accroupi en boule,
le dos rond, l'oreille tournée vers nous, le long doigt levé au bord du tronc qu'il écoute, l'autre main dans la
fourrure : il compte les insectes sous l'écorce.

    python aye_aye.py        fabrique la fiche art/apercus/animaux/aye_aye.png (velours ras, palier 3)
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

TAUPE = M.hexa("#6e5a50")                     # la dominante : taupe sombre (le poil la fonce : on la prend plus claire)
CREME = M.hexa("#f6ead2")                     # l'accent : le long doigt, le bout des poils, le dedans des oreilles
ROSE = M.hexa("#c99a8a")                      # la face nue
AMBRE = M.hexa("#ffc233")                     # les yeux
CORPS = Vector((0.0, 0.050, 0.165))
TETE = Vector((0.0, -0.085, 0.300))
LACET = 20.0


def meche(chemin, large, face, plat=0.40, cotes=14):
    """Une mèche plate (le geste du cheval) couchée le long d'un chemin."""
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
    a = K.Animal("aye_aye")
    a.taille = 0.62

    # ----- le corps : une boule voûtée, accroupie ; le dos hérissé de longues mèches qui retombent des flancs -----
    def boule_(v):
        s = v * [0.118, 0.105, 0.125]
        s[:, 1] += 0.020 * K.lisse((v[:, 2] + 0.2) / 1.0)                           # le dos rond, bombé vers l'arrière
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(boule_), TAUPE, pos=CORPS)
    rng = np.random.default_rng(5)
    meches, bouts = None, None
    for i in range(18):
        t = 2 * math.pi * (i + rng.uniform(-0.3, 0.3)) / 18
        base = np.array([0.108 * math.cos(t), CORPS.y + 0.100 * math.sin(t)])
        radial = np.array([math.cos(t), math.sin(t)])
        hz = CORPS.z + rng.uniform(0.00, 0.075)
        k = 0.8 + 0.6 * rng.random()
        chemin = [(base[0] * 0.9, CORPS.y + (base[1] - CORPS.y) * 0.9, hz + 0.04), (base[0], base[1], hz - 0.01),
                  (base[0] + radial[0] * 0.030, base[1] + radial[1] * 0.030, hz - 0.075 * k),
                  (base[0] + radial[0] * 0.045, base[1] + radial[1] * 0.045, hz - 0.135 * k)]
        m = meche(chemin, 0.034 + 0.010 * rng.random(), (radial[0], radial[1], 0.0))
        if i % 5 == 0:
            bouts = m if bouts is None else bouts + m
        else:
            meches = m if meches is None else meches + m
    a.piece("meches", meches, TAUPE)
    a.piece("meches_claires", bouts, CREME)

    # ----- la tête : large et ronde, le museau court, les dents du rongeur sous la lèvre ; tournée vers nous -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()

    def tete_f(v):
        v = K.bosse(v, (0, -1.0, -0.2), 0.12, 0.35)
        return v * [0.100, 0.092, 0.090]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(tete_f), TAUPE, mat=H)
    a.piece("face", A.boule(1.0, 32, 16).etire(0.058, 0.046, 0.050), ROSE, mat=H @ A.repere((0, -0.060, -0.020)), poil=False)
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.016, 0.011, 0.011), M.hexa("#5a3b3b"), mat=H @ A.repere((0, -0.102, -0.016)), poil=False)
    a.tete = H @ Vector((0, -0.100, -0.010))
    bouche = [H3 @ Vector(d) for d in ((-0.30, -0.80, -0.55), (0.0, -0.90, -0.62), (0.30, -0.80, -0.55))]
    a.broderie("bouche", A.courbe(propres(a.trace("face", H @ Vector((0, -0.060, -0.020)), bouche, 0.004)), 4), 0.0022, M.hexa("#5a3b3b"))
    a.piece("dents", A.boule(1.0, 16, 8).etire(0.014, 0.010, 0.012), CREME, mat=H @ A.repere((0, -0.098, -0.056)), poil=False)

    # ----- les yeux : d'énormes disques d'ambre ; une paupière lourde dessus : il vous toise de la nuit -----
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.50, -0.82, 0.14))
        a.rustine("iris_" + nom, "tete", TETE, regard, 0.34, AMBRE, 0.003, 0)
        p, n = a.surface("tete", TETE, regard)
        a.oeil("oeil_" + nom, p + n * 0.005, n, 0.0215)

    # ----- les oreilles : deux immenses disques minces sur les côtés, le dedans crème ; la gauche tournée vers nous -----
    for nom, c in (("G", 1), ("D", -1)):
        E = A.cadre(H @ Vector((c * 0.090, 0.018, 0.045)), H3 @ Vector((c * 0.80, 0.10, 0.60)), H3 @ Vector((0, 1, 0)))
        a.piece("oreille_" + nom, A.boule(1.0, 36, 18).etire(0.078, 0.014, 0.088).pose((0, 0, 0.060)), TAUPE, mat=E)
        a.piece("pavillon_" + nom, A.boule(1.0, 28, 14).etire(0.060, 0.010, 0.070).pose((0, 0.006, 0.062)), CREME, mat=E, poil=False)

    # ----- les bras : le gauche, levé, se termine par la longue main au doigt démesuré ; le droit retombe -----
    haut = [(0.100, -0.030, 0.215), (0.185, -0.060, 0.240), (0.205, -0.125, 0.280)]
    a.piece("bras_G", A.tube(A.courbe(haut, 6), lambda t: 0.030 - 0.007 * t, 14), TAUPE)
    a.piece("main_G", A.boule(1.0, 24, 12).etire(0.032, 0.032, 0.030), TAUPE, pos=haut[-1])
    doigt = A.tube(A.courbe([(0.205, -0.135, 0.288), (0.222, -0.200, 0.325), (0.232, -0.270, 0.385), (0.235, -0.315, 0.460)], 5),
                   lambda t: 0.010 - 0.004 * t, 10)
    a.piece("doigt", doigt, CREME, poil=False)
    a.piece("articulation", A.boule(1.0, 16, 8).etire(0.016, 0.016, 0.014), CREME, pos=(0.222, -0.200, 0.325), poil=False)
    a.piece("bras_D", A.tube(A.courbe([(-0.100, -0.030, 0.215), (-0.145, -0.075, 0.150), (-0.125, -0.115, 0.085)], 6), lambda t: 0.030 - 0.006 * t, 14), TAUPE)
    a.piece("main_D", A.boule(1.0, 24, 12).etire(0.034, 0.040, 0.026), TAUPE, pos=(-0.125, -0.122, 0.070))

    # ----- les pieds : deux gros orteils posés devant, accroupi ; la queue : un énorme plumeau qui monte dans son dos -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("pied_" + nom, A.boule(1.0, 28, 14).etire(0.040, 0.075, 0.028), TAUPE, pos=(c * 0.085, -0.045, 0.030), rot=(0, 0, c * 12))
    queue = K.tube_peint(A.courbe([(0.0, 0.150, 0.110), (0.0, 0.300, 0.060), (0.040, 0.410, 0.150), (0.060, 0.400, 0.300), (0.030, 0.340, 0.400)], 6),
                         lambda t: 0.050 - 0.020 * t, [(0.75, TAUPE), (1, CREME)], 16)
    a.piece("queue", queue, None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("aye_aye", styles.style_de("aye_aye"), sys.modules[__name__]), "Aye-aye")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py aye_aye). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.427                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.092, 0.170)),
    ('tete', 'corps', (0.003, -0.031, 0.232)),
    ('oreille_G', 'tete', (0.058, -0.047, 0.336)),
    ('patte_av_G', 'corps', (0.234, -0.296, 0.427)),
    ('queue', 'corps', (-0.002, 0.167, 0.120)),
]

PORTEURS = [
    ('meches_claires', 'corps'), ('articulation', 'corps'), ('oeil_reflet', 'tete'), ('pavillon', 'oreille', True),
    ('oreille', 'oreille', True), ('meches', 'corps'), ('bouche', 'tete'), ('corps', 'corps'), ('dents', 'tete'),
    ('doigt', 'patte_av_G'), ('queue', 'queue'), ('tete', 'tete'), ('bras', 'patte_av', True),
    ('main', 'patte_av', True), ('pied', 'patte_av', True), ('face', 'corps'), ('iris', 'tete'), ('oeil', 'tete'),
    ('nez', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'),
    ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add('oreille_G', rot=(0, 0, 20 * cloche(t, 0.50, 0.05) - 8 * g))
    p.add('oreille_D', rot=(0, 0, -20 * cloche(t, 0.88, 0.05) + 6 * d))
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
    for nom, sens in [('patte_av_G', 1), ('patte_av_D', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.paire('oreille', rot=(-8 + 3 * onde(t, 2, -0.25), 0, 0))
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
    p.paire('oreille', rot=(-6 * bas + 5 * leve, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.128 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.235), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
