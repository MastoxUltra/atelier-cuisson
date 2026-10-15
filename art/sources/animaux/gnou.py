"""Le gnou en peluche de velours ras : un gris argent bleuté, la face allongée et noire, une barbe et une crinière
noires hérissées, des cornes en crochets qui partent sur le côté puis se relèvent, le garrot haut et la croupe basse, le
cou épais rayé de fines bandes sombres, de longues jambes fines, la queue en crin noir. Le clown triste de la plaine :
la tête baissée en avant, les cornes pointées devant lui, un œil par en dessous, un antérieur en avant : il va faire
semblant de charger.

    python gnou.py        fabrique la fiche art/apercus/animaux/gnou.png (velours ras, palier 3)
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


ARGENT = np.array(M.hexa("#c4ccdc"))          # la dominante : gris argent bleuté (le poil le fonce : on le prend clair)
BANDE = np.array(M.hexa("#6a7088"))           # les bandes du cou et des épaules
NOIR = np.array(M.hexa("#2e2c34"))            # le museau, la barbe, la crinière, la queue
CORNE = M.hexa("#d0c4a4")
OEIL = M.hexa("#c08a3a")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("gnou")
    a.taille = 2.00

    # ----- le corps : le garrot haut, la croupe basse, le poitrail profond ; des bandes sombres sur l'avant -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.460, 0.700), (0.280, 0.760), (0.020, 0.830), (-0.200, 0.900), (-0.340, 0.930))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.110), (0.15, 0.170), (0.45, 0.185), (0.75, 0.210), (0.92, 0.200), (1.0, 0.0)], L, 72)
    z = corps.v[:, 2]
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(ARGENT, (len(z), 1))
    bande = (((z - 0.55 * L) / 0.062) % 1.0 < 0.34) & (z > 0.55 * L) & (th < 2.2 * (1.0 - 0.35 * (z - 0.55 * L) / (0.45 * L)))
    t[bande] = BANDE
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)
    # la crinière noire : une brosse hérissée de la nuque au garrot
    crin = None
    for i, f in enumerate(np.linspace(0.45, 0.99, 14)):
        c_, av, nq = fil.cadre(f * L)
        r = float(np.interp(f, [0.0, 0.04, 0.15, 0.45, 0.75, 0.92, 1.0], [0.0, 0.110, 0.170, 0.185, 0.210, 0.200, 0.0]))
        e = A.boule(1.0, 10, 6).etire(0.014, 0.026, 0.066).pose(tuple(c_ + nq * (r * 0.98 + 0.028)))
        crin = e if crin is None else crin + e
    a.piece("criniere", crin, tuple(NOIR), poil=False)

    # ----- le cou et la tête : un cou épais, la tête basse tournée vers nous ; une face longue et noire, la barbe ; les cornes -----
    a.piece("cou", A.tube(A.courbe([(0.0, -0.250, 0.920), (0.0, -0.380, 0.880), (0.0, -0.470, 0.800)], 5), lambda t: 0.170 - 0.045 * t, 22), tuple(ARGENT))
    H = A.cadre(Vector((0.0, -0.560, 0.700)), Vector((0.34, -1.0, -0.46)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.100), (0.22, 0.130), (0.46, 0.112), (0.70, 0.100), (0.92, 0.104), (1.0, 0.0)], 0.520, 56, 0.007)
    tete.teinte = np.tile(NOIR, (len(tete.v), 1))
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0.020, -0.130)))
    a.piece("barbe", A.boule(1.0, 24, 12).etire(0.060, 0.050, 0.130), tuple(NOIR), mat=H @ A.repere((0, -0.060, -0.180), (-14, 0, 0)))
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.060, 0.036, 0.030), tuple(NOIR * 0.7), mat=H @ A.repere((0, 0.028, 0.392)), poil=False)
    a.tete = H @ Vector((0, 0.020, 0.250))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.84, 0.30, 0.0))
        a.rustine("iris_" + nom, "tete", H @ Vector((0, 0.020, 0.060)), regard, 0.17, OEIL, 0.003, 0)
        p, n = a.surface("tete", H @ Vector((0, 0.020, 0.060)), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0170)
        # la corne : part sur le côté, descend, puis se relève en crochet
        ch = [H @ Vector(q) for q in ((c * 0.070, 0.090, -0.080), (c * 0.180, 0.060, -0.100), (c * 0.250, 0.060, -0.040), (c * 0.250, 0.060, 0.080), (c * 0.210, 0.050, 0.150))]
        a.piece("corne_" + nom, A.tube(A.courbe(propres(ch), 6), lambda t: 0.034 - 0.026 * t, 14), CORNE, poil=False)
        po = A.profil([(0, 0), (0.034, 0.008), (0.042, 0.034), (0.032, 0.062), (0.012, 0.078), (0, 0.084)], 5)
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.38, 1.0), tuple(ARGENT),
                mat=A.cadre(H @ Vector((c * 0.120, 0.150, -0.140)), H3 @ Vector((c * 0.90, 0.30, 0.10)), H3 @ Vector((c * 0.3, -0.9, 0.0))))

    # ----- les jambes : fines et longues, le genou marqué, les sabots noirs ; l'antérieur gauche avancé -----
    def jambe(pts, r0):
        ft = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.40, r0 * 0.55), (0.50, r0 * 0.66), (0.60, r0 * 0.46), (0.94, r0 * 0.42), (1.0, 0.0)], ft.long, 28, 0.008)
        m.teinte = np.tile(ARGENT, (len(m.v), 1))
        return m.sculpte(ft.couche)
    for nom, pts, r0 in (("av_D", [(-0.100, -0.250, 0.860), (-0.108, -0.250, 0.560), (-0.108, -0.240, 0.300), (-0.108, -0.250, 0.040)], 0.060),
                         ("ar_G", [(0.110, 0.380, 0.700), (0.125, 0.330, 0.480), (0.125, 0.400, 0.280), (0.125, 0.390, 0.040)], 0.068),
                         ("ar_D", [(-0.110, 0.380, 0.700), (-0.125, 0.330, 0.480), (-0.125, 0.400, 0.280), (-0.125, 0.390, 0.040)], 0.068),
                         ("av_G", [(0.100, -0.250, 0.860), (0.108, -0.290, 0.580), (0.108, -0.400, 0.340), (0.108, -0.440, 0.040)], 0.060)):
        a.piece("jambe_" + nom, jambe(pts, r0), None)
        a.piece("sabot_" + nom, A.boule(1.0, 20, 10).etire(0.040, 0.054, 0.030), tuple(NOIR), pos=(pts[-1][0], pts[-1][1] - 0.012, 0.028), poil=False)
    chemin = [(0.0, 0.480, 0.760), (0.0, 0.580, 0.680), (0.0, 0.620, 0.460), (0.010, 0.600, 0.230)]
    a.piece("queue", K.tube_peint(A.courbe(chemin, 6), lambda t: 0.020 + 0.034 * t, [(1, tuple(NOIR))], 14), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("gnou", styles.style_de("gnou"), sys.modules[__name__]), "Gnou")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py gnou). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.779                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.115, 0.868)),
    ('cou', 'corps', (0.008, -0.217, 0.793)),
    ('tete', 'cou', (0.005, -0.478, 0.790)),
    ('oreille_G', 'tete', (0.115, -0.483, 0.882)),
    ('patte_av_D', 'corps', (-0.101, -0.253, 0.830)),
    ('patte_ar_G', 'corps', (0.112, 0.359, 0.678)),
    ('patte_av_G', 'corps', (0.101, -0.256, 0.830)),
    ('queue', 'corps', (-0.000, 0.487, 0.754)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('jambe_av', 'patte_av', True), ('jambe_ar', 'patte_ar', True), ('criniere', 'corps'),
    ('sabot_av', 'patte_av', True), ('sabot_ar', 'patte_ar', True), ('oreille', 'oreille', True), ('truffe', 'corps'),
    ('corps', 'corps'), ('queue', 'queue'), ('barbe', 'tete'), ('corne', 'tete'), ('tete', 'tete'), ('iris', 'tete'),
    ('oeil', 'tete'), ('cou', 'cou'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
    ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('cou', rot=(2 * r, 0, 8 * g - 6 * d))
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
    p.add('cou', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('tete', rot=(3 - 2 * onde(t, 2, -0.2), -2 * c, -2 * s))
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
    p.add('cou', rot=(34 * bas + 4 * coups, 0, 5 * leve))
    p.add('tete', rot=(18 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.234 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.429), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
