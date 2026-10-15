"""L'autruche en peluche de velours ras (2e dessin, d'après photos) : un gros corps ovoïde d'un noir velouté, les ailes et
la queue en panaches de plumes BLANCHES bouclées, un très long cou rosé presque nu en S qui porte une toute petite tête
au grand œil à longs cils et au bec plat et large, et deux très longues jambes roses et épaisses, à deux gros orteils,
plantées bien droites sous le corps. Elle se tient haut, droite, le cou dressé, la tête tournée vers nous : la plus
grande des oiseaux, et la plus perplexe.

    python autruche.py        fabrique la fiche art/apercus/animaux/autruche.png (velours ras, palier 3)
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


ENCRE = np.array(M.hexa("#4a4650"))           # la dominante : noir d'encre velouté (le poil le fonce : on le prend plus clair)
BLANC = np.array(M.hexa("#fffaf2"))           # les plumes des ailes et de la queue
ROSE = np.array(M.hexa("#e8a8a0"))            # le cou, les jambes
BEC = M.hexa("#c89484")                         # le bec : rose sombre, plus foncé que la tête
OEIL = M.hexa("#7a4a30")
CHARBON = M.hexa("#3a3236")
LACET = 30.0


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=36, pas=0.006):
    """Le cou du flamant rose gardé par l'auteur : une pièce tournée très finement échantillonnée (fraction, rayon), couchée
    ensuite le long d'une courbe ; les deux bouts se referment en calotte arrondie."""
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("autruche")
    a.taille = 2.30

    # ----- le corps : un gros œuf noir, le dos un peu plus haut derrière, posé haut sur les jambes -----
    def oeuf(v):
        v = K.bosse(v, (0, -0.75, 0.30), 0.14, 0.40)
        return v * [0.230, 0.320, 0.250]
    corps = A.boule(1.0, 56, 28)
    corps.teinte = np.tile(ENCRE, (len(corps.v), 1))
    a.piece("corps", corps.sculpte(oeuf), None, pos=(0.0, 0.060, 0.740), rot=(8, 0, 0))

    # ----- les plumes : deux grandes ailes blanches en éventail sur les flancs, qui retombent ; la queue en panache dressé -----
    for nom, c in (("G", 1), ("D", -1)):
        aile = A.boule(1.0, 36, 18)
        aile.teinte = np.tile(BLANC, (len(aile.v), 1))
        a.piece("aile_" + nom, aile.etire(0.080, 0.230, 0.190), None, pos=(c * 0.230, 0.090, 0.780), rot=(10, 0, c * 14))
        a.piece("aile_bas_" + nom, A.boule(1.0, 28, 14).etire(0.060, 0.180, 0.110), tuple(BLANC), pos=(c * 0.250, 0.140, 0.640), rot=(18, 0, c * 18))
    for k, (dx, dy, dz, rx) in enumerate(((0.0, 0.350, 0.880, -34), (0.090, 0.340, 0.840, -22), (-0.090, 0.340, 0.840, -22))):
        a.piece("queue_%d" % k, A.boule(1.0, 28, 14).etire(0.070, 0.050, 0.180), tuple(BLANC), pos=(dx, dy, dz), rot=(rx, 0, dx * 90))

    # ----- le cou et la tête, refaits comme ceux du flamant rose gardé : un cou d'une pièce, épais à la base, qui s'amincit
    #       en S doux ; une tête ronde ; un bec plat et large, rose sombre, la pointe noire -----
    BASE = Vector((0.0, -0.150, 0.900))
    pts = ((0.0, 0.0), (0.050, 0.200), (0.110, 0.430), (0.120, 0.640), (0.090, 0.840), (0.130, 0.755))
    pts = ((0.0, 0.0), (-0.040, 0.230), (-0.115, 0.470), (-0.095, 0.680), (-0.140, 0.900), (-0.110, 0.755))
    chemin = ((0.0, 0.0), (-0.060, 0.200), (-0.130, 0.420), (-0.110, 0.620), (-0.130, 0.800))
    enc = K.Fil([tuple(BASE + Vector((0, u, z))) for u, z in chemin], (1, 0, 0))
    Lc = enc.long
    cou = fuseau([(0.0, 0.090), (0.12, 0.066), (0.45, 0.040), (0.85, 0.034), (1.0, 0.040)], Lc, 36)
    cou.teinte = np.tile(ROSE, (len(cou.v), 1))
    a.piece("cou", cou.sculpte(enc.couche), None, poil=False)
    centre, avant, nuque = enc.cadre(Lc)
    H = A.cadre(Vector(centre) + Vector((0.0, -0.030, 0.012)), Vector((0.0, -1.0, -0.12)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 36, 18)
    tete.teinte = np.tile(ROSE, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.054, 0.060, 0.062), None, mat=H, poil=False)
    a.tete = H @ Vector((0, 0.0, 0.110))
    bec = A.tour(A.profil([(0, 0), (0.046, 0.008), (0.050, 0.040), (0.044, 0.082), (0.032, 0.112), (0.014, 0.130), (0, 0.138)], 6), 32)
    K.bandes(bec, [(0.100, tuple(BEC)), (9, tuple(CHARBON))])
    a.piece("bec", bec.etire(1.0, 0.46, 1.0), None, mat=H @ A.repere((0, 0.004, 0.040)), poil=False)
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.70, 0.30, 0.50))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.26, OEIL, 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0200)

    # ----- les jambes : très longues, épaisses, roses, le genou en arrière ; deux gros orteils ; bien droites sous le corps -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.100, 0.060, 0.600), (c * 0.108, 0.040, 0.420), (c * 0.108, 0.075, 0.220), (c * 0.108, 0.060, 0.040)]
        m = A.tube(A.courbe(propres(ch), 6), lambda t: 0.050 - 0.020 * t, 16)
        m.teinte = np.tile(ROSE, (len(m.v), 1))
        a.piece("jambe_" + nom, m, None, poil=False)
        a.piece("orteil_" + nom, A.boule(1.0, 20, 10).etire(0.034, 0.090, 0.028), tuple(ROSE), pos=(c * 0.112, -0.010, 0.030))
        a.piece("petit_orteil_" + nom, A.boule(1.0, 16, 8).etire(0.022, 0.050, 0.022), tuple(ROSE), pos=(c * 0.160, 0.020, 0.024), rot=(0, 0, c * -18))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("autruche", styles.style_de("autruche"), sys.modules[__name__]), "Autruche")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py autruche). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.329                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.209, 0.150)),
    ('cou', 'corps', (0.000, -0.182, 0.898)),
    ('tete', 'cou', (-0.003, -0.281, 1.618)),
    ('patte_ar_G', 'corps', (0.101, 0.058, 0.601)),
    ('patte_av_G', 'corps', (0.114, 0.007, 0.057)),
    ('aile_G', 'corps', (0.230, 0.089, 0.964)),
    ('queue', 'corps', (0.002, 0.276, 0.676)),
]

PORTEURS = [
    ('narine', 'tete'),
    ('petit_orteil', 'corps'), ('oeil_reflet', 'tete'), ('aile_bas', 'aile', True), ('queue_0', 'queue'),
    ('queue_1', 'queue'), ('queue_2', 'queue'), ('orteil', 'patte_av', True), ('corps', 'corps'),
    ('jambe', 'patte_ar', True), ('aile', 'aile', True), ('tete', 'tete'), ('iris', 'tete'), ('oeil', 'tete'),
    ('cils', 'tete'), ('cou', 'cou'), ('bec', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
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
    p.add('queue', rot=(0, 0, 10 * onde(t, 1)))
    p.paire('aile', rot=(0, -3 * cloche(t, 0.55, 0.06), 0))
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
    p.add('cou', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('tete', rot=(3 - 2 * onde(t, 2, -0.2), -2 * c, -2 * s))
    p.add('queue', rot=(-6, 0, -10 * s))
    p.paire('aile', rot=(0, -2 + 2 * onde(t, 2), 0))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.099 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    p.paire('aile', rot=(0, -48 * vol, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.02), rot=(36, 0, 6), ech=(1 + 0.010 * r, 1, 1 + 0.020 * r))
    p.paire('patte_av', rot=(-30, 0, 0))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
