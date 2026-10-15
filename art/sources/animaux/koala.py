"""Le koala en peluche de velours ras : un gris cendré bleuté tout doux, le ventre blanc, de grandes oreilles rondes
tapissées de longs poils crème, un gros nez de cuir noir en bouton, de petits yeux et des mains à deux pouces qui
agrippent. Un dormeur qui s'accroche à une idée : assis sur son séant, le dos rond, les bras serrés autour d'un
tronc qu'on ne voit pas, la tête posée sur l'épaule, les paupières à demi tombées, le nez qui pointe vers nous.

    python koala.py        fabrique la fiche art/apercus/animaux/koala.png (velours ras, palier 3)
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

CENDRE = M.hexa("#c4cad4")                    # la dominante : gris cendré bleuté (le poil le fonce : on le prend clair)
BLANC = M.hexa("#fbf8f0")                     # le ventre, le dedans des oreilles, la gorge
CHARBON = M.hexa("#3a3436")                   # l'accent : le nez, les yeux, les griffes
CORPS = Vector((0.0, 0.050, 0.250))
TETE = Vector((0.0, -0.110, 0.470))
LACET, PENCHE = 20.0, -16.0


def construire():
    a = K.Animal("koala")
    a.taille = 0.80

    # ----- le corps : une poire assise, le dos rond, le ventre blanc devant -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    t = np.tile(np.asarray(CENDRE, float), (len(v), 1))
    t[(v[:, 1] < -0.40) & (v[:, 2] < 0.55)] = BLANC
    corps.teinte = t

    def poire(v):
        v = K.bosse(v, (0, 0.8, 0.0), 0.10, 0.5)                              # le dos rond
        s = v * [0.150, 0.140, 0.190]
        s[:, 0] *= 1 + 0.15 * K.lisse((-v[:, 2] + 0.2) / 1.0)
        return s
    a.piece("corps", corps.sculpte(poire), None, pos=CORPS, rot=(-6, 0, 0))

    # ----- la tête : large et ronde, les joues pleines ; penchée sur l'épaule, tournée vers nous -----
    H = A.repere(TETE, (0, PENCHE, LACET))
    H3 = H.to_3x3()

    def tete_f(v):
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.9, -0.25, -0.30), 0.18, 0.30)
        return v * [0.140, 0.122, 0.118]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(tete_f), CENDRE, mat=H)
    a.tete = H @ Vector((0, -0.130, -0.010))
    # le gros nez de cuir : un bouton ovale noir qui sort du museau
    a.piece("nez", A.boule(1.0, 28, 14).etire(0.042, 0.030, 0.046), CHARBON, mat=H @ A.repere((0, -0.122, -0.012)), poil=False)
    bouche = [H3 @ Vector(d) for d in ((-0.32, -0.80, -0.58), (0.0, -0.92, -0.66), (0.32, -0.80, -0.58))]
    a.broderie("bouche", A.courbe(propres(a.trace("tete", H.to_translation(), bouche, 0.004)), 4), 0.0026, CHARBON)

    # ----- les yeux : petits et rapprochés, sous une paupière lourde ; les oreilles : deux gros disques à fourrure crème -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.46, -0.84, 0.22)))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0145)
        a.piece("lourde_" + nom, K.paupiere(0.018, 0.06), CENDRE, mat=A.cadre(p + n * 0.005, n, H3 @ Vector((0, 0, 1))), poil=False)
        E = A.cadre(H @ Vector((c * 0.120, 0.012, 0.070)), H3 @ Vector((c * 0.70, -0.10, 0.62)), H3 @ Vector((0, 1, 0)))
        a.piece("oreille_" + nom, A.boule(1.0, 36, 18).etire(0.098, 0.030, 0.098).pose((0, 0, 0.060)), CENDRE, mat=E)
        a.piece("fourrure_" + nom, A.boule(1.0, 28, 14).etire(0.072, 0.022, 0.072).pose((0, 0.014, 0.062)), BLANC, mat=E)

    # ----- les bras : serrés autour du tronc qu'on ne voit pas, les mains aux griffes ; les jambes : deux gros genoux -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.130, -0.030, 0.320), (c * 0.190, -0.120, 0.300), (c * 0.120, -0.200, 0.270), (c * 0.040, -0.200, 0.250)]
        a.piece("bras_" + nom, A.tube(A.courbe(chemin, 6), lambda t: 0.040 - 0.008 * t, 14), CENDRE)
        a.piece("main_" + nom, A.boule(1.0, 24, 12).etire(0.036, 0.040, 0.034), CHARBON, pos=chemin[-1])
        a.piece("cuisse_" + nom, A.boule(1.0, 28, 14).etire(0.070, 0.110, 0.070), CENDRE, pos=(c * 0.110, -0.040, 0.080))
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.044, 0.080, 0.028), CHARBON, pos=(c * 0.115, -0.130, 0.030), rot=(0, 0, c * 10))
    a.piece("queue", A.boule(1.0, 20, 10).etire(0.040, 0.040, 0.032), CENDRE, pos=(0, 0.150, 0.100))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("koala", styles.style_de("koala"), sys.modules[__name__]), "Koala")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py koala). Les mesures sont celles du modèle, avant a.taille.
# Le dormeur : assis le dos rond, les bras serrés contre lui comme autour d'un tronc.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.07, 0.15)),            # le bassin : il se penche, se dandine, se roule autour
    ("tete", "corps", (0.0, -0.10, 0.40)),             # la nuque
    ("oreille_G", "tete", (0.120, -0.10, 0.54)),       # la base du gros disque
    ("bras_G", "corps", (0.130, -0.03, 0.33)),         # l'épaule : le bras et la main
    ("cuisse_G", "corps", (0.110, -0.04, 0.12)),       # la hanche : la cuisse et le pied
]

PORTEURS = [("corps", "corps"), ("tete", "tete"), ("nez", "tete"), ("bouche", "tete"), ("oeil", "tete"), ("lourde", "tete"),
            ("oreille", "oreille", True), ("fourrure", "oreille", True), ("bras", "bras", True), ("main", "bras", True),
            ("cuisse", "cuisse", True), ("pied", "cuisse", True), ("queue", "corps"),
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def repos(t):
    """Assis le dos rond, il respire lentement, la tête dodeline, une oreille tressaille, les paupières lourdes."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.30, 0.18), cloche(t, 0.74, 0.14)
    p.add("corps", ech=(1 + 0.012 * r, 1, 1 + 0.020 * r))
    p.add("tete", rot=(3 * d - 2 * g, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add("oreille_G", rot=(0, 0, 18 * cloche(t, 0.50, 0.05)))
    p.add("oreille_D", rot=(0, 0, -18 * cloche(t, 0.88, 0.05)))
    p.paire("bras", rot=(2 * r, 0, 0))
    p.ouvert = borne(0.85 - 0.45 * g - cloche(t, 0.10, 0.03) - cloche(t, 0.62, 0.03))
    return p


def avance(t):
    """Le dandinement du koala à terre : le corps roule d'un côté à l'autre, les bras et les jambes alternent, la tête suit."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    p.add("corps", pos=(0, 0, 0.012 * abs(s)), rot=(4, 7 * s, 3 * c))
    p.add("bras_G", rot=(-20 * s, 0, 0))
    p.add("bras_D", rot=(20 * s, 0, 0))
    p.add("cuisse_G", rot=(18 * s, 0, 0))
    p.add("cuisse_D", rot=(-18 * s, 0, 0))
    p.add("tete", rot=(-3, -5 * s, -3 * c))
    p.paire("oreille", rot=(-6 + 3 * onde(t, 2), 0, 0))
    return p


def mange(t):
    """Il porte à sa bouche, des deux mains, une feuille d'eucalyptus, et mâche longuement, la tête qui roule."""
    p = Pose()
    haut = cloche(t, 0.5, 0.40)
    mache = onde(t, 6) * haut
    p.add("corps", rot=(-4 * haut, 0, 0))
    p.paire("bras", rot=(-62 * haut, 0, 18 * haut))
    p.add("tete", rot=(6 * haut + 4 * mache, 0, 4 * mache))
    p.paire("oreille", rot=(-4 * mache, 0, 0))
    p.ouvert = borne(1 - 0.4 * haut - cloche(t, 0.10, 0.03))
    return p


def joie(t):
    """Il lève les deux bras très haut, se tortille de contentement, un petit sautillement, les oreilles qui battent."""
    p = Pose()
    haut = cloche(t, 0.45, 0.30, False)
    saut = max(0.0, onde(t, 3)) * cloche(t, 0.55, 0.25, False)
    p.add("corps", pos=(0, 0, 0.05 * saut), rot=(-6 * haut, 4 * onde(t, 3) * haut, 0))
    p.paire("bras", rot=(-125 * haut, 0, 20 * haut))
    p.paire("cuisse", rot=(-14 * saut, 0, 0))
    p.add("tete", rot=(-10 * haut, 5 * onde(t, 3) * haut, 0))
    p.paire("oreille", rot=(-18 * haut * (1 + onde(t, 6)) / 2, 0, 0))
    return p


def dort(t):
    """Il s'affaisse sur lui-même, la tête enfoncée dans la poitrine, les bras serrés autour de lui."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", rot=(22, 0, 0), ech=(1 + 0.012 * r, 1, 1 + 0.022 * r))
    p.add("tete", rot=(30, 0, 14))
    p.paire("bras", rot=(-30, 0, -10))
    p.paire("oreille", rot=(-20, 0, 0))
    p.add("oreille_G", rot=(0, 0, 12 * cloche(t, 0.55, 0.05)))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
