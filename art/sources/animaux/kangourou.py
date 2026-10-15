"""Le kangourou en peluche de velours ras : un roux miel chaud, le ventre et le poitrail plus clairs, les oreilles en
longues feuilles, de petits bras courts et repliés, d'énormes pattes arrière aux grands pieds bruns et une queue épaisse
comme un troisième pied. Le boxeur du bush : assis en triangle sur sa queue et ses pieds, le torse haut, les poings
levés à hauteur du menton, la tête de trois quarts, une oreille tournée vers nous : il attend qu'on s'approche.

    python kangourou.py        fabrique la fiche art/apercus/animaux/kangourou.png (velours ras, palier 3)
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

ROUX = M.hexa("#f2a560")                      # la dominante : roux miel (le poil la fonce : on la prend claire)
CLAIR = M.hexa("#ffe2b4")                     # le ventre, le museau, le dedans des oreilles
BRUN = M.hexa("#6a4630")                      # l'accent : le bout des pattes, les poings, le bout des oreilles
CORPS = Vector((0.0, 0.080, 0.520))
TETE = Vector((0.0, -0.100, 1.040))
LACET = 28.0


def construire():
    a = K.Animal("kangourou")
    a.taille = 1.80

    # ----- le corps : une poire dressée, étroite aux épaules et large aux hanches ; le ventre clair devant -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(ROUX, float), (len(v), 1))
    t[(v[:, 1] < -0.35) & (v[:, 2] < 0.65)] = CLAIR
    corps.teinte = t

    def poire(v):
        v = K.bosse(v, (0, -0.9, -0.1), 0.12, 0.45)
        s = v * [0.220, 0.200, 0.440]
        s[:, 0] *= 1 + 0.28 * K.lisse((-v[:, 2] + 0.3) / 1.2)
        s[:, 1] *= 1 + 0.18 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s
    a.piece("corps", corps.sculpte(poire), None, pos=CORPS, rot=(-12, 0, 0))

    # ----- la tête : un long museau doux, le front bombé, les oreilles immenses ; tournée de trois quarts -----
    H = A.repere(TETE, (-8, 0, LACET))
    H3 = H.to_3x3()
    tete = A.tour(A.profil([(0, 0), (0.060, 0.010), (0.102, 0.060), (0.104, 0.130), (0.080, 0.210), (0.056, 0.275), (0.044, 0.315), (0, 0.340)], 6), 48)
    K.bandes(tete, [(0.250, ROUX), (9, CLAIR)])
    a.piece("tete", tete.etire(1.12, 1.18, 1.12), None, mat=H @ A.repere((0, 0.120, -0.090), (90, 0, 0)))
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.028, 0.020, 0.018), M.hexa("#3a2a28"), mat=H @ A.repere((0, -0.300, -0.102)), poil=False)
    a.tete = H @ Vector((0, -0.220, -0.070))
    bouche = [H3 @ Vector(d) for d in ((-0.35, -0.80, -0.55), (0.0, -0.96, -0.60), (0.35, -0.80, -0.55))]
    a.broderie("bouche", A.courbe(propres(a.trace("tete", H @ Vector((0, -0.120, -0.090)), bouche, 0.004)), 4), 0.0026, M.hexa("#3a2a28"))

    # ----- les yeux : grands et doux, sous un long cil ; les oreilles : de grandes feuilles dressées, le bout brun -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.74, -0.52, 0.34)))
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0215)
        po = A.profil([(0, 0), (0.036, 0.012), (0.056, 0.070), (0.054, 0.140), (0.036, 0.205), (0.014, 0.248), (0, 0.262)], 6)
        vers = (H3 @ Vector((c * 0.42, 0.18, 0.88))).normalized()
        E = A.cadre(H @ Vector((c * 0.075, 0.070, 0.080)) - vers * 0.015, vers, H3 @ Vector((c * 0.3, 0.9, -0.1)))
        oreille = K.bandes(A.tour(po, 36).etire(1.0, 0.30, 1.0), [(0.200, ROUX), (9, BRUN)])
        a.piece("oreille_" + nom, oreille, None, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 28).etire(0.60, 0.30, 0.70).pose((0, 0.008, 0.012)), CLAIR, mat=E, poil=False)

    # ----- les bras : courts et repliés, les poings bruns levés à hauteur du menton (le boxeur) -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.150, -0.060, 0.820), (c * 0.210, -0.140, 0.740), (c * 0.150, -0.230, 0.800), (c * 0.085, -0.240, 0.880)]
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.050 - 0.012 * t, 14), ROUX)
        a.piece("poing_" + nom, A.boule(1.0, 24, 12).etire(0.052, 0.058, 0.046), BRUN, pos=chemin[-1])

    # ----- les pattes arrière : deux énormes jambons, les grands pieds bruns posés à plat devant ; la queue : un tronc épais -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.boule(1.0, 36, 18).etire(0.130, 0.250, 0.190), ROUX, pos=(c * 0.210, 0.090, 0.240), rot=(0, 0, c * 6))
        a.piece("pied_" + nom, A.boule(1.0, 28, 14).etire(0.072, 0.260, 0.042), BRUN, pos=(c * 0.220, -0.190, 0.042), rot=(0, 0, c * 4))
    queue = K.tube_peint(A.courbe([(0.0, 0.250, 0.220), (0.0, 0.560, 0.090), (0.0, 0.900, 0.045)], 6), lambda t: 0.210 - 0.150 * t, [(0.85, ROUX), (1, BRUN)], 20)
    a.piece("queue", queue, None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("kangourou", styles.style_de("kangourou"), sys.modules[__name__]), "Kangourou")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py kangourou). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.652                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.123, 0.223)),
    ('tete', 'corps', (0.006, -0.079, 0.838)),
    ('oreille_G', 'tete', (0.029, 0.000, 1.099)),
    ('patte_av_G', 'corps', (0.105, -0.236, 0.877)),
    ('patte_ar_G', 'corps', (0.210, 0.091, 0.427)),
    ('queue', 'corps', (0.000, 0.211, 0.064)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('pavillon', 'oreille', True), ('oreille', 'oreille', True), ('truffe', 'corps'),
    ('cuisse', 'patte_ar', True), ('bouche', 'tete'), ('corps', 'corps'), ('queue', 'queue'), ('poing', 'corps'),
    ('tete', 'tete'), ('oeil', 'tete'), ('bras', 'patte_av', True), ('pied', 'patte_av', True),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.196 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
