"""Le fennec en peluche de velours ras (2e dessin) : un petit RENARD de sable, crème sable (jamais blanc), la face
fine et le museau long et pointu, de grands yeux sombres en amande, et deux oreilles immenses, triangulaires et larges
à la base, aussi hautes que la tête est longue, le dedans rose et poilu ; une queue en panache au bout noir. Couché
comme un sphinx, les pattes avant allongées, la tête relevée et tournée vers nous, le nez un peu en l'air, les
oreilles chacune d'un côté : il écoute tout le désert.

    python fennec.py        fabrique la fiche art/apercus/animaux/fennec.png (velours ras, palier 3)
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


SABLE = np.array(M.hexa("#f2cf94"))           # la dominante : crème sable (le poil le fonce)
DOS = np.array(M.hexa("#e8bc7c"))             # le dos, le dessus du crâne, le dos des oreilles
CREME = np.array(M.hexa("#fff0d0"))           # le ventre, la face, le poitrail, les pattes
ROSE = M.hexa("#f4c8b0")                      # l'accent : le dedans des oreilles
NOIR = np.array(M.hexa("#2e2826"))            # le nez, le bout de la queue, le trait des yeux
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("fennec")
    a.taille = 0.60

    # ----- le corps : un petit corps de renard couché, long et bas, le dos sable, le ventre et la poitrine crème -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.230, 0.075), (0.130, 0.090), (0.010, 0.100), (-0.100, 0.118), (-0.160, 0.140))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.06, 0.062), (0.22, 0.088), (0.55, 0.092), (0.84, 0.082), (0.96, 0.062), (1.0, 0.0)], L, 64)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.where((th > 2.2)[:, None], CREME, np.where((th < 1.1)[:, None], DOS, SABLE))
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou et la tête : un cou fin qui relève la tête ; le crâne petit, le MUSEAU long et pointu, la face crème ;
    #       tournée vers nous, le nez un peu en l'air -----
    a.piece("cou", A.tube(A.courbe([(0.0, -0.130, 0.140), (0.0, -0.170, 0.190), (0.0, -0.190, 0.240)], 5), lambda t: 0.060 - 0.016 * t, 20), tuple(CREME))
    T = A.cadre(Vector((0.0, -0.225, 0.270)), Vector((0.48, -1.0, 0.22)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.044), (0.20, 0.060), (0.36, 0.058), (0.56, 0.044), (0.76, 0.030), (0.92, 0.021), (0.98, 0.014), (1.0, 0.0)],
                  0.190, 48, 0.004)
    tt = np.where((tete.v[:, 1] > 0.020)[:, None], DOS, CREME)
    tt[(tete.v[:, 2] > 0.045) & (tete.v[:, 1] > 0.0) & (tete.v[:, 1] < 0.035)] = SABLE
    tete.teinte = tt
    a.piece("tete", tete.sculpte(lambda v: v * [1.0, 0.86, 1.0]), None, mat=T @ A.repere((0, 0, -0.045)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.014, 0.011, 0.012), tuple(NOIR), mat=T @ A.repere((0, 0.002, 0.146)), poil=False)
    a.tete = T @ Vector((0, 0.0, 0.100))

    # ----- les yeux : grands, sombres, en amande, relevés vers les tempes, cernés d'un trait noir ; les oreilles : immenses
    #       triangles dressés, larges à la base, le dedans rose et poilu ; l'une tournée vers nous, l'autre de côté -----
    po = A.profil([(0, 0), (0.060, 0.010), (0.062, 0.036), (0.052, 0.090), (0.038, 0.150), (0.022, 0.210), (0.008, 0.256), (0, 0.272)], 7)
    for nom, c, ecart in (("G", 1, 0.0), ("D", -1, 1.0)):
        regard = T3 @ Vector((c * 0.70, 0.26, 0.30))
        a.rustine("cerne_" + nom, "tete", T.to_translation(), regard, 0.25, tuple(NOIR), 0.003, 0)
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0165)
        a.piece("amande_" + nom, K.paupiere(0.0190, 0.30), tuple(DOS), mat=A.cadre(p + n * 0.005, n, T3 @ Vector((c * -0.5, 1, 0.1))), poil=False)
        vers = (T3 @ Vector((c * (0.46 + 0.30 * ecart), 0.86 - 0.10 * ecart, -0.30 - 0.15 * ecart))).normalized()
        E = A.cadre(T @ Vector((c * 0.036, 0.040, -0.040)) - vers * 0.008, vers, T3 @ Vector((c * 0.2, 0.0, 1.0)))
        a.piece("oreille_" + nom, A.tour(po, 40).etire(1.0, 0.26, 1.0), tuple(DOS), mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 32).etire(0.68, 0.26, 0.86).pose((0, 0.010, 0.012)), ROSE, mat=E, poil=False)

    # ----- les pattes : les deux avant allongées devant lui (d'une seule pièce, crème, le poignet fin, la petite patte) ;
    #       les cuisses repliées sous les hanches, les pieds arrière devant elles -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.056, -0.050, 0.140), (c * 0.054, -0.120, 0.070), (c * 0.052, -0.200, 0.034), (c * 0.050, -0.270, 0.026)]
        fa = K.Fil(ch, (1, 0, 0))
        av = fuseau([(0.0, 0.030), (0.08, 0.040), (0.40, 0.030), (0.70, 0.022), (0.82, 0.026), (0.94, 0.028), (1.0, 0.0)], fa.long, 24, 0.005)
        av.teinte = np.tile(CREME, (len(av.v), 1))
        a.piece("patte_av_" + nom, av.sculpte(fa.couche), None)
        cu = A.boule(1.0, 32, 16)
        cu.teinte = np.where((cu.v[:, 2] > 0.2)[:, None], SABLE, CREME)
        a.piece("cuisse_" + nom, cu.etire(0.046, 0.100, 0.064), None, pos=(c * 0.080, 0.140, 0.070), rot=(0, 0, c * 8))
        a.piece("pied_ar_" + nom, A.boule(1.0, 20, 10).etire(0.026, 0.070, 0.020), tuple(CREME), pos=(c * 0.066, 0.040, 0.020), rot=(0, 0, c * 4))

    # ----- la queue : un panache épais, qui part de la croupe et se recourbe sur le côté, le bout noir -----
    qf = K.Fil([(0.0, 0.190, 0.080), (0.0, 0.290, 0.072), (0.030, 0.390, 0.060), (0.100, 0.450, 0.052), (0.190, 0.430, 0.046), (0.235, 0.360, 0.042)], (1, 0, 0))
    LQ = qf.long
    queue = fuseau([(0.0, 0.034), (0.20, 0.052), (0.50, 0.062), (0.78, 0.054), (0.92, 0.036), (0.98, 0.018), (1.0, 0.0)], LQ, 40, 0.006)
    queue.teinte = np.where((queue.v[:, 2] > 0.82 * LQ)[:, None], NOIR, np.where((queue.v[:, 1] < -0.010)[:, None], CREME, SABLE))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("fennec", styles.style_de("fennec"), sys.modules[__name__]), "Fennec")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py fennec). Les mesures sont celles du modèle (couché comme un sphinx), avant a.taille.
# Couché, il ne marche pas : il RAMPE, le ventre bas, une patte avant puis l'autre, et les oreilles tournent.

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0.0, 0.14, 0.09)),            # les hanches : il respire, roule, se couche autour
    ("cou", "corps", (0.0, -0.12, 0.14)),
    ("tete", "cou", (0.0, -0.19, 0.24)),               # la nuque
    ("oreille_G", "tete", (0.045, -0.215, 0.30)),      # la base de l'oreille
    ("patte_av_G", "corps", (0.056, -0.05, 0.14)),     # l'épaule
    ("cuisse_G", "corps", (0.080, 0.14, 0.08)),        # la hanche : la cuisse et le pied arrière
    ("queue", "corps", (0.0, 0.19, 0.08)),             # le panache, d'un seul os
]

PORTEURS = [("corps", "corps"), ("cou", "cou"), ("tete", "tete"), ("nez", "tete"), ("cerne", "tete"), ("oeil", "tete"),
            ("amande", "tete"), ("oreille", "oreille", True), ("pavillon", "oreille", True), ("patte_av", "patte_av", True),
            ("cuisse", "cuisse", True), ("pied_ar", "cuisse", True), ("queue", "queue"),
            # les yeux sont posés un par un : leurs paupières s'appellent paupiere_0 et paupiere_1, chacune sur son os
            ("paupiere_0", "paupiere_0"), ("paupiere_1", "paupiere_1"), ("cil_0", "paupiere_0"), ("cil_1", "paupiere_1")]


def repos(t):
    """Couché, il respire ; il tourne la tête d'un côté, puis de l'autre, une oreille puis l'autre qui pivotent ; le panache balance."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.12)
    p.add("corps", ech=(1 + 0.010 * r, 1, 1 + 0.022 * r))
    p.add("cou", rot=(2 * r, 0, 10 * g - 8 * d))
    p.add("tete", rot=(3 * g, -6 * g + 4 * d, 18 * g - 14 * d))
    p.add("oreille_G", rot=(0, 0, 26 * cloche(t, 0.50, 0.05) - 10 * g))
    p.add("oreille_D", rot=(0, 0, -26 * cloche(t, 0.90, 0.05) + 8 * d))
    p.add("queue", rot=(0, 0, -9 * onde(t, 1)))
    p.ouvert = borne(1 - 0.35 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.60, 0.02))
    return p


def avance(t):
    """Il rampe : les pattes avant tirent chacune à son tour, la croupe suit, la tête reste basse, les oreilles couchées."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    p.add("corps", pos=(0, 0, 0.008 * abs(s)), rot=(0, 2 * c, 3 * s))
    p.add("patte_av_G", rot=(-22 * max(0.0, s), 0, 0))
    p.add("patte_av_D", rot=(-22 * max(0.0, -s), 0, 0))
    p.add("cuisse_G", rot=(-9 * max(0.0, -s), 0, 0))
    p.add("cuisse_D", rot=(-9 * max(0.0, s), 0, 0))
    p.add("cou", rot=(6, 0, -3 * s))
    p.add("tete", rot=(-4 + 2 * onde(t, 2), -2 * c, -3 * s))
    p.paire("oreille", rot=(-10 + 4 * onde(t, 2, -0.25), 0, 0))
    p.add("queue", rot=(0, 0, -16 * s))
    return p


def mange(t):
    """Le museau au sable : il flaire, trois petites becquées, puis il relève la tête et mâche, les oreilles dressées."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add("cou", rot=(28 * bas + 4 * coups, 0, 6 * leve))
    p.add("tete", rot=(18 * bas + 8 * coups + 3 * leve * onde(t, 12), -4 * leve, 14 * leve))
    p.paire("oreille", rot=(-8 * bas + 4 * leve, 0, 0))
    p.add("queue", rot=(0, 0, -6 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit droit en l'air toutes pattes repliées, les oreilles dressées, retombe, et fouette du panache."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.70, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.78, 0.20, False)
    p.add("corps", pos=(0, 0, -0.02 * tasse + 0.16 * vol), rot=(-14 * vol + 8 * salut, 0, 0))
    p.paire("patte_av", rot=(-40 * vol, 0, 0))
    p.paire("cuisse", rot=(-30 * vol, 0, 0))
    p.add("cou", rot=(-8 * vol + 10 * tasse, 0, 0))
    p.add("tete", rot=(-8 * vol, 0, 0))
    p.paire("oreille", rot=(-30 * vol, 0, 0))
    p.add("queue", rot=(-20 * vol, 0, -24 * fouet))
    return p


def dort(t):
    """Roulé sur lui-même : la tête posée sur les pattes avant, une oreille rabattue, le panache ramené sur le museau."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, -0.012), ech=(1 + 0.014 * r, 1, 1 + 0.030 * r))
    p.add("cou", rot=(24, 0, 48))
    p.add("tete", rot=(6, 8, 36))
    p.paire("oreille", rot=(-26, 0, 0))
    p.add("oreille_D", rot=(0, 0, -16 * cloche(t, 0.55, 0.05)))
    p.add("patte_av_G", rot=(0, 0, 10))
    p.add("queue", rot=(0, 0, 78))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
