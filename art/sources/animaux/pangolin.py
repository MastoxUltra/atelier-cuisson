"""Le pangolin en peluche de magasin (2e dessin, d'après photos : à quatre pattes, plus de chevalier debout) : un corps
long et bas, de la petite tête pointue en cône jusqu'au bout d'une longue queue épaisse, tout couvert d'une armure
d'écailles terre cuite posées en rangs serrés qui se chevauchent comme des tuiles ; le ventre et les pattes en peau
crème, de petits yeux, de longues griffes de fouisseur aux mains. Il renifle le sol : la tête basse, le museau en avant,
la queue qui traîne derrière lui en grande courbe, une patte avant avancée.

    python pangolin.py        fabrique la fiche art/apercus/animaux/pangolin.png (peluche de magasin, palier 4)
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
TUILE = np.array(M.hexa("#e88a5a"))           # la dominante : terre cuite
TUILE_BRUN = np.array(M.hexa("#b0603c"))      # le bord des écailles, un ton plus bas
DORE = np.array(M.hexa("#ffc872"))            # l'accent : le bout des écailles
CREME = np.array(M.hexa("#fff0d8"))           # le ventre, le museau, les pattes
CHARBON = M.hexa("#4a3a38")                   # les griffes
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 5)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("pangolin")
    a.taille = 1.00

    # ----- tout d'une pièce, du bout du museau au bout de la queue, couché le long d'une courbe : la tête en cône, le cou, le
    #       dos arrondi, la croupe, la longue queue épaisse qui s'effile ; les écailles en tuiles qui se chevauchent -----
    chemin = [(0.0, y, z) for y, z in ((-0.800, 0.110), (-0.650, 0.150), (-0.480, 0.190), (-0.250, 0.260), (0.000, 0.290),
                                       (0.250, 0.270), (0.480, 0.210), (0.730, 0.130), (1.000, 0.075), (1.250, 0.050))]
    chemin = [(0.0 if y < 0.7 else 0.16 * (y - 0.7) ** 1.2, y, z) for _x, y, z in chemin]
    fil = K.Fil(chemin, (1, 0, 0))
    L = fil.long
    pts = [(0.0, 0.0), (0.014, 0.020), (0.030, 0.070), (0.050, 0.130), (0.074, 0.190), (0.100, 0.250), (0.150, 0.330),
           (0.180, 0.420), (0.180, 0.520), (0.160, 0.610), (0.130, 0.700), (0.100, 0.800), (0.070, 0.900), (0.040, 0.970), (0.0, 1.0)]
    corps = fuseau([(f_, r_) for r_, f_ in pts], L, 64)
    x, y, z = corps.v[:, 0], corps.v[:, 1], corps.v[:, 2]
    f = z / L
    th = np.arctan2(x, y)
    ecaille = (f > 0.20)                                                              # le museau et le cou sont en peau
    rang = z / 0.050
    k = np.floor(rang)
    frac = rang - k
    col = (th * 0.17 * (0.5 + 4.0 * np.interp(f, [p[1] for p in pts], [p[0] for p in pts])) / 0.050 + 0.5 * k)
    cadre = col - np.floor(col)
    # le relief : chaque tuile monte en pente douce puis retombe d'un coup sur la suivante
    pente = np.where(ecaille & (np.abs(th) < 2.45), 1.0 + 0.060 * frac, 1.0)
    corps.v[:, 0] *= pente
    corps.v[:, 1] *= pente
    t = np.tile(CREME, (len(z), 1))
    sur = ecaille & (np.abs(th) < 2.45)
    t[sur] = TUILE
    t[sur & (frac < 0.22)] = TUILE_BRUN                                                # le bord d'ombre sous la tuile
    t[sur & (frac > 0.78)] = DORE                                                      # le bout clair
    t[sur & ((cadre < 0.07) | (cadre > 0.93))] = TUILE_BRUN                            # les joints entre les écailles
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)
    a.tete = Vector(fil.cadre(0.10 * L)[0])

    # ----- les yeux minuscules sur la tête ; le nez ; les pattes : courtes, la peau crème, de grandes griffes -----
    c1, av1, nq1 = fil.cadre(0.12 * L)
    lat1 = np.cross(np.array(av1), np.array(nq1))
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("corps", Vector(c1), Vector(lat1 * c * 0.85 + np.array(nq1) * 0.40))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0120)
    c2, av2, nq2 = fil.cadre(0.012 * L)
    a.piece("nez", A.boule(1.0, 14, 8).etire(0.014, 0.016, 0.012), CHARBON, pos=tuple(np.array(c2) + np.array(av2) * 0.006), poil=False)
    for nom, x_, y_, av in (("av_G", 0.130, -0.260, -0.060), ("av_D", -0.130, -0.260, 0.020), ("ar_G", 0.130, 0.330, 0.0), ("ar_D", -0.130, 0.330, 0.0)):
        c = 1 if x_ > 0 else -1
        ch = [(x_ * 0.80, y_, 0.200), (x_ * 1.05, y_ + av * 0.5, 0.110), (x_ * 1.10, y_ + av, 0.030)]
        m = A.tube(A.courbe(propres(ch), 5), lambda t: 0.052 - 0.016 * t, 14)
        m.teinte = np.tile(CREME, (len(m.v), 1))
        a.piece("patte_" + nom, m, None)
        griffes = None
        for k_ in (-1, 0, 1):
            g = A.tour(A.profil([(0, 0), (0.010, 0.004), (0.007, 0.026), (0.003, 0.048), (0, 0.062)], 5), 10)
            g = g.pose((0, 0, 0), (-82, 0, 0)).pose((k_ * 0.026, -0.030, 0.0), (0, 0, k_ * 10))
            griffes = g if griffes is None else griffes + g
        a.piece("griffes_" + nom, griffes, CHARBON, pos=(x_ * 1.10, y_ + av - 0.030, 0.026), poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pangolin", styles.style_de("pangolin"), sys.modules[__name__]), "Pangolin")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py pangolin). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.188                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.738, 0.233)),
    ('tete', 'corps', (0.009, -0.538, 0.151)),
    ('patte_av_G', 'corps', (0.115, -0.269, 0.188)),
    ('patte_ar_G', 'corps', (0.117, 0.330, 0.188)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('griffes_av', 'patte_av', True), ('griffes_ar', 'patte_ar', True),
    ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('corps', 'corps'), ('oeil', 'tete'),
    ('nez', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'),
    ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
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
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.056 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.103), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
