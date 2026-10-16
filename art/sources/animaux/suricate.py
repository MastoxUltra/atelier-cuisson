"""Le suricate en peluche cousue main (2e dessin, d'après photos : plus de nounours) : un fauve sable, des rayures
sombres en travers du dos, un ventre nu et sombre, un corps mince et droit ; une petite tête en COIN, le museau pointu
terminé d'un nez noir, de grandes TACHES NOIRES autour des yeux, de petites oreilles en croissant plantées bas sur les
côtés ; des bras fins, de longs pieds étroits, une queue fine à bout noir. La sentinelle : debout sur ses pattes arrière
et sa queue (un trépied), le torse droit, les mains sur le ventre, la tête haute tournée vers nous, l'œil grand ouvert.

    python suricate.py        fabrique la fiche art/apercus/animaux/suricate.png (cousu main, palier 2)
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


FAUVE = np.array(M.hexa("#f0cc90"))           # la dominante : fauve sable (le poil le fonce)
CLAIR = np.array(M.hexa("#fff0d4"))           # la gorge, le dessous du museau
RAYURE = np.array(M.hexa("#8a6040"))          # l'accent : les rayures du dos
NOIR = np.array(M.hexa("#2e2826"))            # les taches des yeux, les oreilles, le bout de la queue
VENTRE = np.array(M.hexa("#b89480"))          # le ventre nu, plus sombre
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=48, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("suricate")
    a.taille = 0.55

    # ----- le corps : un tronc mince et droit, un peu penché en arrière, le dos rayé, le ventre nu et sombre devant -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.060, 0.080), (0.045, 0.200), (0.020, 0.340), (-0.010, 0.460))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.05, 0.070), (0.20, 0.098), (0.55, 0.086), (0.86, 0.066), (1.0, 0.0)], L, 52)
    z = corps.v[:, 2]
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(FAUVE, (len(z), 1))
    t[(((z - 0.20 * L) / 0.060) % 1.0 < 0.34) & (th < 1.6) & (z > 0.18 * L) & (z < 0.85 * L)] = RAYURE
    t[(th > 2.3) & (z > 0.10 * L) & (z < 0.82 * L)] = VENTRE
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- la tête : un COIN mince, le front plat, le museau pointu et le nez noir ; les grandes taches noires autour des
    #       yeux ; de petites oreilles en croissant, plantées bas sur les côtés -----
    # le cou : un tube qui monte du haut du tronc et ENTRE dans la tête (plus de tête flottante)
    a.piece("cou", A.tube(A.courbe([(0.0, 0.030, 0.350), (0.0, 0.005, 0.455), (0.0, -0.022, 0.530)], 5), lambda t: 0.052 - 0.006 * t, 20), tuple(FAUVE))
    H = A.cadre(Vector((0.0, -0.030, 0.545)), Vector((0.36, -1.0, 0.04)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.10, 0.052), (0.34, 0.060), (0.62, 0.042), (0.86, 0.026), (0.97, 0.017), (1.0, 0.0)], 0.210, 40, 0.005)
    tete.v[:, 0] *= 0.82
    tete.teinte = np.where((np.abs(np.arctan2(tete.v[:, 0], tete.v[:, 1])) > 2.3)[:, None] | (tete.v[:, 2] > 0.74 * 0.210)[:, None], tuple(CLAIR), tuple(FAUVE))
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0, -0.045)))
    a.piece("nez", A.boule(1.0, 16, 8).etire(0.013, 0.011, 0.012), tuple(NOIR), mat=H @ A.repere((0, 0.004, 0.166)), poil=False)
    a.tete = H @ Vector((0, 0.0, 0.110))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.34, 0.30, 0.88))                         # sur l'avant de la tête : les deux yeux se voient de face
        a.rustine("tache_" + nom, "tete", H.to_translation(), regard, 0.32, tuple(RAYURE), 0.003, 0)       # un cerne brun (plus noir) : l'œil noir s'y lit
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.005, n, 0.0270)
        po = A.profil([(0, 0), (0.016, 0.006), (0.021, 0.020), (0.016, 0.034), (0.006, 0.042), (0, 0.046)], 5)
        a.piece("oreille_" + nom, A.tour(po, 20).etire(1.0, 0.40, 1.0), tuple(RAYURE),
                mat=A.cadre(H @ Vector((c * 0.040, 0.030, -0.036)), H3 @ Vector((c * 0.50, 0.84, 0.12)), H3 @ Vector((c * 0.3, -0.5, 0.8))))   # plantée sur le crâne, brune : plus de boule noire flottante

    # ----- les bras fins, les mains jointes sur le ventre ; les cuisses, de LONGS pieds étroits ; la queue : le troisième pied -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.072, 0.004, 0.400), (c * 0.092, -0.030, 0.330), (c * 0.058, -0.066, 0.296), (c * 0.026, -0.070, 0.306)]
        m = A.tube(A.courbe(propres(ch), 5), lambda t: 0.016 - 0.005 * t, 12)
        m.teinte = np.tile(FAUVE, (len(m.v), 1))
        a.piece("bras_" + nom, m, None)
        a.piece("main_" + nom, A.boule(1.0, 16, 8).etire(0.014, 0.020, 0.012), tuple(NOIR), pos=ch[-1])
        a.piece("cuisse_" + nom, A.boule(1.0, 24, 12).etire(0.040, 0.066, 0.056), tuple(FAUVE), pos=(c * 0.062, 0.040, 0.082))
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.020, 0.100, 0.014), tuple(FAUVE), pos=(c * 0.066, -0.030, 0.016), rot=(0, 0, c * 6))
        a.piece("orteils_" + nom, A.boule(1.0, 16, 8).etire(0.016, 0.034, 0.010), tuple(NOIR), pos=(c * 0.070, -0.118, 0.012), rot=(0, 0, c * 6), poil=False)
    chemin = [(0.0, 0.090, 0.100), (0.0, 0.180, 0.054), (0.0, 0.260, 0.032), (0.030, 0.330, 0.024)]
    a.piece("queue", K.tube_peint(A.courbe(propres(chemin), 6), lambda t: 0.028 - 0.016 * t, [(0.80, tuple(FAUVE)), (1, tuple(NOIR))], 12), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("suricate", styles.style_de("suricate"), sys.modules[__name__]), "Suricate")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py suricate). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.261                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.086, 0.155)),
    ('tete', 'corps', (0.004, -0.032, 0.494)),
    ('oreille_G', 'tete', (0.047, 0.011, 0.565)),
    ('patte_av_G', 'corps', (0.077, -0.003, 0.387)),
    ('patte_ar_G', 'corps', (0.064, 0.047, 0.136)),
    ('queue', 'corps', (0.001, 0.109, 0.114)),
]

PORTEURS = [
    ('cou', 'corps'),
    ('oeil_reflet', 'tete'), ('oreille', 'oreille', True), ('orteils', 'patte_av', True),
    ('cuisse', 'patte_ar', True), ('corps', 'corps'), ('queue', 'queue'), ('tache', 'corps'), ('tete', 'tete'),
    ('bras', 'patte_av', True), ('main', 'patte_av', True), ('oeil', 'tete'), ('pied', 'patte_av', True),
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
    pas = 18.0
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
    p.add('corps', rot=(34 * bas + 3 * coups, 0, 0))
    p.paire('patte_av', rot=(-30 * bas, 0, 0))
    p.add('tete', rot=(16 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.078 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.02), rot=(36, 0, 6), ech=(1 + 0.010 * r, 1, 1 + 0.020 * r))
    p.paire('patte_av', rot=(-30, 0, 0))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
