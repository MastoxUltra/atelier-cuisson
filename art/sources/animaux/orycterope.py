"""L'oryctérope en peluche de velours ras (2e dessin, d'après photos : plus de tube rose sur une armure) : le cochon de
terre, d'un gris sable rosé aux poils clairsemés ; le dos très arqué, l'arrière-train haut et lourd ; une tête longue qui
s'effile en un museau tubulaire à la truffe plate, de très longues oreilles dressées qui se rejoignent presque au sommet,
les yeux petits, une grosse queue épaisse à la base qui s'amincit, de fortes pattes aux griffes de pelle. Le museau au
ras du sol, le dos en arc, les oreilles tournées vers nous : il flaire la termitière.

    python orycterope.py        fabrique la fiche art/apercus/animaux/orycterope.png (velours ras, palier 3)
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


SABLE = np.array(M.hexa("#e6cfc0"))           # la dominante : gris sable rosé (le poil le fonce)
ROSE = np.array(M.hexa("#f0c4bc"))            # le museau, le dedans des oreilles, le ventre
FONCE = np.array(M.hexa("#b09890"))           # le dessus de la queue, le bas des pattes
GRIFFE = M.hexa("#d8c8b8")
CHARBON = M.hexa("#3a3234")
PAS = 0.008
LACET = 24.0


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
    a = K.Animal("orycterope")
    a.taille = 1.40

    # ----- le corps, le cou, la tête et le museau d'une pièce, couchés le long d'une courbe : l'arrière-train haut, le dos
    #       qui s'arque, les épaules plus basses, la tête qui descend en un long museau tubulaire -----
    chemin = [(0.0, y, z) for y, z in ((0.520, 0.560), (0.320, 0.640), (0.080, 0.640), (-0.160, 0.560), (-0.400, 0.450),
                                       (-0.620, 0.340), (-0.800, 0.250), (-0.950, 0.200))]
    fil = K.Fil(chemin, (1, 0, 0))
    L = fil.long
    pts = [(0.0, 0.0), (0.02, 0.140), (0.10, 0.210), (0.24, 0.236), (0.40, 0.215), (0.52, 0.170), (0.60, 0.130), (0.68, 0.110),
           (0.76, 0.088), (0.84, 0.070), (0.92, 0.056), (0.975, 0.050), (1.0, 0.0)]
    corps = fuseau(pts, L, 64)
    x, y, z = corps.v[:, 0], corps.v[:, 1], corps.v[:, 2]
    f = z / L
    th = np.abs(np.arctan2(x, y))
    t = np.tile(SABLE, (len(z), 1))
    t[(th > 2.3)] = ROSE
    t[f > 0.84] = ROSE                                                                 # le museau
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)
    a.tete = Vector(fil.cadre(0.84 * L)[0])

    # ----- la truffe plate, les narines ; les yeux petits ; les LONGUES oreilles dressées -----
    c1, av1, nq1 = fil.cadre(0.995 * L)
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.044, 0.020, 0.044), tuple(ROSE), pos=tuple(np.array(c1) + np.array(av1) * 0.006), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("narine_" + nom, A.boule(1.0, 12, 6).etire(0.010, 0.008, 0.010), CHARBON,
                pos=tuple(np.array(c1) + np.array(av1) * 0.026 + np.array([c * 0.016, 0.0, 0.0])), poil=False)
        c2, av2, nq2 = fil.cadre(0.700 * L)
        p, n = a.surface("corps", Vector(c2), Vector(np.array([c * 0.88, 0.0, 0.0]) + np.array(nq2) * 0.30 - np.array(av2) * 0.20))
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0150)
        c3, av3, nq3 = fil.cadre(0.640 * L)
        po = A.profil([(0, 0), (0.036, 0.010), (0.044, 0.060), (0.040, 0.130), (0.030, 0.200), (0.014, 0.248), (0, 0.268)], 6)
        vers = (Vector(nq3) * 0.90 + Vector((c * 0.40, 0.0, 0.0)) - Vector(av3) * 0.10).normalized()
        E = A.cadre(Vector(c3) + Vector(nq3) * 0.100 + Vector((c * 0.040, 0.0, 0.0)), vers, Vector(av3))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 32).etire(1.0, 0.34, 1.0), [(0.100, tuple(SABLE)), (9, tuple(SABLE))]), None, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 24).etire(0.58, 0.28, 0.86).pose((0, 0.008, 0.010)), tuple(ROSE), mat=E, poil=False)

    # ----- les pattes : fortes, les arrière plus longues et coudées, les avant plus courtes aux grandes griffes de pelle -----
    def patte(pts_, r0):
        ft = K.Fil(pts_, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.35, r0 * 0.78), (0.70, r0 * 0.56), (0.94, r0 * 0.52), (1.0, 0.0)], ft.long, 32, 0.008)
        m.teinte = np.where((m.v[:, 2] > 0.60 * ft.long)[:, None], tuple(FONCE), tuple(SABLE))
        return m.sculpte(ft.couche)
    for nom, pts_, r0 in (("av_G", [(0.110, -0.300, 0.440), (0.120, -0.330, 0.250), (0.120, -0.360, 0.040)], 0.090),
                          ("av_D", [(-0.110, -0.300, 0.440), (-0.120, -0.330, 0.250), (-0.120, -0.360, 0.040)], 0.090),
                          ("ar_G", [(0.140, 0.420, 0.540), (0.170, 0.360, 0.330), (0.150, 0.440, 0.040)], 0.110),
                          ("ar_D", [(-0.140, 0.420, 0.540), (-0.170, 0.360, 0.330), (-0.150, 0.440, 0.040)], 0.110)):
        a.piece("patte_" + nom, patte(pts_, r0), None)
        x_, y_, _z = pts_[-1]
        griffes = None
        for k in (-1, 0, 1):
            g = A.tour(A.profil([(0, 0), (0.014, 0.004), (0.010, 0.030), (0.004, 0.056), (0, 0.070)], 5), 10)
            g = g.pose((0, 0, 0), (-84, 0, 0)).pose((k * 0.030, -0.040, 0.0), (0, 0, k * 10))
            griffes = g if griffes is None else griffes + g
        a.piece("griffes_" + nom, griffes, GRIFFE, pos=(x_, y_ - 0.030, 0.026), poil=False)
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(r0 * 0.70, r0 * 0.90, 0.030), tuple(FONCE), pos=(x_, y_ + 0.010, 0.030))

    # ----- la queue : très épaisse à la base, qui s'amincit en pointe -----
    qf = K.Fil([(0.0, 0.540, 0.540), (0.0, 0.700, 0.420), (0.0, 0.820, 0.250), (0.020, 0.860, 0.110)], (1, 0, 0))
    queue = fuseau([(0.0, 0.110), (0.30, 0.090), (0.70, 0.050), (0.96, 0.020), (1.0, 0.0)], qf.long, 36, 0.008)
    queue.teinte = np.where((queue.v[:, 1] > 0.0)[:, None], tuple(FONCE), tuple(SABLE))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("orycterope", styles.style_de("orycterope"), sys.modules[__name__]), "Oryctérope")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py orycterope). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.472                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.164, 0.520)),
    ('tete', 'corps', (0.000, -0.500, 0.440)),
    ('oreille_G', 'tete', (0.042, -0.487, 0.528)),
    ('patte_av_G', 'corps', (0.111, -0.316, 0.420)),
    ('patte_ar_G', 'corps', (0.145, 0.380, 0.524)),
    ('queue', 'corps', (-0.000, 0.533, 0.480)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('griffes_av', 'patte_av', True), ('griffes_ar', 'patte_ar', True),
    ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('pavillon', 'oreille', True),
    ('oreille', 'oreille', True), ('pied_av', 'patte_av', True), ('pied_ar', 'patte_ar', True), ('truffe', 'corps'),
    ('narine', 'tete'), ('corps', 'corps'), ('queue', 'queue'), ('oeil', 'tete'), ('paupiere_0', 'paupiere_0'),
    ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.142 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.260), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
