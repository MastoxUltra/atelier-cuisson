"""L'addax en peluche de velours ras : une antilope du grand erg, blanc pur, trapue, le cou épais barré d'un collier
brun, une touffe brune sur le front, le nez et les joues blancs ; deux longues cornes en SPIRALE, annelées, qui montent
en vrille vers l'arrière ; de larges sabots plats qui ne s'enfoncent pas dans le sable. Le blanc sous le soleil :
debout, la tête un peu basse et tournée vers nous, les cornes dressées comme deux tire-bouchons.

    python addax.py        fabrique la fiche art/apercus/animaux/addax.png (velours ras, palier 3)
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


BLANC = np.array(M.hexa("#fffcf4"))           # la dominante : blanc pur
OMBRE = np.array(M.hexa("#f0e6d0"))           # le dos, le dessus du cou : à peine plus bas
BRUN = np.array(M.hexa("#8a6a48"))            # l'accent : le collier, le front, la touffe de la queue
CORNE = M.hexa("#e0d0a8")                     # les cornes
CORNE_FONCE = M.hexa("#b8a070")
NOIR = np.array(M.hexa("#3a3030"))
PAS = 0.007


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=60, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("addax")
    a.taille = 1.90

    # ----- le corps : un tonneau trapu d'antilope, le garrot un peu haut, tout blanc, le dos à peine plus sombre -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.420, 0.760), (0.230, 0.810), (0.000, 0.850), (-0.200, 0.890), (-0.340, 0.900))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.115), (0.15, 0.180), (0.45, 0.200), (0.75, 0.212), (0.92, 0.190), (0.98, 0.130), (1.0, 0.0)], L, 72)
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    corps.teinte = np.where((th < 0.8)[:, None], OMBRE, BLANC)
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou épais, le collier brun et la barbe ; la tête large, baissée et tournée vers nous -----
    a.piece("cou", A.tube(A.courbe([(0.0, -0.250, 0.920), (0.0, -0.390, 0.900), (0.0, -0.490, 0.830)], 5), lambda t: 0.150 - 0.052 * t, 24), tuple(BLANC))
    a.piece("collier", A.boule(1.0, 40, 20).etire(0.152, 0.152, 0.075), tuple(BRUN), mat=A.cadre(Vector((0.0, -0.345, 0.865)), Vector((0.0, -1.0, -0.20)), Vector((0, 0, 1))))
    a.piece("barbe", A.boule(1.0, 24, 12).etire(0.060, 0.040, 0.110), tuple(BRUN), pos=(0.0, -0.470, 0.700), rot=(-18, 0, 0))
    T = A.cadre(Vector((0.0, -0.600, 0.790)), Vector((0.40, -1.0, -0.34)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.07, 0.078), (0.26, 0.096), (0.52, 0.084), (0.78, 0.072), (0.95, 0.060), (1.0, 0.0)], 0.320, 52, 0.006)
    tt = np.tile(BLANC, (len(tete.v), 1))
    fr = (tete.v[:, 1] > 0.020) & (tete.v[:, 2] > 0.03) & (tete.v[:, 2] < 0.15)
    tt[fr] = BRUN                                                                 # le front brun
    tete.teinte = tt
    a.piece("tete", tete, None, mat=T @ A.repere((0, 0, -0.090)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.034, 0.024, 0.024), tuple(NOIR), mat=T @ A.repere((0, 0.004, 0.232)), poil=False)
    a.tete = T @ Vector((0, 0.0, 0.150))
    for nom, c in (("G", 1), ("D", -1)):
        regard = T3 @ Vector((c * 0.60, 0.38, 0.50))
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.006, n, 0.0225)
        # (paupière retirée : yeux ouverts, bouton net, sans air fatigué ni fâché)
        # la corne en vrille : un axe qui monte vers l'arrière, la tige qui tourne autour, deux tours et demi
        pts = []
        for i in range(0, 41):
            u = i / 40.0
            axe = np.array([c * (0.045 + 0.110 * u), 0.060 + 0.500 * u ** 0.9, -0.020 - 0.200 * u])
            ang = 2 * math.pi * 2.5 * u + (0.0 if c > 0 else math.pi)
            r = 0.028 * (1.0 - 0.45 * u)
            pts.append(tuple(T @ Vector(tuple(axe + np.array([r * math.cos(ang), 0.0, r * math.sin(ang)])))))
        bandes = [((k + 1) / 10.0, tuple(CORNE) if k % 2 == 0 else tuple(CORNE_FONCE)) for k in range(10)]
        a.piece("corne_" + nom, K.tube_peint(A.courbe(propres(pts), 3), lambda t: 0.023 - 0.016 * t, bandes, 12), None)
        po = A.profil([(0, 0), (0.030, 0.008), (0.040, 0.036), (0.032, 0.070), (0.012, 0.100), (0, 0.112)], 5)
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.38, 1.0), tuple(BLANC),
                mat=A.cadre(T @ Vector((c * 0.070, 0.040, -0.030)), T3 @ Vector((c * 0.90, 0.20, -0.30)), T3 @ Vector((c * 0.3, 0.0, 1.0))))

    # ----- les pattes : épaisses, le genou net, les grands sabots plats et sombres ; l'antérieur gauche avancé -----
    def patte(pts, r0):
        ft = K.Fil(pts, (1, 0, 0))
        m = fuseau([(0.0, r0), (0.30, r0 * 0.62), (0.46, r0 * 0.50), (0.52, r0 * 0.62), (0.60, r0 * 0.44), (0.92, r0 * 0.42), (0.97, r0 * 0.54), (1.0, 0.0)],
                   ft.long, 28, 0.007)
        m.teinte = np.tile(BLANC, (len(m.v), 1))
        return m.sculpte(ft.couche)
    for nom, pts, r0 in (("av_D", [(-0.110, -0.220, 0.800), (-0.116, -0.225, 0.520), (-0.116, -0.215, 0.280), (-0.116, -0.225, 0.040)], 0.082),
                         ("ar_G", [(0.120, 0.360, 0.700), (0.130, 0.310, 0.460), (0.130, 0.380, 0.260), (0.130, 0.370, 0.040)], 0.092),
                         ("ar_D", [(-0.120, 0.360, 0.700), (-0.130, 0.310, 0.460), (-0.130, 0.380, 0.260), (-0.130, 0.370, 0.040)], 0.092),
                         ("av_G", [(0.110, -0.220, 0.800), (0.116, -0.255, 0.540), (0.116, -0.350, 0.330), (0.116, -0.385, 0.040)], 0.082)):
        a.piece("patte_" + nom, patte(pts, r0), None)
        a.piece("sabot_" + nom, A.boule(1.0, 24, 12).etire(0.052, 0.068, 0.032), tuple(NOIR), pos=(pts[-1][0], pts[-1][1] - 0.012, 0.030), poil=False)
    a.piece("queue", A.tube(A.courbe(propres([(0.0, 0.440, 0.760), (0.0, 0.500, 0.690), (0.0, 0.510, 0.560)]), 5), lambda t: 0.022 - 0.006 * t, 12), tuple(BLANC))
    a.piece("touffe", A.boule(1.0, 20, 10).etire(0.030, 0.030, 0.062), tuple(BRUN), pos=(0.0, 0.512, 0.520))
    # les proportions de la bête réelle (silhouettes.py contre references_3d) : un corps plus long, des pattes et un cou plus courts
    import deformer_b as DF
    DF.etirer(a, sy=1.15, sz=0.92)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("addax", styles.style_de("addax"), sys.modules[__name__]), "Addax")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py addax). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.681                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.246, 0.787)),
    ('cou', 'corps', (-0.000, -0.274, 0.751)),
    ('tete', 'cou', (0.011, -0.601, 0.749)),
    ('oreille_G', 'tete', (0.063, -0.645, 0.770)),
    ('patte_av_D', 'corps', (-0.111, -0.255, 0.711)),
    ('patte_ar_G', 'corps', (0.122, 0.387, 0.624)),
    ('patte_av_G', 'corps', (0.111, -0.262, 0.710)),
    ('queue', 'corps', (0.002, 0.499, 0.691)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True),
    ('sabot_av', 'patte_av', True), ('sabot_ar', 'patte_ar', True), ('oreille', 'oreille', True),
    ('collier', 'corps'), ('touffe', 'queue'), ('corps', 'corps'), ('corne', 'tete'), ('queue', 'queue'),
    ('barbe', 'tete'), ('tete', 'tete'), ('oeil', 'tete'), ('cou', 'cou'), ('nez', 'tete'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.204 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.375), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
