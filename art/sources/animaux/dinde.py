"""La dinde en peluche, deuxième dessin : le paon du pauvre, bouffi d'orgueil. Un corps de peluche bronze chocolat tout
gonflé, le poitrail bombé jusqu'au menton et sa barbe de crin noir qui en pend ; les ailes bronze qui traînent au sol ;
derrière lui, une roue immense de treize plumes chocolat, barrées de noir et bordées de crème, comme une vraie dinde
bronzée. Tout en haut, une petite tête de feutrine bleu ciel rejetée en arrière, deux petits yeux sous une paupière
hautaine, et la caroncule rouge coquelicot qui lui pend sur le bec : il fait la roue pour personne.

    python dinde.py        fabrique la fiche art/apercus/animaux/dinde.png
    (le premier dessin, refusé : dinde_ancien.py)
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

CORPS = Vector((0.0, -0.02, 0.36))
TETE = Vector((-0.012, -0.185, 0.755))
HAUTAINE = A.repere(TETE, (24, -8, -16), (1.25, 1.25, 1.25))   # la tête : le menton rentré, tournée vers sa droite pour se montrer de profil
CHOCO = M.hexa("#8a5838")                     # le corps : un bronze chocolat (le poil le fonce)
BRONZE = M.hexa("#b98538")                    # la peluche des ailes
SUIE = M.hexa("#2a2224")                      # la barre noire des plumes, la barbe
COQUELICOT = M.hexa("#e2402e")                # l'accent : la caroncule et le fanon
CUIVRE = M.hexa("#93682b")                    # le même bronze en feutrine (elle sort plus claire que le poil) : collerette et pattes

# la roue : onze plumes en éventail plantées dans le croupion, un peu renversées en arrière, et qui penchent d'un rien
MOYEU = Vector((0.0, 0.14, 0.38))
RENVERSE = math.radians(10)
ROUE = A.cadre(MOYEU, (0, -math.cos(RENVERSE), math.sin(RENVERSE)))    # son X = la gauche, son Y monte, son Z regarde devant
RAYURES = [(0.30, K.CHOCOLAT), (0.34, BRONZE), (0.52, K.CHOCOLAT), (0.56, BRONZE), (0.74, K.CHOCOLAT), (0.86, SUIE), (1.0, K.CREME)]
BARRES = [(0.38, K.CHOCOLAT), (0.50, BRONZE), (0.62, K.CHOCOLAT), (0.74, BRONZE), (0.86, SUIE), (1.0, K.CREME)]


def vers(x, y, z):
    """Une direction donnée dans le repère de la tête (devant = -y), rendue dans celui du jardin."""
    return HAUTAINE.to_3x3() @ Vector((x, y, z))


def plume(long, large, bandes):
    """Une plume plate debout sur son pied (son axe Z), étroite en bas, ronde au bout, peinte par bandes :
    « bandes » donne (jusqu'où, de 0 à 1 ; la couleur). Deux tours serrés de part et d'autre de chaque limite :
    les rayures restent nettes."""
    cotes = sorted(set(np.linspace(0.0, 0.80, 25).tolist() + (0.80 + 0.20 * np.sin(np.linspace(0.0, math.pi / 2, 12))).tolist()
                       + [f + e for f, _c in bandes[:-1] for e in (-0.003, 0.003)]))      # des tours serrés au bout : il reste rond

    def demi(t):
        if t <= 0.0 or t >= 1.0:
            return 0.0
        rond = math.sqrt(max(0.0, 1 - ((t - 0.80) / 0.20) ** 2)) if t > 0.80 else 1.0
        return (0.22 + 0.78 * float(K.lisse(t / 0.70))) * rond
    m = A.tour([(large * demi(t), long * t) for t in cotes], 20).etire(1.0, 0.16, 1.0)
    return K.bandes(m, [(long * f, c) for f, c in bandes])


def plaque(m, pied, pointe, plat):
    """Couche une plume (son axe Z) : le pied posé en « pied », la pointe vers « pointe », le plat tourné vers « plat »."""
    z = Vector(pointe).normalized()
    y = (Vector(plat) - z * Vector(plat).dot(z)).normalized()
    x = y.cross(z)
    m.v = np.outer(m.v[:, 0], np.array(x)) + np.outer(m.v[:, 1], np.array(y)) + np.outer(m.v[:, 2], np.array(z)) + np.array(pied)
    return m


def construire():
    a = K.Animal("dinde")
    a.taille = 0.95
    a.tete = HAUTAINE @ Vector((0.02, -0.06, -0.01))

    # ----- la roue : des plumes de feutrine, une devant, une derrière, rayées du pied à la pointe -----
    roue = None
    for i in range(13):
        phi = math.radians(-102 + 17 * i)
        p = plaque(plume(0.60, 0.096, RAYURES), (0, 0, 0.010 if i % 2 else -0.010), (math.sin(phi), math.cos(phi), 0), (0, 0, 1))
        roue = p if roue is None else roue + p
    a.piece("roue", roue, None, mat=ROUE, poil=False)

    # ----- le corps : une grosse boule gonflée, le jabot en avant ; une seule couture, au milieu du poitrail -----
    def coque(v):
        v = K.bosse(v, (0, -0.70, 0.50), 0.26, 0.35)          # le poitrail gonflé jusqu'au menton
        return v * [0.235, 0.255, 0.250]
    corps = A.boule(1.0, 56, 28).sculpte(coque)
    G.sillons(corps, [42], 0.006, 1.1)
    a.piece("corps", corps, CHOCO, pos=CORPS)
    a.couture("poitrail", "corps", 42, 0.16, 0.54, fil=BRONZE)

    # ----- la collerette : neuf pétales de feutrine bronze couchés sur les épaules, autour de la base du cou -----
    sortie = Vector((0, -0.50, 0.866))
    e1 = Vector((1, 0, 0))
    e2 = sortie.cross(e1)
    collerette = None
    for k in range(9):
        autour = e1 * math.cos(math.tau * k / 9) + e2 * math.sin(math.tau * k / 9)
        p, n = a.surface("corps", CORPS, sortie * math.cos(0.46) + autour * math.sin(0.46))
        petale = A.boule(1.0, 20, 10).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.052, 0.062, 0.014)
        m = np.array(A.cadre(p + n * 0.006, n, autour * math.cos(0.46) - sortie * math.sin(0.46)))
        petale.v = petale.v @ m[:3, :3].T + m[:3, 3]
        collerette = petale if collerette is None else collerette + petale
    a.piece("collerette", collerette, CUIVRE, poil=False)
    # la barbe : une touffe de crin noir qui pend du poitrail, comme une cravate
    p, n = a.surface("corps", CORPS, (0, -0.80, 0.42))
    barbe = None
    for k in range(5):
        e = (k - 2) * 0.006
        brin = A.tube(A.courbe([p - n * 0.006 + Vector((e, 0, 0)), p + n * 0.020 + Vector((e * 1.4, 0, -0.030)),
                                p + n * 0.026 + Vector((e * 1.8, 0, -0.085))], 5), lambda t: 0.0060 * (1 - 0.6 * t), 10)
        barbe = brin if barbe is None else barbe + brin
    a.piece("barbe", barbe, SUIE, poil=False)

    # ----- le cou rentré dans les épaules et la petite tête, en feutrine bleu ciel (c'est de la peau, pas de la plume) -----
    cou = A.courbe([(0, -0.10, 0.50), (0, -0.185, 0.61), (-0.004, -0.170, 0.69), (-0.010, -0.175, 0.735)], 6)
    a.piece("cou", A.tube(cou, lambda t: 0.075 - 0.027 * t, 20), K.CIEL, poil=False)
    a.piece("tete", A.boule(1.0, 56, 28).etire(0.058, 0.064, 0.058), K.CIEL, mat=HAUTAINE, poil=False)

    # ----- les yeux : petits, vivants, à demi fermés sous une paupière hautaine : il vous regarde de haut -----
    for nom, cote in (("g", 1), ("d", -1)):
        p, n = a.surface("tete", TETE, vers(0.88 * cote, -0.38, 0.25))
        a.oeil("oeil_" + nom, p + n * 0.002, n, 0.0130)
        a.piece("lourde_" + nom, K.paupiere(0.0130, 0.05), K.CIEL, mat=A.cadre(p + n * 0.003, n, vers(0, 0.1, 1)), poil=False)

    # ----- le bec crème, et la caroncule framboise : elle naît sur le front, passe par-dessus le bec et pend à gauche -----
    bec = A.tour(A.profil([(0, 0), (0.027, 0.005), (0.022, 0.028), (0.011, 0.062), (0, 0.080)], 5), 28)
    a.piece("bec", bec, K.CREME, pos=HAUTAINE @ Vector((0, -0.046, -0.008)), rot=A.viser(vers(0, -1, -0.30)), poil=False)
    pend = A.courbe([tuple(HAUTAINE @ Vector(q)) for q in ((0.0, -0.040, 0.042), (0.003, -0.064, 0.024), (0.012, -0.080, -0.002),
                                                             (0.022, -0.080, -0.040), (0.024, -0.072, -0.078), (0.021, -0.066, -0.100))], 6)
    a.piece("caroncule", A.tube(pend, lambda t: 0.011 + 0.007 * t, 14), COQUELICOT, poil=False)

    # ----- le fanon : trois boules framboise en grappe sous le menton -----
    fanon = None
    for centre, rayon in (((0.004, -0.046, -0.066), 0.023), ((0.014, -0.036, -0.090), 0.020), ((-0.010, -0.034, -0.100), 0.018)):
        boule = A.boule(rayon, 20, 10).pose(centre)
        fanon = boule if fanon is None else fanon + boule
    a.piece("fanon", fanon, COQUELICOT, mat=HAUTAINE, poil=False)

    # ----- les ailes : deux boucliers de peluche bronze qui tombent de l'épaule, cousus sur leur tranche -----
    AILE = A.repere((0.232, 0.01, 0.262), (-55, -6, -5))
    a.piece("aile", A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.036, 0.165, 0.105), BRONZE, mat=AILE, paire=True)
    for cote in (10, 30):
        a.couture("aile%d" % cote, "aile", cote, 0.12, 0.88, "droit", fil=K.CREME, paire=True)
    # au bout de chaque aile, trois rémiges de feutrine barrées de crème, dont la pointe racle le sol
    remiges = None
    for pied, sous, long in (((0.250, 0.085, 0.165), 50, 0.170), ((0.252, 0.045, 0.150), 68, 0.145), ((0.252, 0.0, 0.165), 86, 0.150)):
        t = math.radians(sous)
        p = plaque(plume(long, 0.040, BARRES), pied, (0.05, math.cos(t), -math.sin(t)), (1, 0, 0))
        remiges = p if remiges is None else remiges + p
    a.piece("remiges", remiges, None, poil=False, paire=True)

    # ----- les pattes : courtes, en feutrine bronze, la gauche un pas devant -----
    def patte():
        def doigt(degres):
            t = math.radians(degres)
            return A.boule(1.0, 16, 8).etire(0.013, 0.048, 0.010).pose((0.036 * math.sin(t), -0.036 * math.cos(t), 0), (0, 0, degres))
        return doigt(-30) + doigt(0) + doigt(30) + A.tube([(0, 0.010, 0.17), (0, 0.004, 0.0)], 0.014, 12)
    a.piece("patte_g", patte(), CUIVRE, pos=(0.085, -0.100, 0.010), rot=(0, 0, 10), poil=False)
    a.piece("patte_d", patte(), CUIVRE, pos=(-0.085, -0.045, 0.010), rot=(0, 0, -10), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py dinde). Les mesures sont celles du modèle, avant a.taille.
# La gauche est un pas devant : chaque patte a son os à elle (pas de miroir), et les pattes pendent à la racine, pas au
# corps : un pied posé ne bouge pas quand le corps roule. Les ailes traînent au sol : quand le corps roule ou se couche,
# on les relève d'autant, sinon leurs rémiges passeraient sous l'herbe. La caroncule a son os, sur le front : elle
# ballotte. La roue a le sien, au croupion : elle frémit, se renverse, et se replie pour dormir.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, -0.040, 0.260)),           # au-dessus des pattes : il se rengorge, roule et se penche autour
    ("cou", "corps", (0.0, -0.100, 0.500)),              # le pied du cou, rentré dans les épaules
    ("tete", "cou", (-0.006, -0.160, 0.735)),            # la nuque, en haut du cou
    ("caroncule", "tete", (-0.034, -0.248, 0.782)),      # sa racine, sur le front
    ("roue", "corps", (0.0, 0.140, 0.380)),              # le moyeu de la roue, dans le croupion
    ("aile_G", "corps", (0.212, -0.040, 0.395)),         # l'épaule : l'aile en tombe jusqu'au sol
    ("patte_g", "racine", (0.083, -0.090, 0.180)),       # le haut de chaque patte, dans le corps
    ("patte_d", "racine", (-0.083, -0.035, 0.180)),
]
PORTEURS = [("corps", "corps"), ("poitrail", "corps"), ("collerette", "corps"), ("barbe", "corps"),
            ("roue", "roue"), ("cou", "cou"),
            ("tete", "tete"), ("lourde", "tete"), ("oeil", "tete"), ("bec", "tete"), ("fanon", "tete"),
            ("caroncule", "caroncule"),
            ("aile", "aile", True), ("remiges", "aile", True),
            ("patte_g", "patte_g"), ("patte_d", "patte_d"),
            # les yeux sont posés un par un : l'usine appelle leurs paupières paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def _ailes(p, leve, ecarte=0.0):
    """Les ailes autour de l'épaule : « leve » relève leur bout qui traîne (il recule et monte), « ecarte » les décolle
    du corps."""
    p.paire("aile", rot=(leve, -0.4 * ecarte, -0.6 * ecarte))


def _pas(p, nom, u, recule=0.040, leve=0.032):
    """Une patte à la phase u de son pas (0 : posée devant ; elle porte et glisse vers l'arrière jusqu'à 0,5 ; puis elle se
    lève et revient devant)."""
    s = math.sin(math.tau * u)
    en_l_air = max(0.0, -s)
    p.add(nom, rot=(-12 * en_l_air, 0, 0), pos=(0, -recule * math.cos(math.tau * u), leve * en_l_air))


def repos(t):
    """Il fait la roue pour personne : il respire, se rengorge (le corps gonfle, la roue frémit en crépitant, les ailes
    raclent le sol), puis détourne la tête avec dédain, le nez en l'air ; la caroncule ballotte ; il cligne lentement,
    de haut."""
    p = Pose()
    r = onde(t, 2)
    gonfle = cloche(t, 0.32, 0.13)
    dedain = cloche(t, 0.66, 0.13)
    p.add("corps", ech=(1 + 0.012 * r + 0.05 * gonfle, 1 + 0.03 * gonfle, 1 + 0.018 * r + 0.04 * gonfle))
    p.add("roue", rot=(-4 * gonfle, 2.5 * onde(t, 30) * cloche(t, 0.32, 0.08), 0))
    _ailes(p, 0, 5 * gonfle)
    p.add("cou", rot=(-3 * gonfle, 0, -6 * dedain))
    p.add("tete", rot=(-10 * dedain, 4 * dedain, -18 * dedain))
    p.add("caroncule", rot=(2 * r, 12 * onde(t, 5) * cloche(t, 0.76, 0.10), 0))
    p.ouvert = 1 - cloche(t, 0.18, 0.035) - cloche(t, 0.86, 0.035)
    return p


def avance(t):
    """Il se pavane : un pas lent et pompeux, le corps qui roule à peine sur la patte qui porte, la roue qui tangue à
    contre-temps, la tête qui pique en avant à chaque pas et la caroncule qui ballotte. Les ailes, relevées d'un rien,
    raclent toujours le sol."""
    p = Pose()
    s = math.sin(math.tau * t)
    _pas(p, "patte_g", t)
    _pas(p, "patte_d", t + 0.5)
    p.add("corps", rot=(0, 2.5 * s, 3 * s), pos=(0, 0, 0.008 * (1 - math.cos(2 * math.tau * t)) / 2))
    p.add("roue", rot=(0, -3 * s, -4 * s))
    _ailes(p, 5)
    p.add("cou", rot=(4 * onde(t, 2), 0, 0))
    p.add("tete", rot=(-4 * onde(t, 2), 0, -2 * s))
    p.add("caroncule", rot=(4 * onde(t, 2, 0.15), 8 * onde(t, 1, 0.2), 0))
    return p


def mange(t):
    """Il replie la roue en arrière, plonge le cou jusqu'au sol, pique quatre fois de suite, puis se redresse et refait
    la roue en avalant, la caroncule qui balance."""
    p = Pose()
    leve = cloche(t, 0.86, 0.14)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add("corps", rot=(34 * bas, 0, 0))
    p.add("roue", rot=(-46 * bas, 0, 0))
    _ailes(p, 12 * bas)
    p.add("cou", rot=(98 * bas + 6 * coups, 0, -6 * bas), pos=(0, -0.030 * bas, -0.050 * bas))
    p.add("tete", rot=(-42 * bas + 8 * coups - 6 * leve * abs(onde(t, 6)), 0, 0))
    p.add("caroncule", rot=(-20 * bas, 6 * onde(t, 4) * bas, 0))
    p.ouvert = 1 - cloche(t, 0.93, 0.03)
    return p


def joie(t):
    """Sa fête à lui : le glouglou. Il se gonfle, la roue crépite, les ailes battent le tambour sur le sol, deux petits
    sauts ; il lance le cou en avant et secoue la tête, la caroncule qui vole ; puis il reprend la roue, fier."""
    p = repos(0.0)
    env = math.sin(math.pi * borne(t / 0.88)) if t < 0.88 else 0.0
    glou = cloche(t, 0.55, 0.20, False)
    saut = abs(onde(t, 2)) * env
    p.add("corps", ech=(1 + 0.06 * env, 1 + 0.03 * env, 1 + 0.05 * env), pos=(0, 0, 0.030 * saut))
    for nom in ("patte_g", "patte_d"):
        p.add(nom, pos=(0, 0, 0.030 * saut), rot=(-6 * saut, 0, 0))
    p.add("roue", rot=(-6 * env, 3 * onde(t, 24) * env, 0))
    _ailes(p, 4 * env, 10 * abs(onde(t, 6)) * env)
    p.add("cou", rot=(28 * glou, 0, 0))
    p.add("tete", rot=(-24 * glou, 0, 12 * onde(t, 8) * glou))
    p.add("caroncule", rot=(-15 * glou, 22 * onde(t, 8, 0.2) * env, 0))
    return p


def dort(t):
    """Il dort assis, posé sur le ventre, la roue repliée en une queue étroite couchée derrière lui, les ailes relevées
    contre les flancs, le cou rentré et la tête tombée sur le poitrail, les yeux fermés ; il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.100), ech=(1.03 + 0.012 * r, 1.0, 0.98 + 0.020 * r))
    for nom in ("patte_g", "patte_d"):
        p.add(nom, ech=(1, 1, 0.35))
    p.add("roue", rot=(-62, 0, 0), ech=(0.32, 1, 0.55))
    _ailes(p, 40, 4)
    p.add("cou", rot=(22, 0, 8), pos=(0, 0.030, -0.050))
    p.add("tete", rot=(26, 0, 24))
    p.add("caroncule", rot=(-10, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire, "Dinde")
