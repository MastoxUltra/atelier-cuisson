"""Le narval en peluche de magasin : une sarcelle pâle qui tire sur le vert-de-gris, marbrée de crème comme un vieux
carrelage, le ventre clair, le front lisse et une seule longue défense torsadée en ivoire, qui part du museau comme une
lance. Une licorne de la banquise, tout en élégance : couché sur le ventre, la queue étalée derrière, le torse dressé
et le museau pointé vers le ciel, la défense en l'air, l'œil perdu très haut.

    python narval.py        fabrique la fiche art/apercus/animaux/narval.png (peluche de magasin, palier 4)
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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
SARCELLE = M.hexa("#8fd0cc")                  # la dominante : sarcelle pâle, vert-de-gris
CREME = M.hexa("#fff6e2")                     # les marbrures, le ventre
IVOIRE = M.hexa("#fffbec")                    # l'accent : la défense
OMBRE = M.hexa("#62a8a8")                     # le dos, les nageoires, la queue : un ton plus bas
# l'échine, de la queue (à plat sur la glace) à la tête dressée : (avance vers l'arrière, hauteur)
ECHINE = [(0.78, 0.050), (0.60, 0.078), (0.38, 0.112), (0.15, 0.150), (-0.02, 0.200), (-0.15, 0.265), (-0.26, 0.330)]
GALBE = [(0.0, 0.0), (0.02, 0.012), (0.10, 0.034), (0.22, 0.075), (0.40, 0.132), (0.58, 0.175), (0.72, 0.184), (0.84, 0.164),
         (0.92, 0.136), (0.965, 0.096), (0.992, 0.046), (1.0, 0.0)]


def construire():
    a = K.Animal("narval")
    a.taille = 3.50                          # la défense comprise (la vraie taille)

    # ----- le corps : une seule pièce longue, de la queue au museau, marbrée de crème, le ventre crème, le dos plus sombre -----
    fil = K.Fil([(0.0, y, z) for y, z in ECHINE], (1, 0, 0))
    L = fil.long
    corps = A.tour(A.profil([(r, f * L) for f, r in GALBE], 8), 64)
    corps.teinte = np.tile(np.asarray(SARCELLE, float), (len(corps.v), 1))
    x, y, z = corps.v[:, 0], corps.v[:, 1], corps.v[:, 2]
    marbre = np.sin(23 * z) * np.cos(48 * x + 25 * y) + 0.7 * np.sin(13 * z + 31 * y) * np.cos(37 * x) + 0.4 * np.cos(17 * z - 29 * x)
    corps.teinte[marbre > 0.72] = CREME                                     # des plaques de marbre
    corps.teinte[y < -0.060] = CREME                                          # le ventre
    corps.teinte[(y > 0.085) & (marbre < 0.0)] = OMBRE                        # le dos, par endroits
    corps.teinte[z < 0.14 * L] = OMBRE                                        # le bout de la queue
    a.piece("corps", corps.sculpte(fil.couche), None)
    centre, avant, nuque = fil.cadre(0.97 * L)
    flanc = np.asarray(fil.flanc, float)
    a.tete = Vector(centre + avant * 0.06 + nuque * 0.02)

    # ----- la défense : une longue dent torsadée qui sort du museau, côté gauche, et file vers le ciel -----
    cen, av, nq = fil.cadre(0.985 * L)
    D = A.cadre(Vector(cen + flanc * 0.025), Vector(av * 1.0 + nq * 0.12 - flanc * 0.02), Vector(nq))
    lon = 0.66
    dent = A.tour(A.profil([(0, -0.02), (0.030, 0.0), (0.028, 0.12 * lon), (0.022, 0.45 * lon), (0.014, 0.75 * lon),
                            (0.006, 0.93 * lon), (0, lon)], 6), 36)

    def torsade(v):
        s = v.copy()
        teta = np.arctan2(v[:, 1], v[:, 0])
        k = 1 + 0.17 * np.cos(5 * teta - 22 * v[:, 2])                      # cinq sillons qui tournent le long de la dent
        s[:, 0] *= k
        s[:, 1] *= k
        return s
    a.piece("defense", dent.sculpte(torsade), IVOIRE, mat=D, poil=False)

    # ----- les yeux : de petites billes, très haut sur le côté ; une bouche à peine brodée -----
    for c in (1, -1):
        cen, av, nq = fil.cadre(0.90 * L)
        p, n = a.surface("corps", Vector(cen), Vector(av * 0.15 + flanc * c * 0.95 + nq * 0.25))
        a.bouton("oeil_" + ("G" if c > 0 else "D"), p + n * 0.002, n, 0.020)
        pts = []
        for f, haut in ((0.985, -0.42), (0.955, -0.44), (0.925, -0.38), (0.905, -0.22)):
            cen, av, nq = fil.cadre(f * L)
            pts += propres(a.trace("corps", Vector(cen), [Vector(av * 0.08 + flanc * c + nq * haut)], 0.006))
        a.broderie("sourire_" + ("G" if c > 0 else "D"), A.courbe(pts, 4), 0.0028, OMBRE)

    # ----- les nageoires : deux pagaies posées à plat au bord du torse, qui pointent vers l'arrière -----
    cen, av, nq = fil.cadre(0.78 * L)
    for nom, c in (("G", 1), ("D", -1)):
        depart = Vector(cen + flanc * c * 0.115 - nq * 0.085)
        vers = Vector(flanc * c * 0.62 - av * 0.70 - nq * 0.10)
        a.piece("nageoire_" + nom, A.boule(1.0, 32, 16).etire(0.050, 0.014, 0.095).pose((0, 0, 0.080)), OMBRE,
                mat=A.cadre(depart, vers, Vector(nq)))

    # ----- la queue : deux lobes plats en V, étalés sur la glace derrière lui -----
    cen0, av0, nq0 = fil.cadre(0.0)
    T = A.cadre(Vector(cen0), Vector(-av0), Vector(nq0))
    for nom, c in (("G", 1), ("D", -1)):
        lobe = A.boule(1.0, 28, 14).etire(0.098, 0.012, 0.046).pose((c * 0.082, 0.0, 0.030), (0, -c * 24, 0))
        a.piece("queue_" + nom, lobe, OMBRE, mat=T)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("narval", styles.style_de("narval"), sys.modules[__name__]), "Narval")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py narval). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.189                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.515, 0.189)),
    ('tete', 'corps', (0.001, -0.153, 0.313)),
    ('queue', 'corps', (0.001, 0.755, 0.054)),
]

PORTEURS = [
    ('nageoire', 'corps'), ('defense', 'tete'), ('sourire', 'tete'), ('corps', 'corps'), ('queue', 'queue'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.057 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.104), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.add('tete', rot=(32, 4, 40))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
