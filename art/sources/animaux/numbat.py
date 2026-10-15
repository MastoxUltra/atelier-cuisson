"""Le numbat en peluche de velours ras (2e dessin) : un corps long et bas de marsupial, brun brique, un museau pointu
et fin, la poitrine claire, et sur l'ARRIÈRE du dos six à sept bandes crème en travers de la croupe, bien nettes ; une
queue en goupillon qui se dresse derrière lui. Le chasseur de termites au trot : tête basse, le museau au ras du sol,
une patte avant levée, le dos tendu en ligne, la queue dressée comme un point d'exclamation.

    python numbat.py        fabrique la fiche art/apercus/animaux/numbat.png (velours ras, palier 3)
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

BRIQUE = M.hexa("#cf7a4a")                    # la dominante : brun brique (le poil la fonce : on la prend claire)
CREME = M.hexa("#fff2d8")                     # l'accent : les bandes, la poitrine, le bout des pattes
CHARBON = M.hexa("#3a2c28")                   # le trait de l'œil, le nez
CORPS = Vector((0.0, 0.080, 0.150))
TETE = Vector((0.0, -0.330, 0.150))
LACET, PIQUE = 20.0, 22.0


def construire():
    a = K.Animal("numbat")
    a.taille = 0.60                           # queue comprise

    # ----- le corps : long, bas, étroit ; les bandes crème en travers de l'arrière du dos (de la mi-échine à la croupe) -----
    corps = A.boule(1.0, 64, 32)
    v = corps.v
    t = np.tile(np.asarray(BRIQUE, float), (len(v), 1))
    bande = (v[:, 1] > -0.10) & (v[:, 2] > 0.05) & (np.floor((v[:, 1] + 0.10) / 0.145) % 2 == 0)
    t[bande] = CREME
    t[(v[:, 1] < -0.30) & (v[:, 2] < 0.15)] = CREME
    t[(v[:, 2] < -0.45)] = CREME
    corps.teinte = t

    def long(v):
        v = K.bosse(v, (0, -0.85, 0.20), 0.08, 0.45)
        s = v * [0.068, 0.300, 0.080]
        s[:, 2] = np.where(s[:, 2] < 0, s[:, 2] * 0.80, s[:, 2])
        return s
    a.piece("corps", corps.sculpte(long), None, pos=CORPS)

    # ----- la tête : fine, le museau pointu et long ; basse, le trait charbon à travers l'œil ; les petites oreilles rondes -----
    H = A.repere(TETE, (PIQUE, 0, LACET))
    H3 = H.to_3x3()
    tete = A.tour(A.profil([(0, 0), (0.044, 0.008), (0.058, 0.044), (0.048, 0.095), (0.032, 0.150), (0.020, 0.205), (0.010, 0.238), (0, 0.256)], 6), 36)
    K.bandes(tete, [(0.215, BRIQUE), (9, CREME)])
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0.080, -0.010), (90, 0, 0)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.015, 0.011, 0.011), CHARBON, mat=H @ A.repere((0, -0.176, -0.010)), poil=False)
    a.tete = H @ Vector((0, -0.140, -0.010))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.50, -0.80, 0.28))
        p, n = a.surface("tete", H @ Vector((0, 0.020, -0.010)), regard)
        a.oeil("oeil_" + nom, p + n * 0.005, n, 0.0190)
        # (le trait charbon à travers l'œil est retiré : il se lisait comme un sourcil fâché)
        po = A.profil([(0, 0), (0.024, 0.006), (0.030, 0.022), (0.022, 0.038), (0.008, 0.046), (0, 0.050)], 5)
        E = A.cadre(H @ Vector((c * 0.046, 0.060, 0.026)), H3 @ Vector((c * 0.40, 0.20, 0.90)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.45, 1.0), BRIQUE, mat=E)

    # ----- les pattes : quatre fines, au trot ; l'avant gauche levée, les bouts crème -----
    def patte(points, r0):
        return K.tube_peint(A.courbe(points, 6), lambda t: r0 - 0.008 * t, [(0.82, BRIQUE), (1, CREME)], 12)
    for nom, pts in (("av_D", [(-0.050, -0.130, 0.130), (-0.060, -0.140, 0.080), (-0.062, -0.140, 0.020)]),
                     ("ar_G", [(0.055, 0.260, 0.130), (0.065, 0.300, 0.070), (0.066, 0.280, 0.020)]),
                     ("ar_D", [(-0.055, 0.260, 0.130), (-0.065, 0.250, 0.070), (-0.066, 0.230, 0.020)])):
        a.piece("patte_" + nom, patte(pts, 0.026), None)
        x, y, _z = pts[-1]
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.022, 0.040, 0.014), CREME, pos=(x, y - 0.020, 0.014))
    levee = [(0.050, -0.130, 0.130), (0.062, -0.180, 0.110), (0.064, -0.230, 0.100)]
    a.piece("patte_av_G", patte(levee, 0.026), None)
    a.piece("pied_av_G", A.boule(1.0, 20, 10).etire(0.022, 0.040, 0.014), CREME, pos=(0.064, -0.258, 0.098), rot=(-30, 0, 0))

    # ----- la queue : un goupillon dressé, qui part de la croupe et monte presque droit, brique puis crème -----
    chemin = [(0.0, 0.330, 0.150), (0.0, 0.430, 0.220), (0.0, 0.470, 0.340), (0.0, 0.460, 0.480)]
    queue = K.tube_peint(A.courbe(chemin, 6), lambda t: 0.034 + 0.030 * math.sin(math.pi * min(t * 1.25, 1.0)) - 0.016 * t,
                         [(0.74, BRIQUE), (0.88, CREME), (1, BRIQUE)], 16)
    a.piece("queue", queue, None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("numbat", styles.style_de("numbat"), sys.modules[__name__]), "Numbat")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py numbat). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde
GONFLAGE = True      # gardée par l'auteur sur la base GONFLÉE (planche 17, 15/10) : toujours gonflée

JAMBE = 0.136                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.225, 0.158)),
    ('tete', 'corps', (-0.005, -0.247, 0.149)),
    ('oreille_G', 'tete', (0.024, -0.283, 0.203)),
    ('patte_av_D', 'corps', (-0.057, -0.136, 0.129)),
    ('patte_ar_G', 'corps', (0.059, 0.278, 0.134)),
    ('patte_av_G', 'corps', (0.055, -0.149, 0.145)),
    ('queue', 'corps', (-0.000, 0.328, 0.174)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True),
    ('oreille', 'oreille', True), ('pied_av', 'patte_av', True), ('pied_ar', 'patte_ar', True), ('corps', 'corps'),
    ('queue', 'queue'), ('trait', 'tete'), ('tete', 'tete'), ('oeil', 'tete'), ('nez', 'tete'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.041 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.075), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
