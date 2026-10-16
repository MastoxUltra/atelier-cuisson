"""Le cobra en peluche de velours ras : un tan sable, lové sur le sol en une large spirale, le cou dressé au centre,
et le CAPUCHON ouvert : un grand disque aplati, large comme trois fois le cou, rayé de brun en éventail, tourné vers
nous ; au-dessus, la petite tête plate et lisse, les yeux ronds, la langue fourchue qui goûte l'air. L'avertissement :
il ne bouge pas, il dit juste « je suis là ».

    python cobra.py        fabrique la fiche art/apercus/animaux/cobra.png (velours ras, palier 3)
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


TAN = np.array(M.hexa("#e0c080"))             # la dominante : tan sable (le poil le fonce)
TAN_BAS = np.array(M.hexa("#c09c58"))         # les chevrons du corps, un ton plus bas
BRUN = np.array(M.hexa("#7a5630"))            # l'accent : les rayures du capuchon
CREME = np.array(M.hexa("#fff0c8"))           # la gorge, le dessous de la tête
ROSE = M.hexa("#d8506a")                      # la langue
NOIR = M.hexa("#2e2826")
OR = M.hexa("#e8b030")                        # le fond de l'œil
LACET, PIQUE = 22.0, 12.0                     # la tête tournée un peu vers nous, penchée


def rayon(t):
    """Le rayon du corps le long du chemin (0 = le bout de la queue, 1 = la nuque)."""
    queue = max(0.0, (0.26 - t) / 0.26) ** 1.4
    cou = min(1.0, max(0.0, (t - 0.70) / 0.26))
    return 0.046 - 0.034 * queue - 0.016 * cou * cou * (3 - 2 * cou)


def chemin_du_corps():
    """La spirale posée au sol (une grosse boucle et demie qui se resserre et monte un peu en tournant vers le centre),
    puis le cou qui s'élève tout droit au milieu et se penche vers l'avant sous la tête."""
    spirale = []
    n = 90
    for k in range(n + 1):
        u = k / n
        ang = -math.pi / 2 - 2 * math.pi * 1.6 * (1.0 - u)
        r = 0.27 - 0.21 * u
        spirale.append((r * math.cos(ang), r * math.sin(ang), 0.044 + 0.110 * u))
    cou = [spirale[-3], spirale[-2], spirale[-1], (0.0, -0.050, 0.230), (0.0, -0.034, 0.310), (0.0, -0.030, 0.400),
           (0.0, -0.040, 0.470), (0.0, -0.075, 0.510), (0.0, -0.120, 0.520)]
    lisse = [tuple(q) for q in A.courbe(propres(cou), 6)]
    return spirale[:-3] + lisse


def construire():
    a = K.Animal("cobra")
    a.taille = 1.80

    # ----- le corps : un long boudin peint de chevrons un ton plus bas, lové en spirale, le cou dressé -----
    ch = np.asarray(chemin_du_corps(), float)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(ch, axis=0), axis=1))])
    n = max(16, int(fait[-1] / 0.010))
    u = np.linspace(0.0, 1.0, n)
    ch = np.stack([np.interp(u * fait[-1], fait, ch[:, k]) for k in range(3)], axis=1)
    cotes = 20
    corps = A.tube(ch, rayon, cotes)
    teinte = np.tile(TAN, (len(corps.v), 1))
    s = u * fait[-1]
    chevron = ((s % 0.115) < 0.040) & (s > 0.10) & (ch[:, 2] < 0.28)
    for i in np.nonzero(chevron)[0]:
        teinte[i * cotes:(i + 1) * cotes] = TAN_BAS
    corps.teinte = teinte
    a.piece("corps", corps, None)
    fin = Vector(ch[-1])

    # ----- le capuchon : un grand disque aplati, plus large en haut, rayé de brun en éventail, qui coiffe le cou -----
    cap = A.boule(1.0, 96, 48)
    x, y, z = cap.v[:, 0], cap.v[:, 1], cap.v[:, 2]
    ang = np.arctan2(x, 1.25 - z)
    sombre = (np.sin(ang * 17.0) > 0.30) & (np.hypot(x, z) < 0.88)
    t = np.tile(TAN, (len(z), 1))
    t[sombre] = BRUN
    t[np.hypot(x, z) >= 0.88] = TAN_BAS                                           # le bord du capuchon
    cap.teinte = t

    def evase(v):
        s = v.copy()
        s[:, 0] *= 0.26 + 0.74 * K.lisse((v[:, 2] + 0.75) / 1.5)
        return s
    a.piece("capuchon", cap.sculpte(evase).etire(0.125, 0.040, 0.180), None, mat=A.repere((0.0, -0.034, 0.310), (-4, 0, 0)))

    # ----- la tête : plate, ovale, le museau rond ; les yeux ronds de côté ; les narines ; la langue fourchue -----
    lac, pq = math.radians(LACET), math.radians(PIQUE)
    dirige = Vector((math.sin(lac) * math.cos(pq), -math.cos(lac) * math.cos(pq), -math.sin(pq))).normalized()
    T = A.cadre(fin + dirige * 0.040, dirige, Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.where((tete.v[:, 1] < -0.15)[:, None], CREME, TAN)
    a.piece("tete", tete.etire(0.044, 0.027, 0.064), None, mat=T)
    a.tete = T @ Vector((0, 0.0, 0.050))
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.86, 0.42, 0.16))
        a.rustine("fond_" + nom, "tete", T.to_translation(), regard, 0.24, OR, 0.0025, 0)
        p, n_ = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n_ * 0.003, n_, 0.0092)
        a.piece("narine_" + nom, A.boule(1.0, 12, 6).etire(0.006, 0.005, 0.004), NOIR, mat=A.cadre(T @ Vector((c * 0.014, 0.022, 0.058)), T3 @ Vector((c * 0.2, 0.9, 0.3))), poil=False)
    bout = T @ Vector((0.0, -0.004, 0.062))
    base = [tuple(bout), tuple(bout + T3 @ Vector((0, -0.004, 0.040))), tuple(bout + T3 @ Vector((0, 0.0, 0.080)))]
    # (la langue fourchue, qui se lisait comme une boule rose de près, est retirée : 16/10)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("cobra", styles.style_de("cobra"), sys.modules[__name__]), "Cobra")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py cobra). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.285                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.152, 0.285)),
    ('tete', 'corps', (0.008, -0.125, 0.496)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('capuchon', 'corps'), ('fourche', 'tete'), ('narine', 'tete'), ('langue', 'tete'),
    ('corps', 'corps'), ('tete', 'tete'), ('fond', 'tete'), ('oeil', 'tete'), ('paupiere_0', 'paupiere_0'),
    ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.086 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.157), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.add('tete', rot=(32, 4, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
