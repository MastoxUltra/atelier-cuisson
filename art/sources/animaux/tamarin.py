"""Le tamarin en peluche de velours ras : un or flamme lumineux, plus jaune que le tigre, une crinière de lion qui lui
encadre la tête comme une perruque de soleil, la petite face noire au museau plissé, les mains fines, et une très
longue queue qui s'enroule deux fois. Le seigneur minuscule des branches : accroupi, le torse bombé, la tête relevée
de trois quarts, les yeux d'ambre braqués sur nous, une main en visière : il a un royaume à surveiller.

    python tamarin.py        fabrique la fiche art/apercus/animaux/tamarin.png (velours ras, palier 3)
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

FLAMME = M.hexa("#ffd028")                    # la dominante : or flamme, très lumineux (le poil le fonce : on le prend clair)
CRINIERE = M.hexa("#ffbe1a")                  # la crinière, un ton plus chaud
FACE = M.hexa("#3a3236")                      # l'accent : la face noire, les mains
AMBRE = M.hexa("#ffb82a")                     # les yeux
CORPS = Vector((0.0, 0.040, 0.150))
TETE = Vector((0.0, -0.050, 0.305))
LACET = 24.0


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
    a = K.Animal("tamarin")
    a.taille = 0.55                           # queue comprise

    # ----- le corps : un petit œuf accroupi, le ventre en avant ; le dos or flamme -----
    def oeuf(v):
        s = v * [0.080, 0.075, 0.105]
        s[:, 1] -= 0.012 * K.lisse((v[:, 2] + 0.2) / 1.0)
        return s
    a.piece("corps", A.boule(1.0, 48, 24).sculpte(oeuf), FLAMME, pos=CORPS, rot=(-10, 0, 0))

    # ----- la tête : ronde, petite, la face noire (une rustine large) ; tournée vers nous -----
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 40, 20).etire(0.064, 0.060, 0.060), FLAMME, mat=H)
    a.rustine("face", "tete", TETE, H3 @ Vector((0, -1.0, -0.10)), lambda th: 0.52 + 0.08 * math.cos(2 * th), FACE, 0.003, 0)
    a.tete = H @ Vector((0, -0.090, -0.010))
    museau = A.tour(A.profil([(0, 0), (0.040, 0.006), (0.038, 0.030), (0.028, 0.052), (0.014, 0.066), (0, 0.072)], 6), 28)
    a.piece("museau", museau.etire(1.0, 0.78, 1.0), FACE, mat=H @ A.repere((0, -0.026, -0.022), (90, 0, 0)))
    a.piece("arcade_G", A.boule(1.0, 20, 10).etire(0.036, 0.014, 0.014), CRINIERE, mat=H @ A.repere((0.026, -0.044, 0.026), (0, 0, -14)))
    a.piece("arcade_D", A.boule(1.0, 20, 10).etire(0.036, 0.014, 0.014), CRINIERE, mat=H @ A.repere((-0.026, -0.044, 0.026), (0, 0, 14)))
    bouche = [H3 @ Vector(d) for d in ((-0.26, -0.84, -0.50), (0.0, -0.94, -0.56), (0.26, -0.84, -0.50))]
    a.broderie("bouche", A.courbe(propres(a.trace("tete", TETE, bouche, 0.003)), 4), 0.0016, M.hexa("#ffd0d0"))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.40, -0.90, 0.16))
        p, n = a.surface("tete", TETE, regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0115)
        a.rustine("iris_" + nom, "tete", TETE, regard, 0.22, AMBRE, 0.0025, 0)

    # ----- la crinière : une couronne de mèches plates qui retombent autour de la tête, plus longues sur les côtés et
    #       sous le menton (la perruque de soleil) -----
    rng = np.random.default_rng(3)
    criniere = None
    for i in range(26):
        t = 2 * math.pi * (i + rng.uniform(-0.2, 0.2)) / 26
        haut = math.cos(t)                                         # 1 = sommet de la tête, -1 = sous le menton
        flanc = math.sin(t)
        # on tourne autour de la tête dans le plan frontal : x = flanc, z = haut ; les mèches partent du crâne en arrière
        racine = np.array(TETE) + np.array(H3 @ Vector((0.050 * flanc, 0.012, 0.050 * haut)))
        dehors = np.array(H3 @ Vector((flanc, 0.15, haut)))
        dehors /= np.linalg.norm(dehors)
        longueur = 0.050 + 0.020 * abs(flanc) + 0.012 * rng.random()
        chemin = [tuple(racine), tuple(racine + dehors * 0.018), tuple(racine + dehors * 0.040 + np.array([0, 0.008, -0.012])),
                  tuple(racine + dehors * longueur + np.array([0, 0.016, -0.030 - 0.030 * max(0.0, flanc * flanc)]))]
        m = meche(chemin, 0.020 + 0.006 * rng.random(), tuple(np.cross(dehors, np.array([0, 1.0, 0]))), 0.42)
        criniere = m if criniere is None else criniere + m
    a.piece("criniere", criniere, CRINIERE)

    # ----- les oreilles : de petits ronds noirs, cachés dans la crinière ; les bras : le gauche en visière -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("oreille_" + nom, A.boule(1.0, 20, 10).etire(0.018, 0.010, 0.020), FACE, pos=tuple(H @ Vector((c * 0.070, 0.004, 0.020))))
    gauche = [(0.072, -0.010, 0.215), (0.125, -0.040, 0.250), (0.115, -0.085, 0.325), (0.055, -0.095, 0.350)]
    droit = [(-0.072, -0.010, 0.215), (-0.100, -0.060, 0.150), (-0.085, -0.100, 0.085), (-0.060, -0.115, 0.060)]
    for nom, chemin in (("G", gauche), ("D", droit)):
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.017 - 0.004 * t, 12), FLAMME)
        a.piece("main_" + nom, A.boule(1.0, 20, 10).etire(0.017, 0.022, 0.014), FACE, pos=chemin[-1])

    # ----- les jambes : deux genoux repliés, les pieds noirs à plat ; la queue : très longue, deux boucles -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.boule(1.0, 24, 12).etire(0.034, 0.052, 0.040), FLAMME, pos=(c * 0.062, 0.000, 0.052))
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.024, 0.048, 0.016), FACE, pos=(c * 0.068, -0.050, 0.020), rot=(0, 0, c * 12))
    chemin = [(0.0, 0.110, 0.080), (0.0, 0.200, 0.040), (0.075, 0.250, 0.060), (0.080, 0.210, 0.130), (0.020, 0.190, 0.120), (0.020, 0.250, 0.100),
              (0.100, 0.320, 0.065)]
    queue = K.tube_peint(A.courbe(chemin, 6), lambda t: 0.020 - 0.008 * t, [(0.82, FLAMME), (1, CRINIERE)], 12)
    a.piece("queue", queue, None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tamarin", styles.style_de("tamarin"), sys.modules[__name__]), "Tamarin")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py tamarin). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.227                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.056, 0.099)),
    ('tete', 'corps', (-0.008, -0.016, 0.259)),
    ('oreille_G', 'tete', (0.048, -0.021, 0.319)),
    ('patte_av_G', 'corps', (0.056, -0.095, 0.362)),
    ('patte_ar_G', 'corps', (0.064, 0.006, 0.091)),
    ('queue', 'corps', (-0.002, 0.116, 0.075)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('criniere', 'corps'), ('oreille', 'oreille', True), ('cuisse', 'patte_ar', True),
    ('museau', 'tete'), ('arcade', 'tete'), ('bouche', 'tete'), ('corps', 'corps'), ('queue', 'queue'),
    ('tete', 'tete'), ('bras', 'patte_av', True), ('face', 'corps'), ('main', 'patte_av', True),
    ('pied', 'patte_av', True), ('oeil', 'tete'), ('iris', 'tete'), ('paupiere_0', 'paupiere_0'),
    ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    pas = 18.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
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
    p.add('corps', rot=(34 * bas + 3 * coups, 0, 0))
    p.paire('patte_av', rot=(-30 * bas, 0, 0))
    p.add('tete', rot=(16 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.068 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.02), rot=(36, 0, 6), ech=(1 + 0.010 * r, 1, 1 + 0.020 * r))
    p.paire('patte_av', rot=(-30, 0, 0))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
