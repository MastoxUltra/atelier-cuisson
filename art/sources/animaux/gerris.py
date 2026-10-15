"""Le gerris en peluche, deuxième dessin : la punaise patineuse, un patineur de vitesse en combinaison. Un fuseau de feutrine
noir d'encre au ventre argent, d'une ligne franche le long des flancs ; quatre pattes interminables posées à plat en
grand X, les genoux hauts cerclés de citron, chacune glissant sur une petite lame d'argent. Il file un peu de travers,
tourne la tête vers nous par-dessus l'épaule, le menton haut, deux gros yeux à demi fermés sous des paupières lourdes :
le dandy de la mare, très content de lui.

    python gerris.py        fabrique la fiche art/apercus/animaux/gerris.png
    (le premier dessin, refusé le 14/10 : gerris_ancien.py)
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

ENCRE = M.hexa("#3a3542")                     # le velours du corps, les pattes : un noir d'encre, à peine prune
ARGENT = M.hexa("#dfe3ea")                    # le ventre, les lames, le fil du dos
CITRON = M.hexa("#f2d43a")                    # l'accent : les genouillères
CAP = 0                                       # -35 sur la fiche (il file de travers, on le voit de trois quarts) ; 0 pour le jeu
CORPS = A.repere((0, 0, 0), (0, 0, CAP))
TETE = CORPS @ Vector((0.0, -0.104, 0.062))
PORT = CORPS @ A.repere((0.0, -0.104, 0.062), (-12, 0, 40))   # le menton haut, la tête tournée vers nous
DOS = K.Fil([CORPS @ Vector(p) for p in ((0, 0.115, 0.040), (0, 0.040, 0.044), (0, -0.040, 0.051), (0, -0.088, 0.058))],
            flanc=tuple(CORPS.to_3x3() @ Vector((1, 0, 0))))


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête, rendue dans celui du jardin."""
    return PORT.to_3x3() @ Vector((x, y, z))


def ici(x, y, z):
    """Un point donné dans le repère du corps (qui file de travers), rendu dans celui du jardin."""
    return tuple(CORPS @ Vector((x, y, z)))


def patte(points, gros):
    """Une longue patte de patineur, d'encre : la cuisse monte jusqu'au genou cerclé de citron, puis le tibia et le tarse
    redescendent se coucher à plat sur l'eau."""
    p = [np.array(q, float) for q in points]
    longs = [np.linalg.norm(p[i + 1] - p[i]) for i in range(len(p) - 1)]
    pli = longs[0] / sum(longs)
    return K.tube_peint(A.conges(points, 0.016, 6), lambda t: gros * (1 - 0.45 * t),
                        [(pli - 0.045, ENCRE), (pli + 0.035, CITRON), (9, ENCRE)])


def lame(pied, orteil):
    """Une petite lame de patin d'argent, couchée sous le bout du tarse, dans le sens de la glisse."""
    pied, orteil = Vector(pied), Vector(orteil)
    sens = Vector((orteil.x - pied.x, orteil.y - pied.y, 0)).normalized()
    contour = A.courbe([(0.0, -0.024), (0.0042, -0.012), (0.0046, 0.010), (0.0026, 0.024), (0.0, 0.028), (-0.0026, 0.024),
                        (-0.0046, 0.010), (-0.0042, -0.012)], 5, fermee=True)
    centre = Vector((orteil.x, orteil.y, 0.0022)) - sens * 0.010
    return A.decoupe(contour, 0.0036, 0.0012).sculpte(lambda v: v @ np.array(A.cadre(centre, (0, 0, 1), sens))[:3, :3].T
                                                       + np.array(centre))


def construire():
    a = K.Animal("gerris")
    a.taille = 0.48
    a.tete = PORT @ Vector((0, -0.026, 0.004))

    # ----- le corps : un fuseau de velours tourné de la queue au cou, le thorax un peu bossu, couché le long de sa
    #       glissade ; le ventre argent d'une ligne franche (le +Y de la pièce est le dos) -----
    profil = A.profil([(0, 0), (0.008, 0.004), (0.016, 0.030), (0.019, 0.070), (0.022, 0.110), (0.027, 0.140), (0.026, 0.165),
                       (0.020, 0.188), (0.012, 0.200), (0, 0.205)], 6)
    corps = K.bandes(A.tour(profil, 48).sculpte(lambda v: v * [1.10, 0.86, 1.0]), [(-0.007, ARGENT), (9, ENCRE)], axe=1)
    a.piece("corps", corps.sculpte(DOS.couche), None, poil=False)        # une feutrine lisse : une combinaison de course
    a.couture("dos", "corps", 12, 0.20, 0.90, "droit", fil=ARGENT, large=0.0070, haut=0.0020, pas=0.0110)

    # ----- la tête : un petit œuf de velours, deux gros yeux sur les côtés, à demi fermés sous des paupières lourdes -----
    def caboche(v):
        v = K.bosse(v, (0, -1, -0.15), 0.14, 0.22)
        s = v * [0.026, 0.030, 0.023]
        s[:, 0] *= 1 - 0.20 * K.lisse(-v[:, 1])
        return s
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(caboche), ENCRE, mat=PORT, poil=False)
    for nom, cote in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", TETE, vers(0.78 * cote, -0.48, 0.36))
        # un cerne d'argent autour de l'œil, sans couture : le noir de l'œil s'y détache
        a.rustine("cerne_" + nom, "tete", TETE, n, 0.66, ARGENT, 0.0025, 0)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0160)
        a.piece("lourde_" + nom, K.paupiere(0.0160, 0.10), ENCRE, mat=A.cadre(p + n * 0.005, n, vers(0, 0.2, 1)), poil=False)
        # les antennes : deux fils fins pointés devant lui, en V, comme deux antennes de radio
        p, n = a.surface("tete", TETE, vers(0.30 * cote, -0.80, 0.50))
        fil = A.courbe([p - n * 0.003, p + vers(0.010 * cote, -0.022, 0.016), p + vers(0.024 * cote, -0.050, 0.030),
                        p + vers(0.040 * cote, -0.074, 0.030)], 6)
        a.piece("antenne_" + nom, A.tube(fil, lambda t: 0.0034 - 0.0010 * t, 12), ENCRE, poil=False)
        # les pattes avant : courtes, repliées sous le menton
        bras = A.conges([ici(0.014 * cote, -0.070, 0.044), ici(0.030 * cote, -0.098, 0.030), ici(0.012 * cote, -0.120, 0.026)], 0.010, 5)
        a.piece("bras_" + nom, A.tube(bras, lambda t: 0.0060 - 0.0016 * t, 12), ENCRE, poil=False)

    # ----- les quatre grandes pattes, à plat en grand X : il rame. La gauche du milieu, de notre côté, pousse en arrière,
    #       la droite revient loin devant ; celles de derrière gouvernent -----
    for nom, points, gros in (
            ("milieu_G", [ici(0.018, -0.022, 0.040), ici(0.078, -0.004, 0.096), ici(0.176, 0.070, 0.012), ici(0.204, 0.088, 0.004)], 0.0080),
            ("milieu_D", [ici(-0.018, -0.022, 0.040), ici(-0.076, -0.036, 0.092), ici(-0.151, -0.137, 0.012), ici(-0.174, -0.169, 0.004)], 0.0080),
            ("arriere_G", [ici(0.016, 0.018, 0.038), ici(0.060, 0.050, 0.084), ici(0.090, 0.168, 0.010), ici(0.098, 0.204, 0.004)], 0.0072),
            ("arriere_D", [ici(-0.016, 0.018, 0.038), ici(-0.064, 0.052, 0.080), ici(-0.109, 0.158, 0.010), ici(-0.118, 0.188, 0.004)], 0.0072)):
        a.piece("patte_" + nom, patte(points, gros), None, poil=False)
        a.piece("lame_" + nom, lame(points[-2], points[-1]), ARGENT, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py gerris). Les mesures sont celles du modèle de jeu (CAP = 0), avant a.taille.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.0, 0.046)),                    # le milieu du fuseau
    ("tete", "corps", (0.0, -0.088, 0.058)),                  # la nuque
    ("patte_milieu_G", "corps", (0.018, -0.022, 0.040)),     # les rames : la hanche de la grande patte du milieu
    ("patte_arriere_G", "corps", (0.016, 0.018, 0.038)),     # le gouvernail : la hanche de la patte de derrière
]
PORTEURS = [("corps", "corps"), ("dos", "corps"), ("bras", "corps"),
            ("tete", "tete"), ("cerne", "tete"), ("oeil", "tete"), ("lourde", "tete"), ("antenne", "tete"),
            ("patte_milieu", "patte_milieu", True), ("lame_milieu", "patte_milieu", True),
            ("patte_arriere", "patte_arriere", True), ("lame_arriere", "patte_arriere", True),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def rames(p, angle, leve=0.0):
    """Les deux grandes pattes du milieu, en miroir : angle > 0 les tire vers l'arrière ; leve les soulève."""
    p.paire("patte_milieu", rot=(0, -leve, angle))


def repos(t):
    """Il flotte et se balance sur l'eau, tourne la tête, tapote la surface d'une rame (un rond dans l'eau), cligne."""
    p = Pose()
    r = onde(t, 2)
    p.add("corps", pos=(0, 0, 0.002 * r), rot=(1.5 * onde(t, 2, 0.2), 0, 0))
    p.add("tete", rot=(0, 0, -16 * cloche(t, 0.30, 0.12) + 10 * cloche(t, 0.75, 0.08)))
    tape = cloche(t, 0.55, 0.03) + cloche(t, 0.63, 0.03)
    p.add("patte_milieu_G", rot=(0, -10 * tape, 0))
    p.ouvert = 1 - cloche(t, 0.18, 0.02) - cloche(t, 0.88, 0.02)
    return p


def avance(t):
    """Il rame : les deux grandes pattes tirent ensemble vers l'arrière, il file, les rames reviennent en l'air ;
    les pattes de derrière gouvernent, la tête reste haute."""
    p = Pose()
    tire = 0.5 - 0.5 * math.cos(math.tau * t)                # 0 → 1 → 0 : la rame va de devant à derrière, puis revient
    rames(p, -18 + 36 * tire, 10 * cloche(t, 0.75, 0.22))       # elles reviennent en l'air, de 0,5 à 1
    p.add("corps", pos=(0, -0.006 * math.sin(math.tau * t), 0.002 * cloche(t, 0.75, 0.2)), rot=(-2 * cloche(t, 0.25, 0.2), 0, 0))
    p.paire("patte_arriere", rot=(0, 0, 5 * onde(t, 1, 0.25)))
    p.add("tete", rot=(-3 * cloche(t, 0.25, 0.2), 0, 0))
    return p


def mange(t):
    """Il plonge le nez dans l'eau (une miette qui flotte), trois petits coups, puis relève la tête, content."""
    p = Pose()
    bas = 1 - cloche(t, 0.88, 0.12)
    p.add("corps", rot=(3 * bas, 0, 0))
    p.add("tete", rot=(26 * bas + 6 * abs(onde(t, 6)) * bas, 0, -10 * bas))
    rames(p, -4 * bas)
    p.ouvert = 1 - cloche(t, 0.92, 0.02)
    return p


def joie(t):
    """Un bond sur l'eau, les rames grandes ouvertes, une pirouette d'un quart de tour et retour ; il retombe en patinant."""
    p = Pose()
    env = math.sin(math.pi * borne(t / 0.8)) if t < 0.8 else 0.0
    p.add("corps", pos=(0, 0, 0.040 * env), rot=(-8 * env, 0, 90 * borne(t / 0.8) if t < 0.8 else 0))
    rames(p, -10 * env, 20 * env)
    p.paire("patte_arriere", rot=(0, -12 * env, 0))
    p.add("tete", rot=(-12 * env, 0, 0))
    return p


def dort(t):
    """Posé à plat sur l'eau, les grandes pattes étalées, la tête basse, les yeux fermés ; il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.008), ech=(1.0, 1.0, 1.0 + 0.02 * r))
    p.add("tete", rot=(14, 0, -8))
    rames(p, 6, -4)
    p.paire("patte_arriere", rot=(0, 4, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Gerris")
