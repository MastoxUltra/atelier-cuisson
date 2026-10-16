"""Le chameau (de Bactriane) en peluche de velours ras : un brun chocolat clair tout laineux, DEUX bosses qui retombent un
peu, couronnées de mèches ; un cou bas en S barbu de longs poils, une tête lourde au front frisé et à la grosse lèvre,
des pattes épaisses en pantalon de laine, de larges pieds plats. L'endurant : debout, le cou tendu vers nous, la tête
un peu haute, mâchant lentement une pensée qu'il ne dira pas.

    python chameau.py        fabrique la fiche art/apercus/animaux/chameau.png (velours ras, palier 3)
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


LAINE = np.array(M.hexa("#c09c6c"))           # la dominante : brun chocolat clair laineux (le poil le fonce)
CLAIR = np.array(M.hexa("#dcc49a"))           # le ventre, le dedans des pattes, le museau
FONCE = np.array(M.hexa("#7e5c3c"))           # les mèches : bosses, barbe, front, pantalons
COUSSIN = M.hexa("#8a6a48")
NOIR = np.array(M.hexa("#3a2e28"))
PAS = 0.007


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


def meche(longueur, largeur):
    """Une mèche : un fuseau pendant (axe Z, pointe vers le bas)."""
    return A.boule(1.0, 12, 6).etire(largeur, largeur * 0.8, longueur)


def construire():
    a = K.Animal("chameau")
    a.taille = 2.00

    # ----- le corps : un gros tonneau laineux, DEUX bosses qui s'affaissent, le ventre clair -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.450, 0.930), (0.280, 0.960), (0.040, 0.980), (-0.200, 0.990), (-0.400, 0.980))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.140), (0.14, 0.225), (0.42, 0.245), (0.72, 0.250), (0.90, 0.205), (0.97, 0.140), (1.0, 0.0)], L, 80)
    f = corps.v[:, 2] / L
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    haut = np.clip(corps.v[:, 1] / 0.22, 0.0, 1.0)
    for centre, h in ((0.36, 0.200), (0.64, 0.185)):
        g = np.exp(-((f - centre) / 0.085) ** 2) * haut
        corps.v[:, 1] += h * g
        corps.v[:, 0] *= 1 - 0.16 * g
    corps.teinte = np.where((th > 2.2)[:, None], CLAIR, np.where((corps.v[:, 1] > 0.26)[:, None], FONCE, LAINE))
    a.piece("corps", corps.sculpte(fil.couche), None)
    mech = None
    for centre, h in ((0.36, 0.200), (0.64, 0.185)):                                # les mèches au sommet des bosses
        c_, av, nq = fil.cadre(centre * L)
        for dy, dx, hh in ((0.0, 0.0, 0.080), (0.045, 0.020, 0.062), (-0.045, -0.020, 0.062), (0.0, 0.040, 0.050)):
            m = meche(hh, 0.030).pose(tuple(np.array(c_) + np.array(nq) * (0.235 + h * 0.94) + np.array([dx, dy, 0.0])))
            mech = m if mech is None else mech + m
    a.piece("meches_bosses", mech, tuple(FONCE))

    # ----- le cou : bas et large, en S, d'une seule pièce ; la barbe de longs poils dessous -----
    BASE = Vector((0.0, -0.400, 1.010))
    arc = ((0.0, 0.0), (0.080, 0.100), (0.170, 0.240), (0.200, 0.380), (0.150, 0.500), (0.040, 0.580))
    enc = K.Fil([tuple(BASE + Vector((0, -u, z))) for u, z in arc], (1, 0, 0))
    Lc = enc.long
    rr = [(0.0, 0.165), (0.12, 0.140), (0.40, 0.108), (0.80, 0.088), (1.0, 0.084)]
    cou = fuseau(rr, Lc, 56)
    cou.teinte = np.where((cou.v[:, 1] > 0.020)[:, None], FONCE, LAINE)
    a.piece("cou", cou.sculpte(enc.couche), None)
    barbe = None
    for fr in np.linspace(0.08, 0.96, 9):
        c_, av, nq = enc.cadre(fr * Lc)
        r = float(np.interp(fr, [p[0] for p in rr], [p[1] for p in rr]))
        m = meche(0.095, 0.034).pose(tuple(np.array(c_) - np.array(nq) * (r * 0.92) + np.array([0.0, 0.0, -0.040])))
        barbe = m if barbe is None else barbe + m
    a.piece("barbe", barbe, tuple(FONCE))
    centre, avant, nuque = enc.cadre(Lc)
    bout = Vector(centre)

    # ----- la tête : lourde, le museau large, la grosse lèvre ; le front frisé ; tournée vers nous -----
    T = A.cadre(bout + Vector((0.0, -0.030, 0.020)), Vector((0.36, -1.0, -0.12)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.066), (0.22, 0.092), (0.46, 0.078), (0.72, 0.068), (0.90, 0.070), (0.97, 0.052), (1.0, 0.0)], 0.330, 52, 0.005)
    tete.teinte = np.where((tete.v[:, 2] > 0.20)[:, None], tuple(CLAIR), tuple(LAINE))
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.080)))
    a.tete = T @ Vector((0, 0.0, 0.180))
    a.piece("levre", A.boule(1.0, 24, 12).etire(0.050, 0.026, 0.062), tuple(CLAIR), mat=T @ A.repere((0.0, -0.074, 0.190), (10, 0, 0)))
    a.piece("frisette", A.boule(1.0, 24, 12).etire(0.060, 0.044, 0.050), tuple(FONCE), mat=T @ A.repere((0.0, 0.074, -0.010), (-14, 0, 0)))
    for nom, c in (("G", 1), ("D", -1)):
        pn, nn = a.surface("tete", T @ Vector((0, 0.0, 0.200)), T3 @ Vector((c * 0.45, 0.89, 0.0)))
        a.piece("narine_" + nom, A.boule(1.0, 14, 8).etire(0.006, 0.014, 0.012), tuple(NOIR), mat=A.cadre(pn + nn * 0.002, nn, T3 @ Vector((0, 0, 1))), poil=False)
        regard = T3 @ Vector((c * 0.60, 0.34, 0.50))
        p, n = a.surface("tete", T @ Vector((0, 0.0, 0.030)), regard)
        a.oeil("oeil_" + nom, p + n * 0.006, n, 0.0230)
        # (paupière retirée : yeux ouverts, bouton net, sans air fatigué ni fâché)
        po = A.profil([(0, 0), (0.026, 0.008), (0.032, 0.032), (0.024, 0.056), (0.009, 0.074), (0, 0.082)], 5)
        a.piece("oreille_" + nom, A.tour(po, 20).etire(1.0, 0.45, 1.0), tuple(FONCE),
                mat=A.cadre(T @ Vector((c * 0.052, 0.058, -0.030)), T3 @ Vector((c * 0.50, 0.64, -0.30)), T3 @ Vector((c * 0.3, 0.0, 1.0))))

    # ----- les pattes : épaisses, le genou net, le pantalon de laine, le large pied plat ; l'antérieur gauche avancé -----
    def jambe(pts, r0):
        ft = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.26, r0 * 0.74), (0.44, r0 * 0.54), (0.50, r0 * 0.68), (0.58, r0 * 0.52), (0.80, r0 * 0.58), (0.94, r0 * 0.50), (1.0, 0.0)],
                   ft.long, 32, 0.007)
        zz = m.v[:, 2] / ft.long
        m.teinte = np.where(((zz > 0.60) & (zz < 0.86))[:, None], tuple(FONCE), tuple(LAINE))
        return m.sculpte(ft.couche)
    for nom, pts, r0 in (("av_D", [(-0.150, -0.330, 0.900), (-0.155, -0.335, 0.600), (-0.155, -0.325, 0.320), (-0.155, -0.335, 0.030)], 0.105),
                         ("ar_G", [(0.155, 0.360, 0.880), (0.165, 0.310, 0.600), (0.165, 0.380, 0.330), (0.165, 0.370, 0.030)], 0.115),
                         ("ar_D", [(-0.155, 0.360, 0.880), (-0.165, 0.310, 0.600), (-0.165, 0.380, 0.330), (-0.165, 0.370, 0.030)], 0.115),
                         ("av_G", [(0.150, -0.330, 0.900), (0.155, -0.370, 0.620), (0.155, -0.440, 0.350), (0.155, -0.450, 0.030)], 0.105)):
        a.piece("jambe_" + nom, jambe(pts, r0), None)
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.066, 0.092, 0.028), COUSSIN, pos=(pts[-1][0], pts[-1][1] - 0.020, 0.028), poil=False)
    a.piece("queue", A.tube(A.courbe(propres([(0.0, 0.520, 0.940), (0.0, 0.580, 0.840), (0.0, 0.590, 0.690)]), 5), lambda t: 0.026 - 0.008 * t, 12), tuple(LAINE))
    a.piece("meche_queue", A.boule(1.0, 20, 10).etire(0.034, 0.034, 0.075), tuple(FONCE), pos=(0.0, 0.592, 0.640))
    # les proportions de la bête réelle (silhouettes.py contre references_3d) : un corps plus long, des pattes et un cou plus courts
    import deformer_b as DF
    DF.etirer(a, sy=1.22, sz=0.8)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("chameau", styles.style_de("chameau"), sys.modules[__name__]), "Chameau")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py chameau). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.691                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.293, 0.883)),
    ('cou', 'corps', (0.000, -0.449, 0.895)),
    ('tete', 'cou', (0.011, -0.639, 1.221)),
    ('oreille_G', 'tete', (0.039, -0.534, 1.346)),
    ('patte_av_D', 'corps', (-0.151, -0.406, 0.695)),
    ('patte_ar_G', 'corps', (0.156, 0.407, 0.682)),
    ('patte_av_G', 'corps', (0.150, -0.419, 0.696)),
    ('queue', 'corps', (0.002, 0.622, 0.743)),
]

PORTEURS = [
    ('meches_bosses', 'corps'), ('meche_queue', 'queue'), ('oeil_reflet', 'tete'), ('jambe_av', 'patte_av', True),
    ('jambe_ar', 'patte_ar', True), ('frisette', 'tete'), ('oreille', 'oreille', True), ('pied_av', 'patte_av', True),
    ('pied_ar', 'patte_ar', True), ('narine', 'tete'), ('corps', 'corps'), ('barbe', 'tete'), ('levre', 'tete'),
    ('queue', 'queue'), ('tete', 'tete'), ('oeil', 'tete'), ('cou', 'cou'), ('paupiere_0', 'paupiere_0'),
    ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.207 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.380), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
