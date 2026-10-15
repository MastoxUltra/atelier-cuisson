"""Le lièvre arctique en peluche cousue main (2e dessin : un vrai LIÈVRE, plus la boule lilas) : le lilas pâle de la
robe d'été, le ventre et le pompon de la queue blancs ; assis HAUT sur l'arrière-train, la croupe et les cuisses
énormes, les très longs pieds arrière à plat devant lui, le dos qui monte en pente vers des épaules étroites, de fines
pattes avant, une petite tête de lièvre aux yeux sombres, et deux LONGUES oreilles dressées, bien plus longues que la
tête, noires au bout. Il guette : il est prêt à bondir, un œil sur nous.

    python lievre_arctique.py        fabrique la fiche art/apercus/animaux/lievre_arctique.png (cousu main, palier 2)
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


LILAS = np.array(M.hexa("#e1d6f8"))           # la dominante : lilas pâle (le poil la dore : on la prend nettement plus claire)
OMBRE = np.array(M.hexa("#c7b8ec"))           # le dos, le dessous des pattes, un ton plus bas
CHARBON = np.array(M.hexa("#2d2831"))         # le bout des oreilles (l'accent), la truffe
NEIGE = np.array(M.hexa("#fffaf4"))           # le ventre, le pompon, le museau
JAUNE = M.hexa("#e8d070")                     # les yeux
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
    a = K.Animal("lievre_arctique")
    a.taille = 0.80

    # ----- le corps : un tronc qui monte en pente de la croupe basse aux épaules étroites ; le dos plus sombre, le ventre blanc -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.200, 0.095), (0.110, 0.200), (0.000, 0.300), (-0.070, 0.370))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.05, 0.100), (0.22, 0.150), (0.50, 0.140), (0.80, 0.105), (0.96, 0.070), (1.0, 0.0)], L, 64)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.teinte = np.where((th > 2.3)[:, None], NEIGE, np.where((th < 1.0)[:, None], OMBRE, LILAS))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- les cuisses : énormes, fondues dans la croupe ; les longs pieds arrière, à plat devant elles -----
    for nom, c in (("G", 1), ("D", -1)):
        cu = A.boule(1.0, 36, 18)
        cu.teinte = np.tile(LILAS, (len(cu.v), 1))
        a.piece("cuisse_" + nom, cu.etire(0.074, 0.130, 0.120), None, mat=A.cadre(Vector((c * 0.108, 0.135, 0.150)), Vector((c * 0.10, -0.90, 0.30)), (0, 0, 1)))
        pd = A.boule(1.0, 24, 12)
        pd.teinte = np.where((pd.v[:, 2] < 0.0)[:, None], tuple(OMBRE), tuple(LILAS))
        a.piece("pied_ar_" + nom, pd.etire(0.040, 0.170, 0.030), None, pos=(c * 0.112, 0.020, 0.030), rot=(0, 0, c * 6))

    # ----- les pattes avant : fines, droites, serrées sous le menton, les petites mains blanches -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.050, -0.045, 0.300), (c * 0.054, -0.085, 0.160), (c * 0.054, -0.100, 0.034)]
        a.piece("patte_av_" + nom, A.tube(A.courbe(propres(ch), 5), lambda t: 0.028 - 0.010 * t, 12), tuple(LILAS))
        a.piece("main_" + nom, A.boule(1.0, 16, 8).etire(0.024, 0.036, 0.018), tuple(NEIGE), pos=(c * 0.054, -0.112, 0.020))

    # ----- la tête : petite, le museau fin et blanc, les joues pleines ; haute, tournée vers nous -----
    T = A.cadre(Vector((0.0, -0.120, 0.420)), Vector((0.38, -1.0, 0.06)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.08, 0.062), (0.30, 0.078), (0.58, 0.068), (0.84, 0.050), (0.97, 0.034), (1.0, 0.0)], 0.180, 48, 0.004)
    tete.teinte = np.where((tete.v[:, 2] > 0.60 * 0.180)[:, None], tuple(NEIGE), tuple(LILAS))
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.060)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.016, 0.012, 0.012), tuple(CHARBON), mat=T @ A.repere((0, 0.004, 0.116)), poil=False)
    a.tete = T @ Vector((0, 0.0, 0.080))
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.80, 0.32, 0.30))
        a.rustine("iris_" + nom, "tete", T.to_translation(), regard, 0.17, JAUNE, 0.003, 0)
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0155)
        # l'oreille : LONGUE, étroite, dressée un peu en arrière, le bout noir
        po = A.profil([(0, 0), (0.036, 0.010), (0.040, 0.060), (0.034, 0.130), (0.024, 0.190), (0.010, 0.228), (0, 0.240)], 6)
        vers = (T3 @ Vector((c * 0.26, 0.94, -0.18))).normalized()
        E = A.cadre(T @ Vector((c * 0.040, 0.050, -0.030)) - vers * 0.008, vers, T3 @ Vector((c * 0.2, 0.0, 1.0)))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 36).etire(1.0, 0.30, 1.0), [(0.190, tuple(LILAS)), (9, tuple(CHARBON))]), None, mat=E)
        a.piece("pavillon_" + nom, A.tour(po, 28).etire(0.58, 0.26, 0.84).pose((0, 0.008, 0.010)), M.hexa("#f2c6d8"), mat=E, poil=False)

    # ----- le pompon : une petite boule blanche à la croupe -----
    q = A.boule(1.0, 20, 10)
    q.teinte = np.tile(NEIGE, (len(q.v), 1))
    a.piece("queue", q.etire(0.040, 0.040, 0.040), None, pos=(0.0, 0.232, 0.130))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lievre_arctique", styles.style_de("lievre_arctique"), sys.modules[__name__]), "Lièvre arctique")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py lievre_arctique). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.277                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.172, 0.227)),
    ('tete', 'corps', (0.006, -0.081, 0.368)),
    ('oreille_G', 'tete', (0.020, -0.084, 0.469)),
    ('patte_ar_G', 'corps', (0.107, 0.138, 0.269)),
    ('patte_av_G', 'corps', (0.050, -0.053, 0.286)),
    ('queue', 'corps', (0.001, 0.216, 0.166)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('pavillon', 'oreille', True),
    ('pied_ar', 'patte_av', True), ('oreille', 'oreille', True), ('cuisse', 'patte_ar', True), ('corps', 'corps'),
    ('queue', 'queue'), ('tete', 'tete'), ('main', 'patte_av', True), ('iris', 'tete'), ('oeil', 'tete'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.083 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.153), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
