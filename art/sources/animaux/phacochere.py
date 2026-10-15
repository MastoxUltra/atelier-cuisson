"""Le phacochère en peluche cousue main : un rouille franc, la grosse tête plate et large, quatre verrues, deux défenses
d'ivoire qui se recourbent vers le haut, une crinière en brosse raide sur l'échine, de petites oreilles pointues, et la
queue dressée en antenne à houppe noire. L'important vexé : à genoux sur ses antérieurs, comme il aime, le museau en
avant, la queue droite comme un mât, un œil de travers : il fouille.

    python phacochere.py        fabrique la fiche art/apercus/animaux/phacochere.png (cousu main, palier 2)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import garnitures as G
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


ROUILLE = M.hexa("#d98a58")                   # la dominante : rouille franc (le poil le fonce : on le prend clair)
SOMBRE = M.hexa("#5a3a2c")                    # la crinière, le museau, la houppe
IVOIRE = M.hexa("#fff2d8")                    # l'accent : les défenses
CLAIR = M.hexa("#f2c8a0")                     # le dessous, le tour du museau
CORPS = Vector((0.0, 0.080, 0.360))
TETE = Vector((0.0, -0.360, 0.270))
LACET = 22.0


def construire():
    a = K.Animal("phacochere")
    a.taille = 1.00

    # ----- le corps : un tonneau court, les épaules hautes, la croupe plus basse ; la crinière en brosse raide -----
    def tonneau(v):
        v = K.bosse(v, (0, -0.7, 0.4), 0.14, 0.45)
        s = v * [0.200, 0.320, 0.215]
        s[:, 2] *= 1 - 0.12 * K.lisse((v[:, 1] + 0.0) / 1.0)
        return s
    corps = A.boule(1.0, 56, 28)
    corps.teinte = np.where((corps.v[:, 2] < -0.45)[:, None], np.asarray(CLAIR), np.asarray(ROUILLE))
    G.sillons(corps, [14], 0.005, 1.1)
    a.piece("corps", corps.sculpte(tonneau), None, pos=CORPS)
    a.couture("dos", "corps", 14, 0.35, 0.95)
    rng = np.random.default_rng(6)
    for i, y in enumerate(np.linspace(-0.26, 0.30, 17)):
        h = 0.060 - 0.022 * abs(y) / 0.3
        a.piece("soie_%02d" % i, A.boule(1.0, 10, 6).etire(0.034, 0.040, h + 0.012 * rng.random()), SOMBRE,
                pos=(0.0, CORPS.y + y, CORPS.z + 0.215 * (1 - 0.12 * ((y / 0.32 + 0.0) / 1.0)) + 0.020), rot=(rng.uniform(-14, 14), 0, 0), poil=False)

    # ----- la tête : large, plate sur le dessus, le museau carré ; quatre verrues ; les défenses recourbées ; de côté vers nous -----
    H = A.repere(TETE, (-10, 0, LACET))
    H3 = H.to_3x3()

    def large(v):
        s = K.emousse(v, 0.80)
        s[:, 1] *= 0.80
        return s * [0.150, 0.130, 0.200]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(large), ROUILLE, mat=H @ A.repere((0, 0, 0)))
    a.piece("groin", A.boule(1.0, 32, 16).etire(0.080, 0.062, 0.090), tuple(SOMBRE), mat=H @ A.repere((0, -0.230, -0.030)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.040, 0.030, 0.016), tuple(SOMBRE), mat=H @ A.repere((0, -0.305, -0.026)), poil=False)
    a.tete = H @ Vector((0, -0.220, -0.020))
    # les verrues : trois paires sur la face (sous l'œil, sur la joue, au-dessus du groin), des bosses de peau pâle
    for k, (dx, dy, dz) in enumerate(((0.118, -0.150, 0.026), (0.108, -0.082, -0.052), (0.062, -0.215, 0.050))):
        for c in (1, -1):
            a.piece("verrue_%d%s" % (k, "G" if c > 0 else "D"), A.boule(1.0, 14, 8).etire(0.028, 0.030, 0.022), CLAIR,
                    mat=H @ A.repere((c * dx, dy, dz)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        # les défenses : elles sortent au coin de la gueule, juste à côté du groin, et montent en se recourbant
        ch = [H @ Vector(q) for q in ((c * 0.070, -0.265, -0.060), (c * 0.112, -0.300, -0.052), (c * 0.150, -0.300, 0.010), (c * 0.150, -0.265, 0.110))]
        a.piece("defense_" + nom, A.tube(A.courbe(propres(ch), 6), lambda t: 0.024 - 0.018 * t, 14), IVOIRE, poil=False)
        p, n = a.surface("tete", H @ Vector((0, 0.0, 0.0)), H3 @ Vector((c * 0.62, -0.62, 0.50)))
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0185)
        po = A.profil([(0, 0), (0.030, 0.008), (0.036, 0.034), (0.026, 0.060), (0.008, 0.074), (0, 0.080)], 5)
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.42, 1.0), ROUILLE,
                mat=A.cadre(H @ Vector((c * 0.110, 0.110, 0.080)), H3 @ Vector((c * 0.30, 0.18, 0.95)), H3 @ Vector((c * 0.3, -0.9, 0.0))))

    # ----- les pattes : les antérieurs à genoux (repliés sous la poitrine), les postérieurs droits ; la queue en antenne -----
    for nom, c in (("av_G", 1), ("av_D", -1)):
        a.piece("genou_" + nom, A.boule(1.0, 24, 12).etire(0.050, 0.090, 0.050), ROUILLE, pos=(c * 0.115, -0.230, 0.050), rot=(0, 0, c * 6))
        a.piece("patte_" + nom, A.tube(A.courbe([(c * 0.110, -0.150, 0.230), (c * 0.115, -0.220, 0.100), (c * 0.115, -0.290, 0.030)], 5), 0.054, 14), ROUILLE)
        a.piece("sabot_" + nom, A.boule(1.0, 20, 10).etire(0.040, 0.060, 0.026), SOMBRE, pos=(c * 0.115, -0.340, 0.028), poil=False)
    for nom, c in (("ar_G", 1), ("ar_D", -1)):
        a.piece("patte_" + nom, A.tube(A.courbe([(c * 0.110, 0.300, 0.250), (c * 0.120, 0.290, 0.130), (c * 0.120, 0.300, 0.034)], 5), 0.058, 14), ROUILLE)
        a.piece("sabot_" + nom, A.boule(1.0, 20, 10).etire(0.044, 0.064, 0.028), SOMBRE, pos=(c * 0.120, 0.280, 0.030), poil=False)
    a.piece("queue", A.tube(A.courbe([(0.0, 0.380, 0.400), (0.0, 0.460, 0.520), (0.0, 0.470, 0.700)], 5), 0.016, 12), ROUILLE)
    a.piece("houppe", A.boule(1.0, 16, 8).etire(0.040, 0.040, 0.090), SOMBRE, pos=(0.0, 0.470, 0.770))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("phacochere", styles.style_de("phacochere"), sys.modules[__name__]), "Phacochère")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py phacochere). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.233                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.222, 0.482)),
    ('tete', 'corps', (0.024, -0.250, 0.356)),
    ('oreille_G', 'tete', (0.045, -0.215, 0.342)),
    ('patte_av_G', 'corps', (0.113, -0.163, 0.218)),
    ('patte_ar_G', 'corps', (0.119, 0.293, 0.249)),
    ('queue', 'corps', (0.002, 0.373, 0.415)),
]

PORTEURS = [('soie', 'corps'), 
    ('oeil_reflet', 'tete'), ('sabot_av', 'patte_av', True), ('sabot_ar', 'patte_ar', True),
    ('genou_av', 'patte_av', True), ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True),
    ('verrue_0', 'corps'), ('verrue_1', 'corps'), ('verrue_2', 'corps'), ('verrue_3', 'corps'), ('soie_00', 'tete'),
    ('soie_01', 'tete'), ('soie_02', 'tete'), ('soie_03', 'tete'), ('soie_04', 'tete'), ('soie_05', 'tete'),
    ('soie_06', 'tete'), ('soie_07', 'tete'), ('soie_08', 'tete'), ('soie_09', 'tete'), ('soie_10', 'tete'),
    ('soie_11', 'tete'), ('oreille', 'oreille', True), ('defense', 'tete'), ('houppe', 'corps'), ('corps', 'corps'),
    ('groin', 'corps'), ('queue', 'queue'), ('tete', 'tete'), ('oeil', 'tete'), ('nez', 'tete'), ('dos', 'corps'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.070 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.128), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
