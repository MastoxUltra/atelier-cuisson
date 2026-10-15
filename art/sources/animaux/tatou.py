"""Le tatou en peluche cousue main (2e dessin, d'après photos : un vrai bouclier, plus de manchon) : un rose gris cuir, le
DÔME de la carapace posé sur le dos comme une coque bombée, découpée en bandes articulées étroites (le bouclier large
des épaules, les bandes du milieu qui se resserrent, le bouclier de la croupe), le dessous nu et plus clair ; une petite
tête en coin au museau pointu, deux yeux, de longues oreilles en tuyau fermé sur les côtés ; des pattes courtes aux
griffes de pelle, une longue queue annelée qui s'effile. Le blindé timide : le museau au ras du sol qui renifle, la carapace en
dôme, une patte avant levée ; il est à un souffle de se rouler en boule.

    python tatou.py        fabrique la fiche art/apercus/animaux/tatou.png (cousu main, palier 2)
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


CUIR = np.array(M.hexa("#e0b0a0"))            # la dominante : rose gris cuir (le poil le fonce)
PLAQUE = np.array(M.hexa("#c8968a"))          # les bandes de la carapace, un ton plus bas
JOINT = np.array(M.hexa("#8a6258"))           # les joints entre les bandes
VENTRE = np.array(M.hexa("#f4d8c8"))
GRIFFE = M.hexa("#f2e4cc")
NOIR = M.hexa("#3a3030")
PAS = 0.005


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 5)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("tatou")
    a.taille = 0.75

    # ----- la carapace : une coque en DÔME, plus haute que large au milieu, bordée en bas d'un rebord ; bandes étroites au
    #       milieu (des joints sombres nets, et un léger gradin à chaque joint), boucliers pleins devant et derrière -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.250, 0.140), (0.130, 0.190), (0.000, 0.205), (-0.130, 0.185), (-0.220, 0.145))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.100), (0.14, 0.150), (0.45, 0.170), (0.78, 0.158), (0.94, 0.112), (1.0, 0.0)], L, 80)
    x, y, z = corps.v[:, 0], corps.v[:, 1], corps.v[:, 2]
    th = np.abs(np.arctan2(x, y))
    f = z / L
    bande = (f > 0.30) & (f < 0.74)
    k = ((f - 0.30) / 0.040)
    frac = k - np.floor(k)
    # le gradin : chaque bande se bombe puis retombe au joint
    pente = np.where(bande & (th < 2.15), 1.0 + 0.045 * np.sin(np.pi * frac), 1.0)
    corps.v[:, 0] *= pente
    corps.v[:, 1] *= pente
    corps.v[:, 1] += 0.016 * np.where(th < 1.9, 1.0, 0.0)                              # le dôme : le dessus plus bombé
    t = np.tile(PLAQUE, (len(z), 1))
    t[bande & (frac < 0.12)] = JOINT
    t[(f < 0.26) | (f > 0.78)] = CUIR * 0.96
    t[(f < 0.30) & (f > 0.25)] = JOINT                                                  # le joint du bouclier d'épaule
    t[(f > 0.74) & (f < 0.79)] = JOINT                                                  # le joint du bouclier de croupe
    t[th > 2.15] = VENTRE                                                               # le dessous nu
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- la tête : un coin, le museau pointu ; deux yeux petits mais nets ; de longues oreilles en tuyau fermé -----
    H = A.cadre(Vector((0.0, -0.320, 0.150)), Vector((0.0, -1.0, -0.30)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.056), (0.22, 0.070), (0.46, 0.056), (0.74, 0.038), (0.95, 0.026), (1.0, 0.0)], 0.300, 48, 0.005)
    tete.v[:, 1] *= 0.80
    tete.teinte = np.tile(CUIR, (len(tete.v), 1))
    tete.teinte[(tete.v[:, 2] > 0.05) & (tete.v[:, 2] < 0.075)] = JOINT                # le bandeau à la nuque
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0, -0.050)))
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.018, 0.014, 0.014), tuple(JOINT), mat=H @ A.repere((0, 0.004, 0.252)), poil=False)
    a.tete = H @ Vector((0, 0.0, 0.140))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.58, 0.40, 0.46))                         # sur l'avant de la tête : les deux yeux de face
        p, n = a.surface("tete", H @ Vector((0, 0.0, 0.050)), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0190)
        po = A.profil([(0, 0), (0.020, 0.008), (0.026, 0.050), (0.020, 0.100), (0.010, 0.128), (0, 0.138)], 6)
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.60, 1.0), tuple(CUIR),
                mat=A.cadre(H @ Vector((c * 0.052, 0.040, -0.030)), H3 @ Vector((c * 0.60, 0.55, 0.30)), H3 @ Vector((c * 0.3, -0.9, 0.0))))

    # ----- les pattes : courtes, fortes, aux griffes de pelle ; une patte avant levée ; la queue : un cône cuirassé à joints -----
    for nom, x_, y_, levee in (("av_G", 0.100, -0.160, True), ("av_D", -0.100, -0.160, False), ("ar_G", 0.105, 0.150, False), ("ar_D", -0.105, 0.150, False)):
        c = 1 if x_ > 0 else -1
        bas = (x_ * 1.05, y_ - (0.090 if levee else 0.020), 0.090 if levee else 0.030)
        ch = [(x_, y_, 0.140), (x_ * 1.04, y_ - 0.030, 0.090), bas]
        fl = K.Fil([ch[0], ch[1], ch[2]], (1, 0, 0))
        m = fuseau([(0.0, 0.050), (0.45, 0.042), (0.85, 0.036), (1.0, 0.0)], fl.long, 24, 0.005)
        m.teinte = np.tile(CUIR, (len(m.v), 1))
        a.piece("patte_" + nom, m.sculpte(fl.couche), None)
        g = None
        for k_ in (-1, 0, 1):
            gr = A.tour(A.profil([(0, 0), (0.010, 0.003), (0.008, 0.028), (0.003, 0.052), (0, 0.062)], 5), 10)
            gr = gr.pose((0, 0, 0), (-78, 0, 0)).pose((k_ * 0.020, -0.020, 0.0), (0, 0, k_ * 8))
            g = gr if g is None else g + gr
        a.piece("griffes_" + nom, g, GRIFFE, pos=(bas[0], bas[1] - 0.016, bas[2] - 0.006), poil=False)
    # la queue : LONGUE et fine, annelée, qui s'effile jusqu'à la pointe (plus de cône ni de boule)
    qf = K.Fil([(0.0, 0.240, 0.115), (0.0, 0.420, 0.092), (0.0, 0.620, 0.058), (0.0, 0.820, 0.030)], (1, 0, 0))
    queue = fuseau([(0.0, 0.052), (0.35, 0.036), (0.75, 0.020), (0.97, 0.010), (1.0, 0.0)], qf.long, 32, 0.004)
    queue.teinte = np.where(((queue.v[:, 2] / 0.034) % 1.0 < 0.18)[:, None], tuple(JOINT), tuple(PLAQUE))
    a.piece("queue", queue.sculpte(qf.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tatou", styles.style_de("tatou"), sys.modules[__name__]), "Tatou")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py tatou). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.138                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.146, 0.215)),
    ('tete', 'corps', (0.007, -0.279, 0.155)),
    ('oreille_G', 'tete', (0.056, -0.309, 0.197)),
    ('patte_av_G', 'corps', (0.101, -0.187, 0.136)),
    ('patte_ar_G', 'corps', (0.106, 0.121, 0.141)),
    ('queue', 'corps', (-0.000, 0.261, 0.133)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('griffes_av', 'patte_av', True), ('griffes_ar', 'patte_ar', True),
    ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('oreille', 'oreille', True), ('corps', 'corps'),
    ('queue', 'queue'), ('tete', 'tete'), ('oeil', 'tete'), ('nez', 'tete'), ('paupiere_0', 'paupiere_0'),
    ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.042 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.076), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
