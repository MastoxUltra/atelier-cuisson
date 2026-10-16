"""Le chat des sables en peluche de velours ras : un sable gris et froid, presque pâle, un petit chat trapu à la tête
LARGE et aplatie comme une galette, de grandes oreilles triangulaires plantées bas et écartées, des yeux dorés très
espacés, des favoris touffus en collerette, de courtes jambes à la plante poilue, une queue épaisse annelée au bout
noir. Le fantôme du désert : assis bien droit, les pattes avant côte à côte, la grosse tête tournée vers nous.

    python chat_des_sables.py        fabrique la fiche art/apercus/animaux/chat_des_sables.png (velours ras, palier 3)
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


SABLE = np.array(M.hexa("#ddd2bc"))           # la dominante : sable gris froid (le poil le fonce)
CLAIR = np.array(M.hexa("#faf4e6"))           # le ventre, le museau, le dedans des oreilles, les favoris
DOS = np.array(M.hexa("#c8b898"))             # le dos, le dessus de la tête
RAYE = np.array(M.hexa("#7a5c44"))            # l'accent : les barres des pattes, les anneaux de la queue
NOIR = np.array(M.hexa("#2e2826"))            # le bout de la queue, le nez
OR = M.hexa("#d8c060")                        # les yeux dorés
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=60, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("chat_des_sables")
    a.taille = 0.50

    # ----- le corps : une poire trapue assise, penchée en arrière, la poitrine claire ; les cuisses fondues dans les hanches -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.170, 0.070), (0.110, 0.180), (0.040, 0.300), (0.000, 0.390))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.05, 0.100), (0.20, 0.140), (0.55, 0.124), (0.86, 0.094), (1.0, 0.0)], L, 72)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.teinte = np.where((th > 2.3)[:, None], CLAIR, np.where((th < 1.0)[:, None], DOS, SABLE))
    corps.v[:, 0] *= 1 + 0.18 * np.exp(-((corps.v[:, 2] / L - 0.14) / 0.10) ** 2)
    a.piece("corps", corps.sculpte(fil.couche), None)
    for nom, c in (("G", 1), ("D", -1)):
        cu = A.boule(1.0, 32, 16)
        cu.teinte = np.tile(SABLE, (len(cu.v), 1))
        a.piece("cuisse_" + nom, cu.etire(0.062, 0.090, 0.082), None, mat=A.cadre(Vector((c * 0.092, 0.100, 0.104)), Vector((c * 0.10, -0.95, 0.10)), (0, 0, 1)))
        a.piece("pied_ar_" + nom, A.boule(1.0, 20, 10).etire(0.034, 0.070, 0.022), tuple(CLAIR), pos=(c * 0.100, -0.050, 0.022), rot=(0, 0, c * 5))

    # ----- la tête : LARGE et aplatie, le museau minuscule ; les favoris en collerette ; les grandes oreilles écartées -----
    T = A.cadre(Vector((0.0, -0.036, 0.462)), Vector((0.24, -1.0, -0.04)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    cr = A.boule(1.0, 56, 28)
    cr.teinte = np.where((cr.v[:, 1] > 0.30)[:, None], DOS, SABLE)
    a.piece("tete", cr.etire(0.118, 0.074, 0.088), None, mat=T)
    a.piece("museau", A.boule(1.0, 24, 12).etire(0.036, 0.030, 0.030), tuple(CLAIR), mat=T @ A.repere((0.0, -0.016, 0.074)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.013, 0.009, 0.009), tuple(NOIR), mat=T @ A.repere((0.0, 0.000, 0.098)), poil=False)
    a.tete = T @ Vector((0.0, 0.0, 0.080))
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("favori_" + nom, A.boule(1.0, 20, 10).etire(0.046, 0.034, 0.040), tuple(CLAIR), mat=T @ A.repere((c * 0.092, -0.026, 0.020), (0, 0, c * 18)))
        regard = T3 @ Vector((c * 0.50, 0.12, 0.70))     # rapprochés, à la même hauteur dans le repère de la tête (l'auteur, 16/10 : « replace les yeux »)
        a.rustine("iris_" + nom, "tete", T.to_translation(), regard, 0.17, OR, 0.003, 0)
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0170)
        # (les raies brunes en paupière retirées : elles faisaient des sourcils fâchés et des yeux mi-clos)
        po = A.profil([(0, 0), (0.054, 0.010), (0.056, 0.034), (0.044, 0.070), (0.026, 0.104), (0.010, 0.130), (0, 0.142)], 7)
        vers = (T3 @ Vector((c * 0.78, 0.60, -0.14))).normalized()
        E = A.cadre(T @ Vector((c * 0.088, 0.040, -0.016)) - vers * 0.010, vers, T3 @ Vector((c * 0.2, 0.0, 1.0)))
        a.piece("oreille_" + nom, A.tour(po, 36).etire(1.0, 0.30, 1.0), tuple(DOS), mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 28).etire(0.62, 0.30, 0.80).pose((0, 0.010, 0.012)), tuple(CLAIR), mat=E, poil=False)

    # ----- les pattes avant : d'une seule pièce, du poitrail au sol, des barres brunes ; la queue épaisse annelée -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.060, 0.030, 0.350), (c * 0.058, -0.020, 0.240), (c * 0.056, -0.050, 0.100), (c * 0.056, -0.066, 0.036), (c * 0.056, -0.108, 0.026)]
        fa = K.Fil(ch, (1, 0, 0))
        av = fuseau([(0.0, 0.050), (0.18, 0.046), (0.50, 0.032), (0.74, 0.026), (0.82, 0.030), (0.94, 0.030), (1.0, 0.0)], fa.long, 28, 0.005)
        zz = av.v[:, 2] / fa.long
        ta = np.tile(SABLE, (len(zz), 1))
        ta[(zz > 0.45) & (zz < 0.52)] = RAYE                                       # la barre brune de la patte
        ta[zz > 0.80] = CLAIR
        av.teinte = ta
        a.piece("patte_av_" + nom, av.sculpte(fa.couche), None)
    qf = K.Fil([(0.0, 0.150, 0.070), (0.0, 0.240, 0.050), (0.070, 0.310, 0.034), (0.160, 0.340, 0.030), (0.240, 0.300, 0.030)], (1, 0, 0))
    LQ = qf.long
    queue = fuseau([(0.0, 0.040), (0.30, 0.044), (0.70, 0.040), (0.90, 0.034), (0.98, 0.022), (1.0, 0.0)], LQ, 36, 0.006)
    zq = queue.v[:, 2] / LQ
    tq = np.tile(SABLE, (len(zq), 1))
    for c0 in (0.40, 0.56, 0.72):
        tq[(zq > c0) & (zq < c0 + 0.06)] = RAYE
    tq[zq > 0.86] = NOIR
    queue.teinte = tq
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("chat_des_sables", styles.style_de("chat_des_sables"), sys.modules[__name__]), "Chat des sables")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py chat_des_sables). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.264                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.176, 0.219)),
    ('tete', 'corps', (0.002, 0.007, 0.403)),
    ('oreille_G', 'tete', (0.073, -0.006, 0.506)),
    ('patte_ar_G', 'corps', (0.092, 0.100, 0.186)),
    ('patte_av_G', 'corps', (0.060, 0.006, 0.341)),
    ('queue', 'corps', (-0.001, 0.190, 0.096)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('pavillon', 'oreille', True),
    ('pied_ar', 'patte_av', True), ('oreille', 'oreille', True), ('cuisse', 'patte_ar', True), ('museau', 'tete'),
    ('favori', 'tete'), ('corps', 'corps'), ('queue', 'queue'), ('tete', 'tete'), ('iris', 'tete'), ('oeil', 'tete'),
    ('raie', 'tete'), ('nez', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
    ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.079 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.145), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
