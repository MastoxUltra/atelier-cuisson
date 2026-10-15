"""Le wombat en peluche de velours ras : un brun gris chaud et sombre, un baril sur quatre pattes courtes, la tête
large et plate aux petites oreilles rondes, un gros nez de cuir, des yeux minuscules et les griffes de fouisseur. Le
tank du terrier : le museau au ras du sol, le dos large comme une table, le regard par en dessous, une patte avant
posée sur une motte qu'il est sur le point de creuser.

    python wombat.py        fabrique la fiche art/apercus/animaux/wombat.png (velours ras, palier 3)
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

BRUN = M.hexa("#9a8274")                      # la dominante : brun gris chaud et sombre (le poil la fonce : on la prend claire)
CLAIR = M.hexa("#cdb8a8")                     # le museau, le ventre, un rien plus clair
CHARBON = M.hexa("#3a302c")                   # l'accent : le nez, les griffes
CORPS = Vector((0.0, 0.050, 0.190))
TETE = Vector((0.0, -0.290, 0.195))
LACET, PIQUE = 24.0, 18.0


def construire():
    a = K.Animal("wombat")
    a.taille = 1.00

    # ----- le corps : un baril large et plat dessus, le ventre au ras du sol, la croupe ronde -----
    def baril(v):
        v = K.bosse(v, (0, 0.85, 0.2), 0.08, 0.5)
        s = v * [0.200, 0.330, 0.175]
        s[:, 2] = np.where(s[:, 2] < 0, s[:, 2] * 0.85, s[:, 2])
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(baril), BRUN, pos=CORPS)

    # ----- la tête : large et plate, le front bombé, le museau court et clair, le gros nez de cuir -----
    H = A.repere(TETE, (PIQUE, 0, LACET))
    H3 = H.to_3x3()

    def tete_f(v):
        v = K.bosse(v, (0, -0.9, -0.2), 0.12, 0.40)
        return v * [0.150, 0.130, 0.115]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(tete_f), BRUN, mat=H)
    a.piece("museau", A.boule(1.0, 32, 16).etire(0.074, 0.062, 0.058), CLAIR, mat=H @ A.repere((0, -0.105, -0.020)))
    a.piece("nez", A.boule(1.0, 24, 12).etire(0.044, 0.028, 0.030), CHARBON, mat=H @ A.repere((0, -0.162, -0.008)), poil=False)
    a.tete = H @ Vector((0, -0.150, -0.010))
    bouche = [H3 @ Vector(d) for d in ((-0.34, -0.82, -0.48), (0.0, -0.96, -0.52), (0.34, -0.82, -0.48))]
    a.broderie("bouche", A.courbe(propres(a.trace("museau", H @ Vector((0, -0.105, -0.020)), bouche, 0.004)), 4), 0.0030, CHARBON)

    # ----- les yeux : de minuscules billes, très écartées, sous une paupière lourde ; les oreilles : deux petits ronds -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.78, -0.50, 0.30)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0135)
        a.piece("lourde_" + nom, K.paupiere(0.017, 0.08), BRUN, mat=A.cadre(p + n * 0.005, n, H3 @ Vector((0, 0, 1))), poil=False)
        po = A.profil([(0, 0), (0.030, 0.008), (0.036, 0.026), (0.026, 0.042), (0.010, 0.050), (0, 0.054)], 5)
        E = A.cadre(H @ Vector((c * 0.100, 0.040, 0.072)), H3 @ Vector((c * 0.35, 0.18, 0.92)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.45, 1.0), BRUN, mat=E)

    # ----- les pattes : courtes comme des bornes, les griffes de fouisseur ; la droite avant posée sur une motte -----
    for nom, x, y in (("av_G", 0.130, -0.150), ("av_D", -0.130, -0.150), ("ar_G", 0.135, 0.250), ("ar_D", -0.135, 0.250)):
        c = 1 if x > 0 else -1
        a.piece("patte_" + nom, A.tube(A.courbe([(x, y, 0.180), (x * 1.04, y - 0.010, 0.100), (x * 1.04, y - 0.020, 0.040)], 5), 0.062, 16), BRUN)
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.064, 0.082, 0.030), CLAIR, pos=(x * 1.04, y - 0.050, 0.030))
        griffes = None
        for k in (-1, 0, 1):
            g = A.tour(A.profil([(0, 0), (0.012, 0.004), (0.009, 0.030), (0.004, 0.056), (0, 0.068)], 5), 12)
            g = g.pose((0, 0, 0), (-82, 0, 0)).pose((k * 0.026, -0.060, 0.0), (0, 0, k * 8))
            griffes = g if griffes is None else griffes + g
        a.piece("griffes_" + nom, griffes, CHARBON, pos=(x * 1.04, y - 0.060, 0.026), poil=False)
    a.piece("queue", A.boule(1.0, 20, 10).etire(0.040, 0.034, 0.032), BRUN, pos=(0, 0.370, 0.150))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("wombat", styles.style_de("wombat"), sys.modules[__name__]), "Wombat")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py wombat). Les mesures sont celles du modèle, avant a.taille.
# Le bulldozer : bas, lourd, têtu ; il trottine, il creuse, il bondit comme un parpaing.

from poses import Pose, borne, cloche, onde

JAMBE = 0.18                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.10, 0.19)),         # le milieu du baril : il roule, se cabre, se couche autour
    ("tete", "corps", (0.0, -0.23, 0.20)),          # la nuque
    ("oreille_G", "tete", (0.100, -0.25, 0.265)),
    ("patte_av_G", "corps", (0.130, -0.15, 0.18)),  # l'épaule
    ("patte_ar_G", "corps", (0.135, 0.25, 0.18)),   # la hanche
]

PORTEURS = [("corps", "corps"), ("tete", "tete"), ("museau", "tete"), ("nez", "tete"), ("bouche", "tete"), ("oeil", "tete"),
            ("lourde", "tete"), ("oreille", "oreille", True), ("patte_av", "patte_av", True), ("pied_av", "patte_av", True),
            ("griffes_av", "patte_av", True), ("patte_ar", "patte_ar", True), ("pied_ar", "patte_ar", True),
            ("griffes_ar", "patte_ar", True), ("queue", "corps"),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def repos(t):
    """Il respire fort, flaire l'air, tourne un peu la tête, une oreille bouge, il cligne lentement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add("corps", ech=(1 + 0.014 * r, 1, 1 + 0.024 * r))
    p.add("tete", rot=(1 * onde(t, 4) + 3 * d, -3 * g, 18 * g - 14 * d))
    p.add("oreille_G", rot=(0, 0, 16 * cloche(t, 0.50, 0.05)))
    p.add("oreille_D", rot=(0, 0, -16 * cloche(t, 0.88, 0.05)))
    p.ouvert = borne(1 - cloche(t, 0.08, 0.02) - cloche(t, 0.60, 0.02))
    return p


def avance(t):
    """Le trottinement bas et pesant : les pattes courtes par diagonales, tout le baril qui roule, la tête baissée."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 24.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.6
    p.add("corps", pos=(0, 0, -creux), rot=(1.2 * onde(t, 2, 0.1), 4 * c, 3 * s))
    for nom, sens in (("patte_av_G", 1), ("patte_ar_D", 1), ("patte_av_D", -1), ("patte_ar_G", -1)):
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.026 * max(0.0, -sens * c)))
    p.add("tete", rot=(6 + 2 * onde(t, 2, -0.2), -3 * c, -2 * s))
    p.paire("oreille", rot=(-6 + 3 * onde(t, 2, -0.25), 0, 0))
    return p


def mange(t):
    """Il baisse le museau, creuse un peu de terre des deux pattes avant, mâche, relève la tête."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    fouille = onde(t, 5) * bas
    p.add("corps", rot=(6 * bas, 0, 0))
    p.add("tete", rot=(22 * bas + 3 * leve * onde(t, 12), -3 * leve, 10 * leve))
    p.add("patte_av_G", rot=(22 * max(0.0, fouille) - 8 * bas, 0, 0))
    p.add("patte_av_D", rot=(22 * max(0.0, -fouille) - 8 * bas, 0, 0))
    p.paire("oreille", rot=(-6 * bas, 0, 0))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Une explosion de parpaing : il se tasse, fait trois bonds raides et lourds, les oreilles en arrière, puis se secoue."""
    p = Pose()
    tasse = cloche(t, 0.10, 0.10, False)
    bonds = max(0.0, onde(t, 3, -0.25)) * cloche(t, 0.58, 0.34, False)
    secoue = onde(t, 8) * cloche(t, 0.90, 0.08, False)
    p.add("corps", pos=(0, 0, -0.03 * tasse + 0.17 * bonds), rot=(-8 * bonds + 8 * tasse, 5 * secoue, 4 * secoue))
    p.paire("patte_av", rot=(-18 * bonds, 0, 0))
    p.paire("patte_ar", rot=(16 * bonds, 0, 0))
    p.add("tete", rot=(-10 * bonds + 10 * tasse, 4 * secoue, 0))
    p.paire("oreille", rot=(-18 * bonds, 0, 0))
    return p


def dort(t):
    """Il s'écrase de tout son long, les pattes écartées, le museau posé de côté sur le sol ; il ronfle (le baril gonfle)."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.045), ech=(1 + 0.018 * r, 1, 1 + 0.040 * r))
    p.paire("patte_av", rot=(-30, 0, 18))
    p.paire("patte_ar", rot=(34, 0, 12))
    p.add("tete", rot=(18, 6, 34))
    p.paire("oreille", rot=(-22, 0, 0))
    p.add("oreille_D", rot=(0, 0, -14 * cloche(t, 0.55, 0.05)))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
