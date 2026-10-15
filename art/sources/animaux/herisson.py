"""Le hérisson en peluche : le nez en l'air, la capuche de piquants basse sur les yeux, une feuille morte qu'il n'a pas vue.

    python herisson.py        fabrique la fiche art/apercus/animaux/herisson.png
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
import peluche as K

CORPS = Vector((0.0, 0.03, 0.072))
DOS = Vector((0.0, 0.45, 0.90)).normalized()        # l'axe du manteau de piquants : vers le haut, un peu vers l'arrière


def sur(a, piece, centre, vers):
    """Le point de la surface visé depuis « centre », et la normale à cet endroit."""
    p = a.trace(piece, centre, [vers], 0.0)[0]
    return p, a.trace(piece, centre, [vers], 1.0)[0] - p


def construire():
    a = K.Animal("herisson")
    a.taille = 0.42
    a.tete = Vector((0, -0.095, 0.128))

    # ----- le corps : un galet rond, plus plat dessous, qui s'affine vers le visage -----
    def galet(v):
        avant = K.lisse(-v[:, 1] * 1.1)
        s = v * [0.118, 0.130, 0.112]
        s[:, 2] *= 1 - 0.42 * K.lisse(-4 * v[:, 2])
        s[:, 0] *= 1 - 0.20 * avant
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(galet), K.SABLE, pos=CORPS)

    # ----- le manteau : une grande rustine chocolat qui laisse le visage dehors, ourlée de fil jaune -----
    e1 = DOS.cross(Vector((0, 0, 1))).normalized()
    e2 = DOS.cross(e1)

    def capuche(tour):                                    # l'ouverture du manteau : il s'échancre devant, au-dessus des yeux
        return 1.74 - 0.60 * max(0.0, -math.sin(tour)) ** 1.5

    def vers(angle, tour):                                # une direction à « angle » de l'axe du dos, en tournant autour
        return DOS * math.cos(angle) + (e1 * math.cos(tour) + e2 * math.sin(tour)) * math.sin(angle)
    a.rustine("manteau", "corps", CORPS, DOS, capuche, K.CHOCOLAT, 0.004, feston=0)
    for k in range(20):
        tour = math.tau * (k + 0.5) / 20
        a.broderie("ourlet%d" % k, [a.trace("corps", CORPS, [vers(capuche(tour) + ecart, tour)], haut)[0]
                                    for ecart, haut in ((0.02, 0.002), (-0.04, 0.008), (-0.10, 0.005))], 0.0014, K.JAUNE)

    # ----- le museau : un cône qui pointe le nez en l'air, la truffe en feutrine noire -----
    museau = A.tour(A.profil([(0.058, 0.0), (0.050, 0.03), (0.034, 0.07), (0.019, 0.10), (0, 0.113)], 6), 32)
    NEZ = A.repere(CORPS + Vector((0, -0.062, 0.006)), (70, 0, 0))      # dans ce repère : X la gauche, Y le haut, Z vers la truffe
    a.piece("museau", museau, K.SABLE, mat=NEZ)
    a.couture("museau", "museau", 8, 0.45, 0.94)
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.017, 0.015, 0.014), K.NOIR, mat=NEZ @ A.repere((0, 0.002, 0.112)), poil=False)
    bouche = [a.trace("museau", NEZ @ Vector((0, 0, z)), [NEZ.to_3x3() @ Vector((math.cos(math.radians(d)), math.sin(math.radians(d)), 0))])[0]
              for z, d in ((0.098, -52), (0.088, -40), (0.076, -31), (0.064, -27), (0.054, -25))]
    a.broderie("bouche", bouche, 0.0024, paire=True)            # une bouche toute droite : pas impressionné

    # ----- le visage : deux boutons sous le bord du manteau, deux joues pêche, deux petites oreilles -----
    p, n = sur(a, "corps", CORPS, (0.42, -0.74, 0.50))
    a.bouton("oeil", p, n, 0.018, paire=True)
    a.rustine("joue", "corps", CORPS, (0.62, -0.76, 0.12), 0.17, K.PECHE, 0.0025, 12, paire=True)
    p, n = sur(a, "corps", CORPS, (0.66, -0.50, 0.56))
    oreille = p + n * 0.009
    O = A.cadre(oreille, n, (0, -1, 0.2))
    a.piece("oreille", A.boule(1.0, 24, 12).etire(0.021, 0.009, 0.021), K.SABLE, mat=O, paire=True)
    a.rustine("pavillon", "oreille", oreille, O.to_3x3() @ Vector((0, 1, 0)), 1.0, K.PECHE, 0.002, 0, paire=True)

    # ----- les piquants : des cônes de feutrine, le bout plus clair, tous réunis en une seule pièce -----
    cone = A.tour(A.profil([(0.011, 0.0), (0.0088, 0.013), (0.0045, 0.031), (0, 0.043)], 2), 8)
    clair = (np.array(K.CHOCOLAT) + np.array(K.SABLE)) * 0.5
    cone.teinte = np.array([np.array(K.CHOCOLAT) * (1 - t) + clair * t for t in (cone.v[:, 2] / 0.043) ** 2])
    hasard = np.random.default_rng(7)
    piquants, nombre = None, 430
    for i in range(nombre):                               # des directions bien réparties sur toute la boule ; on garde celles du manteau
        angle, tour = math.acos(1 - 2 * (i + 0.5) / nombre), i * 2.399963
        if angle > capuche(tour) - 0.09:
            continue
        p, n = sur(a, "corps", CORPS, vers(angle, tour))
        if (Vector((abs(p.x), p.y, p.z)) - oreille).length < 0.026:
            continue                                      # pas de piquant dans une oreille
        pique = cone.copie().etire(1.0, 1.0, hasard.uniform(0.85, 1.2))
        pique.teinte = cone.teinte * hasard.uniform(0.85, 1.12)
        couche = (n + Vector((0, 0.45, 0.10)) + Vector(hasard.normal(0, 0.08, 3))).normalized()     # peignés vers l'arrière
        if p.z + couche.z * 0.05 < 0.008:
            continue                                      # celui-là piquerait le sol
        pique.pose(p - n * 0.002, A.viser(couche))
        piquants = pique if piquants is None else piquants + pique
    a.piece("piquants", piquants, None, poil=False)

    # ----- quatre petites pattes en feutrine pêche -----
    def pied(v):
        s = v.copy()
        s[:, 1] -= 0.012 * K.lisse((0.03 - v[:, 2]) / 0.03)
        return s
    patte = A.tour(A.profil([(0, 0), (0.022, 0.003), (0.025, 0.016), (0.019, 0.034), (0.019, 0.06), (0, 0.072)], 5), 24).sculpte(pied)
    a.piece("patte_avant", patte, K.PECHE, pos=(0.058, -0.045, 0.0), poil=False, paire=True)
    a.piece("patte_arriere", patte, K.PECHE, pos=(0.068, 0.090, 0.0), poil=False, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py herisson)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.03, 0.06)),             # l'avant du galet, avec le visage : le milieu du ventre
    ("croupe", "corps", (0, 0.04, 0.06)),             # l'arrière du galet : il plie au même endroit, dans l'autre sens
    ("museau", "corps", (0, -0.035, 0.078)),          # la base du cône
    ("oreille_G", "corps", (0.070, -0.025, 0.130)),
    ("patte_avant_G", "corps", (0.058, -0.045, 0.058)),
    ("patte_arriere_G", "croupe", (0.068, 0.090, 0.058)),
]


def echine(points, cote):
    """Le galet est souple : le visage suit « corps », et le dos passe peu à peu à « croupe » vers l'arrière."""
    arriere = K.lisse((points[:, 1] + 0.01) / 0.14)
    return {"corps": 1.0 - arriere, "croupe": arriere}


# le galet et tout ce qui est cousu dessus plient ensemble, et se rangent avec « corps »
PORTEURS = [("corps", echine, "corps"), ("manteau", echine, "corps"), ("ourlet", echine, "corps"), ("piquants", echine, "corps"),
            ("oeil", echine, "corps"), ("joue", echine, "corps"),
            ("museau", "museau"), ("truffe", "museau"), ("bouche", "museau"),
            ("oreille", "oreille", True), ("pavillon", "oreille", True),
            ("patte_avant", "patte_avant", True), ("patte_arriere", "patte_arriere", True)]


def repos(t):
    """Il respire, lève le nez pour flairer l'air, le museau qui frétille, jette un œil de côté, secoue une oreille."""
    p = Pose()
    r = onde(t, 2)
    flaire = cloche(t, 0.28, 0.16)                       # le nez en l'air
    cote = cloche(t, 0.72, 0.13)                         # un regard vers sa gauche, sans se déranger
    fremit = onde(t, 14) * (0.3 + 0.7 * flaire)          # le museau ne tient pas en place
    p.add("corps", rot=(-13 * flaire, 0, 9 * cote), ech=(1 + 0.012 * r, 1, 1 + 0.022 * r))
    p.add("croupe", rot=(12 * flaire, 0, -9 * cote))     # la croupe reste posée : elle rend au sol ce que l'avant a pris
    p.paire("patte_avant", rot=(13 * flaire, 0, 0), pos=(0, 0, -0.012 * flaire))
    p.add("museau", rot=(-9 * flaire + 4 * fremit, 0, 12 * cote))
    p.add("oreille_G", rot=(0, 28 * (cloche(t, 0.50, 0.025) + cloche(t, 0.56, 0.025)), 0))
    p.ouvert = 1 - cloche(t, 0.10, 0.02) - cloche(t, 0.63, 0.02)
    return p


def avance(t):
    """Il trottine : quatre petits pas pressés par boucle, en diagonale, la croupe qui chaloupe, le nez au ras du sol."""
    p = Pose()
    c, s = math.cos(2 * math.tau * t), math.sin(2 * math.tau * t)
    p.add("corps", pos=(0, 0, 0.003 + 0.006 * abs(s)), rot=(4 + 2 * onde(t, 1), 3 * c, 4 * s))
    p.add("croupe", rot=(-4, -5 * c, -8 * s))
    p.add("museau", rot=(8 + 5 * onde(t, 4), 0, 5 * onde(t, 1)))
    for nom, sens in (("patte_avant_G", 1), ("patte_arriere_D", 1), ("patte_avant_D", -1), ("patte_arriere_G", -1)):
        p.add(nom, rot=(34 * sens * s, 0, 0), pos=(0, 0, 0.018 * max(0.0, -sens * c) - 0.003))
    p.paire("oreille", rot=(-8 * abs(s), 0, 0))
    return p


def mange(t):
    """Le nez piqué dans l'herbe, il fouille par petits coups, puis relève la tête et mâche, le museau qui remue."""
    p = Pose()
    leve = cloche(t, 0.84, 0.14)
    bas = 1 - leve
    coups = max(0.0, onde(t, 5)) ** 2 * bas
    p.add("corps", rot=(13 * bas - 7 * leve + 3 * coups, 0, 5 * onde(t, 1) * bas))
    p.add("croupe", rot=(-11 * bas + 6 * leve, 0, -5 * onde(t, 1) * bas))
    p.paire("patte_avant", rot=(-13 * bas + 7 * leve, 0, 0), pos=(0, 0, 0.014 * bas - 0.007 * leve))
    p.add("museau", rot=(26 * bas + 6 * coups + 5 * onde(t, 10) * leve, 0, 0))
    return p


def joie(t):
    """Il se dresse sur ses pattes arrière, le nez au ciel, et trépigne des pattes avant en remuant la croupe : trois petits sauts."""
    p = Pose()
    u = borne(t / 0.9)
    env = math.sin(math.pi * u)
    saut = abs(math.sin(3 * math.pi * u)) * env
    p.add("corps", pos=(0, 0, 0.026 * env + 0.035 * saut), rot=(-28 * env, 0, 0))
    p.add("croupe", rot=(24 * env, 0, 12 * onde(u, 3) * env))
    p.add("museau", rot=(-10 * env + 5 * onde(u, 6) * env, 0, 0))
    p.add("patte_avant_G", rot=(-18 * env + 26 * onde(u, 6) * env, 0, 0))
    p.add("patte_avant_D", rot=(-18 * env - 26 * onde(u, 6) * env, 0, 0))
    p.paire("oreille", rot=(0, 18 * onde(u, 6) * env, 0))
    return p


def dort(t):
    """En boule : le dos rond, le nez rentré au ras du sol, les pattes cachées, il ne dépasse plus que des piquants."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, 0.014), rot=(30, 0, 0), ech=(1.05 + 0.012 * r, 0.96, 1.03 + 0.025 * r))
    p.add("croupe", rot=(-58, 0, 0))                     # l'arrière s'enroule à son tour
    p.add("museau", rot=(14, 0, 0), ech=(0.8, 0.8, 0.8))
    p.paire("patte_avant", rot=(-45, 0, 0), pos=(0, 0.012, 0.030), ech=(0.7, 0.7, 0.7))
    p.paire("patte_arriere", rot=(45, 0, 0), pos=(0, -0.012, 0.030), ech=(0.7, 0.7, 0.7))
    p.paire("oreille", rot=(-25, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
