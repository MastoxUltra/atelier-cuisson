"""Le quokka en peluche de velours ras (2e dessin) : un beige rosé, une petite poire (étroite en haut, lourde en bas)
sous une tête de rat à la face ronde, le museau court, de petites oreilles rondes, des mains fines levées devant la
poitrine, et une longue queue nue qui part de la croupe et sur laquelle il est assis, comme sur un trépied. Le plus
mignon des malins : assis, la tête penchée d'un côté, les mains jointes, un sourire en coin, un œil plus haut que
l'autre : il vient de décider que vous étiez de la famille.

    python quokka.py        fabrique la fiche art/apercus/animaux/quokka.png (velours ras, palier 3)
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

ROSE = M.hexa("#f0cdb0")                      # la dominante : beige rosé (le poil le fonce : on le prend clair)
CREME = M.hexa("#fff6e8")                     # le ventre, le tour du museau, le dedans des oreilles
NU = M.hexa("#d8b0a0")                        # la queue nue, les paumes
CHARBON = M.hexa("#3a3032")                   # l'accent : le nez, les yeux, le sourire
CORPS = Vector((0.0, 0.040, 0.160))
TETE = Vector((0.0, -0.070, 0.330))
LACET, PENCHE = 20.0, 14.0


def construire():
    a = K.Animal("quokka")
    a.taille = 0.55

    # ----- le corps : une poire assise (étroite aux épaules, lourde en bas), le ventre crème devant -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(ROSE, float), (len(v), 1))
    t[(v[:, 1] < -0.30) & (v[:, 2] < 0.50)] = CREME
    corps.teinte = t

    def poire(v):
        s = v * [0.110, 0.112, 0.160]
        s[:, 0] *= 0.70 + 0.55 * K.lisse((-v[:, 2] + 0.9) / 1.4)               # étroite en haut, large en bas
        s[:, 1] *= 0.75 + 0.45 * K.lisse((-v[:, 2] + 0.9) / 1.4)
        return s
    a.piece("corps", corps.sculpte(poire), None, pos=CORPS)

    # ----- la tête : une petite tête de rat, la face ronde, le museau court en cône, penchée d'un côté -----
    H = A.repere(TETE, (0, PENCHE, LACET))
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 48, 24).etire(0.082, 0.082, 0.080), ROSE, mat=H)
    museau = A.tour(A.profil([(0, 0), (0.042, 0.006), (0.040, 0.030), (0.030, 0.056), (0.016, 0.070), (0, 0.076)], 6), 28)
    a.piece("museau", museau.etire(1.0, 0.82, 1.0), CREME, mat=H @ A.repere((0, -0.040, -0.016), (90, 0, 0)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.017, 0.012, 0.012), CHARBON, mat=H @ A.repere((0, -0.118, -0.016)), poil=False)
    a.tete = H @ Vector((0, -0.110, -0.012))
    # le sourire en coin : un seul trait, relevé du côté de nous
    sourire = [H3 @ Vector(d) for d in ((-0.10, -0.92, -0.42), (0.18, -0.92, -0.46), (0.42, -0.82, -0.40), (0.62, -0.68, -0.28))]
    a.broderie("sourire", A.courbe(propres(a.trace("tete", H.to_translation(), sourire, 0.003)), 4), 0.0026, CHARBON)

    # ----- les yeux : vivants, un peu hauts, l'un légèrement plus haut que l'autre ; les petites oreilles rondes -----
    for nom, c, hausse in (("G", 1, 0.22), ("D", -1, 0.14)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.46, -0.84, hausse)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0140)
        po = A.profil([(0, 0), (0.024, 0.008), (0.028, 0.026), (0.020, 0.042), (0.008, 0.050), (0, 0.054)], 5)
        E = A.cadre(H @ Vector((c * 0.060, 0.020, 0.062)), H3 @ Vector((c * 0.40, 0.20, 0.90)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.45, 1.0), ROSE, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 16).etire(0.62, 0.30, 0.66).pose((0, 0.006, 0.008)), CREME, mat=E, poil=False)

    # ----- les bras : fins, repliés, les mains jointes devant la poitrine ; les jambes : deux gros pieds à plat devant -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.082, -0.020, 0.250), (c * 0.108, -0.070, 0.210), (c * 0.060, -0.112, 0.205), (c * 0.020, -0.118, 0.215)]
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 5), lambda t: 0.020 - 0.006 * t, 12), ROSE)
        a.piece("main_" + nom, A.boule(1.0, 20, 10).etire(0.020, 0.024, 0.016), NU, pos=chemin[-1])
        a.piece("pied_" + nom, A.boule(1.0, 28, 14).etire(0.040, 0.090, 0.026), CREME, pos=(c * 0.075, -0.075, 0.026), rot=(0, 0, c * 10))

    # ----- la queue : longue et nue, qui part de la croupe, s'étale par terre derrière lui et se relève : son trépied -----
    chemin = [(0.0, 0.110, 0.095), (0.0, 0.260, 0.040), (0.050, 0.420, 0.030), (0.120, 0.520, 0.060), (0.140, 0.540, 0.140)]
    queue = K.tube_peint(A.courbe(chemin, 6), lambda t: 0.038 - 0.020 * t, [(0.55, ROSE), (1, NU)], 14)
    a.piece("queue", queue, None, poil=True)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("quokka", styles.style_de("quokka"), sys.modules[__name__]), "Quokka")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py quokka). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.243                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.103, 0.048)),
    ('tete', 'corps', (-0.001, -0.031, 0.264)),
    ('oreille_G', 'tete', (0.060, -0.028, 0.382)),
    ('patte_av_G', 'corps', (0.080, -0.047, 0.243)),
    ('queue', 'corps', (-0.001, 0.122, 0.059)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('pavillon', 'oreille', True), ('oreille', 'oreille', True), ('sourire', 'tete'),
    ('museau', 'tete'), ('corps', 'corps'), ('queue', 'queue'), ('tete', 'tete'), ('bras', 'patte_av', True),
    ('pied', 'patte_av', True), ('oeil', 'tete'), ('main', 'patte_av', True), ('nez', 'tete'),
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
    pas = 18.0
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.073 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.02), rot=(36, 0, 6), ech=(1 + 0.010 * r, 1, 1 + 0.020 * r))
    p.paire('patte_av', rot=(-30, 0, 0))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
