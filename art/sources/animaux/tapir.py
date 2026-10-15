"""Le tapir en peluche de velours ras : l'avant d'un ardoise bleutée moyen, la moitié arrière d'un crème franc qui
tombe d'un trait net en travers du dos, comme une selle jetée sur un baril ; une petite trompe molle qui pend du museau,
des oreilles rondes cernées de blanc et des yeux minuscules. Un doux aveugle des sous-bois : la tête basse, la trompe
qui renifle une odeur, une patte avant avancée à tâtons, tout le poids sur l'arrière-train.

    python tapir.py        fabrique la fiche art/apercus/animaux/tapir.png (velours ras, palier 3)
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

ARDOISE = M.hexa("#7189ad")                   # la dominante : ardoise bleutée moyenne (le poil la fonce)
CREME = M.hexa("#fbf4e4")                     # l'accent : la selle, le bord des oreilles
SOMBRE = M.hexa("#4e5d7c")                    # le museau, le dedans des oreilles, la trompe
SABOT = M.hexa("#3a3a44")                     # les sabots, le bout de la trompe
CROUPE = Vector((0.0, 0.420, 0.370))          # le bout arrière du corps (une pièce tournée, couchée vers l'avant)
LACET, PIQUE = 20.0, 28.0                     # la tête tournée vers nous, le nez au ras du sol


def construire():
    a = K.Animal("tapir")
    a.taille = 2.00

    # ----- le corps : un baril en poire, la croupe énorme et haute, qui s'effile vers les épaules ; crème derrière,
    #       ardoise devant, la limite nette en travers du dos (au tiers avant) -----
    def poire(v):
        s = v.copy()
        s[:, 1] *= np.where(v[:, 1] > 0, 1 + 0.10 * np.exp(-((v[:, 2] - 0.18) / 0.14) ** 2), 0.92)     # la bosse de la croupe
        return s
    corps = A.tour(A.profil([(0, 0), (0.145, 0.015), (0.205, 0.090), (0.225, 0.220), (0.215, 0.380), (0.190, 0.540),
                             (0.150, 0.690), (0.105, 0.780), (0, 0.835)], 6), 56)
    K.bandes(corps, [(0.470, CREME), (9, ARDOISE)])
    a.piece("corps", corps.sculpte(poire), None, pos=CROUPE, rot=(90 + 4, 0, 0))

    # ----- la tête : un long coin tombant, le front bombé, la mâchoire qui avance ; la trompe pend du museau -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre((0.0, -0.470, 0.410), nez)
    T3 = T.to_3x3()
    tete = A.tour(A.profil([(0, 0), (0.060, 0.010), (0.105, 0.060), (0.112, 0.130), (0.092, 0.200), (0.074, 0.255),
                            (0.064, 0.300), (0.052, 0.335), (0, 0.352)], 6), 48)
    K.bandes(tete, [(0.250, ARDOISE), (9, SOMBRE)])
    a.piece("tete", tete.etire(0.86, 1.0, 1.0), None, mat=T)
    a.tete = T @ Vector((0, 0.030, 0.230))
    bout = T @ Vector((0, -0.010, 0.350))
    trompe = [bout, bout + T3 @ Vector((0, -0.020, 0.040)) + Vector((0, 0, -0.045)), bout + T3 @ Vector((0, -0.030, 0.050)) + Vector((0, -0.020, -0.115)),
              bout + T3 @ Vector((0, -0.030, 0.050)) + Vector((0, -0.020, -0.140))]
    a.piece("trompe", K.tube_peint(A.courbe([tuple(q) for q in trompe], 5), lambda t: 0.050 - 0.012 * t, [(0.72, SOMBRE), (1, SABOT)], 16), None)

    # ----- les yeux : minuscules, vivants, très hauts, sous une paupière lourde ; les oreilles : deux ovales cernés de blanc -----
    centre = T @ Vector((0, 0, 0.150))
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", centre, T3 @ Vector((c * 0.80, 0.58, -0.20)))
        a.oeil("oeil_" + nom, pos + n * 0.004, n, 0.0125)
        a.piece("lourde_" + nom, K.paupiere(0.016, 0.10), ARDOISE, mat=A.cadre(pos + n * 0.006, n, T3 @ Vector((0, 1, 0))), poil=False)
        E = A.cadre(T @ Vector((c * 0.068, 0.112, 0.070)), T3 @ Vector((c * 0.55, 0.65, -0.52)), T3 @ Vector((0, 1, 0)))
        a.piece("rebord_" + nom, A.boule(1.0, 28, 14).etire(0.058, 0.026, 0.074), CREME, mat=E)
        a.piece("oreille_" + nom, A.boule(1.0, 28, 14).etire(0.044, 0.030, 0.056).pose((0, 0.008, 0.004)), SOMBRE, mat=E, poil=False)

    # ----- les jambes : courtes, épaisses ; devant ardoise, derrière crème ; trois gros doigts de sabot au bout ;
    #       la patte avant gauche avancée à tâtons -----
    def jambe(points, r0, pivot, haut):
        chemin = A.courbe(points, 6)
        return K.tube_peint(chemin, lambda t: r0 - 0.014 * t, [(0.999, haut), (1, haut)], 18)
    plantees = (("av_D", [(-0.115, -0.320, 0.400), (-0.125, -0.325, 0.250), (-0.125, -0.330, 0.050)], 0.082, ARDOISE),
                ("ar_G", [(0.130, 0.330, 0.400), (0.150, 0.350, 0.250), (0.150, 0.345, 0.050)], 0.098, CREME),
                ("ar_D", [(-0.130, 0.330, 0.400), (-0.150, 0.350, 0.250), (-0.150, 0.345, 0.050)], 0.098, CREME))
    for nom, pts, r0, haut in plantees:
        a.piece("jambe_" + nom, jambe(pts, r0, None, haut), None)
        x, y, _z = pts[-1]
        a.piece("sabot_" + nom, A.boule(1.0, 24, 12).etire(r0 * 0.78, r0 * 0.90, 0.036), SABOT, pos=(x, y - 0.014, 0.030), poil=False)
    for nom, c, x, y, couleur in (("av_G", 1, 0.125, -0.310, ARDOISE), ("av_D", -1, -0.125, -0.310, ARDOISE),
                                  ("ar_G", 1, 0.140, 0.340, CREME), ("ar_D", -1, -0.140, 0.340, CREME)):
        a.piece("epaule_" + nom, A.boule(1.0, 28, 14).etire(0.100, 0.135, 0.125), couleur, pos=(x, y, 0.405))
    levee = [(0.115, -0.320, 0.400), (0.125, -0.350, 0.255), (0.125, -0.440, 0.165), (0.125, -0.470, 0.055)]
    a.piece("jambe_av_G", jambe(levee, 0.082, None, ARDOISE), None)
    a.piece("sabot_av_G", A.boule(1.0, 24, 12).etire(0.064, 0.074, 0.036), SABOT, pos=(0.125, -0.485, 0.030), poil=False)

    # ----- la queue : un petit moignon, crème -----
    a.piece("queue", A.boule(1.0, 20, 10).etire(0.030, 0.040, 0.034), CREME, pos=(0, 0.436, 0.460))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tapir", styles.style_de("tapir"), sys.modules[__name__]), "Tapir")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py tapir). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.392                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.193, 0.373)),
    ('tete', 'corps', (0.018, -0.454, 0.370)),
    ('oreille_G', 'tete', (0.085, -0.579, 0.436)),
    ('patte_av_D', 'corps', (-0.128, -0.325, 0.391)),
    ('patte_ar_G', 'corps', (0.160, 0.363, 0.395)),
    ('patte_av_G', 'corps', (0.126, -0.339, 0.391)),
    ('queue', 'corps', (-0.000, 0.401, 0.447)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('epaule_av', 'corps'), ('epaule_ar', 'corps'), ('jambe_av', 'patte_av', True),
    ('jambe_ar', 'patte_ar', True), ('sabot_av', 'patte_av', True), ('sabot_ar', 'patte_ar', True),
    ('oreille', 'oreille', True), ('trompe', 'tete'), ('lourde', 'tete'), ('rebord', 'corps'), ('corps', 'corps'),
    ('queue', 'queue'), ('tete', 'tete'), ('oeil', 'tete'), ('paupiere_0', 'paupiere_0'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.118 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.216), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
