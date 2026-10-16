"""Le béluga en peluche de magasin : un bleu glacier presque blanc, rond et doux comme un édredon, sans nageoire sur le
dos, le melon du front plus clair et bombé, des joues rebondies, de petits yeux noirs et un sourire brodé qui remonte à
la joue. Un gros chanteur bonne pâte, couché sur le ventre comme échoué sur la banquise : la tête levée, la queue
cambrée en l'air, les petites nageoires à plat de chaque côté.

    python beluga.py        fabrique la fiche art/apercus/animaux/beluga.png (peluche de magasin, palier 4)

Les 5 traits de l'espèce (photos de Commons, 15/10) : 1. tout blanc, un corps rond et dodu sans nageoire dorsale ; 2. un melon
bombé sur le front, au-dessus d'un museau court sans bec ; 3. la bouche aux coins relevés, un sourire fixe ; 4. de petites
nageoires rondes en pagaies ; 5. une queue à deux lobes larges, un pli au cou.
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

GONFLAGE = True       # la base aux volumes gonflés de l'Artiste (fusion.py) : jointures fondues, bouts arrondis


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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
GLACIER = M.hexa("#cfe6fa")                   # la dominante : bleu glacier presque blanc
MELON = M.hexa("#dcedfb")                     # l'accent : le melon, à peine plus clair (un renflement, plus un bonnet)
NAGEOIRE = M.hexa("#9cc4e6")                  # les nageoires, la queue : un ton plus bas
MARINE = M.hexa("#3a5a82")                    # le sourire
# l'échine, de la queue (en l'air) à la tête : (avance vers l'arrière, hauteur)
# (16/10, planche 27 : l'auteur veut les proportions d'un vrai modèle) : le galbe est relevé tranche par tranche sur la
# référence (references_3d/beluga, CC-BY : mesurée, rien d'importé), un tiers plus dodu pour la peluche : le corps le plus
# épais au premier tiers, une longue queue qui s'affine, un cou marqué, une tête plus étroite que le corps mais haute
# (le melon) ; couché presque droit, comme le modèle
ECHINE = [(0.60, 0.215), (0.48, 0.180), (0.30, 0.165), (0.10, 0.168), (-0.10, 0.178), (-0.24, 0.190), (-0.36, 0.200)]
GALBE = [(0.0, 0.0), (0.015, 0.022), (0.045, 0.034), (0.13, 0.061), (0.22, 0.076), (0.30, 0.100), (0.39, 0.121), (0.48, 0.142),
         (0.57, 0.150), (0.65, 0.148), (0.74, 0.138), (0.83, 0.110), (0.87, 0.100), (0.915, 0.098), (0.955, 0.088),
         (0.985, 0.060), (1.0, 0.0)]


def construire():
    a = K.Animal("beluga")
    a.taille = 5.00

    # ----- le corps : une seule pièce longue couchée le long de l'échine en banane ; un pli au cou, des joues pleines -----
    fil = K.Fil([(0.0, y, z) for y, z in ECHINE], (1, 0, 0))
    L = fil.long
    DEGONFLE = 0.88      # le gonflage de la base élargit les volumes d'environ 30 % : on part plus mince
    corps = A.tour(A.profil([(r * DEGONFLE, f * L) for f, r in GALBE], 8), 64)

    def douce(v):
        s = v.copy()
        s[:, 0] *= 1.12                                                             # un peu plus large que haut
        s[:, 1] = np.where(s[:, 1] < 0, s[:, 1] * 0.82, s[:, 1])                     # le ventre aplati sur la glace
        return s
    corps.sculpte(douce)
    corps.teinte = np.tile(np.asarray(GLACIER, float), (len(corps.v), 1))
    corps.teinte[corps.v[:, 2] < 0.16 * L] = NAGEOIRE                                 # le bout de la queue, un ton plus bas
    a.piece("corps", corps.sculpte(fil.couche), None)
    centre, avant, nuque = fil.cadre(0.93 * L)
    flanc = np.asarray(fil.flanc, float)

    # ----- le melon : le front bombé, plus clair, posé sur la tête -----
    M_ = A.cadre(Vector(centre + nuque * 0.052 + avant * 0.015), Vector(avant), Vector(nuque))      # la tête du modèle : haute
    a.piece("melon", A.boule(1.0, 40, 20).etire(0.078, 0.058, 0.080), MELON, mat=M_)                  # devant, le museau court
    a.tete = Vector(centre + avant * 0.10 + nuque * 0.03)
    a.cap_tete = Vector(avant)                                                         # couché : la vue de près suit la tête

    # ----- le sourire : un trait brodé qui court le long du museau et remonte à la joue ; les yeux : de petites billes -----
    for c in (1, -1):
        pts = []
        for f, haut in ((0.992, -0.50), (0.975, -0.52), (0.955, -0.50), (0.935, -0.44)):
            cen, av, nq = fil.cadre(f * L)
            pts += propres(a.trace("corps", Vector(cen), [Vector(av * 0.10 + flanc * c + nq * haut)], 0.006))
        # (le sourire brodé est retiré : vu de face, ses deux traits bleus faisaient des moustaches)
        cen, av, nq = fil.cadre(0.905 * L)
        p, n = a.surface("corps", Vector(cen), Vector(av * 0.55 + flanc * c * 0.70 + nq * 0.35))     # plus en avant : de face, les deux yeux (16/10)
        a.bouton("oeil_" + ("G" if c > 0 else "D"), p + n * 0.002, n, 0.018)

    # ----- les nageoires : deux petites pagaies rondes posées à plat, sous le cou, qui pointent vers l'arrière -----
    cen, av, nq = fil.cadre(0.74 * L)                                                # là où le modèle les porte
    for nom, c in (("G", 1), ("D", -1)):
        depart = Vector(cen + flanc * c * 0.110 - nq * 0.075)
        vers = Vector(flanc * c * 0.78 - av * 0.50 - nq * 0.12)
        W = A.cadre(depart, vers, Vector(nq))
        a.piece("nageoire_" + nom, A.boule(1.0, 32, 16).etire(0.050, 0.014, 0.095).pose((0, 0, 0.082)), NAGEOIRE, mat=W)

    # ----- la queue : deux lobes plats en V au bout de la cambrure, de profil dans le plan de la queue -----
    cen0, av0, nq0 = fil.cadre(0.0)
    T = A.cadre(Vector(cen0), Vector(-av0), Vector(nq0))
    for nom, c in (("G", 1), ("D", -1)):
        lobe = A.boule(1.0, 28, 14).etire(0.098, 0.014, 0.046).pose((c * 0.080, 0.0, 0.030), (0, -c * 24, 0))
        a.piece("queue_" + nom, lobe, NAGEOIRE, mat=T)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("beluga", styles.style_de("beluga"), sys.modules[__name__]), "Béluga")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py beluga). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.203                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.392, 0.203)),
    ('tete', 'corps', (0.007, -0.216, 0.286)),
    ('queue', 'corps', (0.002, 0.626, 0.380)),
]

PORTEURS = [
    ('nageoire', 'corps'), ('sourire', 'tete'), ('corps', 'corps'), ('melon', 'corps'), ('queue', 'queue'),
    ('oeil', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'),
    ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
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
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.061 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.112), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.add('tete', rot=(32, 4, 40))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
