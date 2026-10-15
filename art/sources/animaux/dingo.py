"""Le dingo en peluche de velours ras (3e dessin, d'après photos : plus de bâtons) : un chien sauvage SOUPLE et nerveux,
crème sable clair, le dos lavé de fauve doré, la poitrine et le bout des pattes blancs ; le thorax profond, la taille
fine, les cuisses pleines, des pattes à articulations (coude, poignet devant ; genou, jarret derrière) et de vrais pieds,
un long museau, de grandes oreilles dressées, une queue en brosse tombante au bout blanc. Au trot : la patte avant
gauche levée au milieu de la foulée, la tête basse, l'œil d'ambre fixé sur ce qu'il piste, un regard en coin vers nous.

    python dingo.py        fabrique la fiche art/apercus/animaux/dingo.png (velours ras, palier 3)
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


SABLE = np.array(M.hexa("#fff0cc"))           # la dominante : crème sable clair (le poil la dore)
FAUVE = np.array(M.hexa("#e8c490"))           # le dos lavé de fauve
BLANC = np.array(M.hexa("#fffaf0"))           # la poitrine, le bout des pattes et de la queue
AMBRE = M.hexa("#f0b838")
CHARBON = M.hexa("#3a2e2c")
PAS = 0.007


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("dingo")
    a.taille = 1.20

    # ----- le corps : un thorax profond devant, la taille fine, la croupe pleine ; le dos fauve, la poitrine blanche -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.430, 0.570), (0.250, 0.610), (0.040, 0.620), (-0.180, 0.640), (-0.340, 0.620))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.100), (0.14, 0.140), (0.34, 0.118), (0.52, 0.112), (0.70, 0.150), (0.88, 0.158),
                    (0.97, 0.120), (1.0, 0.0)], L, 64)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    f = corps.v[:, 2] / L
    t = np.tile(SABLE, (len(f), 1))
    t[th < 1.15] = FAUVE
    t[(th > 2.35) & (f > 0.55)] = BLANC
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)
    a.piece("cou", A.tube(A.courbe([(0.0, -0.290, 0.680), (0.0, -0.400, 0.740), (0.0, -0.470, 0.760)], 5), lambda t: 0.100 - 0.026 * t, 20), tuple(SABLE))

    # ----- la tête : un long museau, un front plat ; baissée, tournée vers nous, l'œil d'ambre -----
    T = A.cadre(Vector((0.0, -0.540, 0.740)), Vector((0.34, -1.0, -0.24)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.08, 0.064), (0.28, 0.086), (0.50, 0.070), (0.76, 0.052), (0.95, 0.042), (1.0, 0.0)], 0.300, 52, 0.006)
    tete.teinte = np.where((np.abs(np.arctan2(tete.v[:, 0], tete.v[:, 1])) > 2.5)[:, None], tuple(BLANC),
                           np.where((tete.v[:, 1] > 0.020)[:, None], tuple(FAUVE), tuple(SABLE)))
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.080)))
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.026, 0.020, 0.020), CHARBON, mat=T @ A.repere((0, 0.006, 0.222)), poil=False)
    a.tete = T @ Vector((0, 0.0, 0.140))
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.74, 0.36, 0.16))
        a.rustine("iris_" + nom, "tete", T.to_translation(), regard, 0.17, AMBRE, 0.003, 0)
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0150)
        po = A.profil([(0, 0), (0.046, 0.010), (0.050, 0.040), (0.040, 0.076), (0.020, 0.108), (0, 0.124)], 6)
        vers = (T3 @ Vector((c * 0.34, 0.90, 0.10))).normalized()
        E = A.cadre(T @ Vector((c * 0.058, 0.060, -0.020)) - vers * 0.010, vers, T3 @ Vector((c * 0.2, 0.0, 1.0)))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 32).etire(1.0, 0.34, 1.0), [(0.090, tuple(FAUVE)), (9, tuple(FAUVE))]), None, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 24).etire(0.60, 0.30, 0.78).pose((0, 0.008, 0.010)), tuple(BLANC), mat=E, poil=False)

    # ----- les pattes : de vraies articulations (coude, poignet / genou, jarret), des cuisses pleines, des pieds ; l'avant gauche levé -----
    def jambe(pts, rayons):
        ft = K.Fil(pts, (1, 0, 0))
        m = fuseau([(i / (len(rayons) - 1), r) for i, r in enumerate(rayons)], ft.long, 28, 0.006)
        z = m.v[:, 2] / ft.long
        m.teinte = np.where((z > 0.84)[:, None], tuple(BLANC), tuple(SABLE))
        return m.sculpte(ft.couche)
    av_rayons = [0.066, 0.058, 0.040, 0.030, 0.028, 0.030, 0.026, 0.0]
    ar_rayons = [0.096, 0.084, 0.050, 0.034, 0.028, 0.028, 0.030, 0.0]
    plantees = (("av_D", [(-0.095, -0.240, 0.580), (-0.100, -0.250, 0.400), (-0.100, -0.240, 0.130), (-0.100, -0.250, 0.030)], av_rayons),
                ("ar_G", [(0.105, 0.340, 0.570), (0.120, 0.250, 0.360), (0.110, 0.370, 0.180), (0.110, 0.350, 0.030)], ar_rayons),
                ("ar_D", [(-0.105, 0.340, 0.570), (-0.120, 0.250, 0.360), (-0.110, 0.370, 0.180), (-0.110, 0.350, 0.030)], ar_rayons))
    for nom, pts, ray in plantees:
        a.piece("patte_" + nom, jambe(pts, ray), None)
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.034, 0.060, 0.026), tuple(BLANC), pos=(pts[-1][0], pts[-1][1] - 0.022, 0.026))
    levee = [(0.095, -0.240, 0.580), (0.100, -0.280, 0.420), (0.100, -0.360, 0.340), (0.100, -0.380, 0.250)]
    a.piece("patte_av_G", jambe(levee, av_rayons), None)
    a.piece("pied_av_G", A.boule(1.0, 20, 10).etire(0.034, 0.060, 0.026), tuple(BLANC), pos=(0.100, -0.400, 0.232), rot=(-40, 0, 0))

    # ----- la queue : en brosse, qui retombe, le bout blanc -----
    qf = K.Fil([(0.0, 0.420, 0.580), (0.0, 0.540, 0.500), (0.010, 0.610, 0.360), (0.020, 0.600, 0.220)], (1, 0, 0))
    queue = fuseau([(0.0, 0.040), (0.35, 0.062), (0.80, 0.056), (0.97, 0.030), (1.0, 0.0)], qf.long, 36, 0.006)
    queue.teinte = np.where((queue.v[:, 2] > 0.80 * qf.long)[:, None], tuple(BLANC), tuple(SABLE))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("dingo", styles.style_de("dingo"), sys.modules[__name__]), "Dingo")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py dingo). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.562                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.133, 0.629)),
    ('cou', 'corps', (0.000, -0.254, 0.749)),
    ('tete', 'cou', (0.004, -0.470, 0.732)),
    ('oreille_G', 'tete', (0.042, -0.534, 0.805)),
    ('patte_av_D', 'corps', (-0.096, -0.246, 0.560)),
    ('patte_ar_G', 'corps', (0.107, 0.293, 0.561)),
    ('patte_av_G', 'corps', (0.096, -0.255, 0.566)),
    ('queue', 'corps', (-0.000, 0.426, 0.562)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True),
    ('pavillon', 'oreille', True), ('oreille', 'oreille', True), ('pied_av', 'patte_av', True),
    ('pied_ar', 'patte_ar', True), ('truffe', 'corps'), ('corps', 'corps'), ('queue', 'queue'), ('tete', 'tete'),
    ('iris', 'tete'), ('oeil', 'tete'), ('cou', 'cou'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
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
    p.add('cou', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('tete', rot=(3 - 2 * onde(t, 2, -0.2), -2 * c, -2 * s))
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
    p.add('cou', rot=(34 * bas + 4 * coups, 0, 5 * leve))
    p.add('tete', rot=(18 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.169 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.309), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
