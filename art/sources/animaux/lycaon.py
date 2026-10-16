"""Le lycaon en peluche de magasin : le chien peint, un pelage marbré de grandes taches irrégulières noires, brunes,
blanches et fauves, ne se ressemblant jamais d'un flanc à l'autre ; le museau noir, un masque, de très grandes oreilles
rondes, la queue touffue à bout blanc, de longues pattes fines. Le meneur de meute : debout, la tête haute tournée vers
nous, un antérieur levé comme pour flairer le vent, les oreilles braquées, une gueule entrouverte sur un
sourire.

    python lycaon.py        fabrique la fiche art/apercus/animaux/lycaon.png (peluche de magasin, palier 4)
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
FAUVE = np.array(M.hexa("#e8a860"))           # la dominante : fauve (le brun marbré)
BRUN = np.array(M.hexa("#8a5a38"))
NOIR = np.array(M.hexa("#2e2826"))            # l'accent : les grandes taches noires, le museau
BLANC = np.array(M.hexa("#fff6e8"))
OEIL = M.hexa("#c8903a")
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=72, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def marbrer(m, graine, n=60, rayon=0.060):
    """Peint un marbrage irrégulier : n taches de rayon variable, chacune d'une couleur tirée (noir, brun, blanc, fauve)."""
    rng = np.random.default_rng(graine)
    v = m.v
    t = np.tile(FAUVE, (len(v), 1))
    cibles = v[rng.choice(len(v), size=min(n, len(v)), replace=False)]
    r = rayon * (0.5 + 1.1 * rng.random(len(cibles)))
    d = np.linalg.norm(v[:, None, :] - cibles[None, :, :], axis=2) / r[None, :]
    proche = np.argmin(d, axis=1)
    dedans = d[np.arange(len(v)), proche] < 1.0
    palette = np.array([NOIR, BRUN, BLANC, NOIR, BRUN])
    t[dedans] = palette[rng.integers(0, len(palette), len(cibles))[proche[dedans]]]
    m.teinte = t
    return m


def construire():
    a = K.Animal("lycaon")
    a.taille = 1.50

    # ----- le corps : un levrier robuste, la poitrine profonde, les flancs creusés ; marbré -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.440, 0.560), (0.260, 0.610), (0.040, 0.630), (-0.180, 0.660), (-0.320, 0.640))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.100), (0.14, 0.150), (0.45, 0.150), (0.72, 0.170), (0.92, 0.160), (1.0, 0.0)], L, 80, 0.007)
    marbrer(corps, 5, 52, 0.075)
    a.piece("corps", corps.sculpte(fil.couche), None)
    a.piece("cou", A.tube(A.courbe([(0.0, -0.220, 0.700), (0.0, -0.330, 0.780), (0.0, -0.390, 0.830)], 5), lambda t: 0.105 - 0.030 * t, 20), tuple(FAUVE))

    # ----- la tête : un museau noir, un masque ; les très grandes oreilles rondes ; haute, tournée vers nous -----
    H = A.cadre(Vector((0.0, -0.440, 0.850)), Vector((0.40, -1.0, -0.12)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.07, 0.092), (0.28, 0.115), (0.52, 0.098), (0.78, 0.082), (0.96, 0.068), (1.0, 0.0)], 0.360, 56, 0.006)
    tete.teinte = np.where((tete.v[:, 2] > 0.46 * 0.360)[:, None], NOIR, BRUN)
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0, -0.060)))
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.034, 0.024, 0.022), M.hexa("#1e1a18"), mat=H @ A.repere((0, 0.022, 0.296)), poil=False)
    a.tete = H @ Vector((0, 0.020, 0.200))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.48, 0.30, 0.62))     # plus en avant : de face, les deux yeux (16/10)
        a.rustine("iris_" + nom, "tete", H @ Vector((0, 0.020, 0.100)), regard, 0.22, OEIL, 0.003, 0)
        p, n = a.surface("tete", H @ Vector((0, 0.020, 0.100)), regard)
        a.oeil("oeil_" + nom, p + n * 0.006, n, 0.0215)
        po = A.profil([(0, 0), (0.054, 0.012), (0.070, 0.050), (0.060, 0.092), (0.030, 0.124), (0, 0.136)], 6)
        E = A.cadre(H @ Vector((c * 0.080, 0.080, 0.000)), H3 @ Vector((c * 0.50, 0.85, -0.15)), H3 @ Vector((c * 0.2, 0.0, 1.0)))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 28).etire(1.25, 0.36, 1.30), [(0.100, tuple(BRUN)), (9, tuple(NOIR))]), None, mat=E)
    # la gueule entrouverte : la mâchoire du bas, noire, un peu abaissée, un trait de sourire
    bas = A.boule(1.0, 28, 14).sculpte(lambda v: K.emousse(v, 0.84) * [0.060, 0.032, 0.130])
    a.piece("machoire", bas, tuple(NOIR), mat=H @ A.repere((0, -0.030, 0.200), (-12, 0, 0)))

    # ----- les pattes : longues et fines, marbrées ; un antérieur levé pour flairer ; la queue touffue à bout blanc -----
    def patte(pts, r0, graine):
        f_ = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.40, r0 * 0.60), (0.52, r0 * 0.72), (0.62, r0 * 0.50), (0.94, r0 * 0.46), (1.0, 0.0)], f_.long, 28, 0.008)
        marbrer(m, graine, 14, 0.050)
        m.teinte[m.v[:, 2] > 0.84 * f_.long] = BLANC
        return m.sculpte(f_.couche)
    for nom, pts, r0, g in (("av_D", [(-0.085, -0.240, 0.680), (-0.092, -0.250, 0.460), (-0.092, -0.240, 0.240), (-0.092, -0.250, 0.040)], 0.052, 41),
                            ("ar_G", [(0.090, 0.340, 0.560), (0.104, 0.290, 0.400), (0.104, 0.360, 0.230), (0.104, 0.340, 0.040)], 0.060, 42),
                            ("ar_D", [(-0.090, 0.340, 0.560), (-0.104, 0.290, 0.400), (-0.104, 0.360, 0.230), (-0.104, 0.340, 0.040)], 0.060, 43),
                            ("av_G", [(0.085, -0.240, 0.680), (0.092, -0.260, 0.500), (0.094, -0.350, 0.460), (0.094, -0.380, 0.340)], 0.052, 44)):
        a.piece("patte_" + nom, patte(pts, r0, g), None)
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.036, 0.056, 0.026), tuple(BLANC), pos=(pts[-1][0], pts[-1][1] - 0.020, max(pts[-1][2] - 0.010, 0.026)))
    chemin = [(0.0, 0.440, 0.560), (0.0, 0.560, 0.470), (0.020, 0.620, 0.340), (0.040, 0.620, 0.200)]
    a.piece("queue", K.tube_peint(A.courbe(chemin, 6), lambda t: 0.040 + 0.030 * math.sin(math.pi * min(t * 1.2, 1.0)) - 0.010 * t,
                                  [(0.52, tuple(BRUN)), (0.80, tuple(NOIR)), (1, tuple(BLANC))], 16), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lycaon", styles.style_de("lycaon"), sys.modules[__name__]), "Lycaon")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py lycaon). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.621                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.148, 0.657)),
    ('cou', 'corps', (0.000, -0.175, 0.768)),
    ('tete', 'cou', (0.012, -0.394, 0.798)),
    ('oreille_G', 'tete', (0.081, -0.500, 0.905)),
    ('patte_av_D', 'corps', (-0.086, -0.242, 0.656)),
    ('patte_ar_G', 'corps', (0.092, 0.313, 0.544)),
    ('patte_av_G', 'corps', (0.086, -0.245, 0.663)),
    ('queue', 'corps', (-0.001, 0.439, 0.544)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('machoire', 'corps'),
    ('oreille', 'oreille', True), ('pied_av', 'patte_av', True), ('pied_ar', 'patte_ar', True), ('truffe', 'corps'),
    ('corps', 'corps'), ('queue', 'queue'), ('tete', 'tete'), ('iris', 'tete'), ('oeil', 'tete'), ('cou', 'cou'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.186 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.342), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
