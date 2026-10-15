"""Le renard polaire en peluche, dans sa robe d'hiver : un blanc de neige (c'est ce qu'on attend de lui), les joues blanc
bleuté qui lui font une collerette, le dessous du museau pâle, le bas des pattes gris clair, un panache énorme au bout crème, et des yeux
ambre. Tout le contraire du renard roux : compact et rond, les oreilles petites et arrondies, le museau court. Un
chasseur à l'affût : il écoute ce qui gratte sous la neige, la tête penchée, les oreilles pointées vers le sol devant
lui, la patte avant gauche repliée, prête au bond ; le panache dressé derrière lui.

    python renard_polaire.py        fabrique la fiche art/apercus/animaux/renard_polaire.png (velours ras, palier 3)
    (sa robe d'été, brun fumé, est sa seconde robe)
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

FUME = M.hexa("#dcefff")                      # la dominante : un bleu ciel très clair (l'auteur, 15/10 : blanc, il faisait la robe sauvage)
SOMBRE = M.hexa("#b4d2ec")                    # le bas des pattes : le bleu un ton plus soutenu
CREME = M.hexa("#f4f9ff")                     # les joues, le dessous du museau, le bout du panache, le dedans des oreilles : blanc bleuté
AMBRE = M.hexa("#ffb12a")                     # l'accent : les yeux
CHARBON = M.hexa("#2b2626")                   # la truffe
CORPS = Vector((0.0, 0.03, 0.200))
TETE = Vector((0.0, -0.245, 0.300))
PIQUE, PENCHE, LACET = 14.0, 18.0, 22.0       # la tête : le nez vers le sol devant lui, penchée, tournée vers nous


def construire():
    a = K.Animal("renard_polaire")
    a.taille = 0.95

    # ----- le corps : un œuf rond et dodu, le poitrail bombé, un peu plus bas devant (il se ramasse) -----
    def dodu(v):
        v = K.bosse(v, (0, -0.85, -0.25), 0.12, 0.40)
        arriere = K.lisse((v[:, 1] - 0.3) / 0.7)
        s = v * [0.128, 0.195, 0.118]
        s[:, 0] *= 1 - 0.08 * arriere
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(dodu), FUME, pos=CORPS, rot=(6, 0, 0))

    # ----- la tête : ronde et large, les bajoues gonflées en collerette ; penchée, tournée vers nous -----
    H = A.repere(TETE, (PIQUE, PENCHE, LACET))
    H3 = H.to_3x3()

    def crane(v):
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.90, -0.20, -0.45), 0.24, 0.28)
        return v * [0.116, 0.104, 0.100]
    a.piece("tete", A.boule(1.0, 56, 28).sculpte(crane), FUME, mat=H)
    for nom, c in (("G", 1), ("D", -1)):
        a.rustine("joue_" + nom, "tete", TETE, H3 @ Vector((c * 0.84, -0.36, -0.42)),
                  lambda th: 0.56 + 0.10 * math.cos(2 * th), CREME, 0.003, 0)

    # ----- le museau : court, le dessus fumé, le dessous crème, la truffe charbon -----
    Mz = H @ A.repere((0, -0.074, -0.030), (92, 0, 0))     # X la gauche, Y le dessus, Z vers la truffe
    museau = A.tour(A.profil([(0.056, 0.0), (0.050, 0.028), (0.038, 0.056), (0.024, 0.078), (0, 0.088)], 6), 40).etire(1.0, 0.84, 1.0)
    K.bandes(museau, [(-0.006, CREME), (9, FUME)], axe=1)
    a.piece("museau", museau, None, mat=Mz)
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.017, 0.013, 0.012), CHARBON, mat=Mz @ A.repere((0, 0.006, 0.083)), poil=False)
    a.tete = Mz @ Vector((0, 0.020, 0.020))

    # ----- les yeux ambre : petits et rapprochés (malin), un rond de feutrine ambre, l'œil vivant posé dessus, et une
    #       paupière qui le coiffe à moitié : il fixe sa proie -----
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.42, -0.80, 0.40))
        a.rustine("iris_" + nom, "tete", TETE, regard, 0.190, AMBRE, 0.0025, 0)
        p, n = a.surface("tete", TETE, regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0115)
        P = A.cadre(p + n * 0.005, n, H3 @ Vector((0, 0.15, 1)))
        # (paupière retirée : yeux ouverts, bouton net, sans air fatigué ni fâché)

    # ----- les oreilles : petites, arrondies, pointées vers le sol devant lui ; le dedans crème -----
    po = A.profil([(0, 0), (0.046, 0.014), (0.040, 0.044), (0.025, 0.072), (0.009, 0.088), (0, 0.094)], 6)
    for nom, c in (("G", 1), ("D", -1)):
        vers = (H3 @ Vector((c * 0.42, -0.30, 0.86))).normalized()
        E = A.cadre(H @ Vector((c * 0.066, -0.004, 0.072)) - vers * 0.012, vers, H3 @ Vector((0, -1, 0)))
        a.piece("oreille_" + nom, A.tour(po, 32).etire(1.0, 0.36, 1.0), FUME, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 24).etire(0.62, 0.30, 0.80).pose((0, 0.008, 0.010)), CREME, mat=E, poil=False)

    # ----- les pattes : courtes et épaisses, le bas plus sombre ; l'avant gauche replié, prêt au bond -----
    def patte(points, rayons):
        chemin = A.courbe(points, 6)
        return K.tube_peint(chemin, lambda t: float(np.interp(t, np.linspace(0, 1, len(rayons)), rayons)),
                            [(0.55, FUME), (1, SOMBRE)], 20)
    devant = [0.040, 0.031, 0.027, 0.025]
    derriere = [0.056, 0.044, 0.030, 0.026]
    for nom, points, rayons, pied in (
            ("avant_D", [(-0.064, -0.112, 0.175), (-0.067, -0.124, 0.100), (-0.066, -0.130, 0.040), (-0.066, -0.134, 0.024)], devant, (-0.066, -0.148, 0.020)),
            ("arriere_G", [(0.072, 0.140, 0.195), (0.082, 0.100, 0.125), (0.077, 0.168, 0.070), (0.074, 0.150, 0.026)], derriere, (0.074, 0.138, 0.020)),
            ("arriere_D", [(-0.072, 0.140, 0.195), (-0.082, 0.100, 0.125), (-0.077, 0.168, 0.070), (-0.074, 0.150, 0.026)], derriere, (-0.074, 0.138, 0.020))):
        a.piece("patte_" + nom, patte(points, rayons), None)
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.030, 0.042, 0.021), SOMBRE, pos=pied)
    levee = [(0.064, -0.112, 0.175), (0.069, -0.150, 0.122), (0.071, -0.196, 0.118), (0.072, -0.204, 0.098)]
    a.piece("patte_avant_G", patte(levee, devant), None)
    a.piece("pied_avant_G", A.boule(1.0, 24, 12).etire(0.028, 0.040, 0.020), SOMBRE, pos=(0.072, -0.208, 0.080), rot=(-62, 0, 0))

    # ----- le panache : énorme, aussi gros que lui, dressé en vague au-dessus du dos ; le bout crème -----
    fil = K.Fil([(0.0, 0.195, 0.225), (0.0, 0.310, 0.258), (0.010, 0.410, 0.330), (0.025, 0.460, 0.440), (0.040, 0.440, 0.550),
                 (0.055, 0.370, 0.620), (0.065, 0.300, 0.632)], (1, 0, 0))
    L = fil.long
    queue = A.tour(A.profil([(0, 0), (0.034, 0.02 * L), (0.052, 0.10 * L), (0.096, 0.28 * L), (0.118, 0.48 * L), (0.108, 0.68 * L),
                             (0.076, 0.85 * L), (0.036, 0.96 * L), (0, L)], 6), 44)
    K.bandes(queue, [(0.80 * L, FUME), (9, CREME)])
    a.piece("queue", queue.sculpte(fil.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("renard_polaire", styles.style_de("renard_polaire"), sys.modules[__name__]), "Renard polaire")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py renard_polaire). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.187                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.068, 0.199)),
    ('tete', 'corps', (0.010, -0.155, 0.256)),
    ('oreille_G', 'tete', (0.075, -0.238, 0.346)),
    ('patte_av_D', 'corps', (-0.066, -0.123, 0.172)),
    ('patte_ar_G', 'corps', (0.081, 0.102, 0.206)),
    ('patte_av_G', 'corps', (0.068, -0.139, 0.181)),
    ('queue', 'corps', (-0.000, 0.195, 0.226)),
]

PORTEURS = [
    ('patte_arriere', 'patte_ar', True), ('pied_arriere', 'patte_ar', True), ('patte_avant', 'patte_av', True),
    ('oeil_reflet', 'tete'), ('pied_avant', 'patte_av', True), ('pavillon', 'oreille', True),
    ('oreille', 'oreille', True), ('lourde', 'tete'), ('museau', 'tete'), ('truffe', 'corps'), ('corps', 'corps'),
    ('queue', 'queue'), ('tete', 'tete'), ('joue', 'tete'), ('iris', 'tete'), ('oeil', 'tete'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.056 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.103), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
