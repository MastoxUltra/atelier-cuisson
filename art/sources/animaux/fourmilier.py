"""Le fourmilier en peluche de velours ras : un gris brun, la grande bande noire bordée de blanc qui part de la
poitrine et file en diagonale vers le dos, un long museau tubulaire en baguette à la bouche minuscule, de tout petits
yeux et une queue énorme en panache de plumes pendantes. Il marche sur les articulations, les griffes énormes des
antérieurs repliées : l'aspirateur de termitières : le museau au ras du sol qui renifle, le dos voûté, le panache qui
traîne et se soulève.

    python fourmilier.py        fabrique la fiche art/apercus/animaux/fourmilier.png (velours ras, palier 3)
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


GRIS = np.array(M.hexa("#b4a498"))            # la dominante : gris brun (le poil le fonce : on le prend clair)
NOIR = np.array(M.hexa("#3a3434"))            # l'accent : la bande
BLANC = np.array(M.hexa("#fff6e8"))           # le liseré de la bande
CLAIR = np.array(M.hexa("#d8cabc"))
GRIFFE = M.hexa("#f2e4c8")
CHARBON = M.hexa("#2e2828")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("fourmilier")
    a.taille = 1.80                           # queue comprise

    # ----- le corps : un long œuf voûté ; la grande bande noire bordée de blanc, en diagonale du cou à l'épaule opposée -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.420, 0.380), (0.250, 0.440), (0.000, 0.470), (-0.250, 0.430), (-0.400, 0.340))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.090), (0.14, 0.150), (0.45, 0.185), (0.78, 0.170), (0.94, 0.120), (1.0, 0.0)], L, 80, 0.007)
    x, y, z = corps.v[:, 0], corps.v[:, 1], corps.v[:, 2]
    th = np.arctan2(x, y)
    f = z / L
    diag = f - 0.34 - 0.15 * (th / math.pi)                                            # la diagonale descend du dos vers le ventre
    t = np.tile(GRIS, (len(z), 1))
    t[(f > 0.20) & (np.abs(th) < 2.6)] = GRIS
    t[(np.abs(diag - 0.22) < 0.16) & (f > 0.55) & (np.abs(th) < 2.4)] = BLANC
    t[(np.abs(diag - 0.22) < 0.12) & (f > 0.55) & (np.abs(th) < 2.4)] = NOIR
    t[np.abs(th) > 2.7] = CLAIR
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le museau : un long tube mince qui descend de la tête vers le sol, la bouche minuscule au bout ; la petite tête -----
    H = Vector((0.0, -0.470, 0.340))
    chemin = [H + Vector((0.0, 0.0, 0.030)), H + Vector((0.0, -0.150, -0.020)), H + Vector((0.0, -0.320, -0.100)), H + Vector((0.0, -0.470, -0.200)),
              H + Vector((0.0, -0.560, -0.270))]
    a.piece("museau", K.tube_peint(A.courbe(propres(chemin), 6), lambda t: 0.082 - 0.056 * t, [(0.60, tuple(GRIS)), (1, tuple(NOIR))], 20), None)
    a.piece("tete", A.boule(1.0, 36, 18).etire(0.090, 0.110, 0.095), tuple(GRIS), pos=tuple(H + Vector((0.0, 0.040, 0.030))))
    a.tete = H + Vector((0.0, -0.220, -0.060))
    for nom, c in (("G", 1), ("D", -1)):
        a.oeil("oeil_" + nom, tuple(H + Vector((c * 0.068, -0.040, 0.075))), (c * 0.45, -0.85, 0.30), 0.0200)     # plus en avant : de face, les deux yeux (16/10)
        po = A.profil([(0, 0), (0.026, 0.008), (0.032, 0.030), (0.024, 0.050), (0.008, 0.060), (0, 0.064)], 5)
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.42, 1.0), tuple(NOIR),
                mat=A.cadre(H + Vector((c * 0.070, 0.090, 0.090)), Vector((c * 0.40, 0.10, 0.90)), Vector((c * 0.3, -0.9, 0.0))))

    # ----- la queue : un énorme panache de longues mèches plates, qui traîne et se soulève ; les pattes : courtes, les antérieures
    #       aux énormes griffes repliées (il marche sur les articulations) -----
    racine = np.array([0.0, 0.400, 0.360])
    plume = None
    for k in range(9):
        u = k / 8.0 - 0.5
        ch = [tuple(racine), tuple(racine + np.array([u * 0.10, 0.150, 0.000])), tuple(racine + np.array([u * 0.26, 0.340, -0.060])),
              tuple(racine + np.array([u * 0.40, 0.560, -0.130 + 0.050 * math.cos(u * 3)]))]
        m = A.tube(A.courbe(ch, 6), lambda t: 0.060 + 0.070 * math.sin(math.pi * min(t * 1.15, 1.0)) - 0.030 * t, 12)
        plume = m if plume is None else plume + m
    a.piece("queue", plume, tuple(GRIS))
    for nom, x_, y_ in (("av_G", 0.110, -0.230), ("av_D", -0.110, -0.230), ("ar_G", 0.115, 0.300), ("ar_D", -0.115, 0.300)):
        a.piece("patte_" + nom, A.tube(A.courbe([(x_, y_, 0.310), (x_ * 1.05, y_ - 0.010, 0.170), (x_ * 1.05, y_ - 0.030, 0.050)], 5), 0.048, 14), tuple(GRIS))
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.050, 0.080, 0.030), tuple(NOIR), pos=(x_ * 1.05, y_ - 0.060, 0.030))
        if nom.startswith("av"):
            c = 1 if x_ > 0 else -1
            g = None
            for k in (-1, 0, 1):
                gr = A.tour(A.profil([(0, 0), (0.016, 0.004), (0.012, 0.050), (0.005, 0.100), (0, 0.130)], 5), 12)
                gr = gr.pose((0, 0, 0), (-74, 0, 0)).pose((k * 0.030, -0.040, 0.0), (0, 0, k * 8))
                g = gr if g is None else g + gr
            a.piece("griffes_" + nom, g, GRIFFE, pos=(x_ * 1.05, y_ - 0.090, 0.050), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("fourmilier", styles.style_de("fourmilier"), sys.modules[__name__]), "Fourmilier")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py fourmilier). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.289                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.214, 0.464)),
    ('tete', 'corps', (0.000, -0.329, 0.381)),
    ('oreille_G', 'tete', (0.062, -0.385, 0.438)),
    ('patte_av_G', 'corps', (0.112, -0.235, 0.270)),
    ('patte_ar_G', 'corps', (0.119, 0.291, 0.307)),
    ('queue', 'corps', (0.001, 0.396, 0.404)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('griffes_av', 'patte_av', True), ('patte_av', 'patte_av', True),
    ('patte_ar', 'patte_ar', True), ('oreille', 'oreille', True), ('pied_av', 'patte_av', True),
    ('pied_ar', 'patte_ar', True), ('museau', 'tete'), ('corps', 'corps'), ('queue', 'queue'), ('tete', 'tete'),
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
    p.add('oreille_G', rot=(0, 0, 20 * cloche(t, 0.50, 0.05) - 8 * g))
    p.add('oreille_D', rot=(0, 0, -20 * cloche(t, 0.88, 0.05) + 6 * d))
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
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.paire('oreille', rot=(-8 + 3 * onde(t, 2, -0.25), 0, 0))
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
    p.paire('oreille', rot=(-6 * bas + 5 * leve, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.087 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.159), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
