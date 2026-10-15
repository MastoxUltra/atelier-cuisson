"""La grenouille venimeuse en peluche, cousue main (2e dessin : plus de bébé aux yeux énormes) : un DENDROBATE, fin et
nerveux, le corps mince d'un jaune citron vif tout recouvert d'un RÉSEAU noir en mailles (le dos, la tête, les
cuisses), la tête en coin, de petits yeux noirs à fleur de peau, de longues pattes grêles et des ventouses rondes et
pâles au bout de chaque doigt, les grandes pattes arrière repliées. Posée sur ses quatre pattes, la tête haute : toute
petite, toute vive, elle sait qu'on n'y touche pas.

    python grenouille_venimeuse.py        fabrique la fiche art/apercus/animaux/grenouille_venimeuse.png (cousu main, palier 2)
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

GONFLAGE = True       # la base aux volumes gonflés de l'Artiste (fusion.py) : jointures fondues, bouts arrondis


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


CITRON = np.array(M.hexa("#ffe95a"))          # la dominante : jaune citron vif
NOIR = np.array(M.hexa("#26242c"))            # l'accent : le réseau
VENTRE = np.array(M.hexa("#fff8c0"))          # le ventre, la gorge
VENTOUSE = M.hexa("#fff4b0")                  # le bout des doigts
PAS = 0.005


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


def reseau(m, graine, n=34, largeur=0.0105, ventre=None):
    """Peint un RÉSEAU noir en mailles sur du jaune : le plus proche et le deuxième plus proche de quelques graines tirées
    dans la boîte de la pièce (le joint, là où ils sont presque à égale distance) ; le ventre jaune pâle, sans réseau."""
    rng = np.random.default_rng(graine)
    v = m.v
    lo, hi = v.min(axis=0) - 0.01, v.max(axis=0) + 0.01
    graines = lo + rng.random((n, 3)) * (hi - lo)
    d = np.sort(np.linalg.norm(v[:, None, :] - graines[None, :, :], axis=2), axis=1)[:, :2]
    t = np.tile(CITRON, (len(v), 1))
    t[(d[:, 1] - d[:, 0]) < largeur] = NOIR
    if ventre is not None:
        t[ventre(v)] = VENTRE
    m.teinte = t
    return m


def construire():
    a = K.Animal("grenouille_venimeuse")
    a.taille = 0.34

    # ----- le corps : mince, un peu relevé devant, le dos tout couvert du réseau noir, le ventre pâle -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.120, 0.060), (0.050, 0.075), (-0.020, 0.100), (-0.070, 0.118))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.05, 0.036), (0.28, 0.054), (0.62, 0.052), (0.90, 0.040), (1.0, 0.0)], L, 52, 0.004)
    reseau(corps, 3, 38, 0.0115, ventre=lambda v: (v[:, 1] < -0.030))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- la tête : un coin pointu, bas ; de PETITS yeux noirs, à fleur de tête, sur les côtés du crâne -----
    T = A.cadre(Vector((0.0, -0.105, 0.134)), Vector((0.0, -1.0, 0.16)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.10, 0.042), (0.36, 0.052), (0.64, 0.044), (0.88, 0.030), (0.98, 0.016), (1.0, 0.0)], 0.110, 40, 0.003)
    tete.v[:, 1] *= 0.80
    reseau(tete, 5, 14, 0.0095, ventre=lambda v: (v[:, 1] < -0.020))
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.040)))
    a.tete = T @ Vector((0, 0.0, 0.060))
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.58, 0.55, 0.55))                      # sur l'avant de la tête : les deux yeux de face
        p, n = a.surface("tete", T @ Vector((0, 0.0, 0.020)), regard)
        a.oeil("oeil_" + nom, p + n * 0.003, n, 0.0165)

    # ----- les pattes avant : fines et droites, quatre longs doigts à ventouse ; les arrière : longues, repliées en Z,
    #       le pied à plat, les doigts écartés, chacun sa ventouse -----
    def doigts(centre, cap, long, k=4):
        m = None
        for i in range(k):
            ang = cap + (i - (k - 1) / 2) * 24
            t = math.radians(ang)
            d = A.boule(1.0, 12, 6).etire(0.0045, long, 0.0045).pose((long * math.sin(t) * 0.9, -long * math.cos(t) * 0.9, 0.0), (0, 0, ang))
            v = A.boule(1.0, 12, 6).etire(0.0105, 0.0105, 0.0065).pose((long * math.sin(t) * 1.85, -long * math.cos(t) * 1.85, 0.0))
            m = d + v if m is None else m + d + v
        return m.pose(tuple(centre))
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.034, -0.050, 0.095), (c * 0.052, -0.080, 0.056), (c * 0.058, -0.100, 0.014)]
        m = A.tube(A.courbe(propres(ch), 5), lambda t: 0.013 - 0.005 * t, 12)
        m.teinte = np.tile(CITRON, (len(m.v), 1))
        a.piece("bras_" + nom, m, None)
        a.piece("doigts_av_" + nom, doigts((c * 0.058, -0.104, 0.010), c * 14, 0.030), VENTOUSE, poil=False)
        cu = [(c * 0.046, 0.100, 0.082), (c * 0.092, 0.040, 0.070), (c * 0.084, 0.118, 0.026), (c * 0.074, 0.062, 0.012)]
        mj = A.tube(A.courbe(propres(cu), 6), lambda t: 0.020 - 0.010 * t, 14)
        reseau(mj, 11 + (c > 0), 12, 0.0085)
        a.piece("jambe_ar_" + nom, mj, None)
        a.piece("doigts_ar_" + nom, doigts((c * 0.074, 0.060, 0.010), c * 10, 0.040), VENTOUSE, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("grenouille_venimeuse", styles.style_de("grenouille_venimeuse"), sys.modules[__name__]), "Grenouille venimeuse")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py grenouille_venimeuse). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.090                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.073, 0.083)),
    ('tete', 'corps', (0.007, -0.071, 0.119)),
    ('patte_av_G', 'corps', (0.038, -0.056, 0.090)),
    ('patte_ar_G', 'corps', (0.066, 0.073, 0.090)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('doigts_av', 'patte_av', True), ('doigts_ar', 'patte_ar', True),
    ('jambe_ar', 'patte_ar', True), ('corps', 'corps'), ('tete', 'tete'), ('bras', 'patte_av', True),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.027 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.049), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
