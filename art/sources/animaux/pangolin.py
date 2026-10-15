"""Le pangolin en peluche de magasin : une armure d'écailles terre cuite posées en rangs serrés comme des tuiles, du cou
jusqu'au bout d'une longue queue, le ventre et les pattes en peau crème, une petite tête en cône au museau pointu, des
yeux minuscules et de grandes griffes de fouisseur. Un chevalier au repos : dressé sur ses pattes arrière, appuyé sur
sa queue, les mains repliées sur le ventre, la tête levée de trois quarts, l'air de réfléchir à ce qu'il va creuser.

    python pangolin.py        fabrique la fiche art/apercus/animaux/pangolin.png (peluche de magasin, palier 4)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import garnitures as G
import matieres as M
import peluche as K

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
TUILE = M.hexa("#e88a5a")                     # la dominante : terre cuite
TUILE_BRUN = M.hexa("#b0603c")                # le dessous des écailles, un ton plus bas
DORE = M.hexa("#ffc872")                      # l'accent : le bout des écailles
CREME = M.hexa("#fff0d8")                     # le ventre, le museau, les pattes
CHARBON = M.hexa("#4a3a38")                   # les griffes
CORPS = [(0.0, -0.040, 0.640), (0.0, 0.020, 0.560), (0.0, 0.110, 0.400), (0.0, 0.230, 0.200), (0.0, 0.430, 0.075), (0.0, 0.650, 0.035)]


def construire():
    a = K.Animal("pangolin")
    a.taille = 1.10

    # ----- le corps et la queue : une seule pièce, du cou au bout de la queue, couchée le long d'un fil (le dos en pente) ;
    #       dessus, des rangs de languettes de feutrine : les écailles, qui retombent vers la queue -----
    fil = K.Fil(CORPS, (1, 0, 0))
    L = fil.long
    base = A.tour(A.profil([(0, 0), (0.092, 0.020 * L), (0.150, 0.100 * L), (0.178, 0.260 * L), (0.168, 0.420 * L), (0.130, 0.580 * L),
                            (0.090, 0.730 * L), (0.050, 0.860 * L), (0.022, 0.950 * L), (0, L)], 6), 40)
    base.teinte = np.tile(np.asarray(TUILE_BRUN, float), (len(base.v), 1))
    base = base.sculpte(fil.couche)
    a.piece("corps", base, None, poil=False)
    ecailles = G.franges(base, 0.115, 0.058, 0.050, 0.020,
                         lambda rang, t: tuple(np.asarray(TUILE) * (0.78 + 0.32 * (rang % 2) + 0.18 * t) + np.asarray(DORE) * 0.10 * t), 4, 1, 0.0, 0.97)
    a.piece("ecailles", ecailles, None, poil=False)

    # ----- le ventre : un grand plastron crème, en peau, sur le devant du corps (le dos reste en armure) -----
    centre, avant, nuque = fil.cadre(0.30 * L)
    V = A.cadre(Vector(centre) - Vector(nuque) * 0.040, Vector(avant), Vector(-nuque))
    a.piece("ventre", A.boule(1.0, 36, 18).etire(0.100, 0.060, 0.230), CREME, mat=V, poil=True)

    # ----- la tête : un cône lisse, le museau pointu et rosé, de minuscules yeux ; levée de trois quarts -----
    top = Vector(CORPS[0])
    H = A.cadre(top + Vector((0.0, -0.080, 0.045)), Vector((0.40, -0.90, 0.10)), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = A.tour(A.profil([(0, 0), (0.074, 0.010), (0.082, 0.050), (0.066, 0.110), (0.046, 0.175), (0.030, 0.235), (0.018, 0.285), (0, 0.300)], 6), 40)
    K.bandes(tete, [(0.240, TUILE), (9, CREME)])
    a.piece("tete", tete, None, mat=H, poil=False)
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.020, 0.018, 0.016), M.hexa("#9a5a5a"), mat=H @ A.repere((0, 0, 0.296)), poil=False)
    a.tete = H @ Vector((0, 0, 0.250))
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H @ Vector((0, 0, 0.100)), H3 @ Vector((c * 0.95, 0.15, 0.20)))
        a.bouton("oeil_" + nom, p + n * 0.002, n, 0.018)

    # ----- les bras : épais, repliés sur le ventre ; deux énormes griffes de fouisseur sur chaque main -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.140, 0.000, 0.560), (c * 0.185, -0.075, 0.470), (c * 0.150, -0.150, 0.400)]
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.052 - 0.012 * t, 14), TUILE_BRUN, poil=False)
        a.piece("main_" + nom, A.boule(1.0, 24, 12).etire(0.045, 0.050, 0.040), CREME, pos=(chemin[-1][0], chemin[-1][1] - 0.012, chemin[-1][2] - 0.004))
        griffes = None
        for k in (-1, 0, 1):
            g = A.tour(A.profil([(0, 0), (0.016, 0.004), (0.012, 0.034), (0.005, 0.066), (0, 0.082)], 5), 14)
            g = g.etire(1.0, 1.0, 1.0).pose((0, 0, 0), (-70, 0, 0)).pose((k * 0.032, -0.030, 0.0), (0, 0, -k * 12))
            griffes = g if griffes is None else griffes + g
        a.piece("griffes_" + nom, griffes, CHARBON, pos=(chemin[-1][0], chemin[-1][1] - 0.030, chemin[-1][2] - 0.020), poil=False)

    # ----- les pattes arrière : deux gros pieds plats crème, qui tiennent avec la queue le trépied ; les orteils cousus -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("pied_" + nom, A.boule(1.0, 28, 14).etire(0.064, 0.110, 0.034), CREME, pos=(c * 0.120, -0.020, 0.034), rot=(0, 0, c * 12))
        a.piece("cuisse_" + nom, A.boule(1.0, 28, 14).etire(0.085, 0.120, 0.110), TUILE_BRUN, pos=(c * 0.120, 0.150, 0.150), poil=False)
        a.piece("jambe_" + nom, A.tube(A.courbe([(c * 0.120, 0.110, 0.180), (c * 0.122, 0.040, 0.100), (c * 0.120, 0.000, 0.040)], 5), 0.052, 14), TUILE_BRUN, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pangolin", styles.style_de("pangolin"), sys.modules[__name__]), "Pangolin")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py pangolin). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.505                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.468, 0.333)),
    ('tete', 'corps', (0.031, -0.129, 0.628)),
    ('patte_av_G', 'corps', (0.164, -0.054, 0.505)),
]

PORTEURS = [
    ('ecailles', 'corps'), ('griffes', 'patte_av', True), ('ventre', 'corps'), ('cuisse', 'patte_av', True),
    ('corps', 'corps'), ('jambe', 'patte_av', True), ('tete', 'tete'), ('main', 'patte_av', True),
    ('pied', 'patte_av', True), ('bras', 'patte_av', True), ('oeil', 'tete'), ('nez', 'tete'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
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
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.151 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.278), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.add('tete', rot=(32, 4, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
