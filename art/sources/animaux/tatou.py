"""Le tatou en peluche cousue main : un rose gris cuir, la carapace en larges bandes articulées (le bouclier de
l'épaule, les bandes du milieu, le bouclier de la croupe), le dessous nu, un museau pointu, de petites oreilles en
tuyau, des pattes courtes aux griffes de pelle, une queue en cône cuirassé. Le blindé timide : le museau au ras du sol
qui renifle, le dos en dôme, une patte avant levée ; il est à un souffle de se rouler en boule.

    python tatou.py        fabrique la fiche art/apercus/animaux/tatou.png (cousu main, palier 2)
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


CUIR = np.array(M.hexa("#e0b0a0"))            # la dominante : rose gris cuir (le poil le fonce)
PLAQUE = np.array(M.hexa("#c8968a"))          # les bandes de la carapace, un ton plus bas
JOINT = np.array(M.hexa("#8a6258"))           # les joints entre les bandes
VENTRE = np.array(M.hexa("#f4d8c8"))
GRIFFE = M.hexa("#f2e4cc")
NOIR = M.hexa("#3a3030")
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 5)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("tatou")
    a.taille = 0.75

    # ----- le corps : un dôme long et bas ; la carapace : bouclier, bandes articulées (des joints sombres nets), bouclier ;
    #       le dessous nu -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.250, 0.130), (0.130, 0.170), (0.000, 0.180), (-0.130, 0.165), (-0.220, 0.130))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.090), (0.14, 0.140), (0.45, 0.160), (0.78, 0.150), (0.94, 0.100), (1.0, 0.0)], L, 72)
    z = corps.v[:, 2]
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    f = z / L
    t = np.tile(PLAQUE, (len(z), 1))
    bande = (f > 0.30) & (f < 0.74)
    t[bande & (((f - 0.30) / 0.044) % 1.0 < 0.14)] = JOINT                              # les joints des bandes
    t[(f < 0.26) | (f > 0.78)] = CUIR * 0.96                                           # les deux boucliers
    t[th > 2.05] = VENTRE                                                              # le ventre nu
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- la tête : un coin pointu, le museau long ; les oreilles en tuyau ; les yeux petits ; penchée, le museau au sol -----
    H = A.cadre(Vector((0.0, -0.320, 0.140)), Vector((0.30, -1.0, -0.34)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.070), (0.22, 0.090), (0.46, 0.074), (0.74, 0.054), (0.95, 0.040), (1.0, 0.0)], 0.300, 48, 0.006)
    tete.teinte = np.tile(CUIR, (len(tete.v), 1))
    tete.teinte[(tete.v[:, 2] > 0.10) & (tete.v[:, 2] < 0.16)] = JOINT
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0, -0.050)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.022, 0.016, 0.016), tuple(JOINT), mat=H @ A.repere((0, 0.006, 0.250)), poil=False)
    a.tete = H @ Vector((0, 0.0, 0.140))
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H @ Vector((0, 0.0, 0.020)), H3 @ Vector((c * 0.84, 0.30, 0.0)))
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0120)
        po = A.profil([(0, 0), (0.020, 0.008), (0.028, 0.034), (0.022, 0.060), (0.008, 0.074), (0, 0.080)], 5)
        a.piece("oreille_" + nom, A.tour(po, 20).etire(1.0, 0.45, 1.0), tuple(CUIR),
                mat=A.cadre(H @ Vector((c * 0.060, 0.050, -0.040)), H3 @ Vector((c * 0.50, 0.30, 0.80)), H3 @ Vector((c * 0.3, -0.9, 0.0))))

    # ----- les pattes : courtes, aux griffes de pelle ; une patte avant levée ; la queue : un cône cuirassé à joints -----
    for nom, x_, y_, levee in (("av_G", 0.100, -0.160, True), ("av_D", -0.100, -0.160, False), ("ar_G", 0.105, 0.150, False), ("ar_D", -0.105, 0.150, False)):
        c = 1 if x_ > 0 else -1
        bas = (x_ * 1.05, y_ - (0.090 if levee else 0.020), 0.090 if levee else 0.030)
        a.piece("patte_" + nom, A.tube(A.courbe(propres([(x_, y_, 0.130), (x_ * 1.03, y_ - 0.030, 0.080), bas]), 5), 0.036, 12), tuple(CUIR))
        g = None
        for k in (-1, 0, 1):
            gr = A.tour(A.profil([(0, 0), (0.010, 0.003), (0.008, 0.028), (0.003, 0.052), (0, 0.062)], 5), 10)
            gr = gr.pose((0, 0, 0), (-78, 0, 0)).pose((k * 0.020, -0.020, 0.0), (0, 0, k * 8))
            g = gr if g is None else g + gr
        a.piece("griffes_" + nom, g, GRIFFE, pos=(bas[0], bas[1] - 0.016, bas[2] - 0.006), poil=False)
    queue = fuseau([(0.0, 0.070), (0.40, 0.050), (0.80, 0.026), (1.0, 0.0)], 0.300, 32, 0.006)
    queue.teinte = np.where(((queue.v[:, 2] / 0.040) % 1.0 < 0.16)[:, None], JOINT, PLAQUE)
    qf = K.Fil([(0.0, 0.240, 0.110), (0.0, 0.380, 0.070), (0.0, 0.500, 0.040)], (1, 0, 0))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tatou", styles.style_de("tatou"), sys.modules[__name__]), "Tatou")



# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py tatou). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.124                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.137, 0.180)),
    ('tete', 'corps', (0.017, -0.274, 0.128)),
    ('oreille_G', 'tete', (0.071, -0.328, 0.191)),
    ('patte_av_G', 'corps', (0.101, -0.188, 0.124)),
    ('patte_ar_G', 'corps', (0.107, 0.135, 0.123)),
    ('queue', 'corps', (-0.001, 0.266, 0.149)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('griffes_av', 'patte_av', True), ('griffes_ar', 'patte_ar', True),
    ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('oreille', 'oreille', True), ('corps', 'corps'),
    ('queue', 'queue'), ('tete', 'tete'), ('oeil', 'tete'), ('nez', 'tete'), ('paupiere_0', 'paupiere_0'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.037 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.068), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
