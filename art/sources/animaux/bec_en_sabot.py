"""Le bec-en-sabot en peluche de magasin (3e dessin) : un grand oiseau gris debout, droit comme une statue, vu de trois
quarts, la tête tournée de PROFIL. La tête reste ronde, bien visible, avec son gros œil jaune pâle sous un front lourd
et une petite huppe en pointe ; et le bec en sort vers l'avant et le bas, énorme, en forme de sabot vu de côté : le
dessus qui se bombe en arche, le crochet qui retombe au bout, le dessous plus mince. De longues pattes noires, des
ailes en cape. Il ne bouge pas.

    python bec_en_sabot.py        fabrique la fiche art/apercus/animaux/bec_en_sabot.png (peluche de magasin, palier 4)
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
    """Les points d'un tracé sans doublons consécutifs (deux points identiques à la suite déforment un tube en NaN)."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie


# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
BLEUTE = np.array(M.hexa("#9aa8c4"))          # la dominante : gris bleuté clair
OMBRE = np.array(M.hexa("#6a7694"))           # les ailes, le dos, la huppe
IVOIRE = np.array(M.hexa("#f4e4a8"))          # l'accent : le bec, jaune os
OS_BAS = np.array(M.hexa("#dcc880"))          # le dessous du bec, un ton plus bas
MARBRE = np.array(M.hexa("#9a8e72"))          # le marbrage du bec
OEIL = M.hexa("#fff0a0")
CHARBON = M.hexa("#3a3638")
CORPS = Vector((0.0, 0.050, 0.700))
TETE = Vector((0.0, -0.060, 1.235))
YAW = 0.0                                     # pour le jeu l'oiseau n'est pas tourné (la fiche le regarde déjà de trois quarts)
LACET, PIQUE = 66.0, 6.0                      # la tête tournée de côté : le bec se lit de profil
BEC_PIQUE = 18.0                              # le bec pointé vers le bas


def construire():
    a = K.Animal("bec_en_sabot")
    a.taille = 1.40
    Y = A.repere((0, 0, 0), (0, 0, YAW))
    Y3 = Y.to_3x3()

    def W(v):
        return Y @ Vector(v)

    # ----- le corps : un long œuf droit et mince comme une statue, la poitrine claire, le dos sombre ; les ailes en cape -----
    corps = A.boule(1.0, 56, 28)
    corps.teinte = np.where((corps.v[:, 1] > 0.34)[:, None], OMBRE, BLEUTE)

    def oeuf(v):
        v = K.bosse(v, (0, -0.9, 0.3), 0.10, 0.45)
        s = v * [0.190, 0.170, 0.420]
        s[:, 0] *= 1 - 0.24 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s
    a.piece("corps", corps.sculpte(oeuf), None, mat=Y @ A.repere(CORPS, (-4, 0, 0)))
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 36, 18)
        aile.teinte = np.tile(OMBRE, (len(aile.v), 1))

        def galet(v):
            s = K.emousse(v, 0.88)
            s[:, 1] *= 1 - 0.42 * K.lisse((v[:, 2] + 0.2) / 1.2)
            return s
        a.piece("aile_" + nom, aile.sculpte(galet).etire(0.046, 0.090, 0.340), None,
                mat=Y @ A.repere((c * 0.180, 0.080, 0.640), (-6, 0, c * 5)))

    # ----- le cou : court et épais, qui porte la tête ; la tête : ronde, un peu aplatie, le front lourd ; la huppe -----
    a.piece("cou", A.boule(1.0, 28, 14).etire(0.105, 0.100, 0.125), tuple(BLEUTE), mat=Y @ A.repere((0.0, -0.020, 1.130)))
    HL = A.repere(TETE, (PIQUE, 0, LACET))
    H = Y @ HL
    H3 = H.to_3x3()
    a.piece("tete", A.boule(1.0, 48, 24).etire(0.125, 0.118, 0.112), tuple(BLEUTE), mat=H)
    a.piece("huppe", A.tour(A.profil([(0, 0), (0.050, 0.010), (0.036, 0.090), (0.014, 0.170), (0, 0.210)], 5), 20), tuple(OMBRE),
            mat=A.cadre(W(TETE + Vector((0.0, 0.080, 0.070))), Y3 @ Vector((0.0, 0.60, 0.75)), Vector((0, 0, 1))), poil=False)

    # ----- le bec : un énorme sabot, plus large que la tête, qui SORT de la tête vers l'avant et le bas ; profil bombé,
    #       crochet au bout, dessous plus mince ; un marbrage gris -----
    bec = A.tour(A.profil([(0, 0), (0.104, 0.010), (0.138, 0.070), (0.152, 0.170), (0.144, 0.290), (0.116, 0.380), (0.076, 0.440),
                           (0.036, 0.484), (0, 0.500)], 6), 56)
    z, x, y = bec.v[:, 2], bec.v[:, 0], bec.v[:, 1]
    bec.teinte = np.where((np.sin(21 * z + 5 * x) * np.sin(15 * y + 3 * z) > 0.58)[:, None], MARBRE, np.where((y < -0.040)[:, None], OS_BAS, IVOIRE))

    def sabot(v):
        s = v.copy()
        haut = v[:, 1] > 0
        s[:, 1] *= np.where(haut, 1.15 - 0.20 * K.lisse((v[:, 2] - 0.25) / 0.25), 0.55)           # le dessus bombé, le dessous mince
        s[:, 1] += 0.040 * np.sin(math.pi * np.clip(v[:, 2] / 0.50, 0, 1)) * haut                   # l'arche du dessus
        s[:, 1] -= 0.100 * np.clip((v[:, 2] - 0.36) / 0.14, 0, 1) ** 1.7                           # le crochet retombe
        return s
    lac, pq = math.radians(LACET), math.radians(BEC_PIQUE)
    dirige = Vector((math.sin(lac) * math.cos(pq), -math.cos(lac) * math.cos(pq), -math.sin(pq))).normalized()
    a.piece("bec", bec.sculpte(sabot), None,
            mat=A.cadre(W(TETE + dirige * 0.060 + Vector((0, 0, -0.040))), Y3 @ dirige, Vector((0, 0, 1))), poil=False)
    a.tete = W(TETE + dirige * 0.220 + Vector((0, 0, -0.080)))

    # ----- les yeux : jaune pâle, ronds et fixes, sur le côté de la tête, derrière le bec, sous une arcade lourde -----
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.93, -0.28, 0.22))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.30, OEIL, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.005, n, 0.0240)
        a.piece("arcade_" + nom, K.paupiere(0.030, 0.30), tuple(OMBRE), mat=A.cadre(p + n * 0.006, n, H3 @ Vector((c * -0.2, 1, 0.1))), poil=False)

    # ----- les pattes : longues, minces, noires, de grands pieds à quatre orteils ; la queue : courte -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [W((c * 0.082, 0.060, 0.400)), W((c * 0.090, 0.040, 0.220)), W((c * 0.092, 0.010, 0.040))]
        a.piece("patte_" + nom, A.tube(A.courbe(propres([tuple(q) for q in ch]), 5), 0.026, 14), CHARBON, poil=False)
        doigts = None
        for ang in (-34, -10, 12, 34):
            d = A.boule(1.0, 14, 8).etire(0.013, 0.080, 0.011).pose((0, -0.060, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("orteils_" + nom, doigts, CHARBON, mat=Y @ A.repere((c * 0.092, 0.000, 0.011)), poil=False)
    a.piece("queue", A.boule(1.0, 24, 12).etire(0.070, 0.160, 0.026), tuple(OMBRE), mat=Y @ A.repere((0, 0.270, 0.360), (-26, 0, 0)))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("bec_en_sabot", styles.style_de("bec_en_sabot"), sys.modules[__name__]), "Bec-en-sabot")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py bec_en_sabot). Les mesures sont celles du modèle, avant a.taille.
# Le grand immobile : il tient la pose des heures, le corps ne bouge presque pas ; tout se joue au cou, au bec, aux ailes.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.05, 0.52)),            # le bassin : il roule et se penche autour
    ("cou", "corps", (0.0, -0.02, 1.10)),              # le pied du cou
    ("tete", "cou", (0.0, -0.06, 1.20)),               # la nuque
    ("aile_G", "corps", (0.17, 0.06, 0.97)),           # l'épaule : l'aile pend de là, la pointe en bas
    ("patte_G", "corps", (0.082, 0.06, 0.40)),         # la hanche : la patte et son pied
    ("queue", "corps", (0.0, 0.20, 0.38)),
]

PORTEURS = [("corps", "corps"), ("cou", "cou"), ("tete", "tete"), ("huppe", "tete"), ("bec", "tete"), ("arcade", "tete"),
            ("iris", "tete"), ("oeil", "tete"), ("aile", "aile", True), ("patte", "patte", True), ("orteils", "patte", True),
            ("queue", "queue"),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def repos(t):
    """Statue : il respire à peine, la tête pivote très lentement d'un côté puis de l'autre, le bec s'incline, une aile
    se rajuste, deux clignements lents."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.30, 0.18), cloche(t, 0.74, 0.14)
    p.add("corps", ech=(1 + 0.006 * r, 1, 1 + 0.010 * r))
    p.add("cou", rot=(2 * g, 0, 10 * g - 8 * d))
    p.add("tete", rot=(5 * d - 2 * g, 0, 14 * g - 12 * d))
    p.add("aile_G", rot=(0, -6 * cloche(t, 0.55, 0.06), 0))
    p.add("queue", rot=(2 * r, 0, 0))
    p.ouvert = borne(1 - 0.5 * cloche(t, 0.12, 0.04) - cloche(t, 0.62, 0.04))
    return p


def avance(t):
    """Une longue enjambée lente, de héron : les pattes alternent, le corps oscille, la tête fait son va-et-vient raide."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 22.0
    p.add("corps", pos=(0, 0, -0.02 * (1 - math.cos(math.radians(pas * s)))), rot=(0, 3 * c, 2.5 * s))
    for nom, sens in (("patte_G", 1), ("patte_D", -1)):
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.06 * max(0.0, -sens * c)))
    p.add("cou", rot=(-4 + 3 * onde(t, 2, -0.1), 0, -2 * s))
    p.add("tete", rot=(4 - 3 * onde(t, 2, -0.2), 0, 2 * s))
    p.paire("aile", rot=(0, 0, 0), pos=(0, 0, 0))
    p.add("queue", rot=(0, 0, -5 * s))
    return p


def mange(t):
    """La pêche : il guette, la tête haute, puis se plie d'un coup, le bec plonge au sol, il claque et se redresse."""
    p = Pose()
    plonge = cloche(t, 0.50, 0.16)
    attente = 1 - cloche(t, 0.50, 0.30)
    claque = max(0.0, onde(t, 6)) * cloche(t, 0.72, 0.12)
    p.add("corps", rot=(10 * plonge, 0, 0))
    p.add("cou", rot=(62 * plonge - 4 * attente, 0, 0))
    p.add("tete", rot=(26 * plonge + 10 * claque, 0, 0))
    p.paire("aile", rot=(0, -4 * plonge, 0))
    p.add("queue", rot=(-14 * plonge, 0, 0))
    p.ouvert = borne(1 - cloche(t, 0.30, 0.03))
    return p


def joie(t):
    """Il ouvre les ailes en grand, claque du bec très vite et fait un petit saut raide, puis se range."""
    p = Pose()
    ouvre = cloche(t, 0.45, 0.30, False)
    saut = math.sin(math.pi * borne((t - 0.30) / 0.30))
    claque = onde(t, 8) * cloche(t, 0.55, 0.20, False)
    p.add("corps", pos=(0, 0, 0.14 * saut), rot=(-8 * ouvre, 0, 0))
    p.paire("aile", rot=(0, -62 * ouvre, 0))
    p.add("cou", rot=(-10 * ouvre, 0, 0))
    p.add("tete", rot=(-6 * ouvre + 9 * claque, 0, 0))
    p.paire("patte", rot=(-14 * saut, 0, 0))
    p.add("queue", rot=(-20 * ouvre, 0, 0))
    return p


def dort(t):
    """Debout comme une statue, la tête enfoncée dans les épaules et tournée de côté, les ailes serrées, le bec sur la poitrine."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", ech=(1 + 0.008 * r, 1, 1 + 0.014 * r), rot=(2, 0, 0))
    p.add("cou", rot=(34, 0, 22))
    p.add("tete", rot=(44, 0, 38))
    p.add("queue", rot=(-4, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
