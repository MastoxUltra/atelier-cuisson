"""Le guépard en peluche de magasin : un or pâle doré, le ventre crème, des taches rondes noires nettes semées sur tout
le corps (petites, serrées), une petite tête ronde aux « larmes » noires qui coulent de l'œil à la gueule, un corps
d'une finesse de lévrier, de très longues pattes, la queue annelée. Le sprinter à l'affût : le corps bas et tendu, le
dos creusé, l'avant-main penché, la tête haute tournée vers nous, un antérieur levé : il se décide.

    python guepard.py        fabrique la fiche art/apercus/animaux/guepard.png (peluche de magasin, palier 4)
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
OR = np.array(M.hexa("#f8d890"))              # la dominante : or pâle doré
CREME = np.array(M.hexa("#fff4dc"))           # le ventre, le museau, le dessous
NOIR = np.array(M.hexa("#2e2824"))            # l'accent : les taches
OEIL = M.hexa("#e8b84a")
CHARBON = M.hexa("#2e2824")
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


def tacheter(m, graine, n, rayon, couleur=NOIR, base=OR, ventre=None, ecart=0.0):
    """Peint une pièce encore droite en « base » et y sème n taches rondes nettes (rayon donné, ±30 %), sur des sommets pris au
    hasard ; ventre(v) vrai : crème sans taches."""
    rng = np.random.default_rng(graine)
    v = m.v
    t = np.tile(base, (len(v), 1))
    cibles = v[rng.choice(len(v), size=min(n, len(v)), replace=False)]
    r = rayon * (0.7 + 0.6 * rng.random(len(cibles)))
    d = np.linalg.norm(v[:, None, :] - cibles[None, :, :], axis=2)
    t[(d < r[None, :]).any(axis=1)] = couleur
    if ventre is not None:
        t[ventre(v)] = CREME
    m.teinte = t
    return m


def construire():
    a = K.Animal("guepard")
    a.taille = 1.80

    # ----- le corps : un long fuseau de lévrier, le dos creusé, le poitrail profond ; tacheté de rondes nettes -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.540, 0.660), (0.340, 0.720), (0.080, 0.690), (-0.180, 0.700), (-0.380, 0.690), (-0.470, 0.690))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.03, 0.095), (0.12, 0.135), (0.30, 0.125), (0.50, 0.110), (0.70, 0.135), (0.90, 0.150), (1.0, 0.0)], L, 80, 0.007)
    tacheter(corps, 2, 330, 0.026, ventre=lambda v: (np.abs(np.arctan2(v[:, 0], v[:, 1])) > 2.5))
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- la tête : petite et ronde, le museau court, les larmes noires de l'œil à la gueule ; haute, tournée vers nous -----
    H = A.cadre(Vector((0.0, -0.600, 0.840)), Vector((0.40, -1.0, -0.14)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.08, 0.075), (0.28, 0.092), (0.55, 0.076), (0.82, 0.056), (0.96, 0.046), (1.0, 0.0)], 0.250, 56, 0.005)
    tacheter(tete, 8, 60, 0.012, ventre=lambda v: (v[:, 2] > 0.190) | (np.abs(np.arctan2(v[:, 0], v[:, 1])) > 2.5))
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0, -0.060)))
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.022, 0.016, 0.014), CHARBON, mat=H @ A.repere((0, 0.034, 0.178)), poil=False)
    a.tete = H @ Vector((0, 0.020, 0.120))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.80, 0.40, 0.14))
        a.rustine("iris_" + nom, "tete", H @ Vector((0, 0.020, 0.040)), regard, 0.20, OEIL, 0.003, 0)
        p, n = a.surface("tete", H @ Vector((0, 0.020, 0.040)), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0145)
        larme = [H3 @ Vector((c * (0.80 - 0.10 * t), 0.20 - 0.42 * t, 0.14 + 0.22 * t)) for t in np.linspace(0, 1, 6)]
        a.broderie("larme_" + nom, A.courbe(propres(a.trace("tete", H @ Vector((0, 0.020, 0.040)), larme, 0.003)), 4), 0.0080, tuple(NOIR))
        po = A.profil([(0, 0), (0.030, 0.008), (0.038, 0.030), (0.030, 0.052), (0.012, 0.066), (0, 0.072)], 5)
        E = A.cadre(H @ Vector((c * 0.058, 0.060, -0.020)), H3 @ Vector((c * 0.50, 0.85, -0.15)), H3 @ Vector((c * 0.2, 0.0, 1.0)))
        a.piece("oreille_" + nom, K.bandes(A.tour(po, 24).etire(1.0, 0.42, 1.0), [(0.050, tuple(OR)), (9, tuple(NOIR))]), None, mat=E)
    a.piece("cou", A.tube(A.courbe([(0.0, -0.420, 0.740), (0.0, -0.520, 0.800), (0.0, -0.590, 0.830)], 5), lambda t: 0.090 - 0.026 * t, 18), tuple(OR))

    # ----- les pattes : très longues et fines, tachetées ; un antérieur levé et replié ; les pieds aux griffes sorties -----
    def patte(points, r0):
        m = fuseau([(0.0, r0), (0.40, r0 * 0.62), (0.52, r0 * 0.74), (0.62, r0 * 0.52), (0.95, r0 * 0.46), (1.0, 0.0)],
                   float(np.sum(np.linalg.norm(np.diff(np.asarray(points), axis=0), axis=1))), 28, 0.008)
        return m
    for nom, x, y, r0, plan in (("ar_G", 0.115, 0.430, 0.070, [(0.0, 0.0), (-0.07, 0.30), (0.05, 0.52), (0.04, 0.66)]),
                                ("ar_D", -0.115, 0.430, 0.070, [(0.0, 0.0), (-0.07, 0.30), (0.05, 0.52), (0.04, 0.66)]),
                                ("av_D", -0.095, -0.320, 0.058, [(0.0, 0.0), (0.02, 0.28), (0.00, 0.52), (-0.01, 0.66)])):
        pts = [(x, y + dy, 0.680 - dz) for dy, dz in plan]
        f = K.Fil(pts, (1, 0, 0))
        m = patte(pts, r0)
        m.v *= 1.0
        # reprend la longueur du fil pour la pièce
        m = fuseau([(0.0, r0), (0.40, r0 * 0.62), (0.52, r0 * 0.74), (0.62, r0 * 0.52), (0.95, r0 * 0.46), (1.0, 0.0)], f.long, 28, 0.008)
        tacheter(m, 20 + int(abs(x) * 100), 40, 0.020, ventre=lambda v, L=f.long: v[:, 2] > 0.86 * L)
        a.piece("patte_" + nom, m.sculpte(f.couche), None)
        a.piece("pied_" + nom, A.boule(1.0, 20, 10).etire(0.044, 0.070, 0.024), tuple(OR), pos=(x, pts[-1][1] - 0.028, 0.024))
    levee = [(0.095, -0.320, 0.680), (0.102, -0.340, 0.470), (0.105, -0.420, 0.440), (0.105, -0.460, 0.340)]
    a.piece("patte_av_G", K.tube_peint(A.courbe(levee, 6), lambda t: 0.050 - 0.016 * t, [(1, tuple(OR))], 14), None)
    a.piece("pied_av_G", A.boule(1.0, 20, 10).etire(0.040, 0.064, 0.024), tuple(OR), pos=(0.105, -0.490, 0.316), rot=(-40, 0, 0))

    # ----- la queue : longue, annelée de noir, qui pend et se relève au bout ; le pinceau noir -----
    chemin = [(0.0, 0.540, 0.640), (0.040, 0.760, 0.470), (0.120, 0.920, 0.260), (0.230, 0.980, 0.150), (0.340, 0.940, 0.110)]
    bagues, f, c = [], 0.0, tuple(OR)
    while f < 0.84:
        f += 0.085
        bagues.append((min(f, 0.84), c))
        c = tuple(NOIR) if c == tuple(OR) else tuple(OR)
    bagues[-1] = (0.84, bagues[-1][1])
    bagues.append((1.0, tuple(NOIR)))
    a.piece("queue", K.tube_peint(A.courbe(chemin, 6), lambda t: 0.046 - 0.014 * t, bagues, 16), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("guepard", styles.style_de("guepard"), sys.modules[__name__]), "Guépard")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py guepard). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.660                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.214, 0.709)),
    ('cou', 'corps', (-0.007, -0.386, 0.798)),
    ('tete', 'cou', (0.009, -0.549, 0.801)),
    ('oreille_G', 'tete', (0.050, -0.614, 0.893)),
    ('patte_ar_G', 'corps', (0.115, 0.407, 0.657)),
    ('patte_av_D', 'corps', (-0.095, -0.315, 0.655)),
    ('patte_av_G', 'corps', (0.097, -0.323, 0.669)),
    ('queue', 'corps', (0.006, 0.546, 0.620)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('patte_ar', 'patte_ar', True), ('patte_av', 'patte_av', True),
    ('oreille', 'oreille', True), ('pied_ar', 'patte_ar', True), ('pied_av', 'patte_av', True), ('truffe', 'corps'),
    ('corps', 'corps'), ('queue', 'queue'), ('larme', 'corps'), ('tete', 'tete'), ('iris', 'tete'), ('oeil', 'tete'),
    ('cou', 'cou'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'),
    ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.198 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.363), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
