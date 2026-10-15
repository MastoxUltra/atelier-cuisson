"""Le géocoucou (le grand coureur du désert) en peluche cousue main : un long oiseau maigre brun strié de crème, le
corps à l'horizontale sur de grandes pattes, un cou fin et rayé, une petite tête au bec long et droit, la huppe en
brosse rabattue vers l'arrière, une tache bleue et orange derrière l'œil, une très longue queue relevée aux bouts
blancs. Le coureur : arrêté net sur un pied, la tête tendue vers nous, la queue en l'air, prêt à repartir.

    python geocoucou.py        fabrique la fiche art/apercus/animaux/geocoucou.png (cousu main, palier 2)
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
    """Les points d'un tracé sans doublons consécutifs (deux points identiques à la suite déforment un tube en NaN)."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie


BRUN = np.array(M.hexa("#a88458"))            # la dominante : brun strié (le feutre le fonce)
FONCE = np.array(M.hexa("#5a4230"))           # les stries, la huppe, la queue
CREME = np.array(M.hexa("#fbf0d8"))           # le ventre, les stries claires, le bout de la queue
BEC = np.array(M.hexa("#6a5848"))
BLEU = M.hexa("#8cc0e8")                      # la peau nue derrière l'œil
ORANGE = M.hexa("#f0a050")
CHARBON = M.hexa("#3a3028")
PAS = 0.006
LACET = 20.0


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=48, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def striee(m, pas_a, pas_z, base, fonce, ventre=None):
    """Peint des stries courtes (des tirets) : sombres sur le brun, la fente du ventre crème."""
    v = m.v
    th = np.arctan2(v[:, 0], v[:, 1])
    t = np.tile(base, (len(v), 1))
    t[(np.sin(th * pas_a) > 0.35) & (np.sin(v[:, 2] * pas_z) > -0.1)] = fonce
    if ventre is not None:
        t[ventre(th)] = CREME
    m.teinte = t
    return m


def construire():
    a = K.Animal("geocoucou")
    a.taille = 0.80

    # ----- le corps : un long fuseau à l'horizontale, le dos strié de brun, le ventre crème -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.230, 0.370), (0.120, 0.395), (0.000, 0.420), (-0.100, 0.445))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.06, 0.056), (0.28, 0.088), (0.62, 0.090), (0.88, 0.068), (1.0, 0.0)], L, 56)
    striee(corps, 11.0, 70.0, BRUN, FONCE, ventre=lambda th: np.abs(th) > 2.3)
    a.piece("corps", corps.sculpte(fil.couche), None)
    for nom, c in (("G", 1), ("D", -1)):
        ai = A.boule(1.0, 28, 14)
        ai.teinte = np.where((np.sin(ai.v[:, 1] * 22.0) > 0.55)[:, None], tuple(CREME), tuple(FONCE))
        a.piece("aile_" + nom, ai.etire(0.034, 0.140, 0.062), None, pos=(c * 0.082, 0.070, 0.425), rot=(-6, 0, c * 4))

    # ----- le cou : fin, rayé de crème ; la tête petite, la huppe en brosse, le long bec droit ; l'œil et sa tache nue -----
    cf = K.Fil([(0.0, y, z) for y, z in ((-0.080, 0.440), (-0.150, 0.470), (-0.210, 0.520), (-0.250, 0.575))], (1, 0, 0))
    cou = fuseau([(0.0, 0.050), (0.5, 0.040), (1.0, 0.034)], cf.long, 32)
    striee(cou, 9.0, 60.0, CREME, FONCE)
    a.piece("cou", cou.sculpte(cf.couche), None)
    TETE = Vector((0.0, -0.268, 0.598))
    H = A.repere(TETE, (0, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 36, 18)
    tete.teinte = np.where((tete.v[:, 2] > 0.2)[:, None], tuple(FONCE), tuple(BRUN))
    a.piece("tete", tete.etire(0.044, 0.054, 0.044), None, mat=H)
    a.tete = H @ Vector((0.0, -0.080, -0.010))
    bec = fuseau([(0.0, 0.026), (0.30, 0.024), (0.75, 0.014), (1.0, 0.0)], 0.170, 24, 0.005)
    bec.teinte = np.tile(BEC, (len(bec.v), 1))
    Bm = A.cadre(H @ Vector((0.0, -0.040, -0.004)), H3 @ Vector((0.0, -1.0, -0.10)), Vector((0, 0, 1)))
    a.piece("bec", bec, None, mat=Bm, poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.80, -0.42, 0.14))
        a.rustine("peau_" + nom, "tete", H.to_translation(), regard, 0.34, BLEU, 0.003, 0)
        a.rustine("orange_" + nom, "tete", H.to_translation(), H3 @ Vector((c * 0.84, 0.22, 0.20)), 0.14, ORANGE, 0.0035, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0120)
    for k, (dx, hu) in enumerate(((-0.020, 0.075), (0.0, 0.088), (0.020, 0.075))):
        hup = A.tour(A.profil([(0, 0), (0.018, 0.004), (0.011, 0.040), (0, hu)], 4), 10)
        a.piece("huppe_%d" % k, hup, tuple(FONCE), mat=A.cadre(H @ Vector((dx, 0.024, 0.030)), H3 @ Vector((dx * 3.0, 0.62, 0.58)), (0, 0, 1)), poil=False)

    # ----- les pattes : longues, les cuisses emplumées, le pied à deux orteils devant et deux derrière ; un pas esquissé -----
    for nom, c, avance in (("G", 1, 0.0), ("D", -1, 0.060)):
        a.piece("cuisse_" + nom, A.boule(1.0, 24, 12).etire(0.046, 0.074, 0.062), tuple(BRUN), pos=(c * 0.058, 0.040, 0.350), rot=(-10, 0, 0))
        ch = [(c * 0.056, 0.040, 0.320), (c * 0.058, 0.010 - avance, 0.170), (c * 0.058, -0.010 - avance * 1.2, 0.024)]
        a.piece("patte_" + nom, A.tube(A.courbe(propres(ch), 5), 0.013, 10), tuple(BEC), poil=False)
        for ang in (-28, 28, 160, -160):
            d = A.boule(1.0, 12, 6).etire(0.0075, 0.052, 0.008).pose((0, -0.040, 0.0)).pose((0, 0, 0), (0, 0, ang))
            a.piece("orteil_%s%d" % (nom, ang), d, tuple(BEC), pos=(ch[-1][0], ch[-1][1], 0.010), poil=False)

    # ----- la queue : très longue, relevée, brun sombre aux bouts blancs, large vers le bout -----
    qf = K.Fil([(0.0, 0.200, 0.382), (0.0, 0.330, 0.420), (0.0, 0.470, 0.510), (0.0, 0.560, 0.600)], (1, 0, 0))
    LQ = qf.long
    queue = fuseau([(0.0, 0.040), (0.25, 0.046), (0.65, 0.054), (0.92, 0.046), (1.0, 0.0)], LQ, 36, 0.006)
    queue.teinte = np.where((queue.v[:, 2] > 0.88 * LQ)[:, None], tuple(CREME), tuple(FONCE))
    queue.v[:, 0] *= 1.35
    a.piece("queue", queue.sculpte(lambda v: v * [1.0, 0.45, 1.0]).sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("geocoucou", styles.style_de("geocoucou"), sys.modules[__name__]), "Géocoucou")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py geocoucou). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.408                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.148, 0.405)),
    ('cou', 'corps', (-0.000, -0.086, 0.452)),
    ('tete', 'cou', (-0.003, -0.236, 0.566)),
    ('patte_av_G', 'corps', (0.057, 0.043, 0.408)),
    ('aile_G', 'corps', (0.084, 0.045, 0.487)),
    ('queue', 'corps', (-0.000, 0.211, 0.389)),
]

PORTEURS = [
    ('orteil_G-160', 'patte_av_G'), ('orteil_D-160', 'patte_av_D'), ('oeil_reflet', 'tete'),
    ('orteil_G-28', 'patte_av_G'), ('orteil_G160', 'patte_av_G'), ('orteil_D-28', 'patte_av_D'),
    ('orteil_D160', 'patte_av_D'), ('orteil_G28', 'patte_av_G'), ('orteil_D28', 'patte_av_D'), ('huppe_0', 'tete'),
    ('huppe_1', 'tete'), ('huppe_2', 'tete'), ('orange', 'tete'), ('cuisse', 'patte_av', True), ('corps', 'corps'),
    ('queue', 'queue'), ('patte', 'patte_av', True), ('aile', 'aile', True), ('tete', 'tete'), ('peau', 'tete'),
    ('oeil', 'tete'), ('cou', 'cou'), ('bec', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
    ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('cou', rot=(2 * r, 0, 8 * g - 6 * d))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add('queue', rot=(0, 0, 10 * onde(t, 1)))
    p.paire('aile', rot=(0, -3 * cloche(t, 0.55, 0.06), 0))
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
    p.add('cou', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('tete', rot=(3 - 2 * onde(t, 2, -0.2), -2 * c, -2 * s))
    p.add('queue', rot=(-6, 0, -10 * s))
    p.paire('aile', rot=(0, -2 + 2 * onde(t, 2), 0))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('cou', rot=(34 * bas + 4 * coups, 0, 5 * leve))
    p.add('tete', rot=(18 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.123 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    p.paire('aile', rot=(0, -48 * vol, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.225), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
