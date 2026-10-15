"""Le diable de Tasmanie en peluche de magasin (4e dessin, repris d'une autre base : un quadrupède trapu à la façon de
la mouffette, pas un monstre à la bouche ouverte) : un petit fauve noir et ramassé, le dos arqué et la croupe basse, une
TÊTE énorme, large et lourde portée bas, le museau court et la gueule fermée, de petits yeux, des oreilles rondes qui
rougissent, de courtes pattes épaisses, une queue courte et grasse, et une barre blanche en travers de la poitrine. Il
avance la tête basse, un œil sur nous : il a l'air de mauvaise humeur, c'est son métier.

    python diable_de_tasmanie.py        fabrique la fiche art/apercus/animaux/diable_de_tasmanie.png (peluche de magasin, palier 4)
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


# le style B adoucit les couleurs (vers leur gris) : le noir reste noir, le blanc doit rester franc
CHARBON = np.array(M.hexa("#3a3638"))         # la dominante : charbon profond
BLANC = M.hexa("#fffaf2")                     # l'accent : la barre de la poitrine
CENDRE = np.array(M.hexa("#7a7478"))          # le dessous du museau, le dessous des pattes
OREILLE = M.hexa("#e0586a")                   # le dedans des oreilles : elles rougissent
NEZ = M.hexa("#b8606c")
LACET, PIQUE = 30.0, -6.0
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("diable_de_tasmanie")
    a.taille = 0.75

    # ----- le corps : un tonneau court et lourd, le dos arqué (le haut aux épaules), la croupe basse et large -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.320, 0.150), (0.170, 0.205), (0.000, 0.240), (-0.150, 0.250), (-0.250, 0.225))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.090), (0.16, 0.130), (0.46, 0.145), (0.76, 0.142), (0.93, 0.118), (0.985, 0.075), (1.0, 0.0)], L, 72)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.teinte = np.where((th > 2.5)[:, None], CENDRE, CHARBON)
    # la bande blanche du poitrail, PEINTE sur le corps (le patch cousu se perdait dans le poil) : un croissant d'un flanc à l'autre
    f_ = corps.v[:, 2] / L
    bande = (f_ > 0.80) & (f_ < 0.90) & (th > 0.9) & (th < 2.45)
    corps.teinte[bande] = BLANC
    a.piece("corps", corps.sculpte(fil.couche), None)
    # la barre blanche : une large bande en croissant en travers de la poitrine (devant, de flanc à flanc)

    # ----- le cou fort et la TÊTE : large, lourde, portée bas ; le museau court, la gueule fermée -----
    a.piece("cou", A.tube(A.courbe([(0.0, -0.200, 0.235), (0.0, -0.290, 0.225), (0.0, -0.350, 0.205)], 5), lambda t: 0.125 - 0.012 * t, 24), tuple(CHARBON))
    T = A.cadre(Vector((0.0, -0.400, 0.215)), Vector((0.50, -1.0, -0.22)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.082), (0.22, 0.118), (0.46, 0.114), (0.70, 0.094), (0.90, 0.074), (0.98, 0.048), (1.0, 0.0)], 0.290, 64, 0.005)
    tete.v[:, 0] *= 1.28                                                           # une grosse tête large
    tete.v[:, 1] *= 1.00
    tt = np.tile(CHARBON, (len(tete.v), 1))
    tt[(np.abs(np.arctan2(tete.v[:, 0], tete.v[:, 1])) > 2.3) & (tete.v[:, 2] > 0.12)] = CENDRE
    tete.teinte = tt
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.100)))
    a.piece("nez", A.boule(1.0, 24, 12).etire(0.034, 0.024, 0.022), NEZ, mat=T @ A.repere((0.0, 0.010, 0.182)), poil=False)
    a.tete = T @ Vector((0, 0.0, 0.140))
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.62, 0.50, 0.50))
        p, n = a.surface("tete", T @ Vector((0, 0.0, 0.020)), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0200)               # de vrais yeux noirs vivants, plus de disque gris
        # l'oreille : ronde, plantée haut sur le côté, le dedans qui rougit
        po, no = a.surface("tete", T @ Vector((0, 0.0, 0.0)), T3 @ Vector((c * 0.66, 0.72, -0.28)))
        face, dresse = T3 @ Vector((c * 0.55, 0.45, 0.70)), no + T3 @ Vector((0, 0.2, -0.9))
        E = A.cadre(po + no * 0.010, face, dresse)
        a.piece("oreille_" + nom, A.boule(1.0, 28, 14).etire(0.046, 0.052, 0.016), tuple(CHARBON), mat=E)
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).etire(0.030, 0.036, 0.008), OREILLE, mat=E @ A.repere((0, -0.002, 0.011)), poil=False)
    bouche = a.trace("tete", T @ Vector((0, 0.0, 0.110)), [T3 @ Vector(d) for d in ((0.30, -0.90, 0.30), (0.62, -0.72, 0.10), (0.84, -0.40, -0.02))], 0.004)
    a.broderie("bouche", A.courbe(propres(bouche), 4), 0.0028, tuple(CENDRE))

    # ----- les pattes : courtes, épaisses, l'épaule et la cuisse fondues dans le corps ; les postérieures plus coudées ;
    #       de larges pieds ronds -----
    def patte(pts, r0):
        ft = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.30, r0 * 0.84), (0.62, r0 * 0.66), (0.90, r0 * 0.60), (1.0, 0.0)], ft.long, 28, 0.006)
        m.teinte = np.tile(CHARBON, (len(m.v), 1))
        return m.sculpte(ft.couche)
    for nom, c in (("G", 1), ("D", -1)):
        av = [(c * 0.100, -0.170, 0.215), (c * 0.108, -0.190, 0.120), (c * 0.108, -0.200, 0.032)]
        a.piece("patte_av_" + nom, patte(av, 0.074), None)
        a.piece("pied_av_" + nom, A.boule(1.0, 24, 12).etire(0.054, 0.070, 0.030), tuple(CHARBON), pos=(c * 0.108, -0.222, 0.030))
        ar = [(c * 0.110, 0.200, 0.205), (c * 0.130, 0.150, 0.120), (c * 0.118, 0.215, 0.036)]
        a.piece("patte_ar_" + nom, patte(ar, 0.084), None)
        a.piece("pied_ar_" + nom, A.boule(1.0, 24, 12).etire(0.054, 0.078, 0.030), tuple(CHARBON), pos=(c * 0.118, 0.195, 0.030))
    # la queue : courte et grasse, qui se termine en pointe émoussée
    qf = K.Fil([(0.0, 0.290, 0.170), (0.0, 0.370, 0.160), (0.0, 0.450, 0.130), (0.020, 0.510, 0.090)], (1, 0, 0))
    queue = fuseau([(0.0, 0.066), (0.30, 0.060), (0.75, 0.044), (0.94, 0.028), (1.0, 0.0)], qf.long, 32, 0.006)
    queue.teinte = np.tile(CHARBON, (len(queue.v), 1))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("diable_de_tasmanie", styles.style_de("diable_de_tasmanie"), sys.modules[__name__]), "Diable de Tasmanie")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py diable_de_tasmanie). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.210                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.181, 0.228)),
    ('cou', 'corps', (-0.000, -0.189, 0.148)),
    ('tete', 'cou', (0.012, -0.301, 0.218)),
    ('oreille_G', 'tete', (0.059, -0.378, 0.282)),
    ('patte_av_G', 'corps', (0.101, -0.189, 0.207)),
    ('patte_ar_G', 'corps', (0.115, 0.153, 0.213)),
    ('queue', 'corps', (0.000, 0.302, 0.191)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('poitrine', 'corps'),
    ('oreille', 'oreille', True), ('pied_av', 'patte_av', True), ('pied_ar', 'patte_ar', True), ('amande', 'tete'),
    ('dedans', 'oreille', True), ('bouche', 'tete'), ('corps', 'corps'), ('queue', 'queue'), ('tete', 'tete'),
    ('oeil', 'tete'), ('cou', 'cou'), ('nez', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.063 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.116), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
